"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { WSEvent } from "@/lib/types";

const EVENT_ICONS: Record<string, string> = {
  project_started: "🚀",
  analysis_started: "🧠",
  analysis_completed: "📋",
  agent_created: "🤖",
  agent_status_changed: "🔄",
  task_started: "▶️",
  task_completed: "✅",
  project_completed: "🎉",
};

export function AgentTimeline({ events }: { events: WSEvent[] }) {
  const meaningful = events.filter((e) => e.event !== "agent_log" && e.event !== "heartbeat");

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
      <AnimatePresence initial={false}>
        {meaningful.map((event, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-start gap-3 rounded-lg bg-[var(--bg-card)] p-3 text-sm border border-[var(--border)]"
          >
            <span className="text-lg shrink-0">
              {EVENT_ICONS[event.event] || "📌"}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium text-xs">
                {formatEventName(event.event)}
              </p>
              <p className="text-[var(--text-muted)] text-xs truncate">
                {formatEventData(event)}
              </p>
            </div>
            <span className="text-[var(--text-muted)] text-xs shrink-0">
              {new Date(event.timestamp).toLocaleTimeString()}
            </span>
          </motion.div>
        ))}
      </AnimatePresence>
      {meaningful.length === 0 && (
        <p className="text-center text-[var(--text-muted)] text-sm py-8">
          Timeline will appear here when agents start working…
        </p>
      )}
    </div>
  );
}

function formatEventName(event: string): string {
  return event
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatEventData(event: WSEvent): string {
  const d = event.data;
  if (d.agent_name) return String(d.agent_name);
  if (d.title) return String(d.title);
  if (d.task) return String(d.task);
  if (d.task_count) return `${d.task_count} tasks identified`;
  return "";
}

