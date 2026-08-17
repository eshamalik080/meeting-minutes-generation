/**
 * Auth API client — fully separate from lib/api.ts (the job/pipeline/export
 * client). Reuses only ApiError for consistent error handling.
 */

import { ApiError } from "./api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

export interface AuthResponse {
  access_token: string;
  token_type: string;
  email: string;
}

async function authRequest(path: string, body: unknown): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const parsed = await res.json();
      detail = parsed.detail ?? detail;
    } catch {
      // not JSON — fall back to statusText
    }
    const message =
      typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : String(detail);
    throw new ApiError(message, res.status);
  }
  return res.json() as Promise<AuthResponse>;
}

export function signup(email: string, password: string): Promise<AuthResponse> {
  return authRequest("/auth/signup", { email, password });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return authRequest("/auth/login", { email, password });
}

export async function fetchCurrentUser(token: string): Promise<{ email: string } | null> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  return res.json();
}
