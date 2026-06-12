"""Varied CISSP question stem formats — each rewrites the scenario without duplicating text."""

from __future__ import annotations

import random

ACTION_BY_SLOT = [
    "What should you do FIRST?",
    "Which course of action is BEST?",
    "Which option is MOST appropriate?",
    "Which response should take PRIORITY?",
    "What is the NEXT step?",
    "Which action is LEAST appropriate?",
    "What represents the GREATEST concern from a governance perspective?",
    "Which decision BEST demonstrates due care?",
]


def action_for_slot(slot: int) -> str:
    return ACTION_BY_SLOT[slot % len(ACTION_BY_SLOT)]


def _lc_first(sentence: str) -> str:
    s = sentence.strip()
    if not s:
        return s
    return s[0].lower() + s[1:] if len(s) > 1 else s.lower()


def format_stem(slot: int, narrative: str, industry: str, topic: str) -> str:
    """Apply one of eight exam-style stem archetypes."""
    action = action_for_slot(slot)
    n = narrative.strip()
    ind = industry.strip()
    top = topic.strip()

    formats = (
        _format_board,
        _format_audit,
        _format_regulator,
        _format_incident,
        _format_rfp,
        _format_direct,
        _format_stakeholder,
        _format_metrics,
    )
    builder = formats[slot % len(formats)]
    return builder(n, ind, top, action)


def _format_board(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"During a risk committee session, a {industry} organization must decide how to handle {topic}. "
        f"{narrative} {action}"
    )


def _format_audit(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"Internal audit flagged a {topic} gap at a {industry} company. "
        f"{narrative} {action}"
    )


def _format_regulator(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"Regulators are reviewing {topic} controls at a {industry} firm. "
        f"{narrative} {action}"
    )


def _format_incident(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"After a security event involving {topic}, leadership at a {industry} enterprise needs direction. "
        f"{narrative} {action}"
    )


def _format_rfp(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"A procurement decision will affect {topic} for a {industry} organization. "
        f"{narrative} {action}"
    )


def _format_direct(narrative: str, industry: str, topic: str, action: str) -> str:
    return f"{narrative} {action}"


def _format_stakeholder(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"Stakeholders conflict over {topic} at a {industry} company. "
        f"{narrative} {action}"
    )


def _format_metrics(narrative: str, industry: str, topic: str, action: str) -> str:
    return (
        f"Risk metrics for {topic} are trending poorly at a {industry} organization. "
        f"{narrative} {action}"
    )


def shuffle_choices(
    correct: str,
    wrong: list[str],
    seed: str,
) -> tuple[str, str, str, str, str]:
    """Return choice_a..d and correct letter."""
    choices = [correct] + wrong[:3]
    rng = random.Random(seed)
    rng.shuffle(choices)
    letters = ["A", "B", "C", "D"]
    idx = choices.index(correct)
    return choices[0], choices[1], choices[2], choices[3], letters[idx]
