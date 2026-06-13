"""Study guide catalog and cheat-sheet topic coverage."""
from __future__ import annotations

import random
from collections import defaultdict

from sqlalchemy.orm import Session

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.models import Attempt, Question, SessionRecord

IMPORTANCE_ORDER = ("must", "high", "good")
IMPORTANCE_LABELS = {
    "must": "Must Know",
    "high": "High Value",
    "good": "Good to Reinforce",
}
IMPORTANCE_STUDY_HINTS = {
    "must": "Master these first — core exam concepts you cannot skip.",
    "high": "Study after must-know items — frequently tested supporting ideas.",
    "good": "Review when time allows — depth for tougher curve-ball questions.",
}
# Study-guide drills: knowledge checks first, fewer scenarios per topic
KNOWLEDGE_PER_TOPIC_IN_GUIDE = 1
SCENARIOS_PER_TOPIC_IN_GUIDE = 1


def _catalog_sections() -> list[dict]:
    sections: list[dict] = []
    for block in CHEAT_SHEET["domains"]:
        for section in block["sections"]:
            sections.append(
                {
                    **section,
                    "domain": block["domain"],
                    "domain_name": block["name"],
                }
            )
    return sections


def _scenario_ids_for_topic(db: Session, topic_id: str) -> set[str]:
    """Scenario bank questions mapped to a cheat-sheet topic (tag match only)."""
    mapping = TOPIC_SCENARIO_MAP.get(topic_id, {})
    ids: set[str] = set()
    for tag in mapping.get("tags", []):
        rows = (
            db.query(Question.id)
            .filter(Question.tags.contains("scenario"), Question.tags.contains(tag))
            .all()
        )
        ids.update(r[0] for r in rows)
    return ids


def _knowledge_ids_for_topic(db: Session, topic_id: str) -> set[str]:
    rows = (
        db.query(Question.id)
        .filter(
            Question.tags.contains("knowledge-check"),
            Question.tags.contains(f"topic:{topic_id}"),
        )
        .all()
    )
    return {r[0] for r in rows}


def count_scenario_questions_for_topic(db: Session, topic_id: str) -> int:
    return len(_scenario_ids_for_topic(db, topic_id))


def count_knowledge_questions_for_topic(db: Session, topic_id: str) -> int:
    return len(_knowledge_ids_for_topic(db, topic_id))


def _knowledge_questions_for_topic(
    db: Session,
    topic_id: str,
    *,
    limit: int = KNOWLEDGE_PER_TOPIC_IN_GUIDE,
) -> list[Question]:
    pool = (
        db.query(Question)
        .filter(
            Question.tags.contains("knowledge-check"),
            Question.tags.contains(f"topic:{topic_id}"),
        )
        .all()
    )
    random.shuffle(pool)
    return pool[:limit]


def _scenario_questions_for_topic(
    db: Session,
    topic_id: str,
    *,
    limit: int = SCENARIOS_PER_TOPIC_IN_GUIDE,
) -> list[Question]:
    """Sample manager-style scenario questions for one cheat-sheet topic."""
    mapping = TOPIC_SCENARIO_MAP.get(topic_id, {})
    pool: list[Question] = []
    seen: set[str] = set()

    for tag in mapping.get("tags", []):
        for q in (
            db.query(Question)
            .filter(Question.tags.contains("scenario"), Question.tags.contains(tag))
            .all()
        ):
            if q.id not in seen:
                pool.append(q)
                seen.add(q.id)

    random.shuffle(pool)
    return pool[:limit]


def _guide_questions_for_topic(
    db: Session,
    topic_id: str,
) -> list[Question]:
    """Knowledge-check heavy mix for study-guide drills."""
    pool: list[Question] = []
    seen: set[str] = set()
    for q in _knowledge_questions_for_topic(
        db, topic_id, limit=KNOWLEDGE_PER_TOPIC_IN_GUIDE
    ):
        if q.id not in seen:
            pool.append(q)
            seen.add(q.id)
    for q in _scenario_questions_for_topic(
        db, topic_id, limit=SCENARIOS_PER_TOPIC_IN_GUIDE
    ):
        if q.id not in seen:
            pool.append(q)
            seen.add(q.id)
    return pool


