"""Simplified IRT-style ability tracking for CAT sessions."""

from __future__ import annotations

import math

THETA_START = 0.0
PASS_THETA = 0.35  # calibrated proxy for ~700 scaled pass


def difficulty_weight(level: int) -> float:
    return max(0.5, min(2.0, level / 3.0))


def update_theta(theta: float, correct: bool, difficulty_level: int = 3) -> float:
    delta = 0.1 * difficulty_weight(difficulty_level)
    return round(theta + (delta if correct else -delta), 4)


def pass_likelihood(theta: float) -> float:
    """Estimated pass probability from ability proxy (0–100%)."""
    try:
        pct = 100.0 / (1.0 + math.exp(-(theta - PASS_THETA) * 6))
    except OverflowError:
        pct = 100.0 if theta > PASS_THETA else 0.0
    return round(max(0.0, min(100.0, pct)), 1)


def should_stop_theta(question_count: int, theta: float, min_questions: int = 125) -> bool:
    """Stop when enough items and ability estimate is confident."""
    if question_count < min_questions:
        return False
    likelihood = pass_likelihood(theta)
    return likelihood >= 88.0 or likelihood <= 45.0


def target_difficulty_level(theta: float) -> int:
    """Pick item difficulty closest to estimated ability."""
    # theta roughly -0.5..0.8 maps to levels 2-5
    level = round(3 + theta * 2)
    return max(1, min(5, level))
