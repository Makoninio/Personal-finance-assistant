"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
  label: string;
  href: string;
  active: boolean;
};

const NAV_ITEMS: { label: string; href: string }[] = [
  { label: "Dashboard", href: "#" },
  { label: "Transactions", href: "/transactions" },
  { label: "Subscriptions", href: "#" },
  { label: "Budgets", href: "#" },
  { label: "Assistant", href: "#" },
  { label: "Settings", href: "#" },
];

export default function Sidebar() {
  const pathname = usePathname();

  const items: NavItem[] = NAV_ITEMS.map((item) => ({
    ...item,
    active: item.href !== "#" && pathname.startsWith(item.href),
  }));

  return (
    <aside className="flex h-full w-60 flex-shrink-0 flex-col bg-[#0F172A] text-slate-200">
      <div className="flex items-center gap-2 px-6 py-5">
        <div className="h-7 w-7 rounded-md bg-teal-500" aria-hidden="true" />
        <span className="text-sm font-semibold tracking-wide text-white">
          Finance Assistant
        </span>
      </div>

      <nav className="mt-2 flex-1 px-3">
        <ul className="flex flex-col gap-1">
          {items.map((item) => (
            <li key={item.label}>
              <Link
                href={item.href}
                aria-disabled={item.href === "#"}
                className={[
                  "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  item.active
                    ? "bg-teal-500/15 text-teal-400"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white",
                  item.href === "#" ? "cursor-default opacity-60" : "",
                ].join(" ")}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="px-6 py-4 text-xs text-slate-500">v0.1 &middot; vertical slice</div>
    </aside>
  );
}
