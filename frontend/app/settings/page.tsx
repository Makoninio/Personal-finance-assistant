"use client";

import { useEffect, useState } from "react";
import { getConfigStatus, type ConfigStatus } from "@/lib/api";

type LoadState = "loading" | "ready" | "error";

function StatusBadge({ connected }: { connected: boolean }) {
  return connected ? (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden="true" />
      Connected
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" aria-hidden="true" />
      Not configured
    </span>
  );
}

function ConnectionRow({
  title,
  connected,
  instructions,
}: {
  title: string;
  connected: boolean;
  instructions: string;
}) {
  return (
    <div className="flex flex-col gap-2 border-b border-slate-100 px-5 py-4 last:border-b-0 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="font-medium text-slate-800">{title}</p>
        {!connected && <p className="mt-0.5 text-sm text-slate-500">{instructions}</p>}
      </div>
      <StatusBadge connected={connected} />
    </div>
  );
}

function SkeletonRow() {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4 last:border-b-0">
      <div className="h-4 w-48 animate-pulse rounded bg-slate-100" />
      <div className="h-6 w-24 animate-pulse rounded-full bg-slate-100" />
    </div>
  );
}

export default function SettingsPage() {
  const [status, setStatus] = useState<ConfigStatus | null>(null);
  const [state, setState] = useState<LoadState>("loading");

  useEffect(() => {
    let cancelled = false;
    getConfigStatus()
      .then((res) => {
        if (!cancelled) {
          setStatus(res);
          setState("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-slate-800">Settings</h2>

      <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h3 className="text-sm font-semibold text-slate-800">Connections</h3>
          <p className="mt-0.5 text-sm text-slate-500">
            Status of integrations configured server-side. Keys are never exposed to the browser.
          </p>
        </div>

        {state === "loading" && (
          <>
            <SkeletonRow />
            <SkeletonRow />
          </>
        )}

        {state === "error" && (
          <div className="px-5 py-4 text-sm text-amber-700">
            Could not reach the backend to check connection status. Make sure the API server is
            running and refresh this page.
          </div>
        )}

        {state === "ready" && status && (
          <>
            <ConnectionRow
              title="AI Assistant (OpenAI)"
              connected={status.openai_configured}
              instructions="Add OPENAI_API_KEY to backend/.env and restart the server."
            />
            <ConnectionRow
              title="Bank Connections (Plaid)"
              connected={status.plaid_configured}
              instructions="Add PLAID_CLIENT_ID and PLAID_SECRET to backend/.env and restart the server."
            />
          </>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-800">Your data, your control</h3>
        <p className="mt-2 text-sm text-slate-600">
          Your data stays in your local database. Bank connections use Plaid in Sandbox mode — no
          real bank credentials are ever sent to or stored by this app. API keys live only in{" "}
          <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">backend/.env</code> on your
          machine and are never returned by any endpoint.
        </p>
      </div>
    </div>
  );
}
