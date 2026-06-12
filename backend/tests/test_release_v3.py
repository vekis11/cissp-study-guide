"""Release v3.0 — bank, daily selection, user scoping."""

from types import SimpleNamespace

from app.data.diverse.bank_builder import build_diverse_bank
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
        choice_a="Deploy firewall",
        choice_b="Conduct risk assessment",
        choice_c="Terminate vendor",
        choice_d="Require ISO cert",
        explanation="Assessment before action.",
        source_topic="Vendor risk",
        domain=1,
        domain_name="Security and Risk Management",
        tags="scenario",
    )
    fb = build_manager_feedback(q)
    assert fb["manager_brief"]
    assert len(fb["approach_tips"]) >= 3


def test_cat_2024_constants():
    from app.services.cat_engine import CAT_MAX_QUESTIONS, CAT_MIN_QUESTIONS, CAT_TIME_SECONDS

    assert CAT_MIN_QUESTIONS == 125
    assert CAT_MAX_QUESTIONS == 150
    assert CAT_TIME_SECONDS == 3 * 60 * 60
