"""Study guide catalog and topic coverage."""

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.database import SessionLocal
from app.seed import seed_database
from app.services.study_guide import (
    SCENARIOS_PER_TOPIC_IN_GUIDE,
    build_quiz_groups,
    build_study_guide_payload,
    select_guide_drill_questions,
)


def _catalog_topic_ids() -> set[str]:
    return {
        section["topic_id"]
        for domain in CHEAT_SHEET["domains"]
        for section in domain["sections"]
    }


def test_catalog_has_seventy_topics():
    assert len(_catalog_topic_ids()) == 70


def test_every_catalog_topic_has_scenario_mapping():
    catalog_ids = _catalog_topic_ids()
    assert catalog_ids == set(TOPIC_SCENARIO_MAP.keys())


def test_quiz_groups_cover_all_topics_once():
    seed_database(force=True)
    db = SessionLocal()
    try:
        groups = build_quiz_groups(db)
        tier_topic_ids: set[str] = set()
        for domain in groups["by_domain"]:
            for tier in domain["tiers"]:
                assert tier["question_count"] <= tier["topic_count"] * SCENARIOS_PER_TOPIC_IN_GUIDE
                assert tier["question_count"] >= tier["topic_count"]
                assert len(tier["topic_ids"]) == tier["topic_count"]
                for tid in tier["topic_ids"]:
                    assert tid not in tier_topic_ids
                    tier_topic_ids.add(tid)
        assert tier_topic_ids == _catalog_topic_ids()
        assert groups["exam_path"][0]["importance"] == "must"
        assert groups["exam_path"][0]["question_count"] >= 36
    finally:
        db.close()


def test_guide_drill_returns_scenario_questions_only():
    seed_database(force=True)
    db = SessionLocal()
    try:
        d1_must = select_guide_drill_questions(db, "must", 1)
        assert len(d1_must) == 6 * SCENARIOS_PER_TOPIC_IN_GUIDE
        assert all("scenario" in (q.tags or "") for q in d1_must)
        assert all("manager" in (q.tags or "") for q in d1_must)
        assert all("knowledge-check" not in (q.tags or "") for q in d1_must)
        all_must = select_guide_drill_questions(db, "must", None)
        assert 36 <= len(all_must) <= 36 * SCENARIOS_PER_TOPIC_IN_GUIDE
    finally:
        db.close()


def test_all_cheat_sheet_topics_are_tested_after_seed():
    seed_database(force=True)
    db = SessionLocal()
    try:
        payload = build_study_guide_payload(db)
        assert payload["summary"]["total_topics"] == 70
        assert payload["summary"]["fully_tested"] == 70
        assert payload["summary"]["coverage_percent"] == 100.0
    finally:
        db.close()
