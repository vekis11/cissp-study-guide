"""CISSP-style study guide question bank — direct exam format (150+ items)."""

from __future__ import annotations

import hashlib
import re

from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.data.domains import DOMAIN_NAMES
from app.data.diverse.choice_balance import balance_choice_set
from app.data.diverse.stem_formats import shuffle_choices

STUDY_GUIDE_BANK_TAG = "study-guide-bank-v1"
MIN_STUDY_GUIDE_QUESTIONS = 150

# User-provided reference questions (CISSP direct format)
SEED_QUESTIONS: list[dict] = [
    {
        "id": "sg-seed-001",
        "topic_id": "d6-audit-programs-controls",
        "domain": 6,
        "importance": "high",
        "stem": (
            "Which one of the following factors should NOT be taken into consideration "
            "when planning a security testing schedule for a particular system?"
        ),
        "correct": "Desire to experiment with new testing tools",
        "wrong": [
            "Sensitivity of the information stored on the system",
            "Desirability of the system to attackers",
            "Difficulty of performing the test",
        ],
        "explanation": (
            "Testing schedules should reflect data sensitivity, threat exposure, and feasibility — "
            "not tool experimentation, which is unrelated to risk-based prioritization."
        ),
        "source_topic": "Security Assessment and Testing",
    },
    {
        "id": "sg-seed-002",
        "topic_id": "d3-crypto-basics-symmetric-asymmetric",
        "domain": 3,
        "importance": "must",
        "stem": (
            "John recently received an email message from Bill. "
            "What cryptographic goal would need to be met to convince John that Bill was actually the sender?"
        ),
        "correct": "Nonrepudiation",
        "wrong": ["Confidentiality", "Availability", "Integrity"],
        "explanation": "Nonrepudiation prevents the sender from denying origin — authenticity of sender is the issue here.",
        "source_topic": "Cryptography Basics",
    },
    {
        "id": "sg-seed-003",
        "topic_id": "d1-bcp-bia-rpo-rto",
        "domain": 1,
        "importance": "must",
        "stem": "Joe's Recovery Point Objective (RPO) is set to 24 hours. What does this mean?",
        "correct": "No more than 24 hours of data can be lost.",
        "wrong": [
            "Joe's people must be in the office performing the process 24 hours after a disaster.",
            "Joe has 24 hours to decide what to do in event of an emergency.",
            "All data related to the process must be recovered within 24 hours.",
        ],
        "explanation": "RPO defines the maximum acceptable data loss window — how far back recovery must reach.",
        "source_topic": "BCP, BIA, RPO, and RTO",
    },
    {
        "id": "sg-seed-004",
        "topic_id": "d4-routing-switching-basics",
        "domain": 4,
        "importance": "good",
        "stem": (
            "There are several devices used in LANs, MANs, and WANs that provide communication "
            "between networks and computers. Which device provides the simplest type of connectivity?"
        ),
        "correct": "Repeaters",
        "wrong": ["Switches", "Routers", "Bridges"],
        "explanation": "Repeaters operate at Layer 1 and simply regenerate signals — the simplest connectivity device.",
        "source_topic": "Routing and Switching Basics",
    },
    {
        "id": "sg-seed-005",
        "topic_id": "d2-destruction-remanence",
        "domain": 2,
        "importance": "must",
        "stem": "Which of the following statements correctly identifies a problem with sanitization methods?",
        "correct": "Personnel can perform sanitization steps improperly",
        "wrong": [
            "Even fully incinerated media can offer extractable data",
            "Methods are not available to remove data ensuring unauthorized personnel cannot retrieve data",
            "Stored data is physically etched into the media",
        ],
        "explanation": "Human error in sanitization is a realistic, exam-tested weakness — process and verification matter.",
        "source_topic": "Destruction and Data Remanence",
    },
    {
        "id": "sg-seed-006",
        "topic_id": "d4-firewalls-proxies-waf",
        "domain": 4,
        "importance": "high",
        "stem": "Which type of firewall functions at the Network layer of the OSI Model?",
        "correct": "Packet Filtering Firewall",
        "wrong": [
            "Application-Level Gateway",
            "Circuit-Level Firewall",
            "Network firewall",
        ],
        "explanation": "Packet filters evaluate headers at Layer 3 (Network layer). Application gateways operate higher in the stack.",
        "source_topic": "Firewalls, Proxies, and WAF",
    },
    {
        "id": "sg-seed-007",
        "topic_id": "d1-governance-due-care-diligence",
        "domain": 1,
        "importance": "must",
        "stem": "Which factor is the MOST important item when it comes to ensuring security is successful in an organization?",
        "correct": "Senior management support",
        "wrong": [
            "Effective controls and implementation methods",
            "Updated and relevant security policies and procedures",
            "Security awareness by all employees",
        ],
        "explanation": "Without senior management support, security programs lack authority, budget, and enforcement power.",
        "source_topic": "Governance and Due Care",
    },
    {
        "id": "sg-seed-008",
        "topic_id": "d3-secure-design-principles",
        "domain": 3,
        "importance": "high",
        "stem": (
            "Mr. Green is selecting safeguard mechanisms. "
            "Which attributes should good countermeasures include?"
        ),
        "correct": "Asset protection and testability",
        "wrong": [
            "Asset protection only",
            "Testability only",
            "Neither asset protection nor testability",
        ],
        "explanation": "Effective safeguards protect assets and can be tested to verify they work as intended.",
        "source_topic": "Secure Design Principles",
    },
    {
        "id": "sg-seed-009",
        "topic_id": "d7-control-categories",
        "domain": 7,
        "importance": "must",
        "stem": (
            "Which type of access control uses fences, security policies, security awareness training, "
            "and antivirus software to stop an unwanted or unauthorized activity from occurring?"
        ),
        "correct": "Preventive",
        "wrong": ["Authoritative", "Corrective", "Detective"],
        "explanation": "Preventive controls stop incidents before they occur — fences, policy, training, and AV are preventive.",
        "source_topic": "Security Control Categories",
    },
    {
        "id": "sg-seed-010",
        "topic_id": "d1-risk-formulas-ale",
        "domain": 1,
        "importance": "must",
        "stem": "Mitch is not sure if a risk analysis estimate has been completed. What term is assigned to this situation?",
        "correct": "Uncertainty",
        "wrong": [
            "Scenario Approximation Fear",
            "Scenario Uncertainty Risk",
            "Risk Uncertainty and Risk Fear",
        ],
        "explanation": "Uncertainty exists when reliable data or completed analysis is lacking — a core risk management concept.",
        "source_topic": "Risk Analysis",
    },
    {
        "id": "sg-seed-011",
        "topic_id": "d7-disaster-recovery-sites",
        "domain": 7,
        "importance": "must",
        "stem": (
            "Bob's building burned down. Ken offers Bob use of an empty floor in his building four miles away "
            "under a mutual arrangement. What is this process called?"
        ),
        "correct": "Reciprocal agreements",
        "wrong": ["Trade agreement", "Offsite trading", "Location switching"],
        "explanation": "Reciprocal agreements let organizations share facilities during disasters — informal mutual DR arrangement.",
        "source_topic": "Disaster Recovery Sites",
    },
    {
        "id": "sg-seed-012",
        "topic_id": "d2-classification-labeling",
        "domain": 2,
        "importance": "must",
        "stem": "What is the MOST important aspect of marking media?",
        "correct": "Classification",
        "wrong": [
            "Electronic labeling",
            "Content description",
            "Date labeling",
        ],
        "explanation": "Classification drives handling rules — without it, custodians cannot apply correct protection.",
        "source_topic": "Classification and Labeling",
    },
    {
        "id": "sg-seed-013",
        "topic_id": "d3-crypto-basics-symmetric-asymmetric",
        "domain": 3,
        "importance": "high",
        "stem": "What is an advantage of RSA over DSA?",
        "correct": "It can provide digital signature and encryption functionality.",
        "wrong": [
            "It uses fewer resources and encrypts faster because it uses symmetric keys.",
            "It is a block cipher rather than a stream cipher.",
            "It employs a one-time encryption pad.",
        ],
        "explanation": "RSA supports both encryption and digital signatures; DSA is signature-focused.",
        "source_topic": "Asymmetric Cryptography",
    },
    {
        "id": "sg-seed-014",
        "topic_id": "d7-disaster-recovery-sites",
        "domain": 7,
        "importance": "high",
        "stem": (
            "Becky's company was hit by a tornado. The next day she worked from a nearby facility "
            "and knew the layout as if she had worked there for years. What type of site is this?"
        ),
        "correct": "Hot site",
        "wrong": ["Rolling hot site", "Mirror site", "Redundant site"],
        "explanation": "A hot site is fully configured and can take over quickly — near-immediate operational capability.",
        "source_topic": "Disaster Recovery Sites",
    },
    {
        "id": "sg-seed-015",
        "topic_id": "d1-risk-treatment-options",
        "domain": 1,
        "importance": "high",
        "stem": (
            "What risk can prove to be the MOST detrimental to a company long after the original risk event?"
        ),
        "correct": "Delayed loss",
        "wrong": ["Cascading errors", "Illogical processing", "Immediate loss"],
        "explanation": "Delayed loss surfaces after the event — latent failures and long-tail impacts harm organizations over time.",
        "source_topic": "Risk Treatment",
    },
    {
        "id": "sg-seed-016",
        "topic_id": "d7-lessons-learned-exercises",
        "domain": 7,
        "importance": "must",
        "stem": (
            "Why would an organization need to periodically test disaster recovery and business continuity plans "
            "if they have already been shown to work?"
        ),
        "correct": "Environmental changes may render them ineffective over time.",
        "wrong": [
            "It has low confidence in the abilities of the testers.",
            "To appease senior leadership.",
            "Resources may not be available in the future to test again.",
        ],
        "explanation": "People, systems, and dependencies change — plans must be retested to stay valid.",
        "source_topic": "DR/BCP Testing",
    },
]

