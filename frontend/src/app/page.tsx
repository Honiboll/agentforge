"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ProjectSetup } from "@/components/ProjectSetup";
import { createProject, deleteProject, listProjects, startProject } from "@/lib/api";
import type { Project } from "@/lib/types";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  completed: { label: "Completed", color: "bg-green-500/10 text-green-400 border-green-500/30", icon: "🟢" },
  running: { label: "Running", color: "bg-blue-500/10 text-blue-400 border-blue-500/30", icon: "🔵" },
  pending: { label: "Pending", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30", icon: "🟡" },
  error: { label: "Failed", color: "bg-red-500/10 text-red-400 border-red-500/30", icon: "🔴" },
};

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  const fetchProjects = async () => {
    try {
      const data = await listProjects();
      setProjects(data);
    } catch {
      // ignore on initial load
    } finally {
      setLoadingProjects(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleSubmit = async (request: string, provider: string, model: string) => {
    setLoading(true);
    setError("");
    try {
      const project = await createProject(request, provider, model);
      await startProject(project.id);
      router.push(`/project/${project.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat session?")) return;
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch {
      alert("Failed to delete project");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-12 py-4">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold sm:text-5xl">
          <span className="gradient-text">Forge</span> Your AI Team
        </h1>
        <p className="text-lg text-[var(--text-muted)] max-w-lg mx-auto">
          Describe what you need and AgentForge will create a team of specialized
          AI agents — each with a unique role — working together in real-time.
        </p>
      </motion.div>

      {/* Setup form */}
      <div className="w-full max-w-2xl">
        <ProjectSetup onSubmit={handleSubmit} loading={loading} />
        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-center text-sm text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>

      {/* Feature pills */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex flex-wrap justify-center gap-3 text-xs"
      >
        {[
          "🤖 Dynamic Agents",
          "📡 Live Dashboard",
          "🔌 Any LLM",
          "🔄 Auto Orchestration",
          "🎨 Real-time UI",
        ].map((feature) => (
          <span
            key={feature}
            className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-[var(--text-muted)]"
          >
            {feature}
          </span>
        ))}
      </motion.div>

      {/* Recent Chats / Projects History Section */}
      <div id="projects" className="w-full max-w-4xl space-y-6 pt-6 border-t border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">💬</span>
            <h2 className="text-xl font-bold text-white">Previous Chats & Projects</h2>
            <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs font-semibold text-brand-400 border border-brand-500/20">
              {projects.length}
            </span>
          </div>
          <button
            onClick={fetchProjects}
            className="text-xs text-[var(--text-muted)] hover:text-white transition-colors"
          >
            🔄 Refresh
          </button>
        </div>

        {loadingProjects ? (
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-8 text-center text-sm text-[var(--text-muted)]">
            Loading previous chats…
          </div>
        ) : projects.length === 0 ? (
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-10 text-center space-y-2">
            <div className="text-3xl">📂</div>
            <p className="text-white text-sm font-medium">No previous projects yet</p>
            <p className="text-xs text-[var(--text-muted)]">
              When you submit a request above, it will be saved here so you can review agents anytime!
            </p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            <AnimatePresence>
              {projects.map((proj) => {
                const status = STATUS_CONFIG[proj.status] || STATUS_CONFIG.pending;
                return (
                  <motion.div
                    key={proj.id}
                    layout
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    onClick={() => router.push(`/project/${proj.id}`)}
                    className="group relative flex flex-col justify-between rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4 cursor-pointer hover:border-brand-500 hover:bg-[var(--bg-card-hover)] transition-all"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors line-clamp-1">
                          {proj.title || "Untitled Project"}
                        </h3>
                        <span
                          className={`shrink-0 inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium ${status.color}`}
                        >
                          <span>{status.icon}</span>
                          <span>{status.label}</span>
                        </span>
                      </div>
                      <p className="text-xs text-[var(--text-muted)] line-clamp-2">
                        {proj.user_request}
                      </p>
                      {proj.status === "error" && proj.error_message && (
                        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-2 text-[11px] text-red-300 font-mono line-clamp-2">
                          ⚠️ {proj.error_message}
                        </div>
                      )}
                    </div>

                    <div className="mt-4 flex items-center justify-between pt-3 border-t border-[var(--border)] text-[11px] text-[var(--text-muted)]">
                      <div className="flex items-center gap-2">
                        <span className="capitalize rounded bg-white/5 px-1.5 py-0.5">
                          {proj.provider_name}
                        </span>
                        <span>
                          {new Date(proj.created_at).toLocaleDateString(undefined, {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => handleDelete(proj.id, e)}
                          title="Delete session"
                          className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-all"
                        >
                          🗑️
                        </button>
                        <span className="text-brand-400 group-hover:translate-x-0.5 transition-transform">
                          Open ➔
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}

