"""Build knowledge-check MCQs from cheat sheet catalog sections."""
from __future__ import annotations

import hashlib
import re

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.domains import DOMAIN_NAMES

from app.data.diverse.choice_balance import balance_choice_set
from app.data.diverse.stem_formats import shuffle_choices


def _short_answer(text: str, max_len: int = 120) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def _stem_from_section(section: dict) -> str:
    scenarios = section.get("scenarios") or []
    if scenarios and "?" in scenarios[0]["prompt"]:
        return scenarios[0]["prompt"]
    title = section["title"]
    return (
        f"A leadership review focuses on {title}. "
        "Which option BEST reflects manager-level CISSP judgment for this topic?"
    )


def _correct_from_section(section: dict) -> str:
    scenarios = section.get("scenarios") or []
    if scenarios:
        return _short_answer(scenarios[0]["answer"], 140)
    return _short_answer(section.get("content", section["title"]), 140)


def _question_id(topic_id: str) -> str:
    digest = hashlib.sha1(topic_id.encode()).hexdigest()[:6]
    return f"kq-{topic_id}-{digest}"


def build_knowledge_questions() -> list[dict]:
    """One knowledge-check question per cheat-sheet section."""
    questions: list[dict] = []
    for domain_block in CHEAT_SHEET["domains"]:
        domain = domain_block["domain"]
        for section in domain_block["sections"]:
            topic_id = section["topic_id"]
            correct_text = _correct_from_section(section)
            balanced_correct, balanced_wrong = balance_choice_set(
                correct_text,
                [],
                domain,
                topic_id,
            )
            ca, cb, cc, cd, correct_letter = shuffle_choices(
                balanced_correct,
                balanced_wrong,
                topic_id,
            )
            stem = _stem_from_section(section)
            explanation = (
                f"This aligns with the study guide topic \"{section['title']}\". "
                f"{balanced_correct}"
            )
            questions.append(
                {
                    "id": _question_id(topic_id),
                    "topic_id": topic_id,
                    "domain": domain,
                    "domain_name": DOMAIN_NAMES[domain],
                    "importance": section.get("importance", "high"),
                    "difficulty": "medium",
                    "stem": stem,
                    "choice_a": ca,
                    "choice_b": cb,
                    "choice_c": cc,
                    "choice_d": cd,
                    "correct_choice": correct_letter,
                    "explanation": explanation,
                    "source_topic": section["title"],
                    "tags": f"knowledge-check,topic:{topic_id},cheat-sheet",
                }
            )
    return questions
