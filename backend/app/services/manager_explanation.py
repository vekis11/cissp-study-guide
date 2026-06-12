"""Structured manager-level feedback for every answered question."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Question

_CHOICE_FIELDS = {"A": "choice_a", "B": "choice_b", "C": "choice_c", "D": "choice_d"}

_ACTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("LEAST", re.compile(r"\bLEAST\b", re.I)),
    ("FIRST", re.compile(r"\bFIRST\b|\bBEFORE\b", re.I)),
    ("NEXT", re.compile(r"\bNEXT\b", re.I)),
    ("BEST", re.compile(r"\bBEST\b|\bMOST APPROPRIATE\b|\bMOST SIGNIFICANT\b", re.I)),
    ("PRIMARY", re.compile(r"\bPRIMARY\b|\bPRIORITY\b|\bGREATEST\b", re.I)),
]

_ACTION_TIPS: dict[str, list[str]] = {
    "FIRST": [
        "FIRST means one step — pick assessment, plan activation, or governance before technical fixes.",
        "Eliminate answers that jump to tools, termination, or blanket mandates before understanding the problem.",
        "Ask: what must leadership know or approve before anyone changes production?",
    ],
    "BEST": [
        "BEST favors sustainable governance: policy alignment, risk reduction, and business continuity together.",
        "Reject the fastest technical shortcut if it ignores legal, contractual, or organizational accountability.",
        "The best answer usually scales across the enterprise, not only the loudest incident.",
    ],
    "LEAST": [
        "LEAST = the worst managerial choice — often unethical, out-of-sequence, or reckless.",
        "Strong distractors may look responsible; the LEAST option usually violates due care or proper sequence.",
        "If three answers reflect good practice, the LEAST is the one that breaks governance or law.",
    ],
    "NEXT": [
        "NEXT assumes an earlier step already happened — do not repeat discovery or triage.",
        "Read the vignette for clues about what was already completed (assessment, approval, containment).",
        "Choose the logical follow-on action, not the first step in the playbook.",
    ],
    "PRIMARY": [
        "PRIMARY / GREATEST / PRIORITY questions target the highest organizational concern.",
        "Rank people, law, governance, and reputation above convenience or single-tool fixes.",
        "Address root cause and accountability, not only the symptom visible to users.",
    ],
}

_DOMAIN_TIPS: dict[int, list[str]] = {
    1: [
        "Domain 1: tie decisions to risk appetite, policy hierarchy, and business objectives.",
        "Prefer documented governance (policy → standard → procedure) over ad hoc executive requests.",
    ],
    2: [
        "Domain 2: classify data first, then match handling, retention, and destruction to sensitivity.",
        "Managers own classification and custody — technicians implement controls you select.",
    ],
    3: [
        "Domain 3: defense in depth and secure design beat single-point technical silver bullets.",
        "Cryptography and architecture answers must match the stated business and compliance need.",
    ],
    4: [
        "Domain 4: secure communications and network segmentation support business flows — design for both.",
        "Remote access and wireless scenarios reward zero-trust and strong authentication patterns.",
    ],
    5: [
        "Domain 5: identity is the perimeter — federation, least privilege, and lifecycle beat shared accounts.",
        "PAM and IAM answers should show sustainable process with oversight, not one-off credential sharing.",
    ],
    6: [
        "Domain 6: testing and assessment reduce risk when tied to change and remediation governance.",
        "Managers commission and prioritize assessment — they do not personally run every scan.",
    ],
    7: [
        "Domain 7: incident response rewards documented plans, roles, and communication before tooling.",
        "Operations answers balance detect → contain → eradicate → recover with evidence preservation.",
    ],
    8: [
        "Domain 8: SDLC security embeds requirements, threat modeling, and testing in the delivery pipeline.",
        "DevSecOps choices should reduce defect cost early — shift left, not bolt on after release.",
    ],
}

_UNIVERSAL_TIPS = [
    "Think like a CISO: you own risk decisions, budgets, and cross-functional coordination — not packet captures.",
    "When two answers seem technical, pick the one that improves governance, auditability, or due care.",
    "Read the entire vignette: contract SLAs, regulatory pressure, and deadlines change the BEST answer.",
]

_DISTRACTOR_HINTS: dict[str, str] = {
    "FIRST": "Common traps: deploying tools, firing vendors, or mandating certifications before root-cause analysis.",
    "BEST": "Common traps: one-time fixes, siloed compliance programs, or controls that ignore business continuity.",
    "LEAST": "Common traps: picking an answer that sounds decisive but skips policy, ethics, or proper sequence.",
    "NEXT": "Common traps: repeating initial assessment or escalation steps already described in the scenario.",
    "PRIMARY": "Common traps: focusing on a single CVE or tool when governance or legal exposure is greater.",
}


def _choice_text(question: Question, letter: str) -> str:
    field = _CHOICE_FIELDS.get(letter.upper(), "choice_a")
    return getattr(question, field, "")


def detect_action_word(stem: str) -> str | None:
    for name, pattern in _ACTION_PATTERNS:
        if pattern.search(stem):
            return name
    return None


def _strip_legacy_tips(explanation: str) -> str:
    """Remove generator-appended tips so the brief stays focused on scenario reasoning."""
    markers = (
        " CISSP 'FIRST' questions",
        " 'LEAST appropriate'",
        " 'BEST' favors",
        " 'NEXT' assumes",
        " Focus on the highest-level",
        " Think like a CISO:",
        " On LEAST questions, eliminate",
    )
    text = explanation.strip()
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    if text.startswith("LEAST appropriate:"):
        text = re.sub(r"^LEAST appropriate:\s*'[^']+'\s*—\s*[^.]+\.\s*", "", text).strip()
    return text


def build_manager_brief(question: Question) -> str:
    correct = question.correct_choice.upper()
    correct_text = _choice_text(question, correct)
    core = _strip_legacy_tips(question.explanation)
    action = detect_action_word(question.stem)

    topic_line = ""
    if question.source_topic:
        topic_line = f"This scenario focuses on {question.source_topic}. "

    leadership = (
        f"As the accountable security leader, option {correct} is correct: \"{correct_text}\". "
    )
    reasoning = f"{core} " if core else ""

    distractor = ""
    if action and action in _DISTRACTOR_HINTS:
        distractor = _DISTRACTOR_HINTS[action]

    domain_ctx = f"This falls under {question.domain_name} — frame your reasoning at the program and risk level, not as a hands-on technician."

    parts = [topic_line + leadership + reasoning]
    if distractor:
        parts.append(distractor)
    parts.append(domain_ctx)
    return " ".join(p.strip() for p in parts if p.strip())


def build_approach_tips(question: Question) -> list[str]:
    action = detect_action_word(question.stem)
    tips: list[str] = []

    if action and action in _ACTION_TIPS:
        tips.extend(_ACTION_TIPS[action])

    tips.extend(_DOMAIN_TIPS.get(question.domain, []))
    tips.extend(_UNIVERSAL_TIPS)

    if question.tags and "scenario" in question.tags:
        tips.append("Long vignettes hide the decision point in the last sentence — read for action words (FIRST, BEST, LEAST, NEXT).")

    seen: set[str] = set()
    unique: list[str] = []
    for tip in tips:
        if tip not in seen:
            seen.add(tip)
            unique.append(tip)
    return unique[:7]


def build_manager_feedback(question: Question) -> dict[str, str | list[str]]:
    brief = build_manager_brief(question)
    approach_tips = build_approach_tips(question)
    explanation = brief
    if approach_tips:
        explanation += "\n\nHow to approach similar questions:\n" + "\n".join(f"• {t}" for t in approach_tips)
    return {
        "manager_brief": brief,
        "approach_tips": approach_tips,
        "explanation": explanation,
    }
