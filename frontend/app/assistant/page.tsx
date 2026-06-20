import ChatPanel from "@/components/ChatPanel";

export default function AssistantPage() {
  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      <div>
        <h2 className="text-xl font-semibold text-slate-800">Assistant</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Ask about your spending, subscriptions, or budget — grounded in your
          real transaction data.
        </p>
      </div>

      <ChatPanel className="flex-1 min-h-[28rem]" />
    </div>
  );
}
