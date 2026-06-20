"use client";

import { useEffect, useState } from "react";
import { detectSubscriptions, getSubscriptions, type Subscription } from "@/lib/api";

function formatCurrency(amount: number): string {
  return amount.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

function formatDate(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, string> = {
    active: "bg-emerald-50 text-emerald-700 border-emerald-200",
    cancelled_flagged: "bg-amber-50 text-amber-700 border-amber-200",
    dismissed: "bg-slate-100 text-slate-500 border-slate-200",
  };
  const classes = config[status] ?? "bg-slate-100 text-slate-500 border-slate-200";
  const label = status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${classes}`}>
      {label}
    </span>
  );
}

function SkeletonRows() {
  return (
    <tbody>
      {[0, 1, 2].map((i) => (
        <tr key={i} className="border-b border-slate-100 last:border-b-0">
          {[0, 1, 2, 3, 4].map((j) => (
            <td key={j} className="px-4 py-3">
              <div className="h-4 w-full max-w-[140px] animate-pulse rounded bg-slate-100" />
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}

type LoadState = "loading" | "ready" | "error";

export default function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [scanning, setScanning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getSubscriptions()
      .then((data) => {
        if (cancelled) return;
        setSubscriptions(data);
        setState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setErrorMessage("Could not reach the backend. Make sure the API server is running.");
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleScan() {
    setScanning(true);
    setErrorMessage(null);
    try {
      const data = await detectSubscriptions();
      setSubscriptions(data);
      setState("ready");
    } catch {
      setErrorMessage("Scan failed — could not reach the backend.");
    } finally {
      setScanning(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-800">Subscriptions</h2>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {scanning ? "Scanning…" : "Scan for subscriptions"}
        </button>
      </div>

      {errorMessage && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700">
          {errorMessage}
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="w-full min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3">Merchant</th>
              <th className="px-4 py-3">Cadence</th>
              <th className="px-4 py-3">Last charged</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Amount</th>
            </tr>
          </thead>
          {state === "loading" ? (
            <SkeletonRows />
          ) : (
            <tbody>
              {subscriptions.map((sub) => (
                <tr key={sub.id} className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{sub.merchant_name}</td>
                  <td className="px-4 py-3 capitalize text-slate-600">{sub.cadence}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                    {formatDate(sub.last_seen_date)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={sub.status} />
                  </td>
                  <td className="tabular-nums whitespace-nowrap px-4 py-3 text-right font-medium text-slate-800">
                    {formatCurrency(sub.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          )}
        </table>

        {state === "ready" && subscriptions.length === 0 && (
          <div className="px-6 py-10 text-center text-sm text-slate-500">
            <p className="font-medium text-slate-600">No subscriptions detected yet.</p>
            <p className="mx-auto mt-1 max-w-md">
              Once you connect a bank or upload statements with recurring charges like Netflix or
              Spotify, we&apos;ll detect them here automatically. You can also trigger a scan manually
              with the button above.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
