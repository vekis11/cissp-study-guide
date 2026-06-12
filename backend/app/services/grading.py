"""CISSP-style scaled scoring (study simulation — not official Pearson VUE IRT)."""

from app.data.domains import PASS_SCALED
from app.models import Attempt, Question

DIFFICULTY_POINTS = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
BASE_SCALED = 200  # floor for attempted sessions
SCALED_RANGE = 800  # 200 + 800 = 1000 max


def compute_percent(correct: int, answered: int) -> float:
    if answered == 0:
        return 0.0
    return round((correct / answered) * 100, 1)


def compute_cissp_scaled(attempts: list[Attempt]) -> tuple[float, float, int, int]:
    """
    Returns (scaled_score 0-1000, percent, correct, answered).
    Harder items contribute more — mimics CAT weighting at study altitude.
    """
    weighted_correct = 0.0
    weighted_total = 0.0
    correct = 0
    answered = 0

    for attempt in attempts:
        if not attempt.selected_choice:
            continue
        answered += 1
        q = attempt.question
        weight = DIFFICULTY_POINTS.get(q.difficulty if q else "medium", 1.5)
        weighted_total += weight
        is_correct = attempt.is_correct
        if is_correct is None and q:
            is_correct = attempt.selected_choice == q.correct_choice
        if is_correct:
            correct += 1
            weighted_correct += weight

    percent = compute_percent(correct, answered)
    if answered == 0:
        return 0.0, 0.0, 0, 0

    ratio = weighted_correct / weighted_total if weighted_total else 0
    scaled = round(BASE_SCALED + ratio * SCALED_RANGE, 0)
    scaled = min(max(scaled, 0), 1000)
    return scaled, percent, correct, answered


def passed_cissp(scaled: float) -> bool:
    return scaled >= PASS_SCALED


def grade_label(scaled: float) -> str:
    if scaled >= PASS_SCALED + 100:
        return "Strong Pass"
    if scaled >= PASS_SCALED:
        return "Pass"
    if scaled >= PASS_SCALED - 80:
        return "Near Pass"
    return "Needs Improvement"
