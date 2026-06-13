"""Generate select-all-that-apply (multi-answer) scenario questions."""
from __future__ import annotations

import hashlib
import random

from app.data.diverse.choice_balance import balance_choice_set

MULTI_STEM_SUFFIXES = (
    "Which of the following actions are appropriate? (Select TWO.)",
    "Which responses demonstrate due care? (Select TWO.)",
    "Which options should the security leader pursue? (Select TWO.)",
    "Which of the following are correct? (Select all that apply.)",
)

COMPANION_TEMPLATES = (
    "Document the decision, accountable owners, and success criteria before implementation proceeds.",
    "Engage executive leadership and legal/compliance stakeholders with a clear risk summary.",
    "Establish measurable governance checkpoints and ongoing assurance for the control environment.",
    "Align the response with organizational risk appetite and applicable regulatory obligations.",
    "Ensure cross-functional accountability rather than delegating risk acceptance to technical staff alone.",
)


def _companion_correct(spec: dict, seed: str) -> str:
    rng = random.Random(seed)
    base = COMPANION_TEMPLATES[rng.randint(0, len(COMPANION_TEMPLATES) - 1)]
    topic = spec.get("topic", "security governance")
    if topic.lower() not in base.lower():
        return f"{base} This supports sustained {topic.lower()} at the program level."
    return base


def format_multi_stem(narrative: str, industry: str, topic: str, slot: int) -> str:
    suffix = MULTI_STEM_SUFFIXES[slot % len(MULTI_STEM_SUFFIXES)]
    return (
        f"A {industry} organization is addressing {topic}. "
        f"{narrative.strip()} {suffix}"
    )


def build_multi_question(spec: dict, kernel_idx: int) -> dict | None:
    """One multi-select item per kernel — two correct managerial answers."""
    domain = spec["domain"]
    seed = f"multi-{kernel_idx}-{spec['correct'][:40]}"
    balanced_correct, balanced_wrong = balance_choice_set(
        spec["correct"], spec["wrong"], domain, seed
    )
    companion = _companion_correct(spec, seed)
    choices = [balanced_correct, companion] + balanced_wrong[:2]
    if len(choices) < 4:
        return None

    rng = random.Random(seed)
    rng.shuffle(choices)
    letters = ["A", "B", "C", "D"]
    primary_letter = letters[choices.index(balanced_correct)]
    companion_letter = letters[choices.index(companion)]
    correct_choice = "".join(sorted({primary_letter, companion_letter}))

    stem = format_multi_stem(
        spec["narrative"],
        spec["industry"],
        spec["topic"],
        kernel_idx,
    )
    qid_seed = f"{kernel_idx}-multi-{stem[:60]}"
    h = hashlib.sha256(qid_seed.encode()).hexdigest()[:12]

    return {
        "stem": stem,
        "choice_a": choices[0],
        "choice_b": choices[1],
        "choice_c": choices[2],
        "choice_d": choices[3],
        "correct_choice": correct_choice,
        "id_suffix": h,
    }