_EXTRA_STEMS = (
    "Which of the following is the BEST answer regarding {title}?",
    "Which statement is MOST accurate about {title}?",
    "Which option BEST describes {title}?",
    "Which of the following is correct concerning {title}?",
)


def _qid(topic_id: str, slot: str) -> str:
    digest = hashlib.sha256(f"{topic_id}-{slot}".encode()).hexdigest()[:8]
    return f"sg-{topic_id}-{digest}"


def _pack_question(
    *,
    qid: str,
    topic_id: str,
    domain: int,
    importance: str,
    stem: str,
    correct: str,
    wrong: list[str],
    explanation: str,
    source_topic: str,
    difficulty: str = "medium",
) -> dict:
    balanced_correct, balanced_wrong = balance_choice_set(
        correct, wrong[:3], domain, qid
    )
    ca, cb, cc, cd, letter = shuffle_choices(
        balanced_correct, balanced_wrong, qid
    )
    return {
        "id": qid,
        "topic_id": topic_id,
        "domain": domain,
        "domain_name": DOMAIN_NAMES[domain],
        "importance": importance,
        "difficulty": difficulty,
        "stem": stem.strip(),
        "choice_a": ca,
        "choice_b": cb,
        "choice_c": cc,
        "choice_d": cd,
        "correct_choice": letter,
        "explanation": explanation.strip(),
        "source_topic": source_topic,
        "tags": f"study-guide,knowledge-check,topic:{topic_id},cheat-sheet,{STUDY_GUIDE_BANK_TAG}",
    }