def _tier_session_question_count(db: Session, topic_ids: list[str]) -> int:
    total = 0
    for topic_id in topic_ids:
        total += len(_guide_questions_for_topic(db, topic_id))
    return total


def _tier_pool_ids(db: Session, topic_ids: list[str]) -> set[str]:
    ids: set[str] = set()
    for topic_id in topic_ids:
        for q in _guide_questions_for_topic(db, topic_id):
            ids.add(q.id)
    return ids


def _answered_question_ids(db: Session, user_id: str, question_ids: set[str]) -> set[str]:
    if not question_ids:
        return set()
    rows = (
        db.query(Attempt.question_id)
        .join(SessionRecord, SessionRecord.id == Attempt.session_id)
        .filter(
            SessionRecord.user_id == user_id,
            Attempt.selected_choice.isnot(None),
            Attempt.question_id.in_(question_ids),
        )
        .distinct()
        .all()
    )
    return {r[0] for r in rows}


def tier_progress_counts(
    db: Session,
    user_id: str,
    topic_ids: list[str],
) -> dict[str, int]:
    pool_ids = _tier_pool_ids(db, topic_ids)
    total = len(pool_ids)
    answered = len(_answered_question_ids(db, user_id, pool_ids))
    return {
        "question_count": total,
        "answered_count": answered,
        "remaining_count": max(0, total - answered),
    }


def build_topic_coverage(db: Session) -> list[dict]:
    coverage: list[dict] = []
    for section in _catalog_sections():
        topic_id = section["topic_id"]
        scenario_count = count_scenario_questions_for_topic(db, topic_id)
        knowledge_count = count_knowledge_questions_for_topic(db, topic_id)
        coverage.append(
            {
                "topic_id": topic_id,
                "domain": section["domain"],
                "domain_name": section["domain_name"],
                "title": section["title"],
                "importance": section.get("importance", "high"),
                "knowledge_questions": knowledge_count,
                "scenario_questions": scenario_count,
                "fully_tested": knowledge_count > 0 or scenario_count > 0,
            }
        )
    return coverage


def build_quiz_groups(db: Session, user_id: str | None = None) -> dict:
    """Grouped study-guide quizzes per domain × importance tier."""
    by_domain: list[dict] = []
    global_tiers: dict[str, dict] = {
        imp: {
            "importance": imp,
            "label": IMPORTANCE_LABELS[imp],
            "topic_count": 0,
            "question_count": 0,
            "answered_count": 0,
            "remaining_count": 0,
            "priority": IMPORTANCE_ORDER.index(imp) + 1,
        }
        for imp in IMPORTANCE_ORDER
    }

    weight_by_domain = {w["domain"]: w["weight_percent"] for w in CHEAT_SHEET["domain_weights"]}

    for block in CHEAT_SHEET["domains"]:
        domain = block["domain"]
        by_importance: dict[str, list[dict]] = defaultdict(list)
        for section in block["sections"]:
            by_importance[section["importance"]].append(section)

        tiers: list[dict] = []
        for imp in IMPORTANCE_ORDER:
            sections = by_importance.get(imp, [])
            if not sections:
                continue
            topic_ids = [s["topic_id"] for s in sections]
            progress = (
                tier_progress_counts(db, user_id, topic_ids)
                if user_id
                else {
                    "question_count": _tier_session_question_count(db, topic_ids),
                    "answered_count": 0,
                    "remaining_count": _tier_session_question_count(db, topic_ids),
                }
            )
            tier = {
                "importance": imp,
                "label": IMPORTANCE_LABELS[imp],
                "study_hint": IMPORTANCE_STUDY_HINTS[imp],
                "priority": IMPORTANCE_ORDER.index(imp) + 1,
                "topic_count": len(sections),
                "question_count": progress["question_count"],
                "answered_count": progress["answered_count"],
                "remaining_count": progress["remaining_count"],
                "knowledge_per_topic": KNOWLEDGE_PER_TOPIC_IN_GUIDE,
                "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
                "topic_ids": topic_ids,
                "topic_titles": [s["title"] for s in sections],
            }
            tiers.append(tier)
            global_tiers[imp]["topic_count"] += len(sections)
            global_tiers[imp]["question_count"] += progress["question_count"]
            global_tiers[imp]["answered_count"] += progress["answered_count"]
            global_tiers[imp]["remaining_count"] += progress["remaining_count"]

        by_domain.append(
            {
                "domain": domain,
                "domain_name": block["name"],
                "weight_percent": weight_by_domain.get(domain, 0),
                "tiers": tiers,
            }
        )

    exam_path = []
    for imp in IMPORTANCE_ORDER:
        if global_tiers[imp]["question_count"] <= 0:
            continue
        exam_path.append(
            {
                **global_tiers[imp],
                "study_hint": IMPORTANCE_STUDY_HINTS[imp],
                "knowledge_per_topic": KNOWLEDGE_PER_TOPIC_IN_GUIDE,
                "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
            }
        )

    return {"by_domain": by_domain, "exam_path": exam_path}


