"""
Generates 1000+ CISSP-style scenario questions.

Patterns aligned to public exam guidance (ISC2 outline, manager mindset):
- Long vignettes with business context
- FIRST / BEST / MOST / PRIMARY action words
- Leadership answers over technician fixes
- Plausible distractors that fail on governance, scope, or sequence
"""

from __future__ import annotations

import hashlib
import random

from app.data.domains import DOMAIN_NAMES, DOMAIN_WEIGHTS
from app.data.scenario_templates_premium import PREMIUM_QUESTIONS
from app.data.action_words import (
    ACTION_BEST,
    ACTION_FIRST,
    ACTION_LEAST,
    ACTION_NEXT,
    ACTION_PRIORITY,
)

ORG_NAMES = [
    "Meridian Health Systems",
    "GlobalFin Corporation",
    "Pacific Logistics Group",
    "Summit Energy Partners",
    "NovaRetail International",
    "Apex Manufacturing",
    "Horizon Cloud Services",
    "Cascade Insurance Holdings",
    "Vertex Pharmaceuticals",
    "IronBridge Defense Contractors",
    "BlueStar Financial",
    "Northwind Airlines",
    "Sterling Media Group",
    "Quantum Research Labs",
]

ROLE_INTROS = [
    "You are the CISO",
    "You are the security manager",
    "As the senior security leader",
    "In your role as director of information security",
    "You serve as the organization's risk owner for this initiative",
    "You have been asked to advise the executive committee as the most senior security professional",
    "As the person accountable for enterprise security governance",
]

SITUATION_PRESSURES = [
    "The board expects recommendations at next week's meeting.",
    "Regulators have announced an upcoming examination.",
    "A recent audit cited gaps in documented accountability.",
    "An acquisition integration deadline is 90 days away.",
    "Customer contracts include strict security SLAs.",
    "Media attention following a competitor's breach increases executive scrutiny.",
    "Budget is constrained and every control must show business value.",
]

DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
PASS_SCALED = 700
MAX_SCALED = 1000
BANK_TAG = "bank-v5"


def _qid(domain: int, seed: str) -> str:
    h = hashlib.md5(seed.encode()).hexdigest()[:10]
    return f"gen-d{domain}-{h}"


def _good_alternate(good: str, variant: int) -> str:
    """Plausible paraphrases for LEAST-question distractors."""
    alts = [
        good,
        good.rstrip(".") + " with documented executive approval.",
        good.rstrip(".") + " aligned to existing policy and risk appetite.",
        good.rstrip(".") + " after coordinating with legal and business owners.",
    ]
    return alts[variant % len(alts)]


def _adjust_stem_for_action(stem: str, action: str) -> str:
    """Ensure FIRST/NEXT wording matches scenario state."""
    upper = action.upper()
    if "NEXT" in upper and "initial assessment" not in stem.lower():
        marker = " " + action
        if stem.endswith(marker):
            stem = stem[: -len(marker)] + " Initial assessment and triage are complete." + marker
    if ("FIRST" in upper or "BEFORE" in upper) and "initial assessment and triage are complete" in stem.lower():
        stem = stem.replace(" Initial assessment and triage are complete.", "")
    return stem


