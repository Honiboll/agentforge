"use client";

import { motion } from "framer-motion";
import type { Agent } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";
import { ThinkingAnimation } from "./ThinkingAnimation";
import { LiveLog } from "./LiveLog";
import clsx from "clsx";

const ROLE_ICONS: Record<string, string> = {
  researcher: "🔍",
  coder: "💻",
  reviewer: "✅",
  writer: "✍️",
  planner: "📋",
  custom: "⚙️",
};

const GLOW: Record<string, string> = {
  thinking: "glow-thinking",
  working: "glow-working",
  done: "glow-done",
  error: "glow-error",
};

export function AgentCard({ agent, index }: { agent: Agent; index: number }) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className={clsx(
        "relative rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-5",
        "hover:bg-[var(--bg-card-hover)] transition-all duration-300",
        GLOW[agent.status]
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{ROLE_ICONS[agent.agent_type] || "🤖"}</span>
          <div>
            <h3 className="font-semibold text-white text-sm">{agent.name}</h3>
            <p className="text-xs text-[var(--text-muted)] capitalize">{agent.role}</p>
          </div>
        </div>
        <StatusBadge status={agent.status} />
      </div>

      {/* Description */}
      <p className="text-xs text-[var(--text-muted)] mb-3 line-clamp-2">
        {agent.description}
      </p>

      {/* Thinking animation */}
      {agent.status === "thinking" && (
        <div className="flex items-center gap-2 mb-3">
          <ThinkingAnimation />
          <span className="text-xs text-yellow-400">Processing…</span>
        </div>
      )}

      {/* Live log */}
      <LiveLog logs={agent.logs} />
    </motion.div>
  );
}

