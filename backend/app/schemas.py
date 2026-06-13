from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PracticeMode = Literal["newbie", "fast", "exam"]
StudyPlan = Literal["just_trying", "pass_exam", "high_score", "expert"]
ImportanceTier = Literal["must", "high", "good"]
SessionType = Literal[
    "daily",
    "missed",
    "mock_exam",
    "domain_test",
    "flagged",
    "topic_drill",
    "guide_drill",
    "timed_challenge",
]



class QuestionOut(BaseModel):
    id: str
    domain: int
    domain_name: str
    difficulty: str
    difficulty_level: int | None = None
    topic_id: str | None = None
    reference: str | None = None
    tags: str
    stem: str
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    source_topic: str
    question_type: str = "single"
    select_count: int = 1

    model_config = {"from_attributes": True}


class QuestionWithAnswer(QuestionOut):
    correct_choice: str
    explanation: str


class StartSessionRequest(BaseModel):
    session_type: SessionType
    count: int = Field(default=20, ge=1, le=150)
    domain: int | None = Field(default=None, ge=1, le=8)
    topic_id: str | None = None
    importance: ImportanceTier | None = None
    practice_mode: PracticeMode | None = None
    duration_minutes: int | None = Field(default=None, ge=5, le=180)
    max_wrong: int | None = Field(default=None, ge=0, le=50)


class AnswerRequest(BaseModel):
    question_id: str
    selected_choice: str = Field(min_length=1, max_length=4, pattern="^[ABCD]+$")
    flagged: bool = False
    time_spent_seconds: int | None = Field(default=None, ge=0, le=3600)
    confidence: int | None = Field(default=None, ge=1, le=5)


class FlagUpdateRequest(BaseModel):
    question_id: str
    flagged: bool


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
    time_limit_seconds: int | None = None
    max_wrong_allowed: int | None = None
    wrong_count: int = 0
    theta_proxy: float | None = None
    pass_likelihood: float | None = None
    submitted: bool
    attempts: list[AttemptOut] = []

    model_config = {"from_attributes": True}


class LearningCurvePoint(BaseModel):
    session_id: int
    completed_at: datetime | None
    session_type: str
    passing: float
    security: float | None = None
    hazard: float


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
    pass_likelihood: float | None = None


class WrongChoiceNote(BaseModel):
    choice: str
    text: str
    why_wrong: str


class ExplanationSectionOut(BaseModel):
    key: str
    title: str
    body: str


class AnswerResult(BaseModel):
    is_correct: bool
    correct_choice: str
    explanation: str
    manager_brief: str = ""
    explanation_sections: list[ExplanationSectionOut] = Field(default_factory=list)
    reference_sections: list[ExplanationSectionOut] = Field(default_factory=list)
    trap: str = ""
    approach_tips: list[str] = Field(default_factory=list)
    wrong_choice_notes: list[WrongChoiceNote] = Field(default_factory=list)
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
    explanation_sections: list[ExplanationSectionOut] = Field(default_factory=list)
    reference_sections: list[ExplanationSectionOut] = Field(default_factory=list)
    trap: str = ""
    approach_tips: list[str] = Field(default_factory=list)
    wrong_choice_notes: list[WrongChoiceNote] = Field(default_factory=list)
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


class TopicStats(BaseModel):
    topic_id: str
    title: str
    domain: int
    total_attempts: int
    correct_attempts: int
    pass_rate: float
    readiness: str


class TimingStats(BaseModel):
    avg_seconds_per_question: float
    total_timed_attempts: int
    avg_confidence: float | None = None


class FlashcardOut(BaseModel):
    id: str
    domain: int
    domain_name: str
    topic_id: str
    importance: str
    front: str
    back: str


class DomainModuleOut(BaseModel):
    domain: int
    domain_name: str
    weight: float
    pass_rate: float
    readiness: str
    topic_count: int
    flashcard_count: int
    bank_coverage_percent: float


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
    learning_curve: list[LearningCurvePoint] = Field(default_factory=list)
    weak_topics: list[TopicStats] = Field(default_factory=list)
    timing: TimingStats | None = None
    sm2_due_count: int = 0


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


class TopicCoverageOut(BaseModel):
    topic_id: str
    domain: int
    domain_name: str
    title: str
    importance: str
    knowledge_questions: int
    scenario_questions: int
    fully_tested: bool


class StudyGuideSummaryOut(BaseModel):
    total_topics: int
    fully_tested: int
    coverage_percent: float
    knowledge_questions: int
    scenario_bank: int
    knowledge_per_topic: int = 1
    scenarios_per_topic: int = 1


class GuideQuizTierOut(BaseModel):
    importance: str
    label: str
    study_hint: str
    priority: int
    topic_count: int
    question_count: int
    answered_count: int = 0
    remaining_count: int = 0
    topic_ids: list[str] = Field(default_factory=list)
    topic_titles: list[str] = Field(default_factory=list)


class GuideQuizDomainOut(BaseModel):
    domain: int
    domain_name: str
    weight_percent: int
    tiers: list[GuideQuizTierOut]


class GuideQuizGroupsOut(BaseModel):
    by_domain: list[GuideQuizDomainOut]
    exam_path: list[GuideQuizTierOut]


class StudyGuideOut(BaseModel):
    catalog: dict
    coverage: list[TopicCoverageOut]
    quiz_groups: GuideQuizGroupsOut
    summary: StudyGuideSummaryOut
