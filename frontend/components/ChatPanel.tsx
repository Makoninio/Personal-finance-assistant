"use client";

import { useRef, useState } from "react";
import { sendChatMessage, type ChatHistoryMessage } from "@/lib/api";

type DisplayMessage = {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
};

let nextId = 0;

const NOT_CONFIGURED_HINT =
  "The assistant isn't configured yet — add an OpenAI API key in backend/.env.";

function isNotConfiguredError(message: string): boolean {
  return message.toLowerCase().includes("openai api key not configured");
}

export default function ChatPanel({ className = "" }: { className?: string }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage: DisplayMessage = { id: nextId++, role: "user", content: trimmed };
    const history: ChatHistoryMessage[] = messages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    scrollToBottom();

    try {
      const res = await sendChatMessage(trimmed, history);
      setMessages((prev) => [
        ...prev,
        { id: nextId++, role: "assistant", content: res.reply },
      ]);
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Something went wrong.";
      const friendly = isNotConfiguredError(detail) ? NOT_CONFIGURED_HINT : detail;
      setMessages((prev) => [
        ...prev,
        { id: nextId++, role: "system", content: `⚠️ ${friendly}` },
      ]);
    } finally {
      setIsLoading(false);
      scrollToBottom();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div
      className={`flex h-full min-h-0 flex-col rounded-lg border border-slate-200 bg-white shadow-sm ${className}`}
    >
      <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-center text-sm text-slate-400">
            Ask me anything about your spending, subscriptions, or budget.
          </div>
        )}

        <div className="flex flex-col gap-3">
          {messages.map((m) => {
            if (m.role === "system") {
              return (
                <div
                  key={m.id}
                  className="mx-auto rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-center text-xs text-amber-700"
                >
                  {m.content}
                </div>
              );
            }

            const isUser = m.role === "user";
            return (
              <div key={m.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm shadow-sm ${
                    isUser
                      ? "bg-teal-500 text-white"
                      : "border border-slate-200 bg-slate-50 text-slate-800"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.2s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.1s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-end gap-2 border-t border-slate-200 px-3 py-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your spending, subscriptions, or budget…"
          rows={1}
          disabled={isLoading}
          className="flex-1 resize-none rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-400 focus:outline-none focus:ring-1 focus:ring-teal-400 disabled:opacity-60"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="rounded-md bg-teal-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
