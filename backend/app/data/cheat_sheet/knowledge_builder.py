"""Build knowledge-check MCQs from cheat sheet catalog sections."""
from __future__ import annotations

import hashlib
import re

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.domains import DOMAIN_NAMES

_WRONG_BY_DOMAIN: dict[int, list[str]] = {
    1: [
        "Defer the decision to technical staff without executive risk criteria.",
        "Prioritize speed of delivery over documented governance and accountability.",
        "Apply a one-size-fits-all control without business impact analysis.",
        "Accept residual risk without management approval or monitoring.",
    ],
    2: [
        "Let IT staff set classification levels without data owner approval.",
        "Delete files normally and assume data is unrecoverable.",
        "Share sensitive data broadly to reduce operational friction.",
        "Skip sanitization because the media will be reused internally.",
    ],
    3: [
        "Rely on a single control layer instead of defense in depth.",
        "Use deprecated cryptography because it is faster to deploy.",
        "Skip key management because encryption alone is sufficient.",
        "Ignore physical controls when hardening logical security.",
    ],
    4: [
        "Allow unencrypted management traffic on production networks.",
        "Merge guest and corporate VLANs to simplify routing.",
        "Disable logging to improve network performance.",
        "Use WEP for wireless because it is widely supported.",
    ],
    5: [
        "Grant standing administrator access to reduce help-desk tickets.",
        "Treat password plus PIN as multi-factor authentication.",
        "Share service account credentials across teams for convenience.",
        "Skip recertification because roles rarely change.",
    ],
    6: [
        "Run penetration tests weekly without scoping or approval.",
        "Treat vulnerability scanning results as proof of exploitation.",
        "Skip remediation tracking after assessment findings.",
        "Use only automated tools without validation of control effectiveness.",
    ],
    7: [
        "Begin eradication before preserving volatile forensic evidence.",
        "Restore production systems before verifying malware removal.",
        "Skip lessons learned to return to normal operations faster.",
        "Store backups only on the same site as production systems.",
    ],
    8: [
        "Add security testing only after production deployment.",
        "Rely on client-side input validation alone for web apps.",
        "Ship third-party libraries without composition analysis.",
        "Use verbose error messages to speed developer debugging in production.",
    ],
}


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
            wrong_pool = [w for w in _WRONG_BY_DOMAIN[domain] if w != correct_text]
            choices = [correct_text] + wrong_pool[:3]
            while len(choices) < 4:
                choices.append(f"Ignore {section['title']} until the next audit cycle.")
            labels = ["A", "B", "C", "D"]
            correct_idx = int(hashlib.sha1(topic_id.encode()).hexdigest(), 16) % 4
            rotated = choices[correct_idx:] + choices[:correct_idx]
            choices = rotated
            stem = _stem_from_section(section)
            explanation = (
                f"This aligns with the study guide topic \"{section['title']}\". "
                f"{correct_text}"
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
                    "choice_a": choices[0],
                    "choice_b": choices[1],
                    "choice_c": choices[2],
                    "choice_d": choices[3],
                    "correct_choice": labels[correct_idx],
                    "explanation": explanation,
                    "source_topic": section["title"],
                    "tags": f"knowledge-check,topic:{topic_id},cheat-sheet",
                }
            )
    return questions
