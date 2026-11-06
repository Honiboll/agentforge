"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useAgents } from "@/hooks/useAgents";
import { AgentCard } from "@/components/AgentCard";
import { AgentTimeline } from "@/components/AgentTimeline";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { events, connected } = useWebSocket(projectId);
  const { agents, processEvent } = useAgents();

  // Process incoming events
  useEffect(() => {
    if (events.length > 0) {
      const latest = events[events.length - 1];
      processEvent(latest);
    }
  }, [events, processEvent]);

  const isCompleted = events.some((e) => e.event === "project_completed");
  const analysisEvent = events.find((e) => e.event === "analysis_completed");

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-white">
            {analysisEvent
              ? String(analysisEvent.data.title || "Project Dashboard")
              : "Forging Agents…"}
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Project: <code className="text-xs">{projectId}</code>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`h-2.5 w-2.5 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`}
          />
          <span className="text-xs text-[var(--text-muted)]">
            {connected ? "Connected" : "Reconnecting…"}
          </span>
          {isCompleted && (
            <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-400 border border-green-500/30">
              ✅ Completed
            </span>
          )}
        </div>
      </motion.div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Agents grid */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Agents ({agents.length})
          </h2>
          {agents.length === 0 ? (
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-12 text-center">
              <div className="text-4xl mb-3">🔧</div>
              <p className="text-[var(--text-muted)]">
                Analyzing your request and forging agents…
              </p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {agents.map((agent, i) => (
                <AgentCard key={agent.id} agent={agent} index={i} />
              ))}
            </div>
          )}
        </div>

        {/* Timeline */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Timeline
          </h2>
          <AgentTimeline events={events} />
        </div>
      </div>
    </div>
  );
}

