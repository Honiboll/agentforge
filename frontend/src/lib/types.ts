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
  model_name?: string;
  error_message?: string | null;
  result?: Record<string, unknown> | null;
  created_at: string;
}

export interface WSEvent {
  event: string;
  project_id: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface ModelOption {
  id: string;
  name: string;
  description: string;
}

export interface Provider {
  name: string;
  label: string;
  is_available: boolean;
  requires_key: boolean;
  has_key: boolean;
  default_model: string;
  models: ModelOption[];
}

