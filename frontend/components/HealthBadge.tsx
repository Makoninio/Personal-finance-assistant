"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

type Status = "checking" | "online" | "offline";

export default function HealthBadge() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then((res) => {
        if (!cancelled) {
          setStatus(res.status === "ok" ? "online" : "offline");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("offline");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const config: Record<Status, { dot: string; label: string; text: string }> = {
    checking: {
      dot: "bg-slate-400 animate-pulse",
      label: "Checking backend…",
      text: "text-slate-500",
    },
    online: {
      dot: "bg-emerald-500",
      label: "Backend online",
      text: "text-emerald-600",
    },
    offline: {
      dot: "bg-red-500",
      label: "Backend unreachable",
      text: "text-red-600",
    },
  };

  const current = config[status];

  return (
    <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium shadow-sm">
      <span
        className={`inline-block h-2.5 w-2.5 rounded-full ${current.dot}`}
        aria-hidden="true"
      />
      <span className={current.text}>{current.label}</span>
    </div>
  );
}