def _make(
    domain: int,
    topic: str,
    stem: str,
    correct: str,
    distractors: list[str],
    explanation: str,
    difficulty: str = "hard",
    tags: str = "deep-scenario,manager,scenario",
    seed: str = "",
    action: str = "",
) -> dict:
    stem = _adjust_stem_for_action(stem, action)
    correct_answer = correct
    wrong_choices = list(distractors[:3])
    expl = explanation.strip()

    if action and "LEAST" in action.upper():
        # LEAST = pick the worst managerial option; other choices should be reasonable
        worst = wrong_choices[0]
        correct_answer = worst
        wrong_choices = [
            _good_alternate(correct, 0),
            _good_alternate(correct, 1),
            _good_alternate(correct, 2) if len(wrong_choices) > 1 else _good_alternate(correct, 3),
        ]
        expl = (
            f"LEAST appropriate: '{worst}' — it fails governance, ethics, or sequence. "
            + expl
        )

    choices = [correct_answer] + wrong_choices[:3]
    random.Random(seed or stem).shuffle(choices)
    letters = ["A", "B", "C", "D"]
    idx = choices.index(correct_answer)
    full_explanation = expl

    if BANK_TAG not in tags:
        tags = f"{tags},{BANK_TAG}"

    return {
        "id": _qid(domain, seed or stem),
        "domain": domain,
        "domain_name": DOMAIN_NAMES[domain],
        "difficulty": difficulty,
        "tags": tags,
        "stem": stem,
        "choice_a": choices[0],
        "choice_b": choices[1],
        "choice_c": choices[2],
        "choice_d": choices[3],
        "correct_choice": letters[idx],
        "explanation": full_explanation,
        "source_topic": topic,
    }


def _make_least(*args, **kwargs):
    """Alias used by extended templates; LEAST is handled inside _make when action contains LEAST."""
    kwargs.setdefault("action", ACTION_LEAST[0])
    return _make(*args, **kwargs)


def _manager_tip(action: str) -> str:
    a = action.upper()
    if "FIRST" in a or "BEFORE" in a:
        return " CISSP 'FIRST' questions reward assessment, plan activation, or governance steps—not immediate technical fixes."
    if "LEAST" in a:
        return " 'LEAST appropriate' means identify the worst managerial choice—often extreme, out-of-sequence, or unethical."
    if "BEST" in a or "MOST APPROPRIATE" in a:
        return " 'BEST' favors sustainable governance, policy alignment, and broad risk reduction over the fastest technical shortcut."
    if "NEXT" in a:
        return " 'NEXT' assumes an initial step already occurred—choose the logical follow-on, not the first step again."
    if "PRIMARY" in a or "GREATEST" in a:
        return " Focus on the highest-level organizational concern: people, law, governance, then technology."
    return " Think like a CISO: business risk, policy, and process before tools."


def _scenario(org: str, role: str, context: str, action: str, pressure: str = "") -> str:
    parts = [f"{role} at {org}."]
    parts.append(context.strip())
    if pressure:
        parts.append(pressure.strip())
    body = " ".join(parts)
    if not body.endswith("?"):
        body = f"{body} {action.strip()}"
    return body


# --- Domain template builders ---

