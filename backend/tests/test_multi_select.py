"""Multi-select answer grading and bank generation."""

from app.data.diverse.bank_builder import build_diverse_bank
from app.services.answer_key import (
    grade_answer,
    is_multi_select,
    normalize_submission,
    question_type_for,
    validate_submission,
)


def test_grade_single_and_multi():
    assert grade_answer("B", "B") is True
    assert grade_answer("A", "B") is False
    assert grade_answer("AC", "CA") is True
    assert grade_answer("AC", "AB") is False
    assert grade_answer("ABC", "AC") is False


def test_question_type_detection():
    assert question_type_for("B") == "single"
    assert question_type_for("AC") == "multi"
    assert is_multi_select("BD") is True


def test_validate_submission_rules():
    assert validate_submission("B", "B") == "B"
    assert validate_submission("CA", "AC") == "AC"
    try:
        validate_submission("A", "AC")
        assert False, "should require two picks"
    except ValueError:
        pass


def test_bank_includes_multi_select_questions():
    bank = build_diverse_bank()
    multi = [q for q in bank if "multi-select" in q.get("tags", "")]
    assert len(multi) >= 80
    assert all(len(q["correct_choice"]) >= 2 for q in multi)
    assert len(bank) >= 800
