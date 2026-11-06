"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ProjectSetup } from "@/components/ProjectSetup";
import { createProject, startProject } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (request: string, provider: string) => {
    setLoading(true);
    setError("");
    try {
      const project = await createProject(request, provider);
      await startProject(project.id);
      router.push(`/project/${project.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center gap-8">
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
        transition={{ delay: 0.3 }}
        className="flex flex-wrap justify-center gap-3 text-xs"
      >
        {[
          "🤖 Dynamic Agents",
          "📡 Live Dashboard",
          "🔌 Any LLM",
          "🔄 Auto Orchestration",
          "🎨 Beautiful UI",
        ].map((feature) => (
          <span
            key={feature}
            className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-[var(--text-muted)]"
          >
            {feature}
          </span>
        ))}
      </motion.div>
    </div>
  );
}