def _d1_templates() -> list:
    def policy_first(org, role, action, pressure=""):
        ctx = (
            "Business units publish inconsistent security requirements. "
            "Executives want enterprise-wide direction before teams write operational runbooks. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Policy hierarchy", stem,
            "Publish or update the enterprise security policy to establish executive direction, then define standards",
            [
                "Deploy a new SIEM and begin alerting immediately",
                "Write detailed step-by-step procedures for each team without executive approval",
                "Purchase cyber insurance and defer governance documentation",
            ],
            "Manager mindset: policy sets direction first; standards define mandatory bars; procedures follow. "
            "Technology before governance fails the exam's leadership filter.",
            "hard", "deep-scenario,governance,policy,manager", stem, action,
        )

    def risk_acceptance(org, role, action, pressure=""):
        ctx = (
            "After controls are applied, residual risk on a payment platform still exceeds the approved tolerance. "
            "The business wants to launch in two weeks for a contractual deadline. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Risk acceptance", stem,
            "Document residual risk and obtain explicit executive acceptance before launch",
            [
                "Launch silently because controls were already purchased",
                "Transfer all accountability to the vendor without contract updates",
                "Disable monitoring to avoid alerting leadership to the gap",
            ],
            "Residual risk above tolerance requires documented acceptance by appropriate authority—not hope or concealment.",
            "hard", "risk,scenario", stem, action,
        )

    def due_diligence(org, role, action, pressure=""):
        ctx = (
            "Legal is finalizing a contract with a SaaS provider that will process regulated customer data. "
            "The vendor refuses to share audit reports until after signature. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Due diligence", stem,
            "Complete vendor security assessment and contract security clauses before commitment",
            [
                "Sign immediately and assess during due care after go-live",
                "Accept verbal assurances from the sales engineer",
                "Skip review because the vendor is market-leading",
            ],
            "Due diligence is investigation before commitment. Post-signature monitoring is due care.",
            "hard", "vendor,risk,scenario", stem, action,
        )

    def bia_rpo(org, role, action, pressure=""):
        ctx = (
            "The business impact analysis states payroll cannot lose more than 30 minutes of data "
            "and must recover within six hours. Operations proposes nightly backups only. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "BIA/RPO/RTO", stem,
            "Align backup frequency and recovery design to the documented RPO and RTO targets",
            [
                "Approve nightly backups because they are industry common",
                "Focus only on MTD without validating data loss windows",
                "Prioritize WAN bandwidth upgrades before reviewing BIA outputs",
            ],
            "RPO drives backup frequency; RTO drives recovery architecture. Manager answers tie controls to BIA outcomes.",
            "medium", "continuity,bia,scenario", stem, action,
        )

    def ethics_escalation(org, role, action, pressure=""):
        ctx = (
            "An executive asks you to withhold a confirmed breach from regulators until after a shareholder meeting. "
            "Legal has not yet been engaged. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "ISC2 Ethics", stem,
            "Escalate through proper channels, engage legal counsel, and follow lawful breach notification obligations",
            [
                "Agree to delay all disclosure indefinitely",
                "Delete forensic evidence to reduce liability",
                "Publicly disclose details before internal containment",
            ],
            "Ethics and law outrank loyalty. The CISSP canon prioritizes society, lawful conduct, and proper escalation.",
            "hard", "ethics,scenario", stem, action,
        )

    def legal_hold(org, role, action, pressure=""):
        ctx = (
            "Litigation hold notices were issued yesterday. "
            "IT schedules routine destruction of email archives per retention policy tonight. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Legal hold", stem,
            "Suspend routine destruction for affected data and notify custodians of preservation duties",
            [
                "Proceed with deletion to save storage costs",
                "Delete only executive mailboxes",
                "Wait until court orders explicit system locks",
            ],
            "Legal hold overrides routine retention destruction schedules.",
            "medium", "legal,governance,scenario", stem, action,
        )

    def risk_transfer(org, role, action, pressure=""):
        ctx = (
            "A legacy manufacturing system cannot be patched before a critical production season. "
            "Finance asks whether insurance can address the exposure. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Risk treatment", stem,
            "Evaluate risk transfer alongside compensating controls, documented acceptance, and a remediation timeline",
            [
                "Ignore the vulnerability because insurance exists",
                "Shut down the plant permanently without business analysis",
                "Install host IPS and declare zero residual risk",
            ],
            "Insurance is transfer, not elimination. Managers document residual risk and compensating controls.",
            "medium", "risk,scenario", stem, action,
        )

    def governance_board(org, role, action, pressure=""):
        ctx = (
            "Internal audit finds policies exist but control enforcement is inconsistent and unmeasured. "
            "The board requests a plan. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Governance", stem,
            "Present a governance improvement plan with accountability, metrics, and enforcement mechanisms",
            [
                "Purchase a GRC tool and assign no owners",
                "Replace policies with informal chat guidance",
                "Focus only on penetration testing next quarter",
            ],
            "Governance failures require oversight, accountability, and measurable enforcement—not tools alone.",
            "hard", "governance,scenario", stem, action,
        )

    specs = [
        (policy_first, "with_least"),
        (risk_acceptance, "with_next"),
        (due_diligence, "first_best"),
        (bia_rpo, "standard"),
        (ethics_escalation, "first_best"),
        (legal_hold, "standard"),
        (risk_transfer, "standard"),
        (governance_board, "with_least"),
    ]
    return specs


