"""Study plan recommendations from bank coverage and exam date."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import UserSettings
from app.services.cat_engine import get_bank_coverage


def _days_until_exam(exam_date: str | None) -> int | None:
    if not exam_date:
        return None
    try:
        target = datetime.strptime(exam_date, "%Y-%m-%d").date()
    except ValueError:
        return None
    delta = (target - date.today()).days
    return max(delta, 0)


def build_study_plan(db: Session, settings: UserSettings) -> dict:
    coverage = get_bank_coverage(db, settings.user_id)
    remaining = coverage["bank_remaining"]
    days = _days_until_exam(settings.exam_date)

    if days is not None and days > 0 and remaining > 0:
        per_day = max(1, (remaining + days - 1) // days)
        minutes_est = per_day * 2
    elif remaining > 0:
        per_day = settings.daily_questions
        minutes_est = settings.daily_minutes
    else:
        per_day = settings.daily_questions
        minutes_est = settings.daily_minutes

    message = "Keep practicing across all domains to maintain readiness."
    if remaining == 0:
        message = "You have explored the full question bank — focus on weak domains and mock CAT exams."
    elif days is not None and days > 0:
        message = (
            f"Cover the remaining {remaining} unseen questions before exam day: "
            f"about {per_day} unique questions per day for the next {days} days."
        )
    elif remaining > 0:
        message = f"{remaining} unique questions left in the bank at your current pace."

    return {
        "days_until_exam": days,
        "bank_remaining": remaining,
        "bank_total": coverage["bank_total"],
        "bank_answered_unique": coverage["bank_answered_unique"],
        "bank_coverage_percent": coverage["bank_coverage_percent"],
        "recommended_daily_questions": per_day,
        "recommended_daily_minutes": minutes_est,
        "message": message,
    }
