"""Direct CISSP scenario questions for the main practice bank — not the study guide."""

from __future__ import annotations

import hashlib
import re

from app.data.domains import DOMAIN_NAMES
from app.data.diverse.choice_balance import balance_choice_set
from app.data.diverse.stem_formats import shuffle_choices
from app.data.diverse.topic_specs import TOPIC_SPECS
from app.services.cissp_exam_rules import stem_has_cissp_action

DIRECT_EXAM_TAG = "direct-exam"

_STEM_CLOSERS = (
    "Which course of action is BEST?",
    "What should the organization do FIRST?",
    "Which response is MOST appropriate?",
    "Which option is LEAST appropriate?",
    "What is the NEXT step?",
    "What is the PRIMARY objective from a security management perspective?",
    "Which control BEST mitigates the risk described?",
    "Which response is MOST effective given the business constraints?",
)

# Scenario-based items — Bloom 3–5, business-first, one BEST answer (main bank only)
CURATED_ITEMS: list[dict] = [
    {
        "domain": 6,
        "topic_id": "d6-pentest-rules-engagement",
        "source_topic": "Security Assessment and Testing",
        "difficulty": "medium",
        "stem": (
            "A global bank scheduled a penetration test during a trading-system freeze window. "
            "Legal has not signed off, and operations is unsure which systems are in scope. "
            "Which document MOST clearly defines scope, forbidden actions, and contact procedures?"
        ),
        "correct": "Rules of engagement",
        "wrong": [
            "The vulnerability scan report from last quarter",
            "The corporate incident response plan",
            "The enterprise data classification policy",
        ],
        "explanation": (
            "Rules of engagement authorize what testers may do, how to escalate, and where to stop. "
            "Without them, testing creates legal exposure and operational outages even when intent is good."
        ),
    },
    {
        "domain": 5,
        "topic_id": "d5-auth-factors-mfa",
        "source_topic": "Authentication factors",
        "difficulty": "medium",
        "stem": (
            "Remote administrators authenticate with passwords and one-time codes from a mobile "
            "authenticator to reach production consoles. Auditors ask whether this meets "
            "multifactor expectations after several credential-theft attempts. "
            "Which description is MOST accurate?"
        ),
        "correct": (
            "Multifactor authentication using something you know and something you have"
        ),
        "wrong": [
            "Single-factor authentication because both steps occur at login",
            "Biometric-only authentication with password fallback disabled",
            "Multifactor authentication using two knowledge factors",
        ],
        "explanation": (
            "Passwords are knowledge; mobile authenticators are possession. Different factor types "
            "are required for MFA — two passwords would not qualify."
        ),
    },
    {
        "domain": 2,
        "topic_id": "d2-classification-handling",
        "source_topic": "Data classification",
        "difficulty": "medium",
        "stem": (
            "A sales analyst needs to e-mail a spreadsheet with customer Social Security numbers "
            "to an external marketing partner for a same-day campaign. The partner says encryption "
            "can wait until tomorrow. Which action should occur FIRST?"
        ),
        "correct": "Verify handling rules for the data's classification level",
        "wrong": [
            "Encrypt the message and send it immediately to meet the campaign deadline",
            "Ask the employee's manager after the e-mail is sent to confirm appropriateness",
            "Upload the file to a password-protected cloud folder and share the link",
        ],
        "explanation": (
            "Classification drives permitted handling, storage, and transmission. Controls must "
            "match sensitivity and contractual obligations — not partner urgency."
        ),
    },
    {
        "domain": 7,
        "topic_id": "d7-incident-response-steps",
        "source_topic": "Incident response",
        "difficulty": "medium",
        "stem": (
            "An organization confirms active ransomware on several workstations in a regional office. "
            "Backups are untested, and executives want updates within the hour. "
            "Which step should generally come FIRST in the response?"
        ),
        "correct": "Contain the spread to limit further impact",
        "wrong": [
            "Publish a full public breach notice to meet transparency expectations",
            "Rebuild every system in the environment before scoping the event",
            "Contact law enforcement before any internal triage begins",
        ],
        "explanation": (
            "Containment limits damage while the team preserves evidence and coordinates notifications. "
            "Communication and recovery follow once scope is understood."
        ),
    },
    {
        "domain": 4,
        "topic_id": "d4-vpn-remote-access",
        "source_topic": "Remote access",
        "difficulty": "medium",
        "stem": (
            "Remote workers connect through VPN tunnels to internal applications that carry "
            "unencrypted legacy protocols. A recent audit flagged data-in-transit exposure on "
            "shared home networks. Which control BEST mitigates the risk described?"
        ),
        "correct": "Encrypting traffic inside the VPN tunnel",
        "wrong": [
            "Disabling split tunneling without implementing any encryption",
            "Using longer usernames for VPN accounts to reduce guessing",
            "Allowing shared VPN credentials for on-call staff to speed access",
        ],
        "explanation": (
            "VPNs protect confidentiality and integrity of data in motion. Policy choices like split "
            "tunneling matter, but encryption is the core control for transit exposure."
        ),
    },
    {
        "domain": 1,
        "topic_id": "d1-risk-treatment",
        "source_topic": "Risk treatment",
        "difficulty": "medium",
        "stem": (
            "Leadership reviewed a critical vendor risk and decided the cost to mitigate exceeds "
            "the plausible loss after insurance and detective controls. They documented the "
            "decision with executive sign-off and monitoring. Which risk treatment option is being applied?"
        ),
        "correct": "Risk acceptance",
        "wrong": ["Risk avoidance", "Risk transfer", "Risk mitigation"],
        "explanation": (
            "Risk acceptance documents a conscious decision to live with residual risk, usually with "
            "executive approval and ongoing monitoring — not passive neglect."
        ),
    },
    {
        "domain": 8,
        "topic_id": "d8-sdlc-security-gates",
        "source_topic": "Secure SDLC",
        "difficulty": "hard",
        "stem": (
            "A development team is one sprint from releasing a customer-facing web application. "
            "Security was invited only for a final scan. Product argues that design reviews would "
            "delay revenue. Which activity should have occurred earlier in the lifecycle?"
        ),
        "correct": "Threat modeling and security requirements during design",
        "wrong": [
            "Penetration testing only after production deployment",
            "Security training for users after go-live",
            "Adding a WAF without reviewing application design",
        ],
        "explanation": (
            "Security built into design is cheaper and more defensible than bolting controls on at release. "
            "Testing complements — but does not replace — early design work."
        ),
    },
    {
        "domain": 4,
        "topic_id": "d4-zero-trust",
        "source_topic": "Zero trust",
        "difficulty": "hard",
        "stem": (
            "After credential theft, an attacker moved laterally inside the corporate network despite "
            "a strong perimeter firewall. The CISO wants to reduce implicit trust for internal "
            "applications. Which principle BEST reflects a zero trust approach?"
        ),
        "correct": (
            "Verify explicitly and grant least privilege for every access request"
        ),
        "wrong": [
            "Trust internal users because they passed the perimeter firewall",
            "Rely on network location alone to authorize access to applications",
            "Disable logging on internal traffic to reduce analyst workload",
        ],
        "explanation": (
            "Zero trust assumes breach and verifies each request regardless of network location. "
            "Perimeter-only trust is the model zero trust replaces."
        ),
    },
    {
        "domain": 3,
        "topic_id": "d3-defense-in-depth",
        "source_topic": "Defense in depth",
        "difficulty": "medium",
        "stem": (
            "A payment processor relies on a single next-generation firewall between the internet "
            "and card-processing systems. Assessors note that bypass would expose unsegmented "
            "back-office tools on the same subnet. Which strategy is MOST appropriate?"
        ),
        "correct": (
            "Layer preventive, detective, and corrective controls so no single failure exposes the environment"
        ),
        "wrong": [
            "Replace the firewall annually to maintain vendor support coverage",
            "Trust encryption at the application layer and remove network monitoring",
            "Allow flat networking internally to simplify incident triage",
        ],
        "explanation": (
            "Defense in depth combines complementary controls so one failure does not collapse "
            "the entire control structure — a core architectural principle."
        ),
    },
    {
        "domain": 6,
        "topic_id": "d6-vulnerability-management",
        "source_topic": "Vulnerability management",
        "difficulty": "hard",
        "stem": (
            "A vulnerability scan shows critical findings on a customer-facing cluster days before "
            "a regulated product launch. Patching requires a weekend outage competitors may exploit "
            "if delayed. Which response is MOST effective given the business constraints?"
        ),
        "correct": (
            "Prioritize remediation by asset criticality and exposure, with documented risk "
            "acceptance for any deferrals"
        ),
        "wrong": [
            "Patch every finding immediately without business impact analysis",
            "Ignore critical findings until after launch because scans are often false positives",
            "Disable vulnerability scanning during launch windows to avoid noise",
        ],
        "explanation": (
            "Testing produces evidence; management must prioritize based on business impact and "
            "exposure. Blind patching or ignoring findings both fail due care."
        ),
    },
]


