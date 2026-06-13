from sqlalchemy.orm import Session, joinedload

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.schemas import (
    AnalyticsOut,
    DomainBankStats,
    DomainStats,
    LearningCurvePoint,
    SessionOut,
    TimingStats,
    TopicStats,
)
from app.services.cat_engine import (
    PASS_THRESHOLD,
    compute_score,
    get_bank_coverage,
    get_domain_bank_coverage,
    readiness_label,
    _attempts_for_user,
)
from app.services.spaced_repetition import get_review_stats


PASSING_BENCHMARK = 70.0


def _session_wrong_count(attempts: list[Attempt]) -> int:
    return sum(1 for a in attempts if a.selected_choice and a.is_correct is False)


def _session_to_out_with_stats(db: Session, session: SessionRecord) -> SessionOut:
    attempts = (
        db.query(Attempt)
        .options(joinedload(Attempt.question))
        .filter(Attempt.session_id == session.id)
        .order_by(Attempt.id)
        .all()
    )
    out = SessionOut.model_validate(session)
    out.wrong_count = _session_wrong_count(attempts)
    return out


def build_learning_curve(db: Session, user_id: str, limit: int = 30) -> list[LearningCurvePoint]:
    sessions = (
        db.query(SessionRecord)
        .filter(SessionRecord.user_id == user_id, SessionRecord.submitted == True)  # noqa: E712
        .order_by(SessionRecord.completed_at.asc())
        .limit(limit)
        .all()
    )
    points: list[LearningCurvePoint] = []
    for session in sessions:
        attempts = (
            db.query(Attempt)
            .options(joinedload(Attempt.question))
            .filter(Attempt.session_id == session.id, Attempt.selected_choice.isnot(None))
            .all()
        )
        passing = session.scaled_score / 10 if session.scaled_score is not None else (session.score_percent or 0.0)
        d1_attempts = [a for a in attempts if a.question and a.question.domain == 1]
        d1_correct = sum(1 for a in d1_attempts if a.is_correct)
        security = compute_score(d1_correct, len(d1_attempts)) if d1_attempts else None
        hazard = max(0.0, PASSING_BENCHMARK - passing)
        points.append(
            LearningCurvePoint(
                session_id=session.id,
                completed_at=session.completed_at,
                session_type=session.session_type,
                passing=round(passing, 1),
                security=round(security, 1) if security is not None else None,
                hazard=round(hazard, 1),
            )
        )
    return points


def _topic_titles() -> dict[str, dict]:
    titles: dict[str, dict] = {}
    for dom in CHEAT_SHEET["domains"]:
        for section in dom.get("sections", []):
            tid = section.get("topic_id", "")
            if tid:
                titles[tid] = {"title": section.get("title", tid), "domain": dom["domain"]}
    return titles


def build_weak_topics(db: Session, user_id: str, study_plan: str, limit: int = 10) -> list[TopicStats]:
    titles = _topic_titles()
    attempts = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.is_correct.isnot(None))
        .join(Question, Question.id == Attempt.question_id)
        .all()
    )
    by_topic: dict[str, list[Attempt]] = {}
    for a in attempts:
        tid = a.question.topic_id if a.question else None
        if not tid:
            continue
        by_topic.setdefault(tid, []).append(a)

    stats: list[TopicStats] = []
    for tid, rows in by_topic.items():
        meta = titles.get(tid, {"title": tid, "domain": 0})
        correct = sum(1 for r in rows if r.is_correct)
        total = len(rows)
        rate = compute_score(correct, total)
        stats.append(
            TopicStats(
                topic_id=tid,
                title=meta["title"],
                domain=meta["domain"],
                total_attempts=total,
                correct_attempts=correct,
                pass_rate=rate,
                readiness=readiness_label(rate, study_plan),
            )
        )
    stats.sort(key=lambda s: (s.pass_rate, -s.total_attempts))
    return stats[:limit]


def build_timing_stats(db: Session, user_id: str) -> TimingStats | None:
    rows = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.time_spent_seconds.isnot(None))
        .all()
    )
    if not rows:
        return None
    times = [r.time_spent_seconds for r in rows if r.time_spent_seconds]
    confidences = [r.confidence for r in rows if r.confidence is not None]
    if not times:
        return None
    avg_conf = round(sum(confidences) / len(confidences), 1) if confidences else None
    return TimingStats(
        avg_seconds_per_question=round(sum(times) / len(times), 1),
        total_timed_attempts=len(times),
        avg_confidence=avg_conf,
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
    learning_curve = build_learning_curve(db, user_id, limit=30)
    weak_topics = build_weak_topics(db, user_id, study_plan)
    timing = build_timing_stats(db, user_id)
    sm2 = get_review_stats(db, user_id)

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
        recent_sessions=[_session_to_out_with_stats(db, s) for s in sessions],
        learning_curve=learning_curve,
        weak_topics=weak_topics,
        timing=timing,
        sm2_due_count=sm2["due_now"],
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
