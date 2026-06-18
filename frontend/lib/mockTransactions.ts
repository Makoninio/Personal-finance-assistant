import type { Transaction } from "./api";

// Local fallback fixture used only when the live backend is unreachable.
// Shaped identically to what GET /transactions is expected to return.
export const mockTransactions: Transaction[] = [
  {
    id: "mock-1",
    date: "2026-06-15",
    amount: 4200,
    description: "Paycheck Deposit",
    type: "credit",
    category: "Income",
  },
  {
    id: "mock-2",
    date: "2026-06-14",
    amount: -82.47,
    description: "Whole Foods Market",
    type: "debit",
    category: "Groceries",
  },
  {
    id: "mock-3",
    date: "2026-06-12",
    amount: -15.99,
    description: "Netflix Subscription",
    type: "debit",
    category_id: 7,
  },
  {
    id: "mock-4",
    date: "2026-06-10",
    amount: -64.0,
    description: "Electric Co.",
    type: "debit",
    category: "Utilities",
  },
  {
    id: "mock-5",
    date: "2026-06-08",
    amount: -23.5,
    description: "Corner Cafe",
    type: "debit",
    category: null,
  },
];
