"""CISSP exam simulator rules — shared by question bank and post-answer feedback."""

from __future__ import annotations

import re

from app.data.domains import DOMAIN_NAMES

# Bloom levels 3–5: Apply, Analyze, Evaluate (ISC2 cognitive range)
BLOOM_APPLY = 3
BLOOM_ANALYZE = 4
BLOOM_EVALUATE = 5

DIFFICULTY_TO_BLOOM = {
    "easy": BLOOM_APPLY,
    "medium": BLOOM_ANALYZE,
    "hard": BLOOM_EVALUATE,
}

BLOOM_LABELS = {
    BLOOM_APPLY: "Apply (Bloom Level 3)",
    BLOOM_ANALYZE: "Analyze (Bloom Level 4)",
    BLOOM_EVALUATE: "Evaluate (Bloom Level 5)",
}

DOMAIN_PRINCIPLES: dict[int, str] = {
    1: "Governance, risk appetite, and due care before technical action",
    2: "Protecting data through classification, handling, and lifecycle controls",
    3: "Secure design, defense in depth, and engineering tradeoffs",
    4: "Protecting data in motion and network trust boundaries",
    5: "Identity as the perimeter — authentication, authorization, and accountability",
    6: "Independent assurance, testing scope, and evidence for risk decisions",
    7: "Incident response, continuity, and operational resilience",
    8: "Building security into the SDLC, not bolting it on at release",
}

CROSS_DOMAIN_TOPICS = ("Cloud Security", "AI Security")

_CLOUD_SIGNALS = (
    "cloud", "saas", "iaas", "paas", "aws", "azure", "gcp", "multi-cloud",
    "kubernetes", "container", "serverless", "object storage", "csp",
)
_AI_SIGNALS = (
    " ai ", "artificial intelligence", "machine learning", "ml model", "llm",
    "generative", "large language", "model training", "prompt injection",
    "ai feature", "ai-powered", "ai system",
)

STEM_ACTIONS = (
    "What should you do FIRST?",
    "Which course of action is BEST?",
    "Which option is MOST appropriate?",
    "Which control BEST mitigates the risk described?",
    "What is the PRIMARY objective from a security management perspective?",
    "Which response is MOST effective given the business constraints?",
    "Which response should take PRIORITY?",
    "What is the NEXT step?",
    "Which action is LEAST appropriate?",
    "What represents the GREATEST concern from a governance perspective?",
    "Which decision BEST demonstrates due care?",
)

_CISSP_ACTION_RE = re.compile(
    r"\b(BEST|MOST appropriate|MOST effective|MOST important|MOST accurate|MOST clearly|"
    r"FIRST|PRIMARY|NEXT|LEAST|BEST mitigates|GREATEST concern|take PRIORITY|"
    r"should NOT|NOT be taken)\b",
    re.I,
)


def domain_label(domain: int, domain_name: str | None = None) -> str:
    name = domain_name or DOMAIN_NAMES.get(domain, f"Domain {domain}")
    return f"Domain {domain}: {name}"


def detect_cross_domains(*texts: str) -> list[str]:
    combined = " ".join(t for t in texts if t).lower()
    found: list[str] = []
    if any(s in combined for s in _CLOUD_SIGNALS):
        found.append("Cloud Security")
    if any(s in combined for s in _AI_SIGNALS):
        found.append("AI Security")
    return found


def domain_labels(
    domain: int,
    domain_name: str | None = None,
    *,
    stem: str = "",
    source_topic: str = "",
    tags: str = "",
) -> str:
    """Primary CBK domain plus optional Cloud Security / AI Security cross-tags."""
    primary = domain_label(domain, domain_name)
    cross = detect_cross_domains(stem, source_topic, tags)
    if not cross:
        return primary
    return f"{primary}; {'; '.join(cross)}"


def bloom_label(difficulty: str | None = None, difficulty_level: int | None = None) -> str:
    level = difficulty_level or DIFFICULTY_TO_BLOOM.get(difficulty or "medium", BLOOM_ANALYZE)
    return BLOOM_LABELS.get(level, BLOOM_LABELS[BLOOM_ANALYZE])


def key_principle(domain: int, source_topic: str = "") -> str:
    base = DOMAIN_PRINCIPLES.get(domain, "Manager-level security judgment")
    topic = source_topic.strip()
    if topic:
        return f"{base} — applied to {topic}."
    return f"{base}."


def whats_being_tested(
    question_domain: int,
    source_topic: str,
    action: str | None = None,
    *,
    knowledge_check: bool = False,
) -> str:
    """Single focus line — principle and what the question tests."""
    base = DOMAIN_PRINCIPLES.get(question_domain, "Manager-level security judgment")
    topic = source_topic.strip() if source_topic else "this scenario"

    if knowledge_check:
        return f"Whether you can apply {base} to {topic} — not just recall a partial definition."

    action_leads = {
        "FIRST": f"Whether you can name the FIRST managerial step on {topic} before implementation or enforcement.",
        "BEST": f"Whether you can choose the BEST managerial tradeoff on {topic} when several answers sound reasonable.",
        "LEAST": f"Whether you can spot the LEAST appropriate action on {topic} — not merely the softest-sounding option.",
        "NEXT": f"Whether you can pick the NEXT step on {topic} after earlier triage is already done.",
        "PRIMARY": f"Whether you can identify the PRIMARY concern on {topic} — people, legal duty, or governance.",
        "MULTI": f"Whether you can select every required managerial action for {topic} — not just one good step.",
        "NOT": f"Whether you can spot what should NOT drive a professional decision on {topic}.",
    }
    lead = action_leads.get(action or "", f"Whether you can apply sound manager judgment on {topic}.")
    return f"{lead} Core principle: {base}."


def principle_tested(question_domain: int, source_topic: str) -> str:
    """Alias — kept for callers; use key_principle when action is known."""
    return key_principle(question_domain, source_topic)


def stem_has_cissp_action(stem: str) -> bool:
    return bool(_CISSP_ACTION_RE.search(stem))
