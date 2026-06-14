"""Human-readable feedback after each answered question."""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, Any

from app.services.answer_key import is_multi_select, parse_choices
from app.services.cissp_concept_explanations import lookup_concept_explanation
from app.services.cissp_exam_rules import (
    bloom_label,
    domain_labels,
    key_principle,
)

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
    ("NOT", re.compile(r"\bshould NOT\b|\bNOT be taken\b|\bNOT\b", re.I)),
]

# Scenario signals → direct thinking advice (never echoes the vignette text)
_SCENARIO_THINKING: list[tuple[tuple[str, ...], list[str]]] = [
    (
        ("worm", "trojan", "virus", "malware", "self-replicat", "logic bomb"),
        [
            "Focus on spread behavior — self-replication, user action, and host dependency — not delivery channel or name alone.",
            "Separate threats by what they do inside the environment once introduced, not by how familiar the label sounds.",
        ],
    ),
    (
        ("should not", "not be taken", "testing schedule", "test schedule"),
        [
            "Weigh sensitivity, exposure, and feasibility — not personal curiosity about tools or methods.",
            "Risk-based planning factors belong; experimentation and preference do not.",
        ],
    ),
    (
        ("ransomware", "malware", "breach", "incident", "attack", "compromise", "exfiltrat", "soc "),
        [
            "Contain damage and learn scope before rebuilds, press releases, or calling every external party.",
            "Stabilize first, then communicate and recover — sequence beats looking decisive.",
        ],
    ),
    (
        ("merger", "acqui", "integrat", "clinic", "subsidiary"),
        [
            "Set decision rights and one governance model before connecting systems or policies.",
            "Unclear ownership creates silent gaps — resolve accountability before integration speed.",
        ],
    ),
    (
        ("vendor", "third-party", "supplier", "partner", "outsourc", "fintech", "subcontract"),
        [
            "Due diligence and ongoing oversight beat speed and marketing claims before data is shared.",
            "You still own the risk after signature — trust must be earned with evidence.",
        ],
    ),
    (
        ("cloud", "saas", "aws", "azure", "kubernetes", "container", "serverless"),
        [
            "Shared responsibility means your org still owns data protection, keys, and many controls.",
            "Clarify who patches, monitors, and configures — the provider does not absorb all accountability.",
        ],
    ),
    (
        ("ai ", "artificial intelligence", "machine learning", "generative", "llm", "model"),
        [
            "Govern acceptable use, data boundaries, and ownership before relying on model output.",
            "Treat high-impact automation like any regulated system — oversight matters as much as accuracy.",
        ],
    ),
    (
        ("classif", "sensitive", "pii", "phi", "personal data", "ssn", "customer data", "handling"),
        [
            "Classification drives handling — sensitivity rules come before convenience or deadlines.",
            "Know what the data is and what policy allows before you move, store, or share it.",
        ],
    ),
    (
        ("penetration", "pentest", "vulnerability scan", "security test", "assessment"),
        [
            "Authorized testing needs clear scope, forbidden actions, and contacts before execution.",
            "Findings inform risk decisions — they do not replace ownership of remediation.",
        ],
    ),
    (
        ("policy", "governance", "charter", "raci", "ownership", "executive", "board"),
        [
            "Named owners and documented decisions beat another control nobody can enforce.",
            "Clarity on who decides and who accepts risk prevents quiet program failure.",
        ],
    ),
    (
        ("bcp", "continuity", "disaster", "rpo", "rto", "recovery", "outage", "failover"),
        [
            "Business impact sets recovery priorities — technology follows the timeline leadership accepts.",
            "Executives fund what they understand will hurt operations if it stays down.",
        ],
    ),
    (
        ("remote", "vpn", "work from home", "hybrid"),
        [
            "Protect the session and data in transit — off-site access is still an extended perimeter.",
            "Strong identity and encryption matter more when you do not control the physical workspace.",
        ],
    ),
    (
        ("develop", "sdlc", "release", "application", "software", "devops"),
        [
            "Security in design and requirements costs less than fixing flaws after release.",
            "Shift left under pressure — bolting controls on at go-live is the expensive path.",
        ],
    ),
    (
        ("encrypt", "crypto", "certificate", "key", "nonrepudiation", "integrity", "confidentiality"),
        [
            "Match the security goal to the problem — confidentiality, integrity, authenticity, and nonrepudiation differ.",
            "Pick the property the problem calls for, not the algorithm you remember best.",
        ],
    ),
    (
        ("identity", "authentication", "access", "mfa", "privilege", "iam", "login"),
        [
            "Prove identity first, then grant least privilege — entitlements should match the role.",
            "Different factor types matter for MFA; two passwords still count as one factor.",
        ],
    ),
    (
        ("firewall", "network", "segment", "perimeter", "zero trust", "vpn"),
        [
            "Inside the network is not automatically trusted — verify access on each request.",
            "Think about where data moves and where trust is granted, not just where the fence sits.",
        ],
    ),
    (
        ("risk accept", "risk treat", "risk mitig", "risk transfer", "risk avoid", "residual"),
        [
            "Documented acceptance with executive sign-off is a formal choice, not passive neglect.",
            "Match the treatment name to what leadership actually decided to do with residual risk.",
        ],
    ),
]