def _d2_templates() -> list:
    def owner_vs_custodian(org, role, action, pressure=""):
        ctx = "A new analytics dataset contains PHI and financial records. Teams disagree on who sets sensitivity labels. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Data roles", stem,
            "Have the business data owner define classification and handling requirements for custodians to implement",
            [
                "Let IT administrators choose labels informally",
                "Apply Public classification to simplify sharing",
                "Defer classification until after production deployment",
            ],
            "Owners assign classification; custodians implement. This accountability split is classic CISSP.",
            "medium", "data,roles,scenario", stem, action,
        )

    def sanitization(org, role, action, pressure=""):
        ctx = "Thousands of SSDs from decommissioned clinical workstations must be reused in a lower-trust lab. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Sanitization", stem,
            "Apply purge or destroy methods per policy for the sensitivity level and verify effectiveness",
            [
                "Quick format drives because lab use is internal",
                "Relabel drives as unclassified without wiping",
                "Donate hardware to charity without documentation",
            ],
            "High-sensitivity media requires strong sanitization with verification—not quick formats.",
            "hard", "sanitization,scenario", stem, action,
        )

    def privacy_minimization(org, role, action, pressure=""):
        ctx = "Marketing proposes collecting full browsing history from all visitors 'for future campaigns.' "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Privacy", stem,
            "Limit collection to data necessary for a documented purpose with retention and transparency controls",
            [
                "Approve unlimited retention for analytics flexibility",
                "Merge datasets without review to improve targeting",
                "Disable privacy notices to reduce friction",
            ],
            "Minimization and purpose limitation are manager-level privacy decisions.",
            "medium", "privacy,scenario", stem, action,
        )

    def remanence(org, role, action, pressure=""):
        ctx = "Laptops were wiped, but backups and VM snapshots still contain the same regulated data. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Data remanence", stem,
            "Extend sanitization and inventory to all copies including backups, snapshots, and replicas",
            [
                "Certify laptops clean and ignore offline copies",
                "Encrypt snapshots and skip disposal review",
                "Delete active files only on primary storage",
            ],
            "Data remanence includes copies in backups and snapshots—sanitization must be comprehensive.",
            "hard", "sanitization,scenario", stem, action,
        )

    return [
        (owner_vs_custodian, "standard"),
        (sanitization, "standard"),
        (privacy_minimization, "standard"),
        (remanence, "standard"),
    ]


def _d3_templates() -> list:
    def shared_responsibility(org, role, action, pressure=""):
        ctx = "The organization adopts IaaS for customer-facing APIs. Developers assume the cloud provider handles all patching. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Cloud shared responsibility", stem,
            "Define and communicate customer responsibilities for OS, application, and IAM configuration per the IaaS model",
            [
                "Accept provider responsibility for guest OS and application code",
                "Disable logging to reduce shared responsibility",
                "Move to SaaS to eliminate all customer duties",
            ],
            "IaaS leaves substantial customer responsibility—managers clarify boundaries, not assume total provider ownership.",
            "hard", "cloud,scenario", stem, action,
        )

    def defense_in_depth(org, role, action, pressure=""):
        ctx = "Architecture relies on a single perimeter firewall. Red team lateral movement succeeded after one phishing compromise. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Defense in depth", stem,
            "Recommend layered controls including segmentation, monitoring, and least privilege to limit blast radius",
            [
                "Replace the firewall with a newer model only",
                "Block all outbound traffic permanently",
                "Remove admin rights from security team for safety",
            ],
            "Single-layer designs violate defense in depth—managers choose sustainable layered strategy.",
            "medium", "architecture,scenario", stem, action,
        )

    def zero_trust(org, role, action, pressure=""):
        ctx = "Remote work expanded; VPN grants broad internal access once authenticated. Auditors cite excessive trust on internal networks. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Zero trust", stem,
            "Adopt verify-explicitly access for each resource regardless of network location",
            [
                "Expand flat network zones for performance",
                "Trust all corporate-managed devices implicitly",
                "Disable MFA on internal applications",
            ],
            "Zero trust removes implicit network trust—policy and architecture decision, not a single product.",
            "hard", "cloud,zero-trust,scenario", stem, action,
        )

    def crypto_integrity(org, role, action, pressure=""):
        ctx = "Customers download software updates over the internet and report tampering concerns. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Crypto goals", stem,
            "Implement code signing with trusted PKI and integrity verification for distribution channels",
            [
                "Use symmetric encryption alone on installer files",
                "Obfuscate filenames instead of signing binaries",
                "Rely on TLS without integrity checks at rest",
            ],
            "Integrity and authenticity for downloads require hashing/signing with PKI—not secrecy alone.",
            "medium", "crypto,scenario", stem, action,
        )

    return [
        (shared_responsibility, "standard"),
        (defense_in_depth, "standard"),
        (zero_trust, "standard"),
        (crypto_integrity, "standard"),
    ]


