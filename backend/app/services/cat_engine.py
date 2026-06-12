import random
from collections import defaultdict

from sqlalchemy.orm import Session

from app.data.domains import DOMAIN_WEIGHTS, PASS_SCALED
from app.models import Attempt, Question

DIFFICULTY_ORDER = ["easy", "medium", "hard"]
CAT_MIN_QUESTIONS = 125
CAT_MAX_QUESTIONS = 175
CAT_TIME_SECONDS = 4 * 60 * 60  # ISC2 CAT max time since June 2022
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


def select_questions(
    db: Session,
    count: int,
    domain: int | None = None,
    exclude_ids: set[str] | None = None,
    difficulty: str | None = None,
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
) -> Question | None:
    next_diff = next_cat_difficulty(last_difficulty, is_correct)
    batch = select_questions(
        db,
        1,
        exclude_ids=exclude_ids,
        difficulty=next_diff,
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


def get_missed_question_ids(db: Session) -> list[str]:
    attempts = (
        db.query(Attempt)
        .filter(Attempt.is_correct == False)  # noqa: E712
        .order_by(Attempt.answered_at.desc())
        .all()
    )
    seen: set[str] = set()
    ordered: list[str] = []
    for a in attempts:
        if a.question_id not in seen:
            seen.add(a.question_id)
            ordered.append(a.question_id)
    return ordered