def _qid(domain: int, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:12]
    return f"de-d{domain}-{h}"


def _normalize_narrative(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if cleaned and cleaned[-1] not in ".?!":
        cleaned += "."
    return cleaned


def _direct_stem_from_spec(spec: dict, idx: int) -> str:
    narrative = _normalize_narrative(spec["narrative"])
    industry = spec["industry"]
    topic = spec["topic"]
    closer = _STEM_CLOSERS[idx % len(_STEM_CLOSERS)]
    variant = idx % 3
    if variant == 0:
        return f"{narrative} {closer}"
    if variant == 1:
        return (
            f"A {industry} organization must address {topic.lower()} under business pressure. "
            f"{narrative} {closer}"
        )
    return (
        f"Executives at a {industry} firm are reviewing {topic.lower()} after repeated control gaps. "
        f"{narrative} {closer}"
    )


def _exam_difficulty(raw: str) -> str:
    """Main bank targets Bloom 3–5 — avoid labeling scenario items as recall-level easy."""
    if raw == "easy":
        return "medium"
    return raw


def _pack_direct_question(
    *,
    qid: str,
    domain: int,
    topic_id: str,
    source_topic: str,
    difficulty: str,
    stem: str,
    correct: str,
    wrong: list[str],
    explanation: str,
    tag: str,
) -> dict | None:
    stem = stem.strip()
    if len(stem) < 80 or not stem_has_cissp_action(stem):
        return None
    difficulty = _exam_difficulty(difficulty)
    seed = qid
    balanced_correct, balanced_wrong = balance_choice_set(correct, wrong, domain, seed)
    ca, cb, cc, cd, letter = shuffle_choices(
        balanced_correct,
        balanced_wrong,
        seed + balanced_correct,
    )
    return {
        "id": qid,
        "domain": domain,
        "domain_name": DOMAIN_NAMES[domain],
        "difficulty": difficulty,
        "stem": stem,
        "choice_a": ca,
        "choice_b": cb,
        "choice_c": cc,
        "choice_d": cd,
        "correct_choice": letter,
        "explanation": explanation.strip(),
        "source_topic": source_topic,
        "topic_id": topic_id,
        "tags": f"diverse,direct-exam,manager,scenario,{DIRECT_EXAM_TAG},{tag}",
    }


def _curated_questions() -> list[dict]:
    built: list[dict] = []
    for i, item in enumerate(CURATED_ITEMS):
        tag = item.get("tag", item["topic_id"])
        q = _pack_direct_question(
            qid=_qid(item["domain"], f"curated-{i}-{item['stem'][:48]}"),
            domain=item["domain"],
            topic_id=item["topic_id"],
            source_topic=item["source_topic"],
            difficulty=item.get("difficulty", "medium"),
            stem=item["stem"],
            correct=item["correct"],
            wrong=item["wrong"],
            explanation=item["explanation"],
            tag=tag,
        )
        if q:
            built.append(q)
    return built


def _spec_questions() -> list[dict]:
    built: list[dict] = []
    for idx, spec in enumerate(TOPIC_SPECS):
        domain = spec["domain"]
        topic_id = spec.get("tag", spec["topic"][:64])
        stem = _direct_stem_from_spec(spec, idx)
        q = _pack_direct_question(
            qid=_qid(domain, f"spec-{idx}-{spec['topic'][:40]}"),
            domain=domain,
            topic_id=topic_id,
            source_topic=spec["topic"],
            difficulty=spec.get("difficulty", "hard"),
            stem=stem,
            correct=spec["correct"],
            wrong=spec["wrong"],
            explanation=spec["explanation"],
            tag=spec.get("tag", "isc2"),
        )
        if q:
            built.append(q)
    return built


def build_direct_exam_questions() -> list[dict]:
    """Build scenario-based CISSP questions for mock and daily practice."""
    questions: list[dict] = []
    seen_stems: set[str] = set()
    for q in _curated_questions() + _spec_questions():
        stem_key = hashlib.sha256(q["stem"].encode()).hexdigest()
        if stem_key in seen_stems:
            continue
        seen_stems.add(stem_key)
        questions.append(q)
    return questions
