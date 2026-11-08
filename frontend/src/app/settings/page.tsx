"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { listProviders, saveApiKey, testProvider, detectAndSaveApiKey } from "@/lib/api";
import type { Provider } from "@/lib/types";

export default function SettingsPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [testing, setTesting] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [results, setResults] = useState<Record<string, { ok: boolean; msg: string }>>({});
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [keyNotifs, setKeyNotifs] = useState<Record<string, string>>({});

  // Universal Smart Key Auto-Detector
  const [smartKey, setSmartKey] = useState("");
  const [detectingKey, setDetectingKey] = useState(false);
  const [smartSuccess, setSmartSuccess] = useState("");
  const [smartError, setSmartError] = useState("");

  const handleAutoDetect = async () => {
    if (!smartKey.trim()) return;
    setDetectingKey(true);
    setSmartError("");
    setSmartSuccess("");
    try {
      const res = await detectAndSaveApiKey(smartKey.trim());
      if (res.success) {
        setSmartSuccess(res.message || "Key successfully detected and activated!");
        setSmartKey("");
        loadProviders(true);
      } else {
        setSmartError(res.error || "Could not detect provider for this key");
      }
    } catch (e: unknown) {
      setSmartError(e instanceof Error ? e.message : "Error detecting key");
    } finally {
      setDetectingKey(false);
    }
  };

  const loadProviders = (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    listProviders(isRefresh)
      .then(setProviders)
      .catch(() => {})
      .finally(() => setRefreshing(false));
  };

  useEffect(() => {
    loadProviders(false);
  }, []);

  const [customUrls, setCustomUrls] = useState<Record<string, string>>({
    custom: "https://api.openai.com/v1",
  });

  const handleSaveKey = async (name: string) => {
    const val = keys[name]?.trim();
    if (!val) return;
    setSavingKey(name);
    try {
      const res = await saveApiKey(name, val, name === "custom" ? customUrls[name] : undefined);
      if (res.success) {
        setKeyNotifs((prev) => ({ ...prev, [name]: res.message || "Key saved successfully!" }));
        setKeys((prev) => ({ ...prev, [name]: "" }));
        loadProviders(true);
      } else {
        setKeyNotifs((prev) => ({ ...prev, [name]: res.error || "Failed to save key" }));
      }
    } catch (e: unknown) {
      setKeyNotifs((prev) => ({ ...prev, [name]: e instanceof Error ? e.message : "Error saving key" }));
    } finally {
      setSavingKey(null);
    }
  };

  const handleTest = async (name: string) => {
    setTesting(name);
    try {
      const res = await testProvider(name);
      setResults((prev) => ({
        ...prev,
        [name]: { ok: res.success, msg: res.response || res.error || "" },
      }));
    } catch (e: unknown) {
      setResults((prev) => ({
        ...prev,
        [name]: { ok: false, msg: e instanceof Error ? e.message : "Failed" },
      }));
    } finally {
      setTesting(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">⚙️ Settings</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Configure your LLM providers. Set API keys in your <code>.env</code> file.
          </p>
        </div>
        <button
          onClick={() => loadProviders(true)}
          disabled={refreshing}
          className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs font-medium text-brand-400 hover:text-white hover:border-brand-500 transition-all disabled:opacity-40"
        >
          {refreshing ? "Scanning APIs…" : "🔄 Check for New Models"}
        </button>
      </motion.div>

      {/* Universal Smart Key Auto-Detector */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl border border-brand-500/40 bg-gradient-to-r from-brand-950/40 via-[var(--bg-card)] to-brand-950/20 p-5 space-y-3 shadow-lg shadow-brand-950/20"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚡</span>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Universal Key Auto-Detector
            </h2>
            <span className="rounded-full bg-brand-500/20 px-2 py-0.5 text-[10px] font-semibold text-brand-300 border border-brand-500/30">
              One-Click
            </span>
          </div>
          <span className="text-xs text-[var(--text-muted)]">
            Universal Auto-Detector (Accepts ANY API key from ANY provider)
          </span>
        </div>

        <p className="text-xs text-[var(--text-muted)]">
          Paste ANY API key below. AgentForge accepts any key unconditionally (Gemini, Groq, xAI, OpenAI, Claude, or any custom/proxy key) and activates it immediately.
        </p>

        <div className="flex gap-2">
          <input
            type="password"
            value={smartKey}
            onChange={(e) => setSmartKey(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleAutoDetect();
              }
            }}
            placeholder="Paste ANY API key here (e.g. coa_..., xai-..., gsk_..., AIzaSy..., sk-...)..."
            className="flex-1 rounded-xl border border-[var(--border)] bg-black/50 px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:border-brand-500 focus:outline-none transition-colors"
          />
          <button
            type="button"
            onClick={handleAutoDetect}
            disabled={detectingKey || !smartKey.trim()}
            className="rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 px-4 py-2.5 text-xs font-semibold text-white transition-all shadow-sm flex items-center gap-1.5 shrink-0"
          >
            <span>{detectingKey ? "⏳ Detecting…" : "⚡ Auto-Detect & Activate"}</span>
          </button>
        </div>

        {smartSuccess && (
          <p className="text-xs font-medium text-green-400 bg-green-500/10 border border-green-500/20 rounded-xl p-2.5 flex items-center gap-2">
            <span>✅</span> {smartSuccess}
          </p>
        )}
        {smartError && (
          <p className="text-xs font-medium text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl p-2.5 flex items-center gap-2">
            <span>⚠️</span> {smartError}
          </p>
        )}
      </motion.div>

      <div className="space-y-4">
        {providers.map((p) => (
          <motion.div
            key={p.name}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white">{p.label}</h3>
                  {p.is_available ? (
                    <span className="rounded-full bg-green-500/15 px-2 py-0.5 text-[10px] font-medium text-green-400 border border-green-500/30">
                      Ready
                    </span>
                  ) : p.requires_key && !p.has_key ? (
                    <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-medium text-amber-400 border border-amber-500/30">
                      Key Missing in .env
                    </span>
                  ) : (
                    <span className="rounded-full bg-gray-500/15 px-2 py-0.5 text-[10px] font-medium text-gray-400 border border-gray-500/30">
                      Daemon Offline
                    </span>
                  )}
                </div>
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  Default: <code>{p.default_model}</code>
                </p>
              </div>
              <button
                onClick={() => handleTest(p.name)}
                disabled={testing === p.name}
                className="rounded-lg border border-[var(--border)] px-4 py-2 text-xs font-medium
                           text-[var(--text-muted)] hover:text-white hover:border-brand-500
                           transition-colors disabled:opacity-50"
              >
                {testing === p.name ? "Testing…" : "Test Connection"}
              </button>
            </div>

            {/* Key Input Section */}
            {p.requires_key && (
              <div className="mt-3 pt-3 border-t border-[var(--border)] space-y-2">
                {p.name === "custom" && (
                  <div className="space-y-1.5 pb-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-medium text-[var(--text-muted)]">
                        OpenAI-Compatible Base URL:
                      </span>
                      <span className="text-[10px] text-gray-500">Quick Presets:</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pb-1">
                      <button
                        type="button"
                        onClick={() => setCustomUrls({ ...customUrls, [p.name]: "https://api.x.ai/v1" })}
                        className="rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-cyan-300 border border-white/10 transition-colors"
                      >
                        🤖 xAI Grok
                      </button>
                      <button
                        type="button"
                        onClick={() => setCustomUrls({ ...customUrls, [p.name]: "https://api.groq.com/openai/v1" })}
                        className="rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-amber-300 border border-white/10 transition-colors"
                      >
                        ⚡ Groq
                      </button>
                      <button
                        type="button"
                        onClick={() => setCustomUrls({ ...customUrls, [p.name]: "https://api.deepseek.com" })}
                        className="rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-blue-300 border border-white/10 transition-colors"
                      >
                        🐋 DeepSeek
                      </button>
                      <button
                        type="button"
                        onClick={() => setCustomUrls({ ...customUrls, [p.name]: "https://openrouter.ai/api/v1" })}
                        className="rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-purple-300 border border-white/10 transition-colors"
                      >
                        🌐 OpenRouter
                      </button>
                      <button
                        type="button"
                        onClick={() => setCustomUrls({ ...customUrls, [p.name]: "http://localhost:1234/v1" })}
                        className="rounded bg-white/5 hover:bg-white/10 px-2 py-0.5 text-[10px] text-emerald-300 border border-white/10 transition-colors"
                      >
                        💻 Local (LM Studio / vLLM)
                      </button>
                    </div>
                    <input
                      type="text"
                      placeholder="https://api.openai.com/v1"
                      value={customUrls[p.name] || "https://api.openai.com/v1"}
                      onChange={(e) => setCustomUrls({ ...customUrls, [p.name]: e.target.value })}
                      className="w-full rounded-lg border border-[var(--border)] bg-black/40 px-3 py-1.5 text-xs text-white placeholder-gray-600 focus:border-brand-500 focus:outline-none"
                    />
                  </div>
                )}
                <span className="text-[11px] font-medium text-[var(--text-muted)]">
                  {p.has_key ? "Update API Key:" : "Enter API Key:"}
                </span>
                <div className="flex gap-2">
                  <input
                    type="password"
                    placeholder={
                      p.has_key
                        ? "Key is configured. Paste new key to replace..."
                        : `Paste ${p.label} API key here...`
                    }
                    value={keys[p.name] || ""}
                    onChange={(e) => setKeys({ ...keys, [p.name]: e.target.value })}
                    className="flex-1 rounded-lg border border-[var(--border)] bg-black/40 px-3 py-1.5 text-xs text-white placeholder-gray-600 focus:border-brand-500 focus:outline-none"
                  />
                  <button
                    onClick={() => handleSaveKey(p.name)}
                    disabled={!keys[p.name]?.trim() || savingKey === p.name}
                    className="rounded-lg bg-brand-600 hover:bg-brand-500 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40 transition-colors shrink-0"
                  >
                    {savingKey === p.name ? "Saving…" : "Save Key"}
                  </button>
                </div>
                {keyNotifs[p.name] && (
                  <p className="text-[11px] text-brand-400">{keyNotifs[p.name]}</p>
                )}
              </div>
            )}

            {/* Models list */}
            {p.models && p.models.length > 0 && (
              <div className="mt-3 pt-3 border-t border-[var(--border)]">
                <span className="text-[11px] font-medium text-[var(--text-muted)]">Supported Models:</span>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {p.models.map((m) => (
                    <span
                      key={m.id}
                      className="rounded bg-black/40 border border-[var(--border)] px-2 py-0.5 text-[10px] text-gray-300"
                      title={m.description}
                    >
                      {m.id}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {results[p.name] && (
              <div
                className={`mt-3 rounded-lg p-3 text-xs ${
                  results[p.name].ok
                    ? "bg-green-500/10 text-green-400 border border-green-500/30"
                    : "bg-red-500/10 text-red-400 border border-red-500/30"
                }`}
              >
                {results[p.name].ok ? "✅ " : "❌ "}
                {results[p.name].msg.slice(0, 200)}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

