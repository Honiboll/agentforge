"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface Props {
  onSubmit: (request: string, provider: string) => void;
  loading: boolean;
}

const PROVIDERS = [
  { value: "ollama", label: "🦙 Ollama (Local)" },
  { value: "openai", label: "🟢 OpenAI" },
  { value: "gemini", label: "💎 Google Gemini" },
  { value: "anthropic", label: "🟠 Anthropic" },
];

export function ProjectSetup({ onSubmit, loading }: Props) {
  const [request, setRequest] = useState("");
  const [provider, setProvider] = useState("ollama");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (request.trim()) onSubmit(request.trim(), provider);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto max-w-2xl space-y-6"
    >
      {/* Main input */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-muted)] mb-2">
          Describe what you need
        </label>
        <textarea
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          placeholder="e.g. Build a REST API for a task manager with authentication, database, and documentation…"
          rows={5}
          className="w-full rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3
                     text-white placeholder-gray-600 focus:border-brand-500 focus:ring-1
                     focus:ring-brand-500 focus:outline-none resize-none transition-colors"
        />
      </div>

      {/* Provider selector */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-muted)] mb-2">
          LLM Provider
        </label>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {PROVIDERS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setProvider(p.value)}
              className={`rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
                provider === p.value
                  ? "border-brand-500 bg-brand-500/10 text-brand-400"
                  : "border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] hover:border-gray-600"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
      <motion.button
        type="submit"
        disabled={!request.trim() || loading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full rounded-xl bg-brand-600 px-6 py-3 font-semibold text-white
                   shadow-lg shadow-brand-600/20 transition-all hover:bg-brand-500
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? "Forging Agents…" : "🔥 Forge Agents"}
      </motion.button>
    </motion.form>
  );
}

