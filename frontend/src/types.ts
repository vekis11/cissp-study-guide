export type Page =
  | "home"
  | "daily"
  | "missed"
  | "flagged"
  | "mock"
  | "domain"
  | "study"
  | "timed"
  | "analysis"
  | "settings"
  | "practice"
  | "review"
  | "privacy"
  | "terms";

export type PracticeMode = "newbie" | "fast" | "exam";
export type StudyPlan = "just_trying" | "pass_exam" | "high_score" | "expert";
export type ImportanceTier = "must" | "high" | "good";

export type SessionType =
  | "daily"
  | "missed"
  | "mock_exam"
  | "domain_test"
  | "flagged"
  | "topic_drill"
  | "guide_drill"
  | "timed_challenge";

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
  question_type?: "single" | "multi";
  select_count?: number;
}

export interface Settings {
  practice_mode: PracticeMode;
  daily_minutes: number;
  daily_questions: number;
  study_plan: StudyPlan;
  exam_date: string | null;
  theme: string;
  exam_alert_enabled: boolean;
  daily_prioritize_unseen: boolean;
  daily_weak_domain_bias: boolean;
  daily_avoid_repeats: boolean;
}

export interface StudyPlanAdvice {
  days_until_exam: number | null;
  bank_remaining: number;
  bank_total: number;
  bank_answered_unique: number;
  bank_coverage_percent: number;
  recommended_daily_questions: number;
  recommended_daily_minutes: number;
  message: string;
}

export interface DomainBankStats {
  domain: number;
  domain_name: string;
  bank_total: number;
  bank_answered_unique: number;
  bank_remaining: number;
  bank_coverage_percent: number;
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
  time_limit_seconds?: number | null;
  max_wrong_allowed?: number | null;
  wrong_count?: number;
  submitted: boolean;
}

export interface LearningCurvePoint {
  session_id: number;
  completed_at: string | null;
  session_type: string;
  passing: number;
  security: number | null;
  hazard: number;
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

export interface WrongChoiceNote {
  choice: string;
  text: string;
  why_wrong: string;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_choice: string;
  explanation: string;
  manager_brief?: string;
  approach_tips?: string[];
  wrong_choice_notes?: WrongChoiceNote[];
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
  bank_total: number;
  bank_answered_unique: number;
  bank_remaining: number;
  bank_coverage_percent: number;
  domain_bank_coverage: DomainBankStats[];
  domains: DomainStats[];
  recent_sessions: Session[];
  learning_curve: LearningCurvePoint[];
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
  wrong_choice_notes?: WrongChoiceNote[];
  flagged: boolean;
}

export interface CurrentQuestion {
  complete: boolean;
  index?: number;
  total?: number;
  answered?: number;
  question?: Question;
  attempt_id?: number;
  flagged?: boolean;
  time_limit_seconds?: number | null;
  seconds_remaining?: number | null;
  is_timed_challenge?: boolean;
  wrong_count?: number;
  max_wrong_allowed?: number | null;
  timed_expired?: boolean;
  session?: Session;
}

export interface TopicCoverage {
  topic_id: string;
  domain: number;
  domain_name: string;
  title: string;
  importance: string;
  knowledge_questions: number;
  scenario_questions: number;
  fully_tested: boolean;
}

export interface StudyGuideSummary {
  total_topics: number;
  fully_tested: number;
  coverage_percent: number;
  knowledge_questions: number;
  scenario_bank: number;
  scenarios_per_topic?: number;
}

export interface CheatSheetSection {
  topic_id: string;
  importance: string;
  title: string;
  content: string;
  scenarios?: { prompt: string; answer: string }[];
}

export interface CheatSheetDomain {
  domain: number;
  name: string;
  exam_tips?: string[];
  sections: CheatSheetSection[];
}

export interface GuideQuizTier {
  importance: ImportanceTier;
  label: string;
  study_hint: string;
  priority?: number;
  topic_count: number;
  question_count: number;
  topic_ids?: string[];
  topic_titles?: string[];
}

export interface GuideQuizDomain {
  domain: number;
  domain_name: string;
  weight_percent: number;
  tiers: GuideQuizTier[];
}

export interface GuideQuizGroups {
  by_domain: GuideQuizDomain[];
  exam_path: GuideQuizTier[];
}

export interface StudyGuideData {
  catalog: {
    version: string;
    how_to_use: string;
    importance_legend: { marker: string; label: string; description: string }[];
    domain_weights: { domain: number; name: string; weight_percent: number }[];
    manager_mindset: string;
    final_reminders?: string[];
    exam_format: { note: string };
    domains: CheatSheetDomain[];
  };
  coverage: TopicCoverage[];
  quiz_groups: GuideQuizGroups;
  summary: StudyGuideSummary;
}