def _d4_templates() -> list:
    def segmentation(org, role, action, pressure=""):
        ctx = "Internet-facing web tier has direct routes to internal database VLANs. Recent IR found rapid lateral movement. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            4, "Segmentation", stem,
            "Design DMZ and internal segmentation to isolate public services from sensitive systems",
            [
                "Increase firewall logging without topology changes",
                "Add WAF only on marketing sites",
                "Flatten VLANs to simplify routing",
            ],
            "Segmentation limits blast radius—architectural decision aligned to business continuity.",
            "hard", "network,scenario", stem, action,
        )

    def wireless(org, role, action, pressure=""):
        ctx = "Employees use a single pre-shared key for corporate Wi-Fi across 40 sites. Rogue AP incidents increased. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            4, "Wireless enterprise", stem,
            "Implement enterprise 802.1X authentication with centralized RADIUS and rogue monitoring",
            [
                "Rotate the PSK monthly and share via email",
                "Disable wireless entirely without alternative access",
                "Hide SSID broadcast and keep open guest access on same LAN",
            ],
            "Enterprise wireless requires strong authentication—802.1X/RADIUS, not shared PSK at scale.",
            "medium", "wireless,scenario", stem, action,
        )

    def ddos(org, role, action, pressure=""):
        ctx = "A volumetric attack saturates internet links during peak sales. Server patching alone does not restore service. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            4, "DDoS", stem,
            "Engage upstream scrubbing/CDN/ISP mitigation aligned to business continuity priorities",
            [
                "Reboot web servers repeatedly",
                "Block all international traffic permanently without analysis",
                "Increase database CPU capacity only",
            ],
            "Volumetric DDoS requires network-level response—manager coordinates providers, not just server tuning.",
            "hard", "ddos,scenario", stem, action,
        )

    return [
        (segmentation, "standard"),
        (wireless, "with_least"),
        (ddos, "standard"),
    ]


