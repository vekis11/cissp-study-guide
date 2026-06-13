import random
from collections import defaultdict
from datetime import datetime

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session, joinedload

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS, PASS_SCALED
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.services.irt_cat import THETA_START, target_difficulty_level, update_theta
from app.services.spaced_repetition import get_due_question_ids

DIFFICULTY_ORDER = ["easy", "medium", "hard"]
CAT_MIN_QUESTIONS = 125
CAT_MAX_QUESTIONS = 150
CAT_TIME_SECONDS = 3 * 60 * 60  # ISC2 April 2024 CAT: 3 hours
PASS_THRESHOLD = 70.0


def _difficulty_index(level: str) -> int:
    try:
        return DIFFICULTY_ORDER.index(level)
    except ValueError:
        return 1


def _pick_weighted_domain(domain_counts: dict[int, int], total_answered: int) -> int:
    deficits = {}
    for domain, weight in DOMAIN_WEIGHTS.items():
        expected = weight * max(total_answered, 1)
        deficits[domain] = expected - domain_counts.get(domain, 0)
    return max(deficits, key=deficits.get)


def _attempts_for_user(db: Session, user_id: str):
    return (
        db.query(Attempt)
        .join(SessionRecord, SessionRecord.id == Attempt.session_id)
        .filter(SessionRecord.user_id == user_id)
    )


def get_distinct_answered_question_ids(db: Session, user_id: str) -> set[str]:
    rows = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.selected_choice.isnot(None))
        .with_entities(Attempt.question_id)
        .distinct()
        .all()
    )
    return {r[0] for r in rows}


def get_recent_daily_question_ids(db: Session, user_id: str, sessions_back: int = 5) -> set[str]:
    recent_sessions = (
        db.query(SessionRecord.id)
        .filter(SessionRecord.user_id == user_id, SessionRecord.session_type == "daily")
        .order_by(SessionRecord.started_at.desc())
        .limit(sessions_back)
        .all()
    )
    if not recent_sessions:
        return set()
    session_ids = [s[0] for s in recent_sessions]
    rows = db.query(Attempt.question_id).filter(Attempt.session_id.in_(session_ids)).all()
    return {r[0] for r in rows}


def get_weak_domains(db: Session, user_id: str, threshold: float = PASS_THRESHOLD) -> set[int]:
    weak: set[int] = set()
    for domain_id in DOMAIN_NAMES:
        attempts = (
            _attempts_for_user(db, user_id)
            .join(Question, Question.id == Attempt.question_id)
            .filter(Question.domain == domain_id, Attempt.is_correct.isnot(None))
            .all()
        )
        if not attempts:
            weak.add(domain_id)
            continue
        rate = compute_score(sum(1 for a in attempts if a.is_correct), len(attempts))
        if rate < threshold:
            weak.add(domain_id)
    return weak