def _seed_to_question(seed: dict) -> dict:
    return _pack_question(
        qid=seed["id"],
        topic_id=seed["topic_id"],
        domain=seed["domain"],
        importance=seed["importance"],
        stem=seed["stem"],
        correct=seed["correct"],
        wrong=seed["wrong"],
        explanation=seed["explanation"],
        source_topic=seed["source_topic"],
    )


def _answer_from_scenario(answer: str, title: str) -> str:
    text = re.sub(r"\s+", " ", answer.strip())
    if len(text) > 140:
        return text[:137].rstrip() + "..."
    return text


def _questions_from_section(section: dict, domain: int) -> list[dict]:
    topic_id = section["topic_id"]
    importance = section.get("importance", "high")
    title = section["title"]
    content = section.get("content", "")
    scenarios = section.get("scenarios") or []
    built: list[dict] = []
    seen_stems: set[str] = set()

    for i, sc in enumerate(scenarios):
        prompt = sc.get("prompt", "").strip()
        answer = sc.get("answer", "").strip()
        if not prompt or "?" not in prompt:
            continue
        stem_key = hashlib.sha256(prompt.encode()).hexdigest()
        if stem_key in seen_stems:
            continue
        seen_stems.add(stem_key)
        correct = _answer_from_scenario(answer, title)
        built.append(
            _pack_question(
                qid=_qid(topic_id, f"sc-{i}"),
                topic_id=topic_id,
                domain=domain,
                importance=importance,
                stem=prompt,
                correct=correct,
                wrong=[],
                explanation=f"This aligns with {title}: {correct}",
                source_topic=title,
            )
        )

    # Second question from content bullets or title template
    for slot, template in enumerate(_EXTRA_STEMS):
        if len(built) >= 2:
            break
        stem = template.format(title=title)
        stem_key = hashlib.sha256(stem.encode()).hexdigest()
        if stem_key in seen_stems:
            continue
        lines = [ln.strip(" -•\t") for ln in content.split("\n") if ln.strip()]
        if lines:
            correct = _answer_from_scenario(lines[0], title)
        else:
            correct = _answer_from_scenario(title, title)
        seen_stems.add(stem_key)
        built.append(
            _pack_question(
                qid=_qid(topic_id, f"gen-{slot}"),
                topic_id=topic_id,
                domain=domain,
                importance=importance,
                stem=stem,
                correct=correct,
                wrong=[],
                explanation=f"Study guide topic: {title}. {correct}",
                source_topic=title,
            )
        )

    return built