def _d5_templates() -> list:
    def leaver(org, role, action, pressure=""):
        ctx = "Audit finds 200 contractor VPN accounts active after projects ended. Help desk cites manual process gaps. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "Account lifecycle", stem,
            "Implement joiner-mover-leaver provisioning tied to HR with periodic access recertification",
            [
                "Reset passwords annually for inactive contractors",
                "Convert contractors to shared admin accounts",
                "Disable MFA to speed deprovisioning",
            ],
            "Orphan accounts are governance failures—process and IAM lifecycle fixes beat one-time cleanup.",
            "hard", "iam,lifecycle,scenario", stem, action,
        )

    def sod(org, role, action, pressure=""):
        ctx = "The same analyst can create vendors, approve invoices, and initiate ACH transfers in the ERP system. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "Separation of duties", stem,
            "Redesign roles so no single individual controls end-to-end payment fraud paths",
            [
                "Apply least privilege but keep all duties on one role",
                "Monitor logs after fraud occurs",
                "Increase password length requirements only",
            ],
            "SoD prevents end-to-end control by one person—distinct from least privilege alone.",
            "medium", "sod,scenario", stem, action,
        )

    def federation(org, role, action, pressure=""):
        ctx = "Partner employees need access to your customer portal using their home organization credentials. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "Federation", stem,
            "Establish federated identity trust with defined attributes, provisioning, and audit requirements",
            [
                "Issue local passwords to every partner user",
                "Share a single service account for the partner",
                "Disable authentication for partner APIs",
            ],
            "Cross-org identity requires federation patterns with governance—not shared local accounts.",
            "medium", "federation,scenario", stem, action,
        )

    def pam(org, role, action, pressure=""):
        ctx = "Administrators share root credentials for critical cloud tenants. Session activity is not recorded. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "PAM", stem,
            "Deploy privileged access management with vaulting, session monitoring, and break-glass procedures",
            [
                "Email root passwords to on-call engineers",
                "Remove admin rights from security team",
                "Store credentials in a shared spreadsheet with encryption",
            ],
            "PAM protects elevated access sustainably—manager selects process and tooling with oversight.",
            "hard", "pam,scenario", stem, action,
        )

    return [
        (leaver, "with_least"),
        (sod, "with_least"),
        (federation, "standard"),
        (pam, "with_least"),
    ]


def _d6_templates() -> list:
    def pentest_auth(org, role, action, pressure=""):
        ctx = "A consultant offers to 'quickly scan' production tonight without written approval to impress leadership. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            6, "Assessment authorization", stem,
            "Require defined scope, rules of engagement, and explicit authorization before any testing",
            [
                "Allow scanning because it finds vulnerabilities faster",
                "Run scans secretly to avoid business disruption",
                "Defer authorization until after findings are delivered",
            ],
            "Unauthorized testing fails ethics and process—authorization precedes assessment.",
            "medium", "assessment,ethics,scenario", stem, action,
        )

    def sast_dast(org, role, action, pressure=""):
        ctx = "Release is two weeks away; developers want security testing only in production after go-live. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            6, "SAST/DAST timing", stem,
            "Integrate static and dynamic testing earlier in the pipeline with staging validation before production",
            [
                "Rely on annual penetration tests only",
                "Disable DAST to meet schedule",
                "Test only third-party libraries after breach",
            ],
            "Shift-left testing reduces cost and risk—manager balances delivery with staged assessment.",
            "hard", "sast,dast,scenario", stem, action,
        )

    def vuln_priority(org, role, action, pressure=""):
        ctx = "Scanner reports 400 critical findings. Only 20 assets are internet-facing with sensitive data. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            6, "Vulnerability prioritization", stem,
            "Prioritize remediation based on exposure, asset value, and compensating controls—not CVSS alone",
            [
                "Patch every finding in numeric order regardless of exposure",
                "Ignore non-production findings entirely",
                "Publish the raw scan to all employees",
            ],
            "Context-driven prioritization reflects managerial risk judgment.",
            "medium", "vuln mgmt,scenario", stem, action,
        )

    return [
        (pentest_auth, "first_best"),
        (sast_dast, "with_next"),
        (vuln_priority, "with_next"),
    ]


