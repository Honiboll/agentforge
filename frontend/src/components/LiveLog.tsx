"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentLog } from "@/lib/types";

export function LiveLog({ logs }: { logs: AgentLog[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  const levelColor: Record<string, string> = {
    info: "text-blue-400",
    warning: "text-yellow-400",
    error: "text-red-400",
    debug: "text-gray-500",
  };

  return (
    <div
      ref={containerRef}
      className="h-36 overflow-y-auto rounded-lg bg-black/40 p-3 font-mono text-xs"
    >
      <AnimatePresence initial={false}>
        {logs.map((log, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex gap-2 py-0.5"
          >
            <span className="text-gray-600 shrink-0">
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span className={levelColor[log.level] || "text-gray-400"}>
              {log.message}
            </span>
          </motion.div>
        ))}
      </AnimatePresence>
      {logs.length === 0 && (
        <span className="text-gray-600">Waiting for logs…</span>
      )}
    </div>
  );
}