_DOMAIN_THINKING: dict[int, list[str]] = {
    1: [
        "Lead with governance, ownership, and risk appetite — not the control that looks fastest.",
        "Ask who decides, who accepts risk, and whether due care is visible before action.",
    ],
    2: [
        "Start with data sensitivity and lifecycle rules — handling follows classification.",
        "Protect assets by knowing what the data is, where it lives, and who owns it.",
    ],
    3: [
        "Think design and defense in depth — one layer failing should not collapse the program.",
        "Engineering tradeoffs matter, but secure architecture beats a single shiny control.",
    ],
    4: [
        "Focus on trust boundaries and data in motion — location alone is not authorization.",
        "Network choices should protect confidentiality and integrity across every path.",
    ],
    5: [
        "Identity is the perimeter — authenticate strongly, then authorize least privilege.",
        "Separate proof of identity from entitlements; convenience is a common trap.",
    ],
    6: [
        "Testing and assurance support decisions — scope, authorization, and evidence come first.",
        "Findings are inputs to risk management, not a substitute for ownership.",
    ],
    7: [
        "Operations questions reward sequence — stabilize, understand, then communicate and recover.",
        "Resilience means the business keeps moving, not just that servers come back online.",
    ],
    8: [
        "Security belongs in the lifecycle early — design and requirements beat late patches.",
        "Build it in before release; bolting controls on at go-live is the expensive path.",
    ],
}

_ACTION_THINKING: dict[str, list[str]] = {
    "FIRST": [
        "Read for sequence — name the first managerial step, not the most technical-looking fix.",
        "Ask what must be settled before tools, patches, or enforcement move forward.",
    ],
    "BEST": [
        "Pick the answer you could defend to leadership, legal, and auditors — not just what stops the symptom fastest.",
        "Choose the tradeoff that holds up under business pressure and scrutiny.",
    ],
    "LEAST": [
        "Find the option that crosses a line on ethics, law, or due care — not merely the soft or cautious-sounding one.",
        "Look for the choice that would embarrass you in a post-incident review.",
    ],
    "NEXT": [
        "Assume earlier triage is done and select the step that moves the response forward.",
        "Avoid redoing discovery — pick the sensible next move from the current phase.",
    ],
    "PRIMARY": [
        "Decide whether people, legal duty, or governance is the headline issue before you reach for a control.",
        "Name the concern that should drive every other decision.",
    ],
    "NOT": [
        "Cross off anything driven by preference or curiosity rather than risk-based judgment.",
        "Eliminate the factor that does not belong in a professional, risk-based decision.",
    ],
    "MULTI": [
        "Select every required action — one good step alone will not be enough.",
        "Treat it like a checklist and mark all options that are truly required.",
    ],
    "DEFAULT": [
        "Match the action word to the phase the organization is actually in.",
        "Think like the accountable manager, not the engineer who wants to act now.",
    ],
}

_WATCH_OUT: dict[str, str] = {
    "FIRST": "Reaching for a technical fix before ownership and approvals are in place.",
    "BEST": "Choosing what works in the SOC tonight instead of what leadership can defend long term.",
    "LEAST": "Picking the answer that sounds decisive when the exam wants the ethically or legally reckless one.",
    "NEXT": "Repeating discovery when the vignette already finished that phase.",
    "PRIMARY": "Answering the technical symptom when people, legal duty, or governance is the real issue.",
    "MULTI": "Stopping after one good action when the stem requires every correct option.",
    "NOT": "Treating personal preference or tool curiosity as equal to risk-based planning factors.",
}


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
    return (
        "This is the answer that holds up under manager-level scrutiny — "
        "not just in a lab or on a checklist."
    )


def _section(key: str, title: str, body: str) -> dict[str, str]:
    return {"key": key, "title": title, "body": body.strip()}


