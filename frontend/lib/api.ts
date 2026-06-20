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
    let detail: string | undefined;
    try {
      const body = await res.json();
      detail = typeof body?.detail === "string" ? body.detail : undefined;
    } catch {
      // response wasn't JSON — fall back to the generic message below.
    }
    throw new Error(detail || `Request to ${path} failed with status ${res.status}`);
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

export type Account = {
  id: number;
  institution_id: number;
  institution_name?: string | null;
  plaid_account_id: string;
  name: string;
  type?: string | null;
  mask?: string | null;
  current_balance?: number | null;
  available_balance?: number | null;
};

/** POST /plaid/create_link_token — returns a Plaid Link token to start the hosted Link flow. */
export async function createLinkToken(): Promise<{ link_token: string }> {
  return apiFetch<{ link_token: string }>("/plaid/create_link_token", {
    method: "POST",
  });
}

/** POST /plaid/exchange_public_token — exchanges Link's public_token for accounts + an initial sync. */
export async function exchangePublicToken(publicToken: string): Promise<Account[]> {
  return apiFetch<Account[]>("/plaid/exchange_public_token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ public_token: publicToken }),
  });
}

/** GET /accounts — returns all linked accounts (with their institution name). */
export async function getAccounts(): Promise<Account[]> {
  return apiFetch<Account[]>("/accounts");
}

/** POST /plaid/sync/{institutionId} — manually re-trigger a transactions sync for one institution. */
export async function syncInstitution(
  institutionId: number
): Promise<{ added: number; modified: number; removed: number }> {
  return apiFetch<{ added: number; modified: number; removed: number }>(
    `/plaid/sync/${institutionId}`,
    { method: "POST" }
  );
}

export type ChatRole = "user" | "assistant";

export type ChatHistoryMessage = {
  role: string;
  content: string;
};

export type ChatResponse = {
  reply: string;
};

/**
 * POST /agent/chat — sends a message (plus prior conversation turns) to the
 * LangGraph-backed finance assistant and returns its reply. Throws if the
 * backend returns a non-2xx response (e.g. 400 when OPENAI_API_KEY isn't
 * configured) — the thrown Error's message is the backend's `detail` field
 * when available.
 */
export async function sendChatMessage(
  message: string,
  history: ChatHistoryMessage[]
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/agent/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history }),
  });
}

export type NetWorthSnapshot = {
  total_income: number;
  total_expenses: number;
  net_worth: number;
};

export type CategoryBreakdownEntry = {
  category: string;
  total_spent: number;
  transaction_count: number;
  avg_transaction: number;
  percentage: number;
};

export type MonthlyTrendEntry = {
  month: string;
  total_income: number;
  total_expenses: number;
  net: number;
};

export type TopMerchantEntry = {
  description: string;
  total_spent: number;
  transaction_count: number;
  avg_transaction: number;
};

export type SpendingVelocity = {
  daily_avg: number;
  weekly_avg: number;
  monthly_avg: number;
};

export type HealthScore = {
  score: number;
  factors: string[];
  subscription_count: number;
};

export type InsightsSummary = {
  net_worth: NetWorthSnapshot;
  category_breakdown: CategoryBreakdownEntry[];
  monthly_trends: MonthlyTrendEntry[];
  top_merchants: TopMerchantEntry[];
  spending_velocity: SpendingVelocity;
  health_score: HealthScore;
  budget_recommendations: string[];
};

/** GET /insights/summary — aggregate payload powering the dashboard page. */
export async function getInsightsSummary(): Promise<InsightsSummary> {
  return apiFetch<InsightsSummary>("/insights/summary");
}

export type SubscriptionStatus = "active" | "cancelled_flagged" | "dismissed" | string;

export type Subscription = {
  id: number;
  merchant_name: string;
  amount: number;
  cadence: string;
  first_seen_date: string;
  last_seen_date: string;
  status: SubscriptionStatus;
  detected_by: string;
};

/** GET /subscriptions — list of detected recurring charges. */
export async function getSubscriptions(): Promise<Subscription[]> {
  return apiFetch<Subscription[]>("/subscriptions");
}

/** POST /subscriptions/detect — re-runs detection and returns the refreshed list. */
export async function detectSubscriptions(): Promise<Subscription[]> {
  return apiFetch<Subscription[]>("/subscriptions/detect", { method: "POST" });
}

export type Budget = {
  id: number;
  category_id: number;
  category_name?: string | null;
  period: string;
  amount_limit: number;
  effective_from: string;
  spent_this_period: number;
};

export type BudgetCreatePayload = {
  category_id: number;
  amount_limit: number;
  period?: string;
};

/** GET /budgets — list of configured category budgets. */
export async function getBudgets(): Promise<Budget[]> {
  return apiFetch<Budget[]>("/budgets");
}

/** POST /budgets — creates a budget for a category. */
export async function createBudget(payload: BudgetCreatePayload): Promise<Budget> {
  return apiFetch<Budget>("/budgets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** DELETE /budgets/{id} — removes a budget. */
export async function deleteBudget(id: number | string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/budgets/${id}`, {
    method: "DELETE",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Request to /budgets/${id} failed with status ${res.status}`);
  }
}

export type ConfigStatus = {
  openai_configured: boolean;
  plaid_configured: boolean;
};

/** GET /config/status — which integrations are wired up server-side, never secret values. */
export async function getConfigStatus(): Promise<ConfigStatus> {
  return apiFetch<ConfigStatus>("/config/status");
}
