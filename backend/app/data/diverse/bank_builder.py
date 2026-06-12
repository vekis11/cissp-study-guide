"""Build 800+ diverse CISSP questions from ISC2-aligned topic kernels and varied stem formats."""

from __future__ import annotations

import hashlib

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.data.diverse.multi_select import build_multi_question
from app.data.diverse.stem_formats import format_stem, shuffle_choices
from app.data.diverse.topic_specs import TOPIC_SPECS
from app.data.scenario_templates_premium import PREMIUM_QUESTIONS

BANK_TAG = "bank-v9"
FORMATS_PER_KERNEL = 8
MIN_BANK_SIZE = 800


def _qid(domain: int, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:12]
    return f"dv-d{domain}-{h}"


def _kernel_questions(spec: dict, kernel_idx: int) -> list[dict]:
    questions: list[dict] = []
    domain = spec["domain"]
    topic = spec["topic"]
    industry = spec["industry"]
    narrative = spec["narrative"]
    difficulty = spec.get("difficulty", "hard")

    for slot in range(FORMATS_PER_KERNEL):
        stem = format_stem(slot, narrative, industry, topic)
        seed = f"{kernel_idx}-{slot}-{stem[:80]}"
        ca, cb, cc, cd, correct = shuffle_choices(
            spec["correct"],
            spec["wrong"],
            seed,
        )
        qid = _qid(domain, seed + spec["correct"])
        tags = f"diverse,manager,scenario,{BANK_TAG},{spec.get('tag', 'isc2')}"
        questions.append({
            "id": qid,
            "domain": domain,
            "domain_name": DOMAIN_NAMES[domain],
            "difficulty": difficulty,
            "tags": tags,
            "stem": stem,
            "choice_a": ca,
            "choice_b": cb,
            "choice_c": cc,
            "choice_d": cd,
            "correct_choice": correct,
            "explanation": spec["explanation"],
            "source_topic": topic,
        })
    multi = build_multi_question(spec, kernel_idx)
    if multi:
        qid = _qid(domain, f"multi-{multi['id_suffix']}")
        tags = (
            f"diverse,manager,scenario,multi-select,{BANK_TAG},{spec.get('tag', 'isc2')}"
        )
        questions.append({
            "id": qid,
            "domain": domain,
            "domain_name": DOMAIN_NAMES[domain],
            "difficulty": difficulty,
            "tags": tags,
            "stem": multi["stem"],
            "choice_a": multi["choice_a"],
            "choice_b": multi["choice_b"],
            "choice_c": multi["choice_c"],
            "choice_d": multi["choice_d"],
            "correct_choice": multi["correct_choice"],
            "explanation": (
                f"{spec['explanation']} Select-all questions require every correct "
                "managerial action — partial selections are incorrect."
            ),
            "source_topic": topic,
        })
    return questions


def _dedupe_questions(questions: list[dict]) -> list[dict]:
    seen_ids: set[str] = set()
    seen_stems: set[str] = set()
    unique: list[dict] = []
    for q in questions:
        if q["id"] in seen_ids:
            continue
        stem_key = hashlib.sha256(q["stem"].encode()).hexdigest()
        if stem_key in seen_stems:
            continue
        if len(q["stem"]) < 60 or len(q["stem"]) > 1200:
            continue
        choices = {q["choice_a"], q["choice_b"], q["choice_c"], q["choice_d"]}
        if len(choices) < 4:
            continue
        seen_ids.add(q["id"])
        seen_stems.add(stem_key)
        unique.append(q)
    return unique


def _tag_premium(q: dict) -> dict:
    tags = q.get("tags", "")
    if BANK_TAG not in tags:
        q = {**q, "tags": f"{tags},{BANK_TAG}" if tags else BANK_TAG}
    return q


def build_diverse_bank() -> list[dict]:
    """Assemble premium hand-crafted items plus 8 format variants per topic kernel."""
    questions: list[dict] = [_tag_premium(dict(q)) for q in PREMIUM_QUESTIONS]

    for idx, spec in enumerate(TOPIC_SPECS):
        questions.extend(_kernel_questions(spec, idx))

    unique = _dedupe_questions(questions)
    if len(unique) < MIN_BANK_SIZE:
        raise RuntimeError(f"Bank has {len(unique)} questions; need at least {MIN_BANK_SIZE}")

    # Weight check — ensure each domain represented
    by_domain = {d: 0 for d in DOMAIN_NAMES}
    for q in unique:
        by_domain[q["domain"]] += 1
    for d, weight in DOMAIN_WEIGHTS.items():
        floor = int(MIN_BANK_SIZE * weight * 0.85)
        if by_domain[d] < floor:
            raise RuntimeError(f"Domain {d} only has {by_domain[d]} questions (need ~{floor})")

    return unique


def get_all_questions() -> list[dict]:
    return build_diverse_bank()
