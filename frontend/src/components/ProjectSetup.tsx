"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { listProviders, saveApiKey } from "@/lib/api";
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
  const [selectedProvider, setSelectedProvider] = useState<string>("gemini");
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [customModel, setCustomModel] = useState<string>("");
  const [useCustomModel, setUseCustomModel] = useState<boolean>(false);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Direct UI key input
  const [inlineKey, setInlineKey] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [keySuccess, setKeySuccess] = useState("");
  const [keyError, setKeyError] = useState("");

  const fetchProviders = (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoadingProviders(true);

    listProviders(isRefresh)
      .then((data) => {
        setProviders(data);
        if (data.length > 0) {
          const current = data.find((p) => p.name === selectedProvider) || data.find((p) => p.is_available) || data[0];
          setSelectedProvider(current.name);
          if (!useCustomModel) {
            setSelectedModel(current.default_model || current.models[0]?.id || "");
          }
        }
      })
      .catch(() => {})
      .finally(() => {
        setLoadingProviders(false);
        setRefreshing(false);
      });
  };

  useEffect(() => {
    fetchProviders(false);
  }, []);

  const currentProvider = providers.find((p) => p.name === selectedProvider);

  const handleProviderChange = (providerName: string) => {
    setSelectedProvider(providerName);
    setInlineKey("");
    setKeySuccess("");
    setKeyError("");
    const p = providers.find((item) => item.name === providerName);
    if (p && p.models.length > 0 && !useCustomModel) {
      setSelectedModel(p.default_model || p.models[0].id);
    }
  };

  const handleSaveKey = async () => {
    if (!inlineKey.trim()) return;
    setSavingKey(true);
    setKeyError("");
    setKeySuccess("");
    try {
      const res = await saveApiKey(selectedProvider, inlineKey.trim());
      if (res.success) {
        setKeySuccess(res.message || "Key saved and activated!");
        setInlineKey("");
        fetchProviders(true);
      } else {
        setKeyError(res.error || "Failed to save key");
      }
    } catch (err: unknown) {
      setKeyError(err instanceof Error ? err.message : "Error saving key");
    } finally {
      setSavingKey(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (request.trim()) {
      const finalModel = useCustomModel && customModel.trim() ? customModel.trim() : selectedModel;
      onSubmit(request.trim(), selectedProvider, finalModel);
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
      {currentProvider && (
        <motion.div
          layout
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3 rounded-xl border border-[var(--border)] bg-[var(--bg-card)]/60 p-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-white">
                Select Model for {currentProvider.label}:
              </span>
              <button
                type="button"
                onClick={() => fetchProviders(true)}
                disabled={refreshing}
                title="Check for newly released models from API"
                className="inline-flex items-center gap-1 rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-[var(--text-muted)] hover:text-white transition-all disabled:opacity-40"
              >
                <span>{refreshing ? "⏳ Scanning APIs…" : "🔄 Check for New Models"}</span>
              </button>
            </div>
            <button
              type="button"
              onClick={() => setUseCustomModel(!useCustomModel)}
              className="text-[11px] text-brand-400 hover:underline"
            >
              {useCustomModel ? "← Pick from List" : "✏️ Custom Model Name"}
            </button>
          </div>

          {useCustomModel ? (
            <div className="space-y-1.5 pt-1">
              <label className="block text-[11px] text-[var(--text-muted)]">
                Enter any newly released model identifier (e.g. <code>gemini-2.5-flash</code>, <code>o3-mini</code>, <code>deepseek-v3</code>):
              </label>
              <input
                type="text"
                value={customModel}
                onChange={(e) => setCustomModel(e.target.value)}
                placeholder="e.g. gemini-2.0-flash or gpt-4o-mini"
                className="w-full rounded-lg border border-[var(--border)] bg-black/40 px-3 py-2 text-xs text-white placeholder-gray-600 focus:border-brand-500 focus:outline-none"
              />
            </div>
          ) : (
            <div className="grid gap-2 sm:grid-cols-2 max-h-56 overflow-y-auto pr-1">
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
          )}

          {currentProvider.requires_key && (
            <div className="mt-3 rounded-lg border border-[var(--border)] bg-black/30 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-white flex items-center gap-1.5">
                  <span>🔑</span>
                  <span>
                    {currentProvider.has_key
                      ? `${currentProvider.label} API Key Configured`
                      : `Enter ${currentProvider.label} API Key:`}
                  </span>
                </span>
                {currentProvider.has_key ? (
                  <span className="text-[10px] text-green-400 bg-green-500/10 border border-green-500/20 rounded px-1.5 py-0.5">
                    ✓ Active
                  </span>
                ) : (
                  <span className="text-[10px] text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded px-1.5 py-0.5">
                    Key Required
                  </span>
                )}
              </div>

              <div className="flex gap-2">
                <input
                  type="password"
                  value={inlineKey}
                  onChange={(e) => setInlineKey(e.target.value)}
                  placeholder={
                    currentProvider.has_key
                      ? "Paste new key to replace existing..."
                      : `Paste your ${currentProvider.label} API key here...`
                  }
                  className="flex-1 rounded-lg border border-[var(--border)] bg-black/40 px-3 py-1.5 text-xs text-white placeholder-gray-600 focus:border-brand-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleSaveKey}
                  disabled={!inlineKey.trim() || savingKey}
                  className="rounded-lg bg-brand-600 hover:bg-brand-500 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40 transition-colors shrink-0 shadow-sm"
                >
                  {savingKey ? "Saving…" : "Save & Activate"}
                </button>
              </div>

              {keySuccess && <p className="text-[11px] text-green-400">✅ {keySuccess}</p>}
              {keyError && <p className="text-[11px] text-red-400">❌ {keyError}</p>}
            </div>
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
        {loading
          ? "Forging Agents…"
          : `🔥 Forge Agents with ${useCustomModel && customModel ? customModel : selectedModel || selectedProvider}`}
      </motion.button>
    </motion.form>
  );
}

