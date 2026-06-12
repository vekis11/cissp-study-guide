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

_ACTION_TIPS: dict[str, str] = {
    "FIRST": "FIRST = assess or govern before any technical fix.",
    "BEST": "BEST = sustainable governance and risk reduction, not the fastest shortcut.",
    "LEAST": "LEAST = pick the worst managerial choice (ethics, sequence, or due care).",
    "NEXT": "NEXT = follow-on step only; don't repeat triage or discovery.",
    "PRIMARY": "PRIMARY = people, law, and governance over tools or symptoms.",
}

_DOMAIN_TIPS: dict[int, str] = {
    1: "Think policy and risk appetite — not packet-level fixes.",
    2: "Match data handling to classification and legal obligations.",
    3: "Choose layered, sustainable architecture over silver bullets.",
    4: "Balance security with how the business actually communicates.",
    5: "Identity lifecycle and least privilege beat shared accounts.",
    6: "Commission assessment; prioritize remediation with governance.",
    7: "Follow the IR plan: roles, comms, then containment and recovery.",
    8: "Shift-left security in the SDLC beats post-release patches.",
}

_WRONG_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bterminat|\bfire\b|\bdismiss|\brevok.*employ", re.I), "Reactive personnel action without investigation, policy, or HR/legal process is poor management."),
    (re.compile(r"\bdeploy\b|\binstall\b|\bpatch\b|\breimage\b|\bimplement.*immediately", re.I), "Jumps to a technical fix before assessment, governance, or business alignment."),
    (re.compile(r"\bblock all\b|\bdisable all\b|\bshut down\b|\bban\b|\bprohibit all", re.I), "Too disruptive — managers balance security with business continuity and proportional response."),
    (re.compile(r"\bignore\b|\bdefer\b|\bwait\b|\bwithout\b.*\breview", re.I), "Defers due care, legal obligation, or accountability when leadership must act."),
    (re.compile(r"\btrust\b|\bverbal\b|\bassurance\b|\bwithout.*audit", re.I), "Relies on trust or assurances instead of documented due diligence."),
    (re.compile(r"\bemail\b|\bshare via\b|\bspreadsheet\b|\busb\b", re.I), "Weak or informal handling — not a sustainable governance or data-protection control."),
    (re.compile(r"\bdelete\b|\bdestroy\b|\bwipe\b|\breimage\b", re.I), "Destructive action may destroy evidence or violate retention/legal hold requirements."),
    (re.compile(r"\bcertif|\biso\b|\bcompliance badge", re.I), "Checkbox compliance without context rarely answers governance or risk questions by itself."),
    (re.compile(r"\binsurance\b|\btransfer\b.*only", re.I), "Risk transfer alone does not eliminate accountability or required compensating controls."),
    (re.compile(r"\bshared account|\bsingle account|\broot credential", re.I), "Shared or elevated credentials violate accountability and least-privilege principles."),
    (re.compile(r"\bhide\b|\bconceal\b|\bdelay.*notif|\bwithhold", re.I), "Concealment or delayed disclosure conflicts with ethics, law, and incident obligations."),
    (re.compile(r"\bpenetration test only\b|\bscan only\b|\baudit only\b", re.I), "A single assessment activity does not replace program-level governance or remediation."),
    (re.compile(r"\baccept risk\b.*without|\bsilently\b", re.I), "Residual risk requires documented acceptance by the right authority — not informal tolerance."),
]

_LEAST_WRONG_NOTE = (
    "On LEAST questions, this is actually a reasonable managerial action — "
    "the LEAST appropriate choice is usually reckless, unethical, or out of sequence."
)

_ACTION_WRONG_FALLBACK: dict[str, str] = {
    "FIRST": "Not the first step — assessment, plan activation, or governance should precede this action.",
    "BEST": "Plausible tactically, but not the BEST sustainable governance or risk-reduction choice.",
    "NEXT": "Wrong sequence — this repeats an earlier step or skips the logical follow-on.",
    "LEAST": _LEAST_WRONG_NOTE,
    "PRIMARY": "Addresses a symptom or tool, not the greatest organizational or governance concern.",
}

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


def _infer_why_wrong(choice_text: str, action: str | None, is_least_question: bool) -> str:
    if is_least_question:
        for pattern, reason in _WRONG_PATTERNS:
            if pattern.search(choice_text):
                return f"Sounds decisive, but on LEAST items the worst choice is usually the reckless or unethical option. {reason}"
        return _LEAST_WRONG_NOTE

    for pattern, reason in _WRONG_PATTERNS:
        if pattern.search(choice_text):
            return reason

    if action and action in _ACTION_WRONG_FALLBACK:
        return _ACTION_WRONG_FALLBACK[action]

    return (
        "Plausible under pressure, but a manager should favor governance, documented risk decisions, "
        "and business alignment over quick technical or extreme actions."
    )


def build_wrong_choice_notes(question: Question) -> list[dict[str, str]]:
    """Brief manager-level notes for each incorrect option."""
    correct = question.correct_choice.upper()
    action = detect_action_word(question.stem)
    is_least = action == "LEAST"
    notes: list[dict[str, str]] = []

    for letter in ("A", "B", "C", "D"):
        if letter == correct:
            continue
        text = _choice_text(question, letter)
        notes.append({
            "choice": letter,
            "text": text,
            "why_wrong": _infer_why_wrong(text, action, is_least),
        })

    return notes


def build_approach_tips(question: Question) -> list[str]:
    """At most two short tips: action-word discipline + domain framing."""
    action = detect_action_word(question.stem)
    tips: list[str] = []

    if action and action in _ACTION_TIPS:
        tips.append(_ACTION_TIPS[action])

    domain_tip = _DOMAIN_TIPS.get(question.domain)
    if domain_tip and domain_tip not in tips:
        tips.append(domain_tip)

    return tips[:2]


def build_manager_feedback(question: Question) -> dict:
    brief = build_manager_brief(question)
    approach_tips = build_approach_tips(question)
    wrong_choice_notes = build_wrong_choice_notes(question)
    explanation = brief
    if wrong_choice_notes:
        explanation += "\n\nWhy other options are wrong:\n"
        for note in wrong_choice_notes:
            explanation += f"{note['choice']}: {note['why_wrong']}\n"
    if approach_tips:
        explanation += "\nQuick tips:\n" + "\n".join(f"• {t}" for t in approach_tips)
    return {
        "manager_brief": brief,
        "approach_tips": approach_tips,
        "wrong_choice_notes": wrong_choice_notes,
        "explanation": explanation.strip(),
    }
