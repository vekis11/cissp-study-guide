"""Study guide catalog and topic coverage."""

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.cheat_sheet.study_guide_bank import MIN_STUDY_GUIDE_QUESTIONS, build_study_guide_questions
from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.database import SessionLocal
from app.models import Attempt, Question, SessionRecord
from app.seed import seed_database
from app.services.study_guide import (
    SCENARIOS_PER_TOPIC_IN_GUIDE,
    build_quiz_groups,
    build_study_guide_payload,
    select_guide_drill_questions,
    tier_progress_counts,
    _topic_ids_for_tier,
)


def _catalog_topic_ids() -> set[str]:
    return {
        section["topic_id"]
        for domain in CHEAT_SHEET["domains"]
        for section in domain["sections"]
    }


def test_study_guide_bank_has_150_plus():
    qs = build_study_guide_questions()
    assert len(qs) >= MIN_STUDY_GUIDE_QUESTIONS
    assert sum(1 for q in qs if q["id"].startswith("sg-seed")) == 16
    assert all("study-guide" in q["tags"] for q in qs)


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


def test_guide_drill_uses_study_guide_format_only():
    seed_database(force=True)
    db = SessionLocal()
    try:
        d1_must = select_guide_drill_questions(db, "must", 1)
        topic_count = len([s for s in CHEAT_SHEET["domains"][0]["sections"] if s["importance"] == "must"])
        assert len(d1_must) >= topic_count
        assert all("study-guide" in (q.tags or "") for q in d1_must)
        assert all("scenario" not in (q.tags or "") or "study-guide" in (q.tags or "") for q in d1_must)
        assert SCENARIOS_PER_TOPIC_IN_GUIDE == 0
        all_must = select_guide_drill_questions(db, "must", None)
        assert len(all_must) >= 36
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
        assert payload["summary"]["study_guide_questions"] >= MIN_STUDY_GUIDE_QUESTIONS
    finally:
        db.close()


def test_tier_progress_tracks_answered_questions():
    seed_database(force=True)
    db = SessionLocal()
    try:
        from app.services.study_guide import _study_guide_questions_for_topic

        user_id = "progress-test-user"
        topic_ids = _topic_ids_for_tier(1, "must")
        questions: list[Question] = []
        for topic_id in topic_ids[:2]:
            questions.extend(_study_guide_questions_for_topic(db, topic_id))
        assert len(questions) >= 2

        session = SessionRecord(
            user_id=user_id,
            mode="practice",
            session_type="guide_drill",
            total_questions=2,
            domain_filter=1,
        )
        db.add(session)
        db.flush()
        for q in questions[:2]:
            db.add(
                Attempt(
                    session_id=session.id,
                    question_id=q.id,
                    selected_choice="A",
                    is_correct=True,
                )
            )
        db.commit()

        groups = build_quiz_groups(db, user_id)
        d1_must = next(
            t for d in groups["by_domain"] if d["domain"] == 1 for t in d["tiers"] if t["importance"] == "must"
        )
        assert d1_must["answered_count"] >= 2
        assert d1_must["remaining_count"] == d1_must["question_count"] - d1_must["answered_count"]
    finally:
        db.close()
