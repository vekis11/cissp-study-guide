"""Study guide catalog and cheat-sheet topic coverage."""
from __future__ import annotations

import random
from collections import defaultdict

from sqlalchemy.orm import Session

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.models import Question

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
# Representative manager-style scenarios per cheat-sheet topic in a tier quiz
SCENARIOS_PER_TOPIC_IN_GUIDE = 2


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


def count_scenario_questions_for_topic(db: Session, topic_id: str) -> int:
    return len(_scenario_ids_for_topic(db, topic_id))


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


def _tier_session_question_count(db: Session, topic_ids: list[str]) -> int:
    total = 0
    for topic_id in topic_ids:
        available = count_scenario_questions_for_topic(db, topic_id)
        if available:
            total += min(SCENARIOS_PER_TOPIC_IN_GUIDE, available)
    return total


def build_topic_coverage(db: Session) -> list[dict]:
    coverage: list[dict] = []
    for section in _catalog_sections():
        topic_id = section["topic_id"]
        scenario_count = count_scenario_questions_for_topic(db, topic_id)
        coverage.append(
            {
                "topic_id": topic_id,
                "domain": section["domain"],
                "domain_name": section["domain_name"],
                "title": section["title"],
                "importance": section.get("importance", "high"),
                "knowledge_questions": 0,
                "scenario_questions": scenario_count,
                "fully_tested": scenario_count > 0,
            }
        )
    return coverage


def build_quiz_groups(db: Session) -> dict:
    """Grouped study-guide quizzes: scenario sessions per domain × importance tier."""
    by_domain: list[dict] = []
    global_tiers: dict[str, dict] = {
        imp: {
            "importance": imp,
            "label": IMPORTANCE_LABELS[imp],
            "topic_count": 0,
            "question_count": 0,
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
            session_count = _tier_session_question_count(db, topic_ids)
            tier = {
                "importance": imp,
                "label": IMPORTANCE_LABELS[imp],
                "study_hint": IMPORTANCE_STUDY_HINTS[imp],
                "priority": IMPORTANCE_ORDER.index(imp) + 1,
                "topic_count": len(sections),
                "question_count": session_count,
                "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
                "topic_ids": topic_ids,
                "topic_titles": [s["title"] for s in sections],
            }
            tiers.append(tier)
            global_tiers[imp]["topic_count"] += len(sections)
            global_tiers[imp]["question_count"] += session_count

        by_domain.append(
            {
                "domain": domain,
                "domain_name": block["name"],
                "weight_percent": weight_by_domain.get(domain, 0),
                "tiers": tiers,
            }
        )

    exam_path = [
        {
            **global_tiers[imp],
            "study_hint": IMPORTANCE_STUDY_HINTS[imp],
            "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
        }
        for imp in IMPORTANCE_ORDER
        if global_tiers[imp]["question_count"] > 0
    ]

    return {"by_domain": by_domain, "exam_path": exam_path}


def build_study_guide_payload(db: Session) -> dict:
    coverage = build_topic_coverage(db)
    total = len(coverage)
    tested = sum(1 for c in coverage if c["fully_tested"])
    scenario_bank = db.query(Question).filter(Question.tags.contains("scenario")).count()
    return {
        "catalog": CHEAT_SHEET,
        "coverage": coverage,
        "quiz_groups": build_quiz_groups(db),
        "summary": {
            "total_topics": total,
            "fully_tested": tested,
            "coverage_percent": round(100 * tested / total, 1) if total else 0,
            "knowledge_questions": 0,
            "scenario_bank": scenario_bank,
            "scenarios_per_topic": SCENARIOS_PER_TOPIC_IN_GUIDE,
        },
    }


def select_topic_drill_questions(db: Session, topic_id: str, count: int = 10) -> list[Question]:
    """Manager-style scenario questions for a single cheat-sheet topic."""
    pool = _scenario_questions_for_topic(db, topic_id, limit=count)
    return pool


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
    *,
    per_topic: int = SCENARIOS_PER_TOPIC_IN_GUIDE,
) -> list[Question]:
    """Manager-style scenario quiz for a domain × importance tier (or all domains)."""
    if importance not in IMPORTANCE_LABELS:
        return []

    topic_ids = _topic_ids_for_tier(domain, importance)
    if not topic_ids:
        return []

    pool: list[Question] = []
    seen: set[str] = set()

    for topic_id in topic_ids:
        for q in _scenario_questions_for_topic(db, topic_id, limit=per_topic):
            if q.id not in seen:
                pool.append(q)
                seen.add(q.id)

    random.shuffle(pool)
    return pool
