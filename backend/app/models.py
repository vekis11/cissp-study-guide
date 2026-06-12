from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    domain: Mapped[int] = mapped_column(Integer, index=True)
    domain_name: Mapped[str] = mapped_column(String(128))
    difficulty: Mapped[str] = mapped_column(String(16), default="medium")
    tags: Mapped[str] = mapped_column(String(256), default="")
    stem: Mapped[str] = mapped_column(Text)
    choice_a: Mapped[str] = mapped_column(Text)
    choice_b: Mapped[str] = mapped_column(Text)
    choice_c: Mapped[str] = mapped_column(Text)
    choice_d: Mapped[str] = mapped_column(Text)
    correct_choice: Mapped[str] = mapped_column(String(8))
    explanation: Mapped[str] = mapped_column(Text)
    source_topic: Mapped[str] = mapped_column(String(256), default="")


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="legacy")
    mode: Mapped[str] = mapped_column(String(32))
    session_type: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    scaled_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    domain_filter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_wrong_allowed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted: Mapped[bool] = mapped_column(Boolean, default=False)

    attempts: Mapped[list["Attempt"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), index=True)
    selected_choice: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)

    session: Mapped["SessionRecord"] = relationship(back_populates="attempts")
    question: Mapped["Question"] = relationship()


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    practice_mode: Mapped[str] = mapped_column(String(16), default="newbie")
    daily_minutes: Mapped[int] = mapped_column(Integer, default=30)
    daily_questions: Mapped[int] = mapped_column(Integer, default=20)
    study_plan: Mapped[str] = mapped_column(String(32), default="pass_exam")
    exam_date: Mapped[str | None] = mapped_column(String(16), nullable=True)
    theme: Mapped[str] = mapped_column(String(16), default="dark")
    exam_alert_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_prioritize_unseen: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_weak_domain_bias: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_avoid_repeats: Mapped[bool] = mapped_column(Boolean, default=True)