def _whats_being_tested(
    question_domain: int,
    source_topic: str,
    action: str | None,
    *,
    knowledge_check: bool = False,
) -> str:
    topic = source_topic.strip() if source_topic else "this scenario"

    if knowledge_check:
        return (
            f"This question checks whether you can apply CISSP judgment to {topic} — "
            "not merely recall an isolated fact."
        )

    action_leads = {
        "FIRST": f"This question checks whether you know the FIRST managerial step for {topic}.",
        "BEST": f"This question checks whether you can choose the BEST managerial response for {topic}.",
        "LEAST": f"This question checks whether you can spot the LEAST appropriate action on {topic}.",
        "NEXT": f"This question checks whether you can pick the NEXT step for {topic} after earlier work is done.",
        "PRIMARY": f"This question checks whether you can name the PRIMARY concern for {topic}.",
        "MULTI": f"This question checks whether you can select every required action for {topic}.",
        "NOT": f"This question checks whether you can spot what should NOT drive a professional decision on {topic}.",
    }
    return action_leads.get(
        action or "",
        f"This question checks whether you can apply sound manager judgment to {topic}.",
    )


def _pick_variant(seed: str, options: list[str]) -> str:
    if not options:
        return ""
    idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(options)
    return options[idx]


def _scenario_thinking(combined: str, seed: str) -> str | None:
    lower = combined.lower()
    for keywords, lines in _SCENARIO_THINKING:
        if any(k in lower for k in keywords):
            return _pick_variant(seed, lines)
    return None


_STUDY_GUIDE_THINKING = [
    "Apply the complete principle — partial truths are there to pull you off the best answer.",
    "Reach for the idea that fully holds together, not the keyword that sounds familiar from notes.",
    "Pick the line that completes the CBK concept, not the definition that is only half true.",
]


def _how_to_think(question: Question, action: str | None) -> str:
    """Direct manager lens — unique per question, never repeats the vignette."""
    stem = question.stem or ""
    topic = question.source_topic or ""
    seed = f"{getattr(question, 'id', '')}|{stem}|{topic}|think"
    combined = f"{stem} {topic} {question.tags or ''}"
    action_key = action if action in _ACTION_THINKING else "DEFAULT"
    action_line = _pick_variant(f"{seed}|action", _ACTION_THINKING[action_key])

    if "study-guide" in (question.tags or "") or "knowledge-check" in (question.tags or ""):
        lead = _pick_variant(f"{seed}|sg", _STUDY_GUIDE_THINKING)
        return f"{lead} {action_line}"

    scenario_line = _scenario_thinking(combined, seed)
    if scenario_line:
        return f"{scenario_line} {action_line}"

    domain = int(getattr(question, "domain", 1) or 1)
    domain_line = _pick_variant(
        f"{seed}|dom",
        _DOMAIN_THINKING.get(domain, _DOMAIN_THINKING[1]),
    )
    return f"{domain_line} {action_line}"


def _manager_hint(question: Question, action: str | None) -> str:
    """Alias for approach tips API."""
    return _how_to_think(question, action)


def _distractor_inferior(question: Question, letter: str, action: str | None) -> str:
    lower = _choice_text(question, letter).lower()
    topic = question.source_topic or question.domain_name or "this situation"

    if any(k in lower for k in ("assess", "risk assessment", "evaluate risk", "identify risk")):
        return (
            "Risk assessment is sound in many programs, but it is premature here before "
            "ownership and scope are established."
        )
    if any(k in lower for k in ("deploy", "install", "patch", "implement", "block", "terminate", "segment")):
        return (
            "A technical control can be correct later; in this scenario it skips governance, "
            "sequence, or business alignment."
        )
    if any(k in lower for k in ("iso", "certification", "certified", "soc 2", "audit report", "vendor")):
        return (
            "Third-party assurance is valuable during vendor review, but it does not replace "
            "internal ownership and accountability here."
        )
    if any(k in lower for k in ("policy", "governance", "charter", "ownership", "executive", "board")):
        return (
            "Governance is often the right family of controls, but another option better matches "
            "the action word and scenario phase."
        )
    if any(k in lower for k in ("notify", "communicat", "inform", "disclosure")):
        return (
            "Communication is frequently required, but the timing or priority is wrong relative "
            "to what the stem asks."
        )
    if any(k in lower for k in ("legal", "compliance", "regulat", "counsel", "contract")):
        return (
            "Legal and compliance involvement may be necessary, but alone it does not satisfy "
            "the BEST managerial sequence in this vignette."
        )
    if any(k in lower for k in ("immediately", "without", "ignore", "all users", "shut down", "disable")):
        return (
            "Forceful action can be warranted in some incidents, but here it bypasses "
            "proportionality, approvals, or due care."
        )
    if "study-guide" in (question.tags or "") or "knowledge-check" in (question.tags or ""):
        return (
            "This statement can be true in a narrow textbook sense, but it is not the BEST "
            "answer for the full CISSP principle being tested."
        )
    if action == "NOT":
        return (
            "This is a legitimate planning factor — the stem asks for the one that should not "
            "influence the schedule."
        )
    if action == "LEAST":
        return (
            "This option is plausible, but it is not the one that fails on ethics, law, or due care."
        )
    return (
        f"In another phase of {topic}, this could be reasonable — it is not the BEST fit "
        "for this scenario."
    )


