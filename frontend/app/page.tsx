import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold text-slate-800">Dashboard</h2>
      <p className="max-w-md text-sm text-slate-500">
        This is a placeholder for the dashboard. Tonight&apos;s vertical slice
        focuses on the{" "}
        <Link href="/transactions" className="font-medium text-teal-600 hover:underline">
          Transactions
        </Link>{" "}
        page.
      </p>
    </div>
  );
}
