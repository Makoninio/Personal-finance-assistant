"use client";

import { useEffect, useMemo, useState } from "react";
import {
  createBudget,
  deleteBudget,
  getBudgets,
  getTransactions,
  type Budget,
} from "@/lib/api";

function formatCurrency(amount: number): string {
  return amount.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

function progressColor(ratio: number): string {
  if (ratio >= 1) return "bg-red-500";
  if (ratio >= 0.85) return "bg-amber-500";
  return "bg-teal-500";
}

function progressTextColor(ratio: number): string {
  if (ratio >= 1) return "text-red-600";
  if (ratio >= 0.85) return "text-amber-600";
  return "text-slate-600";
}

function SkeletonCard() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="h-4 w-32 animate-pulse rounded bg-slate-100" />
      <div className="mt-3 h-2 w-full animate-pulse rounded-full bg-slate-100" />
      <div className="mt-2 h-3 w-24 animate-pulse rounded bg-slate-100" />
    </div>
  );
}

type LoadState = "loading" | "ready" | "error";

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categoryMap, setCategoryMap] = useState<Map<string, number>>(new Map());
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [selectedCategory, setSelectedCategory] = useState("");
  const [amountLimit, setAmountLimit] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  async function loadAll() {
    setState("loading");
    setErrorMessage(null);
    try {
      const [budgetList, transactions] = await Promise.all([getBudgets(), getTransactions()]);
      setBudgets(budgetList);

      const map = new Map<string, number>();
      for (const tx of transactions) {
        const name = tx.category;
        const id = tx.category_id;
        if (name && id !== undefined && id !== null && !map.has(name)) {
          map.set(name, Number(id));
        }
      }
      setCategoryMap(map);
      setState("ready");
    } catch {
      setErrorMessage("Could not reach the backend. Make sure the API server is running.");
      setState("error");
    }
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setState("loading");
      setErrorMessage(null);
      try {
        const [budgetList, transactions] = await Promise.all([getBudgets(), getTransactions()]);
        if (cancelled) return;
        setBudgets(budgetList);

        const map = new Map<string, number>();
        for (const tx of transactions) {
          const name = tx.category;
          const id = tx.category_id;
          if (name && id !== undefined && id !== null && !map.has(name)) {
            map.set(name, Number(id));
          }
        }
        setCategoryMap(map);
        setState("ready");
      } catch {
        if (cancelled) return;
        setErrorMessage("Could not reach the backend. Make sure the API server is running.");
        setState("error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const categoryOptions = useMemo(() => Array.from(categoryMap.keys()).sort(), [categoryMap]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    const categoryId = categoryMap.get(selectedCategory);
    const limit = parseFloat(amountLimit);

    if (!selectedCategory || categoryId === undefined) {
      setFormError("Choose a category.");
      return;
    }
    if (!amountLimit || Number.isNaN(limit) || limit <= 0) {
      setFormError("Enter a valid amount limit greater than 0.");
      return;
    }

    setSubmitting(true);
    try {
      await createBudget({ category_id: categoryId, amount_limit: limit });
      setSelectedCategory("");
      setAmountLimit("");
      await loadAll();
    } catch {
      setFormError("Could not create the budget — the backend may be unreachable.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await deleteBudget(id);
      setBudgets((prev) => prev.filter((b) => b.id !== id));
    } catch {
      setErrorMessage("Could not delete the budget — the backend may be unreachable.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-slate-800">Budgets</h2>

      {errorMessage && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700">
          {errorMessage}
        </div>
      )}

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-800">Create a budget</h3>
        <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex flex-1 flex-col gap-1">
            <label htmlFor="category" className="text-xs font-medium text-slate-500">
              Category
            </label>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              disabled={state !== "ready" || categoryOptions.length === 0}
              className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-teal-500 focus:outline-none disabled:opacity-60"
            >
              <option value="">Select a category…</option>
              {categoryOptions.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-1 flex-col gap-1">
            <label htmlFor="amount" className="text-xs font-medium text-slate-500">
              Monthly limit ($)
            </label>
            <input
              id="amount"
              type="number"
              min="0"
              step="0.01"
              value={amountLimit}
              onChange={(e) => setAmountLimit(e.target.value)}
              placeholder="e.g. 300"
              className="rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-800 tabular-nums focus:border-teal-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={submitting || state !== "ready"}
            className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Adding…" : "Add budget"}
          </button>
        </form>
        {formError && <p className="mt-2 text-sm text-red-600">{formError}</p>}
        {state === "ready" && categoryOptions.length === 0 && (
          <p className="mt-2 text-sm text-slate-500">
            No categories found yet — add some transactions first.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {state === "loading" &&
          [0, 1, 2].map((i) => <SkeletonCard key={i} />)}

        {state === "ready" &&
          budgets.map((budget) => {
            const ratio = budget.amount_limit > 0 ? budget.spent_this_period / budget.amount_limit : 0;
            const widthPct = Math.max(2, Math.min(100, ratio * 100));
            return (
              <div key={budget.id} className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-slate-800">{budget.category_name ?? "Uncategorized"}</p>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{budget.period}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(budget.id)}
                    disabled={deletingId === budget.id}
                    className="text-xs font-medium text-slate-400 hover:text-red-600 disabled:opacity-50"
                  >
                    {deletingId === budget.id ? "Removing…" : "Delete"}
                  </button>
                </div>

                <div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full transition-all ${progressColor(ratio)}`}
                      style={{ width: `${widthPct}%` }}
                    />
                  </div>
                  <div className="mt-1.5 flex items-center justify-between text-xs">
                    <span className={`tabular-nums font-medium ${progressTextColor(ratio)}`}>
                      {formatCurrency(budget.spent_this_period)} spent
                    </span>
                    <span className="tabular-nums text-slate-500">
                      of {formatCurrency(budget.amount_limit)}
                    </span>
                  </div>
                  {ratio >= 1 && (
                    <p className="mt-1 text-xs font-medium text-red-600">Over budget this period.</p>
                  )}
                  {ratio >= 0.85 && ratio < 1 && (
                    <p className="mt-1 text-xs font-medium text-amber-600">Approaching the limit.</p>
                  )}
                </div>
              </div>
            );
          })}
      </div>

      {state === "ready" && budgets.length === 0 && (
        <div className="rounded-lg border border-slate-200 bg-white px-6 py-10 text-center text-sm text-slate-500">
          No budgets yet — create one above to start tracking a category against a monthly limit.
        </div>
      )}
    </div>
  );
}
