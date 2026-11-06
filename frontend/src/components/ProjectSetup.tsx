"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { listProviders } from "@/lib/api";
import type { Provider, ModelOption } from "@/lib/types";

interface Props {
  onSubmit: (request: string, provider: string, model: string) => void;
  loading: boolean;
}

const PROVIDER_ICONS: Record<string, string> = {
  ollama: "🦙",
  gemini: "💎",
  openai: "🟢",
  anthropic: "🟠",
};

export function ProjectSetup({ onSubmit, loading }: Props) {
  const [request, setRequest] = useState("");
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>("ollama");
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [loadingProviders, setLoadingProviders] = useState(true);

  useEffect(() => {
    listProviders()
      .then((data) => {
        setProviders(data);
        if (data.length > 0) {
          // Prefer first ready provider, or fallback to first
          const ready = data.find((p) => p.is_available) || data[0];
          setSelectedProvider(ready.name);
          setSelectedModel(ready.default_model || ready.models[0]?.id || "");
        }
      })
      .catch(() => {})
      .finally(() => setLoadingProviders(false));
  }, []);

  const currentProvider = providers.find((p) => p.name === selectedProvider);

  const handleProviderChange = (providerName: string) => {
    setSelectedProvider(providerName);
    const p = providers.find((item) => item.name === providerName);
    if (p && p.models.length > 0) {
      setSelectedModel(p.default_model || p.models[0].id);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (request.trim()) {
      onSubmit(request.trim(), selectedProvider, selectedModel);
    }
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

      {/* Provider Selector with API Key & Availability Inspection */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-[var(--text-muted)]">
            AI Provider & Key Status
          </label>
          <span className="text-xs text-[var(--text-muted)]">
            Checked via environment keys
          </span>
        </div>

        {loadingProviders ? (
          <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4 text-center text-xs text-[var(--text-muted)]">
            Checking API keys & available models…
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
            {providers.map((p) => {
              const isSelected = selectedProvider === p.name;
              return (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => handleProviderChange(p.name)}
                  className={`relative flex flex-col items-start gap-1 rounded-xl border p-3 text-left transition-all ${
                    isSelected
                      ? "border-brand-500 bg-brand-500/10 text-white shadow-sm ring-1 ring-brand-500/50"
                      : "border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] hover:border-gray-600 hover:text-white"
                  }`}
                >
                  <div className="flex w-full items-center justify-between">
                    <span className="text-base">{PROVIDER_ICONS[p.name] || "🤖"}</span>
                    {p.is_available ? (
                      <span className="inline-flex items-center rounded-full bg-green-500/15 px-1.5 py-0.5 text-[10px] font-medium text-green-400">
                        Ready
                      </span>
                    ) : p.requires_key && !p.has_key ? (
                      <span className="inline-flex items-center rounded-full bg-amber-500/15 px-1.5 py-0.5 text-[10px] font-medium text-amber-400">
                        No Key
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-gray-500/15 px-1.5 py-0.5 text-[10px] font-medium text-gray-400">
                        Offline
                      </span>
                    )}
                  </div>
                  <span className="text-xs font-semibold">{p.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Individual Model Selector */}
      {currentProvider && currentProvider.models.length > 0 && (
        <motion.div
          layout
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2 rounded-xl border border-[var(--border)] bg-[var(--bg-card)]/60 p-4"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-white">
              Select Specific Model for {currentProvider.label}:
            </span>
            <span className="text-[11px] text-[var(--text-muted)]">
              {currentProvider.models.length} models available
            </span>
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            {currentProvider.models.map((m: ModelOption) => {
              const isModelSelected = selectedModel === m.id;
              return (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setSelectedModel(m.id)}
                  className={`flex flex-col items-start rounded-lg border p-2.5 text-left transition-all ${
                    isModelSelected
                      ? "border-brand-500 bg-brand-500/15 text-white ring-1 ring-brand-500/40"
                      : "border-[var(--border)] bg-black/20 text-[var(--text-muted)] hover:border-gray-500 hover:text-white"
                  }`}
                >
                  <div className="flex w-full items-center justify-between">
                    <span className="text-xs font-semibold text-white">{m.name}</span>
                    <code className="text-[10px] text-brand-400">{m.id}</code>
                  </div>
                  <p className="mt-1 text-[11px] text-[var(--text-muted)] line-clamp-1">
                    {m.description}
                  </p>
                </button>
              );
            })}
          </div>

          {!currentProvider.is_available && currentProvider.requires_key && (
            <p className="mt-2 text-[11px] text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              💡 <strong>API Key missing:</strong> To use this provider, add your key to <code>.env</code> file (e.g. <code>{currentProvider.name.toUpperCase()}_API_KEY=...</code>).
            </p>
          )}
        </motion.div>
      )}

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
        {loading ? "Forging Agents…" : `🔥 Forge Agents with ${selectedModel || selectedProvider}`}
      </motion.button>
    </motion.form>
  );
}

