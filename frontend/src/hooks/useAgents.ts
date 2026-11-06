"use client";

import { useState, useCallback } from "react";
import type { Agent, AgentStatus, AgentLog, WSEvent } from "@/lib/types";

/**
 * Manages a local collection of agents, updating them from WebSocket events.
 */
export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);

  const processEvent = useCallback((event: WSEvent) => {
    switch (event.event) {
      case "agent_created":
        setAgents((prev) => [
          ...prev,
          {
            id: event.data.agent_id as string,
            name: event.data.agent_name as string,
            role: event.data.role as string,
            description: (event.data.description as string) || "",
            agent_type: event.data.agent_type as string,
            status: "idle" as AgentStatus,
            logs: [],
            created_at: event.timestamp,
          },
        ]);
        break;

      case "agent_status_changed":
        setAgents((prev) =>
          prev.map((a) =>
            a.id === event.data.agent_id
              ? { ...a, status: event.data.new_status as AgentStatus }
              : a
          )
        );
        break;

      case "agent_log":
        setAgents((prev) =>
          prev.map((a) =>
            a.id === event.data.agent_id
              ? { ...a, logs: [...a.logs, event.data.log as AgentLog] }
              : a
          )
        );
        break;

      default:
        break;
    }
  }, []);

  const reset = useCallback(() => setAgents([]), []);

  return { agents, processEvent, reset };
}

