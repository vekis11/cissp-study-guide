"""Direct knowledge-check stems — application-level, not pure recall."""

from __future__ import annotations

import hashlib

_KNOWLEDGE_PROMPTS = (
    "A program review covers {topic}. Which decision is MOST appropriate for a security leader?",
    "Which response BEST mitigates risk related to {topic} at the program level?",
    "When evaluating {topic}, which option is the MOST effective managerial choice?",
    "Which statement BEST reflects how {topic} should be handled under CISSP governance principles?",
    "Leadership asks for guidance on {topic}. Which answer is the BEST course of action?",
)


def knowledge_stem(topic: str, seed: str) -> str:
    idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_KNOWLEDGE_PROMPTS)
    return _KNOWLEDGE_PROMPTS[idx].format(topic=topic)
