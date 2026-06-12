"""Knowledge-check questions aligned to cheat sheet catalog topics."""
from __future__ import annotations

from app.data.cheat_sheet.knowledge_builder import build_knowledge_questions

# Built at import so catalog edits stay in sync without a separate seed file.
KNOWLEDGE_QUESTIONS: list[dict] = build_knowledge_questions()


def get_knowledge_questions() -> list[dict]:
    """Return all knowledge-check questions (one per catalog section)."""
    return KNOWLEDGE_QUESTIONS


def get_questions_for_topic(topic_id: str) -> list[dict]:
    """Return knowledge questions for a catalog topic_id."""
    return [q for q in KNOWLEDGE_QUESTIONS if q["topic_id"] == topic_id]
