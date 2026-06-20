from fastapi import APIRouter, HTTPException

from app.agent.graph import AgentNotConfiguredError, run_agent
from app.core.config import settings
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Chat with the LangGraph-based personal finance assistant. The agent
    grounds its answers in the user's real transaction data via tool calls
    (spending summaries, transaction lookups, subscriptions, trends, health
    score) rather than inventing numbers."""
    if not settings.openai_configured:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured — add OPENAI_API_KEY to backend/.env",
        )

    history = [item.model_dump() for item in request.history]

    try:
        reply = run_agent(request.message, history)
    except AgentNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent failed to respond: {exc}") from exc

    return ChatResponse(reply=reply)
