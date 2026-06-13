"""SM-2 spaced repetition for question review scheduling."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import UserQuestionReview

DEFAULT_EASE = 2.5
MIN_EASE = 1.3


def _quality_from_answer(is_correct: bool, confidence: int | None) -> int:
    """Map answer outcome to SM-2 quality 0–5."""
    if confidence is not None:
        if is_correct:
            return min(5, 3 + confidence // 2)
        return max(0, confidence // 2 - 1)
    return 4 if is_correct else 1


def get_or_create_review(db: Session, user_id: str, question_id: str) -> UserQuestionReview:
    row = (
        db.query(UserQuestionReview)
        .filter(UserQuestionReview.user_id == user_id, UserQuestionReview.question_id == question_id)
        .first()
    )
    if row:
        return row
    row = UserQuestionReview(
        user_id=user_id,
        question_id=question_id,
        ease_factor=DEFAULT_EASE,
        interval_days=0,
        repetitions=0,
    )
    db.add(row)
    db.flush()
    return row


def update_review(
    db: Session,
    user_id: str,
    question_id: str,
    is_correct: bool,
    confidence: int | None = None,
) -> UserQuestionReview:
    """Apply SM-2 update after an attempt."""
    review = get_or_create_review(db, user_id, question_id)
    q = _quality_from_answer(is_correct, confidence)

    if q < 3:
        review.repetitions = 0
        review.interval_days = 1
    else:
        if review.repetitions == 0:
            review.interval_days = 1
        elif review.repetitions == 1:
            review.interval_days = 6
        else:
            review.interval_days = max(1, round(review.interval_days * review.ease_factor))
        review.repetitions += 1

    review.ease_factor = max(
        MIN_EASE,
        review.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)),
    )
    review.next_review_at = datetime.utcnow() + timedelta(days=review.interval_days)
    review.last_quality = q
    review.updated_at = datetime.utcnow()
    return review


def get_due_question_ids(db: Session, user_id: str, limit: int = 50) -> list[str]:
    """Questions due for SM-2 review, oldest due first."""
    now = datetime.utcnow()
    rows = (
        db.query(UserQuestionReview)
        .filter(
            UserQuestionReview.user_id == user_id,
            UserQuestionReview.next_review_at.isnot(None),
            UserQuestionReview.next_review_at <= now,
        )
        .order_by(UserQuestionReview.next_review_at.asc())
        .limit(limit)
        .all()
    )
    return [r.question_id for r in rows]


def get_review_stats(db: Session, user_id: str) -> dict:
    now = datetime.utcnow()
    total = db.query(UserQuestionReview).filter(UserQuestionReview.user_id == user_id).count()
    due = (
        db.query(UserQuestionReview)
        .filter(
            UserQuestionReview.user_id == user_id,
            UserQuestionReview.next_review_at.isnot(None),
            UserQuestionReview.next_review_at <= now,
        )
        .count()
    )
    return {"scheduled_cards": total, "due_now": due}
