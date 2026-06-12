from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PracticeMode = Literal["newbie", "fast", "exam"]
StudyPlan = Literal["just_trying", "pass_exam", "high_score", "expert"]
SessionType = Literal["daily", "missed", "mock_exam", "domain_test", "flagged"]


class QuestionOut(BaseModel):
    id: str
    domain: int
    domain_name: str
    difficulty: str
    tags: str
    stem: str
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    source_topic: str

    model_config = {"from_attributes": True}


class QuestionWithAnswer(QuestionOut):
    correct_choice: str
    explanation: str


class StartSessionRequest(BaseModel):
    session_type: SessionType
    count: int = Field(default=20, ge=1, le=150)
    domain: int | None = Field(default=None, ge=1, le=8)
    practice_mode: PracticeMode | None = None


class AnswerRequest(BaseModel):
    question_id: str
    selected_choice: str = Field(pattern="^[ABCD]$")
    flagged: bool = False


class SubmitSessionRequest(BaseModel):
    session_id: int


class AttemptOut(BaseModel):
    id: int
    question_id: str
    selected_choice: str | None
    is_correct: bool | None
    flagged: bool
    question: QuestionOut | None = None
    correct_choice: str | None = None
    explanation: str | None = None

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    mode: str
    session_type: str
    started_at: datetime
    completed_at: datetime | None
    score_percent: float | None
    scaled_score: float | None = None
    total_questions: int
    correct_count: int
    domain_filter: int | None
    submitted: bool
    attempts: list[AttemptOut] = []

    model_config = {"from_attributes": True}


class SessionProgress(BaseModel):
    answered: int
    total_in_session: int
    max_questions: int
    can_submit: bool
    score_percent: float
    scaled_score: float
    passed: bool
    pass_threshold_scaled: int = 700


class SubmitResult(BaseModel):
    session: SessionOut
    scaled_score: float
    score_percent: float
    passed: bool
    grade_label: str
    pass_threshold_scaled: int = 700


class AnswerResult(BaseModel):
    is_correct: bool
    correct_choice: str
    explanation: str
    manager_brief: str = ""
    approach_tips: list[str] = Field(default_factory=list)
    score_percent: float
    session_complete: bool


class ReviewItemOut(BaseModel):
    attempt_id: int
    question: QuestionOut
    selected_choice: str | None
    correct_choice: str
    is_correct: bool | None
    explanation: str
    manager_brief: str = ""
    approach_tips: list[str] = Field(default_factory=list)
    flagged: bool


class DomainStats(BaseModel):
    domain: int
    domain_name: str
    weight: float
    total_attempts: int
    correct_attempts: int
    pass_rate: float
    readiness: str


class DomainBankStats(BaseModel):
    domain: int
    domain_name: str
    bank_total: int
    bank_answered_unique: int
    bank_remaining: int
    bank_coverage_percent: float


class StudyPlanOut(BaseModel):
    days_until_exam: int | None
    bank_remaining: int
    bank_total: int
    bank_answered_unique: int
    bank_coverage_percent: float
    recommended_daily_questions: int
    recommended_daily_minutes: int
    message: str


class AnalyticsOut(BaseModel):
    overall_pass_rate: float
    overall_readiness: str
    total_questions_answered: int
    total_sessions: int
    exam_pass_threshold: float
    bank_total: int = 0
    bank_answered_unique: int = 0
    bank_remaining: int = 0
    bank_coverage_percent: float = 0.0
    domain_bank_coverage: list[DomainBankStats] = Field(default_factory=list)
    domains: list[DomainStats]
    recent_sessions: list[SessionOut]


class SettingsOut(BaseModel):
    practice_mode: PracticeMode
    daily_minutes: int
    daily_questions: int
    study_plan: StudyPlan
    exam_date: str | None
    theme: str
    exam_alert_enabled: bool
    daily_prioritize_unseen: bool = True
    daily_weak_domain_bias: bool = True
    daily_avoid_repeats: bool = True

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    practice_mode: PracticeMode | None = None
    daily_minutes: int | None = Field(default=None, ge=5, le=240)
    daily_questions: int | None = Field(default=None, ge=5, le=100)
    study_plan: StudyPlan | None = None
    exam_date: str | None = None
    theme: str | None = None
    exam_alert_enabled: bool | None = None
    daily_prioritize_unseen: bool | None = None
    daily_weak_domain_bias: bool | None = None
    daily_avoid_repeats: bool | None = None


class DomainInfo(BaseModel):
    id: int
    name: str
    weight: float


class CatNextQuestion(BaseModel):
    session: SessionOut
    question: QuestionOut
    question_number: int
    max_questions: int
    time_limit_seconds: int
    should_stop: bool
