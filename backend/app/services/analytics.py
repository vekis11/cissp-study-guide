from datetime import datetime

from sqlalchemy.orm import Session

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.schemas import AnalyticsOut, DomainStats, SessionOut
from app.services.cat_engine import PASS_THRESHOLD, compute_score, readiness_label


def build_analytics(db: Session) -> AnalyticsOut:
    settings = db.query(UserSettings).first()
    study_plan = settings.study_plan if settings else "pass_exam"

    domain_stats: list[DomainStats] = []
    total_attempts = 0
    total_correct = 0

    for domain_id in sorted(DOMAIN_NAMES):
        attempts = (
            db.query(Attempt)
            .join(Question, Question.id == Attempt.question_id)
            .filter(Question.domain == domain_id, Attempt.is_correct.isnot(None))
            .all()
        )
        d_total = len(attempts)
        d_correct = sum(1 for a in attempts if a.is_correct)
        total_attempts += d_total
        total_correct += d_correct
        rate = compute_score(d_correct, d_total)
        domain_stats.append(
            DomainStats(
                domain=domain_id,
                domain_name=DOMAIN_NAMES[domain_id],
                weight=DOMAIN_WEIGHTS[domain_id],
                total_attempts=d_total,
                correct_attempts=d_correct,
                pass_rate=rate,
                readiness=readiness_label(rate, study_plan),
            )
        )

    overall = compute_score(total_correct, total_attempts)
    sessions = (
        db.query(SessionRecord)
        .filter(SessionRecord.submitted == True)  # noqa: E712
        .order_by(SessionRecord.completed_at.desc())
        .limit(10)
        .all()
    )

    return AnalyticsOut(
        overall_pass_rate=overall,
        overall_readiness=readiness_label(overall, study_plan),
        total_questions_answered=total_attempts,
        total_sessions=db.query(SessionRecord).filter(SessionRecord.submitted == True).count(),  # noqa: E712
        exam_pass_threshold=PASS_THRESHOLD,
        domains=domain_stats,
        recent_sessions=[SessionOut.model_validate(s) for s in sessions],
    )