def select_daily_questions(
    db: Session,
    count: int,
    user_id: str,
    settings: UserSettings | None = None,
) -> list[Question]:
    """
    Daily practice: domain-weighted mix, prioritize unseen, optional weak-domain bias,
    exclude recent daily repeats, shuffle each session.
    """
    pool = db.query(Question).all()
    if not pool:
        return []

    settings = settings or UserSettings(user_id=user_id)
    due_ids = get_due_question_ids(db, user_id, limit=min(count // 2 + 5, 20))
    recent_ids = get_recent_daily_question_ids(db, user_id, sessions_back=5)
    answered_ids = get_distinct_answered_question_ids(db, user_id)
    weak_domains = get_weak_domains(db, user_id) if settings.daily_weak_domain_bias else set()

    by_domain: dict[int, list[Question]] = defaultdict(list)
    for q in pool:
        by_domain[q.domain].append(q)

    avoid_answered = settings.daily_avoid_repeats and len(answered_ids) < len(pool)

    def tier(q: Question) -> int:
        if q.id in recent_ids:
            return 4
        if settings.daily_prioritize_unseen and q.id not in answered_ids:
            return 0
        if avoid_answered and q.id in answered_ids:
            return 3
        if q.id in answered_ids:
            return 2
        return 1

    selected: list[Question] = []
    used: set[str] = set()

    if due_ids:
        due_map = {q.id: q for q in db.query(Question).filter(Question.id.in_(due_ids)).all()}
        for qid in due_ids:
            if qid in due_map and len(selected) < count:
                selected.append(due_map[qid])
                used.add(qid)

    attempts = 0
    max_attempts = count * 50

    while len(selected) < count and attempts < max_attempts:
        attempts += 1
        if weak_domains and random.random() < 0.45:
            target_domain = random.choice(sorted(weak_domains))
        else:
            deficits = {
                d: (DOMAIN_WEIGHTS[d] * max(count, 1)) - sum(1 for s in selected if s.domain == d)
                for d in DOMAIN_WEIGHTS
            }
            target_domain = max(deficits, key=deficits.get)

        candidates = [q for q in by_domain.get(target_domain, []) if q.id not in used]
        if not candidates:
            candidates = [q for q in pool if q.id not in used]
        if not candidates:
            break

        candidates.sort(key=lambda q: (tier(q), random.random()))
        pick = candidates[0]
        if avoid_answered and tier(pick) >= 3 and len(answered_ids) < len(pool):
            unseen = [q for q in candidates if q.id not in answered_ids]
            if unseen:
                pick = unseen[0]

        selected.append(pick)
        used.add(pick.id)

    random.shuffle(selected)
    return selected[:count]


def get_bank_coverage(db: Session, user_id: str) -> dict:
    bank_total = db.query(func.count(Question.id)).scalar() or 0
    answered_unique = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.selected_choice.isnot(None))
        .with_entities(func.count(distinct(Attempt.question_id)))
        .scalar()
        or 0
    )
    remaining = max(bank_total - answered_unique, 0)
    coverage = round((answered_unique / bank_total) * 100, 1) if bank_total else 0.0
    return {
        "bank_total": bank_total,
        "bank_answered_unique": answered_unique,
        "bank_remaining": remaining,
        "bank_coverage_percent": coverage,
    }


def get_domain_bank_coverage(db: Session, user_id: str) -> list[dict]:
    answered_by_domain: dict[int, set[str]] = defaultdict(set)
    rows = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.selected_choice.isnot(None))
        .join(Question, Question.id == Attempt.question_id)
        .with_entities(Question.domain, Attempt.question_id)
        .all()
    )
    for domain, qid in rows:
        answered_by_domain[domain].add(qid)

    result = []
    for domain_id in sorted(DOMAIN_NAMES):
        bank_total = db.query(Question).filter(Question.domain == domain_id).count()
        answered = len(answered_by_domain.get(domain_id, set()))
        remaining = max(bank_total - answered, 0)
        pct = round((answered / bank_total) * 100, 1) if bank_total else 0.0
        result.append({
            "domain": domain_id,
            "domain_name": DOMAIN_NAMES[domain_id],
            "bank_total": bank_total,
            "bank_answered_unique": answered,
            "bank_remaining": remaining,
            "bank_coverage_percent": pct,
        })
    return result


def select_questions(
    db: Session,
    count: int,
    domain: int | None = None,
    exclude_ids: set[str] | None = None,
    difficulty: str | None = None,
    difficulty_level: int | None = None,
    cat_mode: bool = False,
    domain_counts: dict[int, int] | None = None,
) -> list[Question]:
    query = db.query(Question)
    if domain:
        query = query.filter(Question.domain == domain)
    if exclude_ids:
        query = query.filter(~Question.id.in_(exclude_ids))
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    pool = query.all()
    if difficulty_level and pool:
        near = [
            q for q in pool
            if q.difficulty_level is not None and abs(q.difficulty_level - difficulty_level) <= 1
        ]
        if near:
            pool = near
    if not pool:
        return []

    if cat_mode and not domain:
        domain_counts = domain_counts or {}
        selected: list[Question] = []
        used_ids: set[str] = set(exclude_ids or [])
        by_domain: dict[int, list[Question]] = defaultdict(list)
        for q in pool:
            by_domain[q.domain].append(q)
        for _ in range(count):
            target_domain = _pick_weighted_domain(domain_counts, len(selected))
            candidates = [q for q in by_domain.get(target_domain, []) if q.id not in used_ids]
            if not candidates:
                candidates = [q for q in pool if q.id not in used_ids]
            if not candidates:
                break
            choice = random.choice(candidates)
            selected.append(choice)
            used_ids.add(choice.id)
            domain_counts[target_domain] = domain_counts.get(target_domain, 0) + 1
        return selected

    if len(pool) <= count:
        random.shuffle(pool)
        return pool
    return random.sample(pool, count)


