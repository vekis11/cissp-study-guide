from sqlalchemy.orm import Session

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.schemas import AnalyticsOut, DomainBankStats, DomainStats, SessionOut
from app.services.cat_engine import (
    PASS_THRESHOLD,
    compute_score,
    get_bank_coverage,
    get_domain_bank_coverage,
    readiness_label,
    _attempts_for_user,
)


def build_analytics(db: Session, user_id: str) -> AnalyticsOut:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    study_plan = settings.study_plan if settings else "pass_exam"

    domain_stats: list[DomainStats] = []
    total_attempts = 0
    total_correct = 0

    for domain_id in sorted(DOMAIN_NAMES):
        attempts = (
            _attempts_for_user(db, user_id)
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
        .filter(SessionRecord.user_id == user_id, SessionRecord.submitted == True)  # noqa: E712
        .order_by(SessionRecord.completed_at.desc())
        .limit(10)
        .all()
    )

    coverage = get_bank_coverage(db, user_id)
    domain_bank = [DomainBankStats(**row) for row in get_domain_bank_coverage(db, user_id)]

    return AnalyticsOut(
        overall_pass_rate=overall,
        overall_readiness=readiness_label(overall, study_plan),
        total_questions_answered=total_attempts,
        total_sessions=db.query(SessionRecord)
        .filter(SessionRecord.user_id == user_id, SessionRecord.submitted == True)  # noqa: E712
        .count(),
        exam_pass_threshold=PASS_THRESHOLD,
        bank_total=coverage["bank_total"],
        bank_answered_unique=coverage["bank_answered_unique"],
        bank_remaining=coverage["bank_remaining"],
        bank_coverage_percent=coverage["bank_coverage_percent"],
        domain_bank_coverage=domain_bank,
        domains=domain_stats,
        recent_sessions=[SessionOut.model_validate(s) for s in sessions],
    )


def export_analytics_csv(db: Session, user_id: str) -> str:
    data = build_analytics(db, user_id)
    lines = [
        "CISSP Study Companion — Progress Export",
        f"Overall accuracy,{data.overall_pass_rate}%",
        f"Readiness,{data.overall_readiness}",
        f"Bank coverage,{data.bank_answered_unique}/{data.bank_total} ({data.bank_coverage_percent}%)",
        f"Total attempts,{data.total_questions_answered}",
        f"Completed sessions,{data.total_sessions}",
        "",
        "Domain,Weight,Attempts,Correct,Pass Rate,Readiness,Bank Seen,Bank Total,Bank %",
    ]
    bank_map = {d.domain: d for d in data.domain_bank_coverage}
    for d in data.domains:
        b = bank_map.get(d.domain)
        lines.append(
            f"{d.domain_name},{d.weight},{d.total_attempts},{d.correct_attempts},"
            f"{d.pass_rate}%,{d.readiness},"
            f"{b.bank_answered_unique if b else 0},{b.bank_total if b else 0},"
            f"{b.bank_coverage_percent if b else 0}%"
        )
    return "\n".join(lines)
