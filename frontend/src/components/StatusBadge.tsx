"use client";

import type { AgentStatus } from "@/lib/types";
import clsx from "clsx";

const CONFIG: Record<AgentStatus, { label: string; emoji: string; color: string; animate: string }> = {
  idle: { label: "Idle", emoji: "⏸️", color: "bg-gray-600", animate: "" },
  thinking: { label: "Thinking", emoji: "🟡", color: "bg-yellow-500", animate: "animate-pulse" },
  working: { label: "Working", emoji: "🔵", color: "bg-blue-500", animate: "animate-spin-slow" },
  done: { label: "Done", emoji: "🟢", color: "bg-green-500", animate: "" },
  error: { label: "Error", emoji: "🔴", color: "bg-red-500", animate: "" },
  waiting: { label: "Waiting", emoji: "⏳", color: "bg-orange-400", animate: "animate-bounce-slow" },
};

export function StatusBadge({ status }: { status: AgentStatus }) {
  const cfg = CONFIG[status] || CONFIG.idle;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium text-white",
        cfg.color,
        cfg.animate
      )}
    >
      <span>{cfg.emoji}</span>
      {cfg.label}
    </span>
  );
}