def _d7_templates() -> list:
    def ir_first(org, role, action, pressure=""):
        ctx = "Ransomware is encrypting file shares; help desk reports widespread user alerts; executives demand immediate recovery. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "Incident response", stem,
            "Activate the IR plan, contain spread, preserve evidence, and escalate per documented procedures",
            [
                "Pay ransom immediately without analysis",
                "Wipe all systems before documenting indicators",
                "Disable all logging to reduce noise",
            ],
            "FIRST in IR: follow plan, contain, preserve evidence as appropriate—avoid panic actions.",
            "hard", "ir,scenario", stem, action,
        )

    def change_emergency(org, role, action, pressure=""):
        ctx = "Production outage requires an emergency patch. Engineers want to bypass all change records. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "Change management", stem,
            "Authorize emergency change with documented approval, back-out plan, and post-implementation review",
            [
                "Apply patch with no records to restore service fastest",
                "Wait for next CAB meeting in two weeks",
                "Rollback monitoring instead of fixing root cause",
            ],
            "Emergency changes still require control and documentation—speed with accountability.",
            "medium", "change,scenario", stem, action,
        )

    def backup(org, role, action, pressure=""):
        ctx = "Backups exist but restores have not been tested in 18 months. Ransomware risk increased. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "Backup testing", stem,
            "Implement regular restore testing with immutable/offsite copies aligned to RPO/RTO",
            [
                "Increase backup frequency without test restores",
                "Store backups on same production SAN only",
                "Delete old backups to save costs immediately",
            ],
            "Untested backups are assumptions—managers mandate verified recovery capability.",
            "medium", "backup,scenario", stem, action,
        )

    def evidence(org, role, action, pressure=""):
        ctx = "Legal may pursue action after a suspected insider theft. IT plans to reimage laptops tonight. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "Evidence preservation", stem,
            "Preserve volatile and persistent evidence following chain-of-custody before destructive remediation",
            [
                "Reimage immediately to remove malware",
                "Copy files to USB without logging handlers",
                "Delete logs to protect employee privacy",
            ],
            "Evidence preservation and chain of custody precede destructive actions when legal outcome matters.",
            "hard", "ir,evidence,scenario", stem, action,
        )

    return [
        (ir_first, "first_best"),
        (change_emergency, "standard"),
        (backup, "with_next"),
        (evidence, "first_best"),
    ]


def _d8_templates() -> list:
    def shift_left(org, role, action, pressure=""):
        ctx = "Security reviews occur only at release gate; recurring OWASP flaws appear late and delay launches. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "Shift-left SDLC", stem,
            "Embed threat modeling, requirements, and security testing throughout the SDLC",
            [
                "Hire more QA testers at release only",
                "Block all open-source libraries permanently",
                "Remove developer access to staging",
            ],
            "Shift-left reduces cost of flaws—process integration, not a final gate alone.",
            "medium", "sdlc,scenario", stem, action,
        )

    def broken_access(org, role, action, pressure=""):
        ctx = "API users change object IDs in URLs to access other customers' records. UI hides buttons but server checks are weak. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "Broken access control", stem,
            "Enforce server-side authorization on every request for each object",
            [
                "Hide unauthorized buttons in the mobile app",
                "Add CAPTCHA to login only",
                "Increase TLS cipher strength",
            ],
            "Authorization must be enforced server-side—UI hiding is not a control.",
            "hard", "owasp,api,scenario", stem, action,
        )

    def devsecops(org, role, action, pressure=""):
        ctx = "Developers bypass pipeline gates to meet sprint commitments; secrets appear in repositories. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "DevSecOps", stem,
            "Automate security gates in CI/CD with secret scanning, policy enforcement, and fast feedback",
            [
                "Email developers not to commit secrets",
                "Disable pipelines to prevent bypass",
                "Accept risk until next major version",
            ],
            "DevSecOps integrates security into delivery with automation—cultural and process leadership.",
            "hard", "devsecops,scenario", stem, action,
        )

    def ai_governance(org, role, action, pressure=""):
        ctx = "Teams deploy generative AI tools using customer data without review. Legal and privacy are unaware. "
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "AI governance", stem,
            "Establish approved AI use cases, data handling rules, and legal/privacy review before deployment",
            [
                "Allow unrestricted AI usage for innovation speed",
                "Ban all AI without alternative workflow planning",
                "Store all prompts in public repositories for transparency",
            ],
            "AI governance is a leadership decision—policy and review before widespread deployment.",
            "hard", "ai,governance,scenario", stem, action,
        )

    return [
        (shift_left, "standard"),
        (broken_access, "standard"),
        (devsecops, "standard"),
        (ai_governance, "first_best"),
    ]


