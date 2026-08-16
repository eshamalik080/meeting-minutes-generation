/**
 * Typed client for the FastAPI backend. In dev, requests to API_BASE
 * ("/api") are proxied to http://127.0.0.1:8000 by vite.config.ts, so no
 * env var is needed locally. Set VITE_API_BASE_URL for other environments
 * (see .env.example).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

export type JobStatusValue = "pending" | "processing" | "completed" | "failed";

export interface UploadResponse {
  job_id: string;
  status: JobStatusValue;
}

export interface StatusResponse {
  job_id: string;
  status: JobStatusValue;
  filename: string;
  stage: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActionItem {
  task: string;
  owner: string;
  deadline: string;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  speaker: string;
  text: string;
}

export interface MeetingMinutes {
  job_id: string;
  source_filename: string;
  generated_at: string;
  duration_seconds: number | null;
  summary: string;
  key_topics: string[];
  decisions: string[];
  action_items: ActionItem[];
  transcript: TranscriptSegment[];
  participants: string[];
}

export type ExportFormat = "json" | "html" | "pdf";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    const message =
      typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : String(detail);
    throw new ApiError(message, res.status);
  }
  return res.json() as Promise<T>;
}

export function uploadMeeting(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/upload", { method: "POST", body: formData });
}

export function getStatus(jobId: string): Promise<StatusResponse> {
  return request<StatusResponse>(`/status/${jobId}`);
}

export function getResult(jobId: string): Promise<MeetingMinutes> {
  return request<MeetingMinutes>(`/result/${jobId}`);
}

export function exportUrl(jobId: string, format: ExportFormat): string {
  return `${API_BASE}/export/${jobId}?format=${format}`;
}

export { ApiError };