def build_study_guide_payload(db: Session, user_id: str | None = None) -> dict:
    coverage = build_topic_coverage(db)
    total = len(coverage)
    tested = sum(1 for c in coverage if c["fully_tested"])
    knowledge_bank = db.query(Question).filter(Question.tags.contains("knowledge-check")).count()
    scenario_bank = db.query(Question).filter(Question.tags.contains("scenario")).count()
    return {
        "catalog": CHEAT_SHEET,
        "coverage": coverage,
        "quiz_groups": build_quiz_groups(db, user_id),
        "summary": {
            "total_topics": total,
            "fully_tested": tested,
            "coverage_percent": round(100 * tested / total, 1) if total else 0,
            "knowledge_questions": knowledge_bank,
            "scenario_bank": scenario_bank,
            "knowledge_per_topic": KNOWLEDGE_PER_TOPIC_IN_GUIDE,
            "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
        },
    }


def select_topic_drill_questions(db: Session, topic_id: str, count: int = 10) -> list[Question]:
    """Knowledge-check heavy drill for a single cheat-sheet topic."""
    knowledge = _knowledge_questions_for_topic(db, topic_id, limit=max(1, count // 2 + 1))
    scenario_limit = max(1, count - len(knowledge))
    scenarios = _scenario_questions_for_topic(db, topic_id, limit=scenario_limit)
    pool: list[Question] = []
    seen: set[str] = set()
    for q in knowledge + scenarios:
        if q.id not in seen:
            pool.append(q)
            seen.add(q.id)
    random.shuffle(pool)
    return pool[:count]


def _topic_ids_for_tier(domain: int | None, importance: str) -> list[str]:
    ids: list[str] = []
    for section in _catalog_sections():
        if section["importance"] != importance:
            continue
        if domain is not None and section["domain"] != domain:
            continue
        ids.append(section["topic_id"])
    return ids


def select_guide_drill_questions(
    db: Session,
    importance: str,
    domain: int | None = None,
) -> list[Question]:
    """Knowledge-check weighted quiz for a domain × importance tier (or all domains)."""
    if importance not in IMPORTANCE_LABELS:
        return []

    topic_ids = _topic_ids_for_tier(domain, importance)
    if not topic_ids:
        return []

    pool: list[Question] = []
    seen: set[str] = set()

    for topic_id in topic_ids:
        for q in _guide_questions_for_topic(db, topic_id):
            if q.id not in seen:
                pool.append(q)
                seen.add(q.id)

    random.shuffle(pool)
    return pool