ACTION_MODES = {
    "standard": ACTION_BEST + ACTION_FIRST + ACTION_PRIORITY,
    "first_best": ACTION_BEST + ACTION_FIRST,
    "with_least": ACTION_BEST + ACTION_FIRST + ACTION_LEAST,
    "with_next": ACTION_BEST + ACTION_FIRST + ACTION_NEXT,
    "least_only": ACTION_LEAST,
    "next_only": ACTION_NEXT,
}


def _actions_for_mode(mode: str) -> list[str]:
    return ACTION_MODES.get(mode, ACTION_MODES["standard"])


def _collect_builders(domain: int) -> list[tuple]:
    from app.data.scenario_templates_extended import EXTENDED_BY_DOMAIN

    specs = list(DOMAIN_BUILDERS[domain]())
    if domain in EXTENDED_BY_DOMAIN:
        specs.extend(EXTENDED_BY_DOMAIN[domain]())
    return specs


DOMAIN_BUILDERS = {
    1: _d1_templates,
    2: _d2_templates,
    3: _d3_templates,
    4: _d4_templates,
    5: _d5_templates,
    6: _d6_templates,
    7: _d7_templates,
    8: _d8_templates,
}


def generate_all_questions(min_total: int = 1050) -> list[dict]:
    """Generate at least min_total unique CISSP-style scenario questions weighted by domain."""
    per_domain_target = {d: max(int(min_total * DOMAIN_WEIGHTS[d]), 100) for d in DOMAIN_NAMES}
    questions: list[dict] = [_tag_premium(q) for q in PREMIUM_QUESTIONS]
    seen_ids: set[str] = {q["id"] for q in questions}
    seen_stems: set[str] = set()

    for domain, target in per_domain_target.items():
        premium_count = sum(1 for q in questions if q["domain"] == domain)
        needed = max(target - premium_count, 0)
        if needed == 0:
            continue

        specs = _collect_builders(domain)
        idx = 0
        added = 0
        attempts = 0
        max_attempts = needed * 25

        while added < needed and attempts < max_attempts:
            builder, mode = specs[idx % len(specs)]
            actions = _actions_for_mode(mode)
            org = ORG_NAMES[idx % len(ORG_NAMES)]
            role = ROLE_INTROS[(idx // len(ORG_NAMES)) % len(ROLE_INTROS)]
            action = actions[idx % len(actions)]
            pressure = SITUATION_PRESSURES[idx % len(SITUATION_PRESSURES)] if idx % 2 == 0 else ""
            seed = f"{domain}-{idx}-{org}-{action}-{pressure}"

            q = builder(org, role, action, pressure)
            idx += 1
            attempts += 1

            if q["id"] in seen_ids:
                continue
            stem_key = q["stem"][:200]
            if stem_key in seen_stems:
                continue
            if not _validate_question(q, action):
                continue

            seen_ids.add(q["id"])
            seen_stems.add(stem_key)
            questions.append(q)
            added += 1

    return questions


def _tag_premium(q: dict) -> dict:
    tags = q.get("tags", "")
    if BANK_TAG not in tags:
        q = {**q, "tags": f"{tags},{BANK_TAG}" if tags else BANK_TAG}
    return q


def _validate_question(q: dict, action: str) -> bool:
    """Reject incoherent or malformed items."""
    stem = q.get("stem", "")
    if len(stem) < 80 or len(stem) > 900:
        return False
    if stem.count("?") > 2:
        return False
    choices = {q["choice_a"], q["choice_b"], q["choice_c"], q["choice_d"]}
    if len(choices) < 4:
        return False
    return True


def get_all_questions() -> list[dict]:
    return generate_all_questions(1050)
