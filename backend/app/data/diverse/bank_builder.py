"""Build 800+ diverse CISSP questions from ISC2-aligned topic kernels and varied stem formats."""

from __future__ import annotations

import hashlib

from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.data.cheat_sheet.knowledge_builder import build_knowledge_questions
from app.data.diverse.choice_balance import balance_choice_set, is_length_giveaway
from app.data.diverse.knowledge_stems import knowledge_stem
from app.data.diverse.multi_select import build_multi_question
from app.data.diverse.stem_formats import format_stem, shuffle_choices
from app.data.diverse.topic_specs import TOPIC_SPECS
from app.data.scenario_templates_premium import PREMIUM_QUESTIONS

from app.services.cissp_exam_rules import DIFFICULTY_TO_BLOOM

BANK_TAG = "bank-v12"
KNOWLEDGE_SLOT = 7
FORMATS_PER_KERNEL = 8
MIN_BANK_SIZE = 800

DIFFICULTY_TO_LEVEL = DIFFICULTY_TO_BLOOM
DOMAIN_REFERENCES = {
    1: "ISC2 CBK Domain 1; NIST SP 800-30; ISO 27001",
    2: "ISC2 CBK Domain 2; NIST SP 800-88",
    3: "ISC2 CBK Domain 3; NIST SP 800-53",
    4: "ISC2 CBK Domain 4; NIST SP 800-207",
    5: "ISC2 CBK Domain 5; NIST SP 800-63",
    6: "ISC2 CBK Domain 6; ISO 27001 A.8",
    7: "ISC2 CBK Domain 7; NIST SP 800-61",
    8: "ISC2 CBK Domain 8; OWASP ASVS",
}


def _tag_to_topic_id() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for topic_id, cfg in TOPIC_SCENARIO_MAP.items():
        for tag in cfg.get("tags", []):
            mapping[tag] = topic_id
    return mapping


_TAG_TOPIC = _tag_to_topic_id()


def _question_meta(spec: dict, domain: int) -> dict:
    tag = spec.get("tag", "")
    topic_id = _TAG_TOPIC.get(tag, tag or spec["topic"][:64])
    diff = spec.get("difficulty", "hard")
    return {
        "topic_id": topic_id,
        "difficulty_level": DIFFICULTY_TO_LEVEL.get(diff, 3),
        "reference": DOMAIN_REFERENCES.get(domain, "ISC2 CBK"),
    }


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
        seed = f"{kernel_idx}-{slot}-{topic[:40]}"
        balanced_correct, balanced_wrong = balance_choice_set(
            spec["correct"], spec["wrong"], domain, seed
        )
        if slot == KNOWLEDGE_SLOT:
            stem = knowledge_stem(topic, seed)
            q_type = "knowledge-check"
        else:
            stem = format_stem(slot, narrative, industry, topic)
            q_type = "scenario"
        ca, cb, cc, cd, correct = shuffle_choices(
            balanced_correct,
            balanced_wrong,
            seed + balanced_correct,
        )
        qid = _qid(domain, seed + spec["correct"])
        tags = f"diverse,manager,{q_type},{BANK_TAG},{spec.get('tag', 'isc2')}"
        meta = _question_meta(spec, domain)
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
            **meta,
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
            **_question_meta(spec, domain),
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
        if len(q["stem"]) < 35 or len(q["stem"]) > 1200:
            continue
        choices = {q["choice_a"], q["choice_b"], q["choice_c"], q["choice_d"]}
        if len(choices) < 4:
            continue
        correct_letter = q["correct_choice"]
        letter_map = {
            "A": q["choice_a"],
            "B": q["choice_b"],
            "C": q["choice_c"],
            "D": q["choice_d"],
        }
        correct_text = letter_map.get(correct_letter, "")
        wrong_texts = [v for k, v in letter_map.items() if k != correct_letter]
        if is_length_giveaway(correct_text, wrong_texts):
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
    """Assemble premium items, scenario + knowledge-check variants, and cheat-sheet knowledge bank."""
    questions: list[dict] = [_tag_premium(dict(q)) for q in PREMIUM_QUESTIONS]

    for idx, spec in enumerate(TOPIC_SPECS):
        questions.extend(_kernel_questions(spec, idx))

    for kq in build_knowledge_questions():
        kq = dict(kq)
        importance = kq.pop("importance", None)
        tags = kq.get("tags", "")
        if importance:
            tags = f"{tags},importance:{importance}"
        kq["tags"] = f"{tags},{BANK_TAG}".strip(",")
        if not kq.get("reference"):
            kq["reference"] = DOMAIN_REFERENCES.get(kq["domain"], "ISC2 CBK")
        kq["difficulty_level"] = DIFFICULTY_TO_LEVEL.get(kq.get("difficulty", "medium"), 3)
        questions.append(kq)

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