def _why_correct_prose(question: Question, letters: list[str], action: str | None) -> str:
    """Plain-language rationale for the correct choice — CBK-grounded, like sample exam keys."""
    correct_texts = [_choice_text(question, letter).strip() for letter in letters]
    combined_correct = "; ".join(correct_texts)
    core = _strip_legacy_tips(question.explanation or "")

    return lookup_concept_explanation(
        stem=question.stem or "",
        correct_text=combined_correct,
        source_topic=question.source_topic or "",
        domain=int(getattr(question, "domain", 1) or 1),
        action=action,
        stored_explanation=core,
    )


def _best_answer_prose(question: Question, letters: list[str], action: str | None) -> str:
    thinking = _how_to_think(question, action)
    rationale = _why_correct_prose(question, letters, action)
    label = " and ".join(letters)
    if is_multi_select(question.correct_choice) and len(letters) > 1:
        return (
            f"{thinking}\n\nCorrect answer: {label}\n"
            f"{rationale}"
        )
    return f"{thinking}\n\nCorrect answer: {label}\n{rationale}"


def _distractors_reference(question: Question, action: str | None) -> str:
    correct_set = parse_choices(question.correct_choice)
    lines: list[str] = []
    for letter in ("A", "B", "C", "D"):
        if letter in correct_set:
            continue
        lines.append(f"{letter} — {_distractor_inferior(question, letter, action)}")
    return "\n".join(lines)


def _watch_out(question: Question) -> str:
    action = detect_action_word(question.stem)
    if action and action in _WATCH_OUT:
        return _WATCH_OUT[action]
    if "study-guide" in (question.tags or "") or "knowledge-check" in (question.tags or ""):
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
            "why_wrong": _distractor_inferior(question, letter, action),
        })
    return notes


def _difficulty_for(question: Question) -> str | None:
    return getattr(question, "difficulty", None)


def _difficulty_level_for(question: Question) -> int | None:
    return getattr(question, "difficulty_level", None)


def build_explanation_sections(
    question: Question,
    selected_choice: str | None = None,
    is_correct: bool | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    action = detect_action_word(question.stem)
    correct_letters = sorted(parse_choices(question.correct_choice))
    primary_correct = correct_letters[0] if correct_letters else question.correct_choice.upper()
    knowledge = "knowledge-check" in (question.tags or "") or "study-guide" in (question.tags or "")

    tested = _whats_being_tested(
        question.domain,
        question.source_topic or "",
        action,
        knowledge_check=knowledge,
    )

    main: list[dict[str, str]] = [
        _section("context", "What's being tested", tested),
    ]

    best_title = (
        "Why the correct answers are BEST"
        if len(correct_letters) > 1
        else "Why the correct answer is BEST"
    )
    prose = _best_answer_prose(question, correct_letters, action)
    main.append(_section("correct_answer", best_title, prose))

    distractor_body = _distractors_reference(question, action)
    reference: list[dict[str, str]] = []
    if distractor_body:
        reference.append(
            _section("distractors", "Why each distractor is inferior", distractor_body)
        )
    reference.extend([
        _section(
            "domain",
            "Domain(s)",
            domain_labels(
                question.domain,
                question.domain_name,
                stem=question.stem,
                source_topic=question.source_topic or "",
                tags=question.tags or "",
            ),
        ),
        _section(
            "principle",
            "Key CISSP principle tested",
            key_principle(question.domain, question.source_topic or ""),
        ),
        _section(
            "cognitive_level",
            "Cognitive level",
            bloom_label(_difficulty_for(question), _difficulty_level_for(question)),
        ),
        _section("watch_out", "Easy mistake", _watch_out(question)),
    ])
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
    action = detect_action_word(question.stem)
    return [_how_to_think(question, action), build_trap_line(question)]


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
        "approach_tips": build_approach_tips(question),
        "wrong_choice_notes": wrong_notes,
        "explanation": brief,
    }
