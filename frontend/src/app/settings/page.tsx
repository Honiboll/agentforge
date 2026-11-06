"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { listProviders, testProvider } from "@/lib/api";
import type { Provider } from "@/lib/types";

export default function SettingsPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [testing, setTesting] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, { ok: boolean; msg: string }>>({});

  useEffect(() => {
    listProviders().then(setProviders).catch(() => {});
  }, []);

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
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-white">⚙️ Settings</h1>
        <p className="text-sm text-[var(--text-muted)] mt-1">
          Configure your LLM providers. Set API keys in your <code>.env</code> file.
        </p>
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
                <h3 className="font-semibold text-white">{p.label}</h3>
                <p className="text-xs text-[var(--text-muted)]">
                  {p.requires_key ? "Requires API key in .env" : "No API key needed"}
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