def _acronym_questions() -> list[dict]:
    """Extra items from cheat-sheet quick reference acronyms."""
    acronyms = CHEAT_SHEET.get("quick_reference", {}).get("acronyms", [])
    domain_by_topic = {
        "ALE": (1, "d1-risk-formulas-ale", "must"),
        "BIA": (1, "d1-bcp-bia-rpo-rto", "must"),
        "RPO": (1, "d1-bcp-bia-rpo-rto", "must"),
        "RTO": (1, "d1-bcp-bia-rpo-rto", "must"),
        "DR": (7, "d7-disaster-recovery-sites", "must"),
        "DLP": (2, "d2-dlp-drm-watermark", "high"),
        "IAM": (5, "d5-access-control-models", "must"),
        "IR": (7, "d7-incident-response-steps", "must"),
        "MFA": (5, "d5-auth-factors-mfa", "must"),
        "PAM": (5, "d5-pam-secrets-management", "high"),
        "SOAR": (7, "d7-soar-siem-soc-operations", "high"),
    }
    built: list[dict] = []
    for item in acronyms:
        acronym = item["acronym"]
        name = item["name"]
        if acronym not in domain_by_topic:
            continue
        domain, topic_id, importance = domain_by_topic[acronym]
        stem = f"What does the acronym {acronym} stand for in CISSP context?"
        built.append(
            _pack_question(
                qid=_qid(topic_id, f"acr-{acronym}"),
                topic_id=topic_id,
                domain=domain,
                importance=importance,
                stem=stem,
                correct=name,
                wrong=[
                    f"{name} (operational only)",
                    f"Alternate {acronym} definition",
                    f"Legacy {acronym} term",
                ],
                explanation=f"{acronym} means {name}.",
                source_topic=name,
                difficulty="easy",
            )
        )
    return built


def build_study_guide_questions() -> list[dict]:
    """Build 150+ direct-format CISSP study guide questions."""
    questions: list[dict] = []
    seen_ids: set[str] = set()
    seen_stems: set[str] = set()

    for seed in SEED_QUESTIONS:
        q = _seed_to_question(seed)
        stem_key = hashlib.sha256(q["stem"].encode()).hexdigest()
        if q["id"] in seen_ids or stem_key in seen_stems:
            continue
        seen_ids.add(q["id"])
        seen_stems.add(stem_key)
        questions.append(q)

    for block in CHEAT_SHEET["domains"]:
        domain = block["domain"]
        for section in block["sections"]:
            for q in _questions_from_section(section, domain):
                stem_key = hashlib.sha256(q["stem"].encode()).hexdigest()
                if q["id"] in seen_ids or stem_key in seen_stems:
                    continue
                seen_ids.add(q["id"])
                seen_stems.add(stem_key)
                questions.append(q)

    for q in _acronym_questions():
        stem_key = hashlib.sha256(q["stem"].encode()).hexdigest()
        if q["id"] in seen_ids or stem_key in seen_stems:
            continue
        seen_ids.add(q["id"])
        seen_stems.add(stem_key)
        questions.append(q)

    if len(questions) < MIN_STUDY_GUIDE_QUESTIONS:
        raise RuntimeError(
            f"Study guide bank has {len(questions)} questions; need {MIN_STUDY_GUIDE_QUESTIONS}+"
        )
    return questions


def build_knowledge_questions() -> list[dict]:
    """Primary study guide bank (replaces legacy one-question-per-topic builder)."""
    return build_study_guide_questions()
