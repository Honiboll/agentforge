/** API client for the AgentForge backend. */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// --- Projects ---

export function createProject(user_request: string, provider?: string) {
  return request<{ id: string }>("/api/projects/", {
    method: "POST",
    body: JSON.stringify({ user_request, provider }),
  });
}

export function listProjects() {
  return request<Array<Record<string, string>>>("/api/projects/");
}

export function getProject(id: string) {
  return request<Record<string, unknown>>(`/api/projects/${id}`);
}

export function startProject(id: string) {
  return request<{ status: string }>(`/api/projects/${id}/start`, { method: "POST" });
}

export function deleteProject(id: string) {
  return request<{ status: string }>(`/api/projects/${id}`, { method: "DELETE" });
}

// --- Agents ---

export function listAgentTypes() {
  return request<Array<{ type: string }>>("/api/agents/types");
}

// --- Providers ---

export function listProviders() {
  return request<Array<{ name: string; label: string; requires_key: boolean }>>("/api/providers/");
}

export function testProvider(provider: string) {
  return request<{ success: boolean; response?: string; error?: string }>("/api/providers/test", {
    method: "POST",
    body: JSON.stringify({ provider }),
  });
}