def pick_next_cat_question(
    db: Session,
    exclude_ids: set[str],
    last_difficulty: str,
    is_correct: bool,
    domain_counts: dict[int, int],
    theta: float = THETA_START,
    last_difficulty_level: int = 3,
) -> Question | None:
    new_theta = update_theta(theta, is_correct, last_difficulty_level)
    target_level = target_difficulty_level(new_theta)
    next_diff = next_cat_difficulty(last_difficulty, is_correct)
    batch = select_questions(
        db,
        1,
        exclude_ids=exclude_ids,
        difficulty=next_diff,
        difficulty_level=target_level,
        cat_mode=True,
        domain_counts=domain_counts,
    )
    if batch:
        return batch[0]
    batch = select_questions(
        db,
        1,
        exclude_ids=exclude_ids,
        difficulty_level=target_level,
        cat_mode=True,
        domain_counts=domain_counts,
    )
    if batch:
        return batch[0]
    batch = select_questions(db, 1, exclude_ids=exclude_ids, cat_mode=True, domain_counts=domain_counts)
    return batch[0] if batch else None


def session_domain_counts(attempts: list[Attempt]) -> dict[int, int]:
    counts: dict[int, int] = defaultdict(int)
    for a in attempts:
        if a.question:
            counts[a.question.domain] += 1
    return dict(counts)


def next_cat_difficulty(current: str, is_correct: bool) -> str:
    idx = _difficulty_index(current)
    if is_correct:
        idx = min(idx + 1, len(DIFFICULTY_ORDER) - 1)
    else:
        idx = max(idx - 1, 0)
    return DIFFICULTY_ORDER[idx]


def should_stop_cat(answered: int, correct: int, min_questions: int = CAT_MIN_QUESTIONS) -> bool:
    if answered < min_questions:
        return False
    if answered >= CAT_MAX_QUESTIONS:
        return True
    score = (correct / answered) * 100 if answered else 0
    if answered >= min_questions and (score >= 85 or score <= 55):
        return True
    return False


def compute_score(correct: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)


def readiness_label(pass_rate: float, study_plan: str) -> str:
    thresholds = {
        "just_trying": 50,
        "pass_exam": PASS_THRESHOLD,
        "high_score": 80,
        "expert": 90,
    }
    target = thresholds.get(study_plan, PASS_THRESHOLD)
    if pass_rate >= target + 10:
        return "Exam Ready"
    if pass_rate >= target:
        return "Near Ready"
    if pass_rate >= target - 15:
        return "Building"
    return "Needs Focus"


def get_missed_question_ids(db: Session, user_id: str) -> list[str]:
    """SM-2 due reviews plus last-wrong questions, most overdue first."""
    due = get_due_question_ids(db, user_id, limit=100)
    attempts = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.selected_choice.isnot(None))
        .order_by(Attempt.answered_at.desc())
        .all()
    )
    last_by_question: dict[str, Attempt] = {}
    for attempt in attempts:
        if attempt.question_id not in last_by_question:
            last_by_question[attempt.question_id] = attempt

    missed: list[tuple[str, datetime]] = []
    for qid, attempt in last_by_question.items():
        if attempt.is_correct is False:
            missed.append((qid, attempt.answered_at))

    missed.sort(key=lambda item: item[1])
    wrong_ids = [qid for qid, _ in missed]

    merged: list[str] = []
    seen: set[str] = set()
    for qid in due + wrong_ids:
        if qid not in seen:
            seen.add(qid)
            merged.append(qid)
    return merged


def get_flagged_question_ids(db: Session, user_id: str) -> list[str]:
    rows = (
        _attempts_for_user(db, user_id)
        .filter(Attempt.flagged == True)  # noqa: E712
        .order_by(Attempt.answered_at.desc())
        .all()
    )
    seen: set[str] = set()
    ordered: list[str] = []
    for attempt in rows:
        if attempt.question_id not in seen:
            seen.add(attempt.question_id)
            ordered.append(attempt.question_id)
    return ordered
