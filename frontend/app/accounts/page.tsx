"use client";

import { useCallback, useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import {
  createLinkToken,
  exchangePublicToken,
  getAccounts,
  syncInstitution,
  type Account,
} from "@/lib/api";

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

type GroupedInstitution = {
  institutionId: number;
  institutionName: string;
  accounts: Account[];
};

function groupByInstitution(accounts: Account[]): GroupedInstitution[] {
  const groups = new Map<number, GroupedInstitution>();
  for (const account of accounts) {
    const existing = groups.get(account.institution_id);
    if (existing) {
      existing.accounts.push(account);
    } else {
      groups.set(account.institution_id, {
        institutionId: account.institution_id,
        institutionName: account.institution_name ?? "Linked Bank",
        accounts: [account],
      });
    }
  }
  return Array.from(groups.values());
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(true);
  const [accountsError, setAccountsError] = useState<string | null>(null);

  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);

  const [syncingInstitutionId, setSyncingInstitutionId] = useState<number | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const loadAccounts = useCallback(async () => {
    setLoadingAccounts(true);
    setAccountsError(null);
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch {
      setAccountsError("Could not reach the backend to load accounts.");
    } finally {
      setLoadingAccounts(false);
    }
  }, []);

  // Fetch on mount without calling the setState-bearing callback directly
  // from the effect body — state updates happen inside the .then() closure.
  // (loadingAccounts/accountsError already start at their "loading" defaults above.)
  useEffect(() => {
    let cancelled = false;
    getAccounts()
      .then((data) => {
        if (!cancelled) setAccounts(data);
      })
      .catch(() => {
        if (!cancelled) setAccountsError("Could not reach the backend to load accounts.");
      })
      .finally(() => {
        if (!cancelled) setLoadingAccounts(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const onSuccess = useCallback(
    async (publicToken: string) => {
      setConnecting(true);
      setConnectError(null);
      try {
        await exchangePublicToken(publicToken);
        await loadAccounts();
      } catch {
        setConnectError("Linked with Plaid, but saving the account failed. Try syncing again below.");
      } finally {
        setConnecting(false);
        setLinkToken(null);
      }
    },
    [loadAccounts]
  );

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess,
    onExit: () => setConnecting(false),
  });

  // Auto-open Link as soon as the token arrives and the script is ready.
  useEffect(() => {
    if (linkToken && ready) {
      open();
    }
  }, [linkToken, ready, open]);

  async function handleConnectBank() {
    setConnectError(null);
    setConnecting(true);
    try {
      const { link_token } = await createLinkToken();
      setLinkToken(link_token);
    } catch (err) {
      setConnecting(false);
      const message = err instanceof Error ? err.message : "Could not start Plaid Link.";
      setConnectError(
        message.includes("400")
          ? "Plaid is not configured on the backend yet — add PLAID_CLIENT_ID and PLAID_SECRET to backend/.env."
          : "Could not start Plaid Link. Is the backend running?"
      );
    }
  }

  async function handleSync(institutionId: number) {
    setSyncingInstitutionId(institutionId);
    setSyncMessage(null);
    try {
      const result = await syncInstitution(institutionId);
      setSyncMessage(
        `Synced: ${result.added} added, ${result.modified} updated, ${result.removed} removed.`
      );
      await loadAccounts();
    } catch {
      setSyncMessage("Sync failed — is the backend reachable?");
    } finally {
      setSyncingInstitutionId(null);
    }
  }

  const groups = groupByInstitution(accounts);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-800">Accounts</h2>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">Connect a bank account</h3>
            <p className="mt-1 max-w-xl text-sm text-slate-500">
              Read-only access via Plaid Sandbox. We never see your real bank login. This
              demo runs against Plaid&apos;s Sandbox environment only — no real bank or
              account data is ever linked.
            </p>
          </div>
          <button
            onClick={handleConnectBank}
            disabled={connecting}
            className="inline-flex shrink-0 items-center justify-center rounded-md bg-teal-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {connecting ? "Connecting…" : "Connect a bank"}
          </button>
        </div>

        {connectError && (
          <div className="mt-3 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {connectError}
          </div>
        )}
      </div>

      {syncMessage && (
        <div className="rounded-md border border-teal-200 bg-teal-50 px-4 py-2 text-sm text-teal-700">
          {syncMessage}
        </div>
      )}

      {accountsError && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700">
          {accountsError}
        </div>
      )}

      {!loadingAccounts && !accountsError && groups.length === 0 && (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
          <p className="text-sm font-medium text-slate-700">No accounts connected yet.</p>
          <p className="mt-1 text-sm text-slate-500">
            Once you connect a bank above, its accounts and recent transactions will show
            up here — and automatically flow into Transactions and Insights too.
          </p>
        </div>
      )}

      {groups.length > 0 && (
        <div className="flex flex-col gap-4">
          {groups.map((group) => (
            <div
              key={group.institutionId}
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-800">
                  {group.institutionName}
                </h3>
                <button
                  onClick={() => handleSync(group.institutionId)}
                  disabled={syncingInstitutionId === group.institutionId}
                  className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {syncingInstitutionId === group.institutionId
                    ? "Syncing…"
                    : "Sync transactions"}
                </button>
              </div>

              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {group.accounts.map((account) => (
                  <div
                    key={account.id}
                    className="rounded-md border border-slate-100 bg-slate-50 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-800">
                        {account.name}
                      </span>
                      {account.mask && (
                        <span className="text-xs text-slate-400">•••• {account.mask}</span>
                      )}
                    </div>
                    {account.type && (
                      <div className="mt-0.5 text-xs capitalize text-slate-500">
                        {account.type}
                      </div>
                    )}
                    <div className="mt-3 flex items-baseline justify-between">
                      <span className="text-xs text-slate-500">Current</span>
                      <span className="tabular-nums text-sm font-semibold text-slate-800">
                        {formatCurrency(account.current_balance)}
                      </span>
                    </div>
                    <div className="mt-1 flex items-baseline justify-between">
                      <span className="text-xs text-slate-500">Available</span>
                      <span className="tabular-nums text-sm text-slate-600">
                        {formatCurrency(account.available_balance)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
