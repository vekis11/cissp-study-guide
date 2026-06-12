import type {
  Analytics,
  AnswerResult,
  CurrentQuestion,
  DomainInfo,
  ReviewItem,
  Session,
  SessionProgress,
  SessionType,
  Settings,
  SubmitResult,
} from "./types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string; questions: number }>("/health"),
  domains: () => request<DomainInfo[]>("/domains"),
  questionCounts: () => request<Record<string, number>>("/questions/count"),
  settings: {
    get: () => request<Settings>("/settings"),
    update: (data: Partial<Settings>) =>
      request<Settings>("/settings", { method: "PUT", body: JSON.stringify(data) }),
  },
  analytics: () => request<Analytics>("/analytics"),
  missed: () => request<{ count: number; questions: unknown[] }>("/missed"),
  sessions: {
    start: (data: { session_type: SessionType; count: number; domain?: number }) =>
      request<Session>("/sessions/start", { method: "POST", body: JSON.stringify(data) }),
    get: (id: number) => request<Session>(`/sessions/${id}`),
    progress: (id: number) => request<SessionProgress>(`/sessions/${id}/progress`),
    current: (id: number) => request<CurrentQuestion>(`/sessions/${id}/current`),
    answer: (id: number, data: { question_id: string; selected_choice: string; flagged?: boolean }) =>
      request<AnswerResult>(`/sessions/${id}/answer`, { method: "POST", body: JSON.stringify(data) }),
    submit: (id: number) => request<SubmitResult>(`/sessions/${id}/submit`, { method: "POST", body: JSON.stringify({}) }),
    review: (id: number) =>
      request<{
        session: Session;
        results: ReviewItem[];
        scaled_score: number;
        passed: boolean;
        pass_threshold_scaled: number;
      }>(`/sessions/${id}/review`),
  },
};
