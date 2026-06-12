export type Page =
  | "home"
  | "daily"
  | "missed"
  | "mock"
  | "domain"
  | "analysis"
  | "settings"
  | "practice"
  | "review"
  | "privacy"
  | "terms";

export type PracticeMode = "newbie" | "fast" | "exam";
export type StudyPlan = "just_trying" | "pass_exam" | "high_score" | "expert";
export type SessionType = "daily" | "missed" | "mock_exam" | "domain_test";

export interface Question {
  id: string;
  domain: number;
  domain_name: string;
  difficulty: string;
  tags: string;
  stem: string;
  choice_a: string;
  choice_b: string;
  choice_c: string;
  choice_d: string;
  source_topic: string;
}

export interface Settings {
  practice_mode: PracticeMode;
  daily_minutes: number;
  daily_questions: number;
  study_plan: StudyPlan;
  exam_date: string | null;
  theme: string;
  exam_alert_enabled: boolean;
}

export interface Session {
  id: number;
  mode: string;
  session_type: string;
  started_at: string;
  completed_at: string | null;
  score_percent: number | null;
  scaled_score?: number | null;
  total_questions: number;
  correct_count: number;
  domain_filter: number | null;
  submitted: boolean;
}

export interface SessionProgress {
  answered: number;
  total_in_session: number;
  max_questions: number;
  can_submit: boolean;
  score_percent: number;
  scaled_score: number;
  passed: boolean;
  pass_threshold_scaled: number;
}

export interface SubmitResult {
  session: Session;
  scaled_score: number;
  score_percent: number;
  passed: boolean;
  grade_label: string;
  pass_threshold_scaled: number;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_choice: string;
  explanation: string;
  manager_brief?: string;
  approach_tips?: string[];
  score_percent: number;
  session_complete: boolean;
}

export interface DomainInfo {
  id: number;
  name: string;
  weight: number;
}

export interface DomainStats {
  domain: number;
  domain_name: string;
  weight: number;
  total_attempts: number;
  correct_attempts: number;
  pass_rate: number;
  readiness: string;
}

export interface Analytics {
  overall_pass_rate: number;
  overall_readiness: string;
  total_questions_answered: number;
  total_sessions: number;
  exam_pass_threshold: number;
  domains: DomainStats[];
  recent_sessions: Session[];
}

export interface ReviewItem {
  attempt_id: number;
  question: Question;
  selected_choice: string | null;
  correct_choice: string;
  is_correct: boolean | null;
  explanation: string;
  manager_brief?: string;
  approach_tips?: string[];
  flagged: boolean;
}

export interface CurrentQuestion {
  complete: boolean;
  index?: number;
  total?: number;
  question?: Question;
  attempt_id?: number;
  flagged?: boolean;
  time_limit_seconds?: number | null;
  session?: Session;
}
