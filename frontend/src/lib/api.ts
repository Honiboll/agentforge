/** API client for the AgentForge backend. */

import type { Project, Provider } from "./types";

const getApiEndpoints = (path: string): string[] => {
  const custom = process.env.NEXT_PUBLIC_API_URL;
  if (custom) {
    return [`${custom.replace(/\/$/, "")}${path}`];
  }

  // 1. Same-origin relative path (handled by Next.js rewrites)
  const endpoints: string[] = [path];

  // 2. Direct fallbacks for maximum resilience
  if (typeof window !== "undefined") {
    const host = window.location.hostname || "127.0.0.1";
    endpoints.push(`http://${host}:8000${path}`);
    if (host !== "127.0.0.1") endpoints.push(`http://127.0.0.1:8000${path}`);
    if (host !== "localhost") endpoints.push(`http://localhost:8000${path}`);
  } else {
    endpoints.push(`http://127.0.0.1:8000${path}`);
  }

  return endpoints;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const endpoints = getApiEndpoints(path);
  let lastError: Error | null = null;

  for (const url of endpoints) {
    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json", ...options?.headers },
        ...options,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
      }
      return (await res.json()) as T;
    } catch (err: unknown) {
      lastError = err instanceof Error ? err : new Error(String(err));
      // Continue to next endpoint fallback
    }
  }

  throw lastError || new Error("Failed to connect to AgentForge backend");
}

// --- Projects ---

export function createProject(
  user_request: string,
  provider?: string,
  model?: string,
  api_key?: string,
  base_url?: string
) {
  return request<{ id: string }>("/api/projects/", {
    method: "POST",
    body: JSON.stringify({ user_request, provider, model, api_key, base_url }),
  });
}

export function listProjects() {
  return request<Project[]>("/api/projects/");
}

export function getProject(id: string) {
  return request<Project>(`/api/projects/${id}`);
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

export function listProviders(refresh = false) {
  return request<Provider[]>(`/api/providers/${refresh ? "?refresh=true" : ""}`);
}

export function testProvider(provider: string, model?: string) {
  return request<{ success: boolean; response?: string; error?: string }>("/api/providers/test", {
    method: "POST",
    body: JSON.stringify({ provider, model }),
  });
}

export function saveApiKey(provider: string, api_key: string, base_url?: string) {
  return request<{ success: boolean; message?: string; error?: string }>("/api/providers/key", {
    method: "POST",
    body: JSON.stringify({ provider, api_key, base_url }),
  });
}

export function detectAndSaveApiKey(api_key: string) {
  return request<{
    success: boolean;
    provider?: string;
    provider_label?: string;
    message?: string;
    unlocked_models?: string[];
    error?: string;
  }>("/api/providers/detect-key", {
    method: "POST",
    body: JSON.stringify({ api_key }),
  });
}

