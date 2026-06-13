"""Human-readable feedback after each answered question."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from app.services.answer_key import is_multi_select, parse_choices
from app.services.cissp_exam_rules import domain_label, whats_being_tested

if TYPE_CHECKING:
    from app.models import Question

_CHOICE_FIELDS = {"A": "choice_a", "B": "choice_b", "C": "choice_c", "D": "choice_d"}

_ACTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("LEAST", re.compile(r"\bLEAST\b", re.I)),
    ("FIRST", re.compile(r"\bFIRST\b|\bBEFORE\b", re.I)),
    ("NEXT", re.compile(r"\bNEXT\b", re.I)),
    (
        "BEST",
        re.compile(
            r"\bBEST\b|\bMOST APPROPRIATE\b|\bMOST SIGNIFICANT\b|\bMOST accurate\b|"
            r"\bMOST correct\b|\bMOST effective\b|\bBEST mitigates\b",
            re.I,
        ),
    ),
    ("PRIMARY", re.compile(r"\bPRIMARY\b|\bPRIORITY\b|\bGREATEST\b", re.I)),
]

_WATCH_OUT: dict[str, str] = {
    "FIRST": "Reaching for a technical fix before ownership and approvals are in place.",
    "BEST": "Choosing what works in the SOC tonight instead of what leadership can defend long term.",
    "LEAST": "Picking the answer that sounds decisive when the exam wants the ethically or legally reckless one.",
    "NEXT": "Repeating discovery when the vignette already finished that phase.",
    "PRIMARY": "Answering the technical symptom when people, legal duty, or governance is the real issue.",
    "MULTI": "Stopping after one good action when the stem requires every correct option.",
}

_PEOPLE_WORDS = (
    "employee", "staff", "user", "customer", "patient", "people", "privacy",
    "safety", "notify", "communicat", "stakeholder", "witness",
)
_LEGAL_WORDS = (
    "legal", "law", "regulat", "compliance", "contract", "breach", "gdpr",
    "hipaa", "pci", "sox", "duty", "mandat", "subpoena",
)
_GOVERNANCE_WORDS = (
    "governance", "policy", "ownership", "owner", "executive", "leadership",
    "board", "charter", "accountable", "risk accept", "approve", "framework",
)


def _choice_text(question: Question, letter: str) -> str:
    field = _CHOICE_FIELDS.get(letter.upper(), "choice_a")
    return getattr(question, field, "")


def detect_action_word(stem: str) -> str | None:
    if re.search(r"select (two|all|three)|select all that apply", stem, re.I):
        return "MULTI"
    for name, pattern in _ACTION_PATTERNS:
        if pattern.search(stem):
            return name
    return None


def _strip_legacy_tips(explanation: str) -> str:
    markers = (
        " CISSP 'FIRST' questions",
        " 'LEAST appropriate'",
        " 'BEST' favors",
        " 'NEXT' assumes",
        " Focus on the highest-level",
        " Think like a CISO:",
        " On LEAST questions, eliminate",
        " Select-all questions require",
    )
    text = explanation.strip()
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    if text.startswith("LEAST appropriate:"):
        text = re.sub(r"^LEAST appropriate:\s*'[^']+'\s*—\s*[^.]+\.\s*", "", text).strip()
    return text


def _core_explanation(question: Question) -> str:
    core = _strip_legacy_tips(question.explanation)
    if core:
        return core
    return "This is the answer that holds up under manager-level scrutiny — not just in a lab."


def _section(key: str, title: str, body: str) -> dict[str, str]:
    return {"key": key, "title": title, "body": body.strip()}


def _distractor_brief(question: Question, letter: str, action: str | None) -> str:
    """Where a wrong answer fits, why people pick it, and why it fails here."""
    lower = _choice_text(question, letter).lower()
    topic = question.source_topic or question.domain_name or "this situation"

    if any(k in lower for k in ("assess", "risk assessment", "evaluate risk", "identify risk")):
        where = f"After scope and ownership are clear, assessing risk before a planned rollout on {topic} is sound."
        mistake = "Many candidates treat “assess first” as universal — it is, but not before basic governance exists."
        why_not = _why_not_here(action, "assessment comes before ownership is established in this vignette.")
    elif any(k in lower for k in ("deploy", "install", "patch", "implement", "block", "terminate", "segment")):
        where = "Once approvals, architecture, and owners are set, pushing a technical control for {topic} is appropriate.".format(
            topic=topic
        )
        mistake = "Technical staff reach for fixes they can execute this week — the exam rewards sequence over speed."
        why_not = _why_not_here(action, "implementation is premature for what the stem is asking.")
    elif any(k in lower for k in ("iso", "certification", "certified", "soc 2", "audit report", "vendor")):
        where = f"During vendor due diligence or contract negotiation on {topic}, asking for third-party assurance helps."
        mistake = "A certificate feels like proof — so it is tempting when you need a defensible answer fast."
        why_not = _why_not_here(action, "external assurance does not replace internal ownership and governance here.")
    elif any(k in lower for k in ("policy", "governance", "charter", "ownership", "executive", "board")):
        where = f"Early in a {topic} program, establishing policy and named owners is exactly what you want."
        mistake = "Governance answers can look slow or vague next to concrete technical options."
        why_not = _why_not_here(action, "this option is close but not the BEST fit for the action word in the stem.")
    elif any(k in lower for k in ("notify", "communicat", "inform", "disclosure")):
        where = f"After scope is understood, communicating about {topic} to stakeholders is often required."
        mistake = "Communication sounds caring and compliant — easy to choose when an incident is implied."
        why_not = _why_not_here(action, "notification timing or priority is wrong relative to what was asked.")
    elif any(k in lower for k in ("legal", "compliance", "regulat", "counsel", "contract")):
        where = f"When regulatory triggers or contracts drive {topic}, involving legal/compliance is appropriate."
        mistake = "Legal/compliance options feel safe — candidates pick them to avoid choosing a wrong technical step."
        why_not = _why_not_here(action, "legal involvement alone does not satisfy the BEST managerial sequence here.")
    elif any(k in lower for k in ("immediately", "without", "ignore", "all users", "shut down", "disable")):
        where = "In a confirmed active breach with executive sign-off, forceful containment may be warranted."
        mistake = "Urgent wording mirrors real incidents — stress pushes you toward the most aggressive line."
        why_not = _why_not_here(action, "speed and scope here skip proportional response or required approvals.")
    elif "knowledge-check" in (question.tags or ""):
        where = "In a narrow textbook or tool-specific context, this statement can be true."
        mistake = "Partial truths stand out when you recognize one familiar phrase from study notes."
        why_not = "The CISSP exam wants the most complete CBK principle, not the narrowly true line."
    else:
        where = f"In another phase of a {topic} initiative, this could be a reasonable manager decision."
        mistake = "It reads like solid due care — similar wording appears in many correct answers across the bank."
        why_not = _why_not_here(action, "it does not best match the scenario and action word in this question.")

    return (
        f"Where it fits: {where}\n"
        f"Easy to pick because: {mistake}\n"
        f"Why not here: {why_not}"
    )


def _why_not_here(action: str | None, reason: str) -> str:
    if action == "FIRST":
        return f"This is a FIRST question — {reason}"
    if action == "NEXT":
        return f"This is a NEXT question — {reason}"
    if action == "LEAST":
        return f"This is a LEAST question — {reason}"
    if action == "BEST" or action == "PRIMARY":
        return f"BEST/PRIMARY bar — {reason}"
    if action == "MULTI":
        return f"Select-all — {reason}"
    return reason.capitalize() if reason else "It does not best match this stem."


def _short_reason_wrong(question: Question, letter: str, action: str | None) -> str:
    brief = _distractor_brief(question, letter, action)
    easy_line = next((ln.split(": ", 1)[1] for ln in brief.split("\n") if ln.startswith("Easy to pick")), "")
    why_line = next((ln.split(": ", 1)[1] for ln in brief.split("\n") if ln.startswith("Why not here")), "")
    return f"You picked {letter}. {easy_line} {why_line}".strip()


def _correct_summary(question: Question, letters: list[str], action: str | None) -> str:
    core = _core_explanation(question)
    if is_multi_select(question.correct_choice) and len(letters) > 1:
        labels = " and ".join(letters)
        return f"{labels} are both required. {core}"

    letter = letters[0]
    if action == "FIRST":
        lead = f"{letter} is BEST because it establishes ownership and direction before anyone touches systems."
    elif action == "LEAST":
        lead = f"{letter} is BEST because it is the option that fails on ethics, law, or due care."
    elif action == "NEXT":
        lead = f"{letter} is BEST because it moves the response forward without redoing earlier work."
    elif action == "BEST":
        lead = f"{letter} is BEST — the answer you could defend to leadership, legal, and auditors."
    else:
        lead = f"{letter} is BEST because it directly matches what the question is asking."

    return f"{lead} {core}"


def _distractors_section(question: Question, action: str | None) -> str:
    correct_set = parse_choices(question.correct_choice)
    blocks: list[str] = []
    for letter in ("A", "B", "C", "D"):
        if letter in correct_set:
            continue
        blocks.append(f"{letter}\n{_distractor_brief(question, letter, action)}")
    return "\n\n".join(blocks)


def _dominant_lens(text: str, stem: str) -> str:
    combined = f"{text} {stem}".lower()
    if any(w in combined for w in _PEOPLE_WORDS):
        return "people"
    if any(w in combined for w in _LEGAL_WORDS):
        return "legal"
    if any(w in combined for w in _GOVERNANCE_WORDS):
        return "governance"
    if any(w in combined for w in ("incident", "breach", "ransomware", "outage")):
        return "people"
    return "governance"


def _manager_view(question: Question, letter: str) -> str:
    lens = _dominant_lens(_choice_text(question, letter), question.stem)
    if lens == "people":
        return "People come first — communication, privacy, and safety beat a quiet technical fix."
    if lens == "legal":
        return "Legal and contractual duty matters. Skipping required steps creates liability."
    return "Governance matters — named owners, documented decisions, and leadership sign-off."


def _watch_out(question: Question) -> str:
    action = detect_action_word(question.stem)
    if action and action in _WATCH_OUT:
        return _WATCH_OUT[action]
    if "knowledge-check" in (question.tags or ""):
        return "Choosing a line that is true in a narrow context but not the most complete CBK principle."
    return "Picking what works operationally while skipping ownership, legal duty, or business alignment."


def _wrong_choice_notes(question: Question, action: str | None) -> list[dict[str, str]]:
    correct_set = parse_choices(question.correct_choice)
    notes: list[dict[str, str]] = []
    for letter in ("A", "B", "C", "D"):
        if letter in correct_set:
            continue
        notes.append({
            "choice": letter,
            "text": _choice_text(question, letter),
            "why_wrong": _distractor_brief(question, letter, action),
        })
    return notes


def build_explanation_sections(
    question: Question,
    selected_choice: str | None = None,
    is_correct: bool | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    action = detect_action_word(question.stem)
    correct_letters = sorted(parse_choices(question.correct_choice))
    primary_correct = correct_letters[0] if correct_letters else question.correct_choice.upper()
    knowledge = "knowledge-check" in (question.tags or "")

    main: list[dict[str, str]] = [
        _section(
            "context",
            "What's being tested",
            whats_being_tested(
                question.domain,
                question.source_topic or "",
                action,
                knowledge_check=knowledge,
            ),
        ),
    ]

    if selected_choice and is_correct is not None:
        user_letters = sorted(parse_choices(selected_choice))
        if is_correct:
            letter = user_letters[0] if user_letters else selected_choice.upper()
            main.append(
                _section(
                    "your_answer",
                    "You got it",
                    _correct_summary(
                        question,
                        user_letters if is_multi_select(question.correct_choice) else [letter],
                        action,
                    ),
                )
            )
        else:
            if user_letters:
                u = user_letters[0] if len(user_letters) == 1 else ", ".join(user_letters)
                main.append(
                    _section("your_answer", f"Why {u} isn't it", _short_reason_wrong(question, user_letters[0], action))
                )
            main.append(
                _section(
                    "correct_answer",
                    f"Why {', '.join(correct_letters)} is BEST" if len(correct_letters) > 1 else f"Why {primary_correct} is BEST",
                    _correct_summary(question, correct_letters, action),
                )
            )
    else:
        main.append(
            _section(
                "correct_answer",
                f"Why {', '.join(correct_letters)} is BEST" if len(correct_letters) > 1 else f"Why {primary_correct} is BEST",
                _correct_summary(question, correct_letters, action),
            )
        )

    distractor_body = _distractors_section(question, action)
    if distractor_body:
        main.append(_section("distractors", "Why the others fall short", distractor_body))

    reference: list[dict[str, str]] = [
        _section("domain", "Domain", domain_label(question.domain, question.domain_name)),
        _section("manager_lens", "Manager view", _manager_view(question, primary_correct)),
        _section("watch_out", "Easy mistake", _watch_out(question)),
    ]
    return main, reference


def _sections_to_brief(main: list[dict[str, str]], reference: list[dict[str, str]]) -> str:
    parts = [f"{s['title']}\n{s['body']}" for s in main + reference]
    return "\n\n".join(parts)


def build_trap_line(question: Question) -> str:
    return _watch_out(question)


def build_manager_brief(
    question: Question,
    selected_choice: str | None = None,
    is_correct: bool | None = None,
) -> str:
    main, reference = build_explanation_sections(question, selected_choice, is_correct)
    return _sections_to_brief(main, reference)


def build_approach_tips(question: Question) -> list[str]:
    return [build_trap_line(question)]


def build_manager_feedback(
    question: Question,
    selected_choice: str | None = None,
    is_correct: bool | None = None,
) -> dict[str, Any]:
    action = detect_action_word(question.stem)
    main, reference = build_explanation_sections(question, selected_choice, is_correct)
    brief = _sections_to_brief(main, reference)
    trap = build_trap_line(question)
    wrong_notes = _wrong_choice_notes(question, action)

    return {
        "manager_brief": brief,
        "explanation_sections": main,
        "reference_sections": reference,
        "trap": trap,
        "approach_tips": [trap],
        "wrong_choice_notes": wrong_notes,
        "explanation": brief,
    }
