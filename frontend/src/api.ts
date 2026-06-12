import { getUserId } from "./utils/userId";
import type {
  Analytics,
  AnswerResult,
  CurrentQuestion,
  DomainInfo,
  ImportanceTier,
  ReviewItem,
  Session,
  SessionProgress,
  SessionType,
  Settings,
  StudyGuideData,
  StudyPlanAdvice,
  SubmitResult,
} from "./types";

const BASE = "/api";

function authHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-User-Id": getUserId(),
  };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () =>
    request<{
      status: string;
      questions: number;
      version?: string;
      cat_min?: number;
      cat_max?: number;
      cat_hours?: number;
    }>("/health"),
  domains: () => request<DomainInfo[]>("/domains"),
  questionCounts: () => request<Record<string, number>>("/questions/count"),
  studyPlan: () => request<StudyPlanAdvice>("/study-plan"),
  studyGuide: () => request<StudyGuideData>("/study-guide"),
  studyGuideCoverage: () =>
    request<{ coverage: StudyGuideData["coverage"]; summary: StudyGuideData["summary"] }>(
      "/study-guide/coverage"
    ),
  settings: {
    get: () => request<Settings>("/settings"),
    update: (data: Partial<Settings>) =>
      request<Settings>("/settings", { method: "PUT", body: JSON.stringify(data) }),
  },
  analytics: () => request<Analytics>("/analytics"),
  exportAnalytics: async () => {
    const res = await fetch(`${BASE}/analytics/export`, { headers: authHeaders() });
    if (!res.ok) throw new Error("Export failed");
    return res.text();
  },
  missed: () => request<{ count: number; questions: unknown[] }>("/missed"),
  flagged: () => request<{ count: number; questions: unknown[] }>("/flagged"),
  sessions: {
    start: (data: {
      session_type: SessionType;
      count?: number;
      domain?: number;
      topic_id?: string;
      importance?: ImportanceTier;
      duration_minutes?: number;
      max_wrong?: number;
    }) => request<Session>("/sessions/start", { method: "POST", body: JSON.stringify(data) }),
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
