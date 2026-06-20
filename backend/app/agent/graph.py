"""
LangGraph-based personal finance chat agent.

Uses `langgraph.prebuilt.create_react_agent` to build a real ReAct-style
tool-calling agent graph: the LLM reasons about which tool(s) to call, the
graph executes them, feeds results back to the LLM, and loops until it's
ready to answer. This is a genuine LangGraph `StateGraph` under the hood
(not a hand-rolled one, but not a single-shot completion either) — the
pragmatic choice for grounding answers in real tool output tonight.
"""
from functools import lru_cache

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.agent.tools import ALL_TOOLS
from app.core.config import settings

SYSTEM_PROMPT = """You are a personal finance assistant embedded in a budgeting app.

You have tools that query the user's real transaction data, subscriptions,
spending trends, and financial health score. Always call the appropriate
tool(s) to get real numbers before answering questions about the user's
finances — never invent or estimate amounts, categories, or merchant names.

When relevant, cite specific transactions, categories, or dollar amounts
from the tool results to support your answer. If the data doesn't contain
what's needed to answer a question, say so plainly instead of guessing.

Keep answers concise and conversational — a few sentences, not an essay,
unless the user asks for a detailed breakdown."""


class AgentNotConfiguredError(RuntimeError):
    """Raised when the agent is invoked without an OpenAI API key configured."""


@lru_cache(maxsize=1)
def _build_agent():
    """Build (and cache) the LangGraph react agent. Cached because constructing
    the ChatOpenAI client and compiling the graph is not free, and the tool
    list/system prompt never change at runtime."""
    if not settings.openai_configured:
        raise AgentNotConfiguredError(
            "OpenAI API key not configured — add OPENAI_API_KEY to backend/.env"
        )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.openai_api_key, temperature=0)
    return create_react_agent(llm, tools=ALL_TOOLS, prompt=SYSTEM_PROMPT)


def _history_to_messages(history: list[dict]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        # System messages from history are ignored; the agent has its own system prompt.
    return messages


def run_agent(message: str, history: list[dict] | None = None) -> str:
    """Invoke the agent with a user message (plus optional prior turns) and
    return the assistant's final text reply.

    Raises AgentNotConfiguredError if OPENAI_API_KEY isn't set — callers
    (the /agent/chat route) should catch this and return a clean 400.
    """
    agent = _build_agent()

    messages = _history_to_messages(history or [])
    messages.append(HumanMessage(content=message))

    result = agent.invoke({"messages": messages})
    final_messages = result["messages"]

    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content

    return "I wasn't able to come up with a response — please try rephrasing your question."
