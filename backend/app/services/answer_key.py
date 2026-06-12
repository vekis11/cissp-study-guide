"""Parse and grade single- and multi-select answers (e.g. B vs ACD)."""
from __future__ import annotations

_VALID = frozenset("ABCD")


def parse_choices(value: str | None) -> frozenset[str]:
    if not value:
        return frozenset()
    return frozenset(c for c in value.upper() if c in _VALID)


def format_choices(letters: frozenset[str] | set[str]) -> str:
    return "".join(sorted(letters))


def is_multi_select(correct_choice: str | None) -> bool:
    return len(parse_choices(correct_choice)) > 1


def question_type_for(correct_choice: str | None) -> str:
    return "multi" if is_multi_select(correct_choice) else "single"


def grade_answer(selected: str | None, correct: str | None) -> bool:
    """Exact match — all correct letters selected, no extras."""
    return parse_choices(selected) == parse_choices(correct)


def normalize_submission(selected: str) -> str:
    """Sorted unique letters for storage."""
    return format_choices(parse_choices(selected))


def validate_submission(selected: str, correct: str | None) -> str:
    parsed = parse_choices(selected)
    correct_set = parse_choices(correct)
    if not parsed:
        raise ValueError("Select at least one answer")
    if is_multi_select(correct):
        if len(parsed) != len(correct_set):
            raise ValueError(f"Select exactly {len(correct_set)} answers for this question")
    elif len(parsed) != 1:
        raise ValueError("Select exactly one answer for this question")
    return format_choices(parsed)
