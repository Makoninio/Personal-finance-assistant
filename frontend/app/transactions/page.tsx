import { getTransactions, type Transaction } from "@/lib/api";
import { mockTransactions } from "@/lib/mockTransactions";

// Avoid static caching — this page should reflect live backend state on
// every request (and the dev server shouldn't cache the fetch failure).
export const dynamic = "force-dynamic";

function resolveCategory(tx: Transaction): string {
  if (tx.category) return tx.category;
  if (tx.category_id !== undefined && tx.category_id !== null) {
    return `Category ${tx.category_id}`;
  }
  return "Uncategorized";
}

function formatDate(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatAmount(amount: number): string {
  const formatted = Math.abs(amount).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
  });
  return amount < 0 ? `-${formatted}` : formatted;
}

async function loadTransactions(): Promise<{
  transactions: Transaction[];
  usingFallback: boolean;
}> {
  try {
    const transactions = await getTransactions();
    return { transactions, usingFallback: false };
  } catch {
    return { transactions: mockTransactions, usingFallback: true };
  }
}

export default async function TransactionsPage() {
  const { transactions, usingFallback } = await loadTransactions();

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-800">Transactions</h2>
      </div>

      {usingFallback && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700">
          Showing sample data — backend not reachable.
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="w-full min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => {
              const isDebit = tx.type === "debit" || tx.amount < 0;
              return (
                <tr
                  key={tx.id}
                  className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50"
                >
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                    {formatDate(tx.date)}
                  </td>
                  <td className="px-4 py-3 text-slate-800">{tx.description}</td>
                  <td className="px-4 py-3 text-slate-600">{resolveCategory(tx)}</td>
                  <td
                    className={`tabular-nums whitespace-nowrap px-4 py-3 text-right font-medium ${
                      isDebit ? "text-red-600" : "text-emerald-600"
                    }`}
                  >
                    {formatAmount(tx.amount)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {transactions.length === 0 && (
          <div className="px-4 py-6 text-center text-sm text-slate-500">
            No transactions found.
          </div>
        )}
      </div>
    </div>
  );
}
