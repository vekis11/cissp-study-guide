"""Release v3.0 — bank, daily selection, user scoping."""

from types import SimpleNamespace

from app.data.diverse.bank_builder import build_diverse_bank
from app.data.diverse.choice_balance import is_length_giveaway
from app.services.manager_explanation import build_manager_feedback


def test_bank_size_and_uniqueness():
    qs = build_diverse_bank()
    assert len(qs) >= 800
    stems = {q["stem"] for q in qs}
    assert len(stems) == len(qs)


def test_manager_feedback_shape():
    q = SimpleNamespace(
        stem="What should you do FIRST?",
        correct_choice="B",
        choice_a="Conduct a formal risk assessment and document acceptance criteria before deploying new controls.",
        choice_b="Establish a governance charter with defined risk ownership before integrating acquired systems.",
        choice_c="Require the vendor to provide ISO 27001 certification before contract signature.",
        choice_d="Deploy network segmentation immediately while policy updates are drafted.",
        explanation="Governance and ownership must precede technical integration.",
        source_topic="Vendor risk",
        domain=1,
        domain_name="Security & Risk Management",
        tags="scenario",
    )
    fb = build_manager_feedback(q, selected_choice="A", is_correct=False)
    assert fb["explanation_sections"]
    assert fb["reference_sections"]
    main_titles = [s["title"] for s in fb["explanation_sections"]]
    ref_titles = [s["title"] for s in fb["reference_sections"]]
    assert "What's being tested" in main_titles
    assert "Manager hint" not in main_titles
    assert "Principle tested" not in main_titles
    assert "Why A isn't it" not in main_titles
    assert "Why the correct answer is BEST" in main_titles
    assert "Why each distractor is inferior" not in main_titles
    assert "Why each distractor is inferior" in ref_titles
    assert "Domain(s)" in ref_titles
    assert "Key CISSP principle tested" in ref_titles
    assert "Cognitive level" in ref_titles
    assert "Easy mistake" in ref_titles
    correct = next(s for s in fb["explanation_sections"] if s["key"] == "correct_answer")
    assert not correct["body"].startswith("Correct answer:")
    assert "Correct answer: B" in correct["body"]
    assert "first managerial step" in correct["body"].lower() or "vendor" in correct["body"].lower()
    assert fb["trap"]
    assert len(fb["wrong_choice_notes"]) == 3
    assert "Why the other options" not in fb["explanation"]

    q2 = SimpleNamespace(
        stem=(
            "An organization confirms active ransomware on several workstations. "
            "Which step should generally come FIRST in the response?"
        ),
        correct_choice="A",
        choice_a="Contain the spread to limit further impact",
        choice_b="Publish a full public breach notice",
        choice_c="Rebuild every system in the environment",
        choice_d="Contact law enforcement before any internal triage",
        explanation="Containment limits damage while scope is understood.",
        source_topic="Incident response",
        domain=7,
        domain_name="Security Operations",
        tags="scenario",
    )
    fb2 = build_manager_feedback(q2, selected_choice="B", is_correct=False)
    body1 = next(s for s in fb["explanation_sections"] if s["key"] == "correct_answer")["body"]
    body2 = next(s for s in fb2["explanation_sections"] if s["key"] == "correct_answer")["body"]
    assert body1 != body2
    assert "organization confirms active ransomware" not in body2.lower()
    assert "contain" in body2.lower()


def test_choice_lengths_not_obvious():
    qs = build_diverse_bank()
    single = [q for q in qs if len(q["correct_choice"]) == 1]
    longest_is_correct = 0
    for q in single:
        letter_map = {
            "A": q["choice_a"],
            "B": q["choice_b"],
            "C": q["choice_c"],
            "D": q["choice_d"],
        }
        correct = letter_map[q["correct_choice"]]
        wrong = [v for k, v in letter_map.items() if k != q["correct_choice"]]
        if len(correct) >= max(len(w) for w in wrong):
            longest_is_correct += 1
        assert not is_length_giveaway(correct, wrong)
    rate = longest_is_correct / len(single)
    assert rate < 0.45, f"Correct answer longest in {rate:.0%} of questions"


def test_cloud_ai_and_direct_exam_scenarios():
    from app.services.cissp_exam_rules import stem_has_cissp_action

    qs = build_diverse_bank()
    cloud_ai = [q for q in qs if "cloud-ai-exam" in q.get("tags", "")]
    direct = [q for q in qs if "direct-exam" in q.get("tags", "") and "study-guide" not in q.get("tags", "")]
    assert len(cloud_ai) >= 10
    assert len(direct) >= 100
    for q in cloud_ai + direct[:20]:
        assert stem_has_cissp_action(q["stem"])
        assert len(q["stem"]) >= 80


def test_all_sessions_start_adaptive():
    from app.database import SessionLocal
    from app.main import _start_adaptive_session
    from app.models import Attempt, SessionRecord
    from app.seed import seed_database
    from app.services.irt_cat import THETA_START

    seed_database(force=True)
    db = SessionLocal()
    try:
        user_id = "adaptive-test-user"
        session = _start_adaptive_session(
            db,
            user_id=user_id,
            session_type="daily",
            mode="newbie",
            count=5,
        )
        assert session.theta_proxy == THETA_START
        assert session.total_questions == 5
        attempts = db.query(Attempt).filter(Attempt.session_id == session.id).all()
        assert len(attempts) == 1
        row = db.query(SessionRecord).filter(SessionRecord.id == session.id).first()
        assert row is not None
    finally:
        db.close()


def test_cat_2024_constants():
    from app.services.cat_engine import CAT_MAX_QUESTIONS, CAT_MIN_QUESTIONS, CAT_TIME_SECONDS

    assert CAT_MIN_QUESTIONS == 125
    assert CAT_MAX_QUESTIONS == 150
    assert CAT_TIME_SECONDS == 3 * 60 * 60
