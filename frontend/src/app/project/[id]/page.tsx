"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useAgents } from "@/hooks/useAgents";
import { AgentCard } from "@/components/AgentCard";
import { AgentTimeline } from "@/components/AgentTimeline";
import { getProject, startProject } from "@/lib/api";
import type { Project, Agent, AgentStatus } from "@/lib/types";

export default function ProjectPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const { events, connected } = useWebSocket(projectId);
  const { agents, processEvent, setInitialAgents } = useAgents();

  const [project, setProject] = useState<Project | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  // Load project on mount via REST API
  const fetchProjectData = useCallback(async () => {
    try {
      const data = await getProject(projectId);
      setProject(data);
      if (data.status === "error" && data.error_message) {
        setErrorMessage(data.error_message);
      }
      // If agents already exist in result (e.g. historical completed run), load them
      if (data.result && Array.isArray((data.result as any).agents) && agents.length === 0) {
        const historicalAgents: Agent[] = (data.result as any).agents.map((a: any) => ({
          id: a.agent_id,
          name: a.agent_name,
          role: a.role,
          description: "",
          agent_type: a.role,
          status: (a.success ? "done" : "error") as AgentStatus,
          logs: a.error ? [{ message: a.error, level: "error", timestamp: new Date().toISOString() }] : [],
          created_at: new Date().toISOString(),
        }));
        setInitialAgents(historicalAgents);
      }
    } catch {
      // ignore
    }
  }, [projectId, agents.length, setInitialAgents]);

  useEffect(() => {
    fetchProjectData();
  }, [fetchProjectData]);

  // Process incoming events
  useEffect(() => {
    if (events.length > 0) {
      const latest = events[events.length - 1];
      processEvent(latest);

      // Check for failure event
      if (latest.event === "project_failed") {
        const err = String(latest.data?.error || "Project execution failed.");
        setErrorMessage(err);
      }
    }
  }, [events, processEvent]);

  const handleRetry = async () => {
    setRetrying(true);
    setErrorMessage(null);
    try {
      await startProject(projectId);
      await fetchProjectData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to restart project");
    } finally {
      setRetrying(false);
    }
  };

  const isCompleted = events.some((e) => e.event === "project_completed") || project?.status === "completed";
  const isFailed = !!errorMessage || project?.status === "error";
  const analysisEvent = events.find((e) => e.event === "analysis_completed");

  const displayTitle =
    analysisEvent?.data?.title ||
    project?.title && project.title !== "Untitled"
      ? String(analysisEvent?.data?.title || project?.title)
      : isFailed
      ? "Execution Halted"
      : "Forging Agents…";

  // Provide contextual hints based on error content
  const getContextualHint = (err: string) => {
    const lower = err.toLowerCase();
    if (lower.includes("location is not supported")) {
      return {
        icon: "🌍",
        title: "Geographic Restriction Detected",
        tip: "Google Gemini restricts API access from certain countries/regions. Please turn on a VPN or Proxy routed through the US or Europe, or switch provider to Ollama (100% offline & free) or OpenAI.",
      };
    }
    if (lower.includes("api key") || lower.includes("key is missing") || lower.includes("not valid") || lower.includes("401") || lower.includes("403")) {
      return {
        icon: "🔑",
        title: "API Key Issue Detected",
        tip: "Your API key appears missing, expired, or invalid. Please click 'Go to Settings' below to check or update your key, or enter a new key in the Provider selector.",
      };
    }
    if (lower.includes("cannot connect to ollama") || lower.includes("connection refused") || lower.includes("10061")) {
      return {
        icon: "🦙",
        title: "Ollama Connection Failed",
        tip: "Make sure Ollama is installed and running on your machine. Open a terminal and run 'ollama run llama3.2' to start the local server.",
      };
    }
    if (lower.includes("quota") || lower.includes("resource_exhausted") || lower.includes("429")) {
      return {
        icon: "⏳",
        title: "API Rate / Quota Limit Exceeded",
        tip: "Your AI provider has temporarily rate-limited your account or your quota ran out. Wait a moment or choose another model/provider.",
      };
    }
    return null;
  };

  const hint = errorMessage ? getContextualHint(errorMessage) : null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-3"
      >
        <button
          onClick={() => router.push("/#projects")}
          className="inline-flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-brand-400 transition-colors"
        >
          <span>←</span> Back to all chats & projects
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">{displayTitle}</h1>
            <p className="text-sm text-[var(--text-muted)] mt-1">
              Project: <code className="text-xs">{projectId}</code>
              {project?.provider_name && (
                <span className="ml-3 rounded-full bg-[var(--bg-card)] px-2.5 py-0.5 text-xs border border-[var(--border)] text-gray-300">
                  {project.provider_name} {project.model_name ? `• ${project.model_name}` : ""}
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                connected ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className="text-xs text-[var(--text-muted)]">
              {connected ? "Connected" : "Reconnecting…"}
            </span>
            {isCompleted && !isFailed && (
              <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-400 border border-green-500/30">
                ✅ Completed
              </span>
            )}
            {isFailed && (
              <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-400 border border-red-500/30">
                🔴 Failed
              </span>
            )}
          </div>
        </div>
      </motion.div>

      {/* Prominent Error Alert Card */}
      <AnimatePresence>
        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            className="rounded-2xl border border-red-500/40 bg-red-950/20 backdrop-blur p-6 space-y-4 shadow-xl shadow-red-950/30"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/20 text-xl border border-red-500/30 text-red-400">
                  ⚠️
                </div>
                <div>
                  <h2 className="text-base font-bold text-red-300">
                    Execution Failed — Reason Identified
                  </h2>
                  <p className="text-xs text-red-200/70">
                    The AI orchestrator could not proceed due to the error below:
                  </p>
                </div>
              </div>
            </div>

            {/* Error Message Box */}
            <div className="rounded-xl border border-red-500/30 bg-black/50 p-4">
              <p className="text-xs font-mono text-red-300 break-words whitespace-pre-wrap leading-relaxed">
                {errorMessage}
              </p>
            </div>

            {/* Contextual Diagnosis & Tip */}
            {hint && (
              <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-200">
                <span className="text-base shrink-0">{hint.icon}</span>
                <div className="space-y-1">
                  <p className="font-semibold text-amber-300">{hint.title}</p>
                  <p className="text-amber-200/80 leading-relaxed">{hint.tip}</p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={handleRetry}
                disabled={retrying}
                className="rounded-xl bg-brand-600 px-4 py-2 text-xs font-medium text-white hover:bg-brand-500 transition-colors disabled:opacity-50 inline-flex items-center gap-2"
              >
                <span>🔄</span> {retrying ? "Retrying…" : "Retry Task"}
              </button>
              <button
                onClick={() => router.push("/settings")}
                className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-2 text-xs font-medium text-gray-200 hover:text-white hover:border-brand-500 transition-colors inline-flex items-center gap-2"
              >
                <span>⚙️</span> Go to Settings
              </button>
              <button
                onClick={() => router.push("/")}
                className="rounded-xl border border-transparent px-4 py-2 text-xs font-medium text-[var(--text-muted)] hover:text-white transition-colors"
              >
                New Prompt
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Agents grid */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Agents ({agents.length})
          </h2>
          {agents.length === 0 ? (
            isFailed ? (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-12 text-center space-y-2">
                <div className="text-4xl mb-3">🛑</div>
                <p className="text-sm font-semibold text-red-300">
                  Pipeline halted during initial analysis
                </p>
                <p className="text-xs text-[var(--text-muted)] max-w-md mx-auto">
                  Agents could not be created because the AI provider encountered an error. Review the error box above and click Retry after resolving it.
                </p>
              </div>
            ) : (
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-12 text-center">
                <div className="text-4xl mb-3 animate-pulse">🔧</div>
                <p className="text-[var(--text-muted)] text-sm">
                  Analyzing your request and forging agents…
                </p>
              </div>
            )
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

