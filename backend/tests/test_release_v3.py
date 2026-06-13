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
    assert "Principle tested" not in main_titles
    assert "Why A isn't it" in main_titles
    assert "Why B is BEST" in main_titles
    assert "Why the others fall short" in main_titles
    assert "Domain" in ref_titles
    assert "Manager view" in ref_titles
    assert "Easy mistake" in ref_titles
    distractors = next(s for s in fb["explanation_sections"] if s["key"] == "distractors")
    assert "Where it fits:" in distractors["body"]
    assert "Easy to pick because:" in distractors["body"]
    assert "Why not here:" in distractors["body"]
    tested = next(s for s in fb["explanation_sections"] if s["key"] == "context")
    assert "Core principle:" in tested["body"]
    assert fb["trap"]
    assert len(fb["wrong_choice_notes"]) == 3
    assert "Why the other options" not in fb["explanation"]


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


def test_cat_2024_constants():
    from app.services.cat_engine import CAT_MAX_QUESTIONS, CAT_MIN_QUESTIONS, CAT_TIME_SECONDS

    assert CAT_MIN_QUESTIONS == 125
    assert CAT_MAX_QUESTIONS == 150
    assert CAT_TIME_SECONDS == 3 * 60 * 60
