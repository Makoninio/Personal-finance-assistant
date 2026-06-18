// Small fetch wrapper for talking to the FastAPI backend.
//
// Base URL is read from NEXT_PUBLIC_API_URL (falls back to localhost:8000
// for local dev when the env var isn't set).

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type HealthResponse = {
  status: string;
};

export type TransactionType = "debit" | "credit";

export type Transaction = {
  id: string | number;
  date: string;
  amount: number;
  description: string;
  type: TransactionType;
  category?: string | null;
  category_id?: number | string | null;
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    // Always hit the network — this is a live dashboard, not static content.
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Request to ${path} failed with status ${res.status}`);
  }

  return (await res.json()) as T;
}

/** GET /health — returns { status: "ok" } when the backend is reachable. */
export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

/** GET /transactions — returns the list of transactions from the backend. */
export async function getTransactions(): Promise<Transaction[]> {
  return apiFetch<Transaction[]>("/transactions");
}
