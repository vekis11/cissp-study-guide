"""Scenario-only application stems — Bloom 3–5, embedded in business context."""

from __future__ import annotations

import hashlib

_SCENARIO_PROMPTS = (
    "A program review covers {topic}. {context} Which decision is MOST appropriate for a security leader?",
    "When evaluating {topic}, {context} Which option is the MOST effective managerial choice?",
    "Leadership asks for guidance on {topic}. {context} Which answer is the BEST course of action?",
    "Risk metrics for {topic} are trending poorly. {context} Which response is MOST effective given the business constraints?",
    "After an internal review of {topic}, {context} Which course of action is BEST?",
)


def knowledge_stem(topic: str, seed: str, context: str = "") -> str:
    idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_SCENARIO_PROMPTS)
    ctx = context.strip() or "Several options sound reasonable."
    if ctx and ctx[-1] not in ".?!":
        ctx += "."
    return _SCENARIO_PROMPTS[idx].format(topic=topic, context=ctx)
