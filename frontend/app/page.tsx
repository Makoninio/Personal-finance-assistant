import { getInsightsSummary, getSubscriptions, type InsightsSummary } from "@/lib/api";

// Avoid static caching — this page should reflect live backend state on
// every request (and the dev server shouldn't cache a fetch failure).
export const dynamic = "force-dynamic";

function formatCurrency(amount: number): string {
  const formatted = Math.abs(amount).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
  });
  return amount < 0 ? `-${formatted}` : formatted;
}

function healthScoreColor(score: number): { ring: string; text: string } {
  if (score >= 70) return { ring: "stroke-emerald-500", text: "text-emerald-600" };
  if (score >= 40) return { ring: "stroke-amber-500", text: "text-amber-600" };
  return { ring: "stroke-red-500", text: "text-red-600" };
}

type LoadResult =
  | { ok: true; summary: InsightsSummary; subscriptionCount: number }
  | { ok: false; error: string };

async function loadDashboardData(): Promise<LoadResult> {
  try {
    const [summary, subscriptions] = await Promise.all([
      getInsightsSummary(),
      getSubscriptions().catch(() => []),
    ]);
    const activeSubscriptions = subscriptions.filter((s) => s.status === "active").length;
    return { ok: true, summary, subscriptionCount: activeSubscriptions };
  } catch {
    return {
      ok: false,
      error: "Could not reach the backend. Showing nothing to report yet — start the API server and refresh.",
    };
  }
}

function ScoreRing({ score }: { score: number }) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - clamped / 100);
  const colors = healthScoreColor(clamped);

  return (
    <div className="relative flex h-16 w-16 flex-shrink-0 items-center justify-center">
      <svg viewBox="0 0 64 64" className="h-16 w-16 -rotate-90">
        <circle
          cx="32"
          cy="32"
          r={radius}
          fill="none"
          strokeWidth="6"
          className="stroke-slate-100"
        />
        <circle
          cx="32"
          cy="32"
          r={radius}
          fill="none"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={colors.ring}
        />
      </svg>
      <span className={`absolute text-sm font-semibold tabular-nums ${colors.text}`}>
        {clamped}
      </span>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  valueClassName,
  children,
}: {
  label: string;
  value: string;
  valueClassName?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
        <p className={`mt-1 text-2xl font-semibold tabular-nums ${valueClassName ?? "text-slate-800"}`}>
          {value}
        </p>
      </div>
      {children}
    </div>
  );
}

function CategoryBreakdownCard({ summary }: { summary: InsightsSummary }) {
  const rows = summary.category_breakdown;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-800">Spending by category</h3>
      {rows.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">
          No categorized expenses yet — once transactions come in, the breakdown shows up here.
        </p>
      ) : (
        <ul className="mt-4 flex flex-col gap-3">
          {rows.map((row) => (
            <li key={row.category} className="flex flex-col gap-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-slate-700">{row.category}</span>
                <span className="tabular-nums text-slate-500">
                  {formatCurrency(row.total_spent)} &middot; {row.percentage.toFixed(1)}%
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-teal-500"
                  style={{ width: `${Math.max(2, Math.min(100, row.percentage))}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function MonthlyTrendCard({ summary }: { summary: InsightsSummary }) {
  const rows = summary.monthly_trends;
  const maxValue = Math.max(1, ...rows.map((r) => Math.max(r.total_income, r.total_expenses)));

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-800">Monthly trend</h3>
      {rows.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No monthly history yet.</p>
      ) : (
        <div className="mt-4 flex flex-col gap-4">
          {rows.map((row) => (
            <div key={row.month} className="flex flex-col gap-1">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-medium text-slate-700">{row.month}</span>
                <span className="tabular-nums">
                  Net{" "}
                  <span className={row.net >= 0 ? "text-emerald-600" : "text-red-600"}>
                    {formatCurrency(row.net)}
                  </span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-14 text-right text-[11px] text-slate-400">Income</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${(row.total_income / maxValue) * 100}%` }}
                  />
                </div>
                <span className="w-20 tabular-nums text-right text-[11px] text-slate-500">
                  {formatCurrency(row.total_income)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-14 text-right text-[11px] text-slate-400">Expenses</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-red-400"
                    style={{ width: `${(row.total_expenses / maxValue) * 100}%` }}
                  />
                </div>
                <span className="w-20 tabular-nums text-right text-[11px] text-slate-500">
                  {formatCurrency(row.total_expenses)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function BudgetRecommendationsCard({ summary }: { summary: InsightsSummary }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-800">Budget recommendations</h3>
      {summary.budget_recommendations.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No recommendations right now.</p>
      ) : (
        <ul className="mt-3 flex flex-col gap-2">
          {summary.budget_recommendations.map((rec, idx) => (
            <li
              key={idx}
              className="flex items-start gap-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700"
            >
              <span className="mt-0.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-teal-500" aria-hidden="true" />
              {rec}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default async function Home() {
  const result = await loadDashboardData();

  if (!result.ok) {
    return (
      <div className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold text-slate-800">Dashboard</h2>
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {result.error}
        </div>
      </div>
    );
  }

  const { summary, subscriptionCount } = result;

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-slate-800">Dashboard</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          label="Net worth"
          value={formatCurrency(summary.net_worth.net_worth)}
          valueClassName={summary.net_worth.net_worth >= 0 ? "text-emerald-600" : "text-red-600"}
        />
        <SummaryCard label="This month's spend" value={formatCurrency(summary.net_worth.total_expenses)} />
        <SummaryCard
          label="Financial health"
          value={`${summary.health_score.score} / 100`}
        >
          <ScoreRing score={summary.health_score.score} />
        </SummaryCard>
        <SummaryCard label="Active subscriptions" value={String(subscriptionCount)} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategoryBreakdownCard summary={summary} />
        <MonthlyTrendCard summary={summary} />
      </div>

      <BudgetRecommendationsCard summary={summary} />
    </div>
  );
}
