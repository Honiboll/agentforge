/**  TypeScript types shared across the frontend. */

export type AgentStatus = "idle" | "thinking" | "working" | "done" | "error" | "waiting";

export interface AgentLog {
  message: string;
  level: string;
  timestamp: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  agent_type: string;
  status: AgentStatus;
  logs: AgentLog[];
  created_at: string;
}

export interface Project {
  id: string;
  title: string;
  user_request: string;
  status: string;
  provider_name: string;
  created_at: string;
}

export interface WSEvent {
  event: string;
  project_id: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface Provider {
  name: string;
  label: string;
  requires_key: boolean;
}

