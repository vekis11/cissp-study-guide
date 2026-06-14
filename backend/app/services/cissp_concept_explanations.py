"""CISSP-aligned concept explanations — grounded in CBK facts for post-answer feedback."""

from __future__ import annotations

import re
from typing import Callable

ConceptRule = tuple[tuple[str, ...], Callable[[str, str], str | None]]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _has_all(combined: str, *needles: str) -> bool:
    return all(n in combined for n in needles)


def _worm_trojan(_correct: str, _stem: str) -> str:
    return (
        "The standard difference between a worm and a Trojan is that worms self-replicate, "
        "whereas Trojans do not. A Trojan horse is anything that sneaks in under the guise of "
        "something else — it may not be a virus itself, but can still carry malicious code with it. "
        "A Trojan typically enters when a user runs what looks like legitimate software. Unlike "
        "viruses and worms, Trojans cannot replicate on their own; they spread when users install "
        "or execute the disguised program. Worms, by contrast, are standalone programs that copy "
        "themselves across networks — often without any user action — by exploiting vulnerabilities "
        "or weak configurations."
    )


def _security_testing_not(_correct: str, _stem: str) -> str:
    return (
        "The sensitivity of information on the system, how attractive the system is to attackers, "
        "and how difficult the test is to perform are all legitimate inputs to a risk-based testing "
        "schedule. Those factors help you prioritize where testing effort protects the business. "
        "A desire to experiment with new testing tools is personal or operational curiosity — it "
        "should not drive when production systems are tested."
    )


def _nonrepudiation_sender(_correct: str, _stem: str) -> str:
    return (
        "If John needs proof that Bill actually sent the message, the cryptographic goal is "
        "nonrepudiation — the sender cannot later deny having sent it. Confidentiality protects "
        "content from unauthorized reading; integrity shows the message was not altered; "
        "availability keeps systems reachable. None of those prove origin the way nonrepudiation does."
    )


def _rpo_meaning(_correct: str, _stem: str) -> str:
    return (
        "Recovery Point Objective (RPO) defines how much data loss the business will accept — "
        "it is a time-based measure of acceptable loss, not how long recovery takes. An RPO of "
        "24 hours means you can afford to lose up to one day of data at most. Recovery Time "
        "Objective (RTO) covers how long restoration may take; RPO covers how far back you must "
        "be able to restore."
    )


def _rto_meaning(_correct: str, _stem: str) -> str:
    return (
        "Recovery Time Objective (RTO) is the maximum acceptable downtime before a process or "
        "system must be restored. It answers how long the business can wait — not how much data "
        "may be lost. RPO addresses data loss tolerance; RTO addresses time to recovery."
    )


def _mfa_factors(_correct: str, _stem: str) -> str:
    return (
        "Multifactor authentication requires two or more different factor types — typically "
        "something you know (password), something you have (token or phone), or something you "
        "are (biometric). Two passwords are still one factor type. Pairing a password with a "
        "mobile authenticator app satisfies MFA because knowledge and possession are both present."
    )


def _rules_of_engagement(_correct: str, _stem: str) -> str:
    return (
        "Rules of engagement define what testers may do, what is off limits, how to escalate, "
        "and who to contact when something goes wrong. Without that written authorization, "
        "penetration testing can cause outages or legal exposure even when the intent is good. "
        "Scan reports, incident plans, and classification policies support security work but do "
        "not replace explicit test authorization."
    )


def _contain_first(_correct: str, _stem: str) -> str:
    return (
        "When active malware is confirmed, the first priority is limiting spread so you can "
        "understand scope without making the problem worse. Public disclosure, full rebuilds, "
        "or calling external parties may be necessary later — but containment protects the rest "
        "of the environment while triage continues."
    )


def _risk_acceptance(_correct: str, _stem: str) -> str:
    return (
        "Risk acceptance is a formal management decision to live with residual risk — documented "
        "and signed by someone with authority to accept it. Ignoring a finding is not acceptance. "
        "Transfer shifts risk (often via insurance or contract); mitigation reduces it; avoidance "
        "eliminates the activity causing the risk."
    )


def _due_diligence_vendor(_correct: str, _stem: str) -> str:
    return (
        "Before sharing data with a third party, due diligence verifies the vendor can protect "
        "it — reviews, questionnaires, evidence of controls, and contractual security requirements. "
        "Marketing claims or speed-to-contract do not replace verifying how the vendor handles "
        "your data and who remains accountable after signature."
    )


def _zero_trust(_correct: str, _stem: str) -> str:
    return (
        "Zero trust removes implicit trust based on network location. Every access request is "
        "verified explicitly and granted least privilege — whether the user came from VPN, office, "
        "or the internet. Segmenting the network helps, but segmentation alone still assumes "
        "trust inside the fence."
    )


def _shared_responsibility(_correct: str, _stem: str) -> str:
    return (
        "In cloud environments, the provider secures the platform — but your organization still "
        "owns data protection, identity configuration, encryption keys, and many application "
        "controls. 'The cloud is certified' does not transfer accountability for your data "
        "to the provider."
    )


def _least_privilege(_correct: str, _stem: str) -> str:
    return (
        "Least privilege means users and systems receive only the access required for their role — "
        "no more. It limits damage from compromised accounts and insider mistakes. Broad admin "
        "rights for convenience violate this principle even when passwords are strong."
    )


def _separation_of_duties(_correct: str, _stem: str) -> str:
    return (
        "Separation of duties splits critical functions so one person cannot complete a sensitive "
        "transaction alone — for example, one person initiates payment and another approves it. "
        "That reduces fraud and error. Giving one super-user every permission defeats the control."
    )


def _hashing_vs_encryption(_correct: str, stem: str) -> str:
    if "password" in _norm(stem) or "password" in _norm(_correct):
        return (
            "Passwords should be stored as one-way hashes, not reversible encryption — so a "
            "database leak does not immediately expose plaintext credentials. Hashing verifies "
            "integrity of a value; encryption protects confidentiality when recovery of the "
            "original is required."
        )
    return (
        "Hashing produces a fixed-length fingerprint used to verify integrity — it is one-way "
        "and not meant to recover the original. Encryption protects confidentiality and can be "
        "reversed with the proper key. Pick hashing when you need to detect change, not hide "
        "recoverable secrets."
    )


def _symmetric_vs_asymmetric(_correct: str, _stem: str) -> str:
    return (
        "Symmetric encryption uses one shared key for both encryption and decryption — fast for "
        "bulk data but key distribution is hard. Asymmetric encryption uses a public/private key "
        "pair — slower but solves secure key exchange and digital signatures. Hybrid systems often "
        "use both."
    )


def _vuln_scan_vs_pentest(_correct: str, _stem: str) -> str:
    return (
        "Vulnerability scanning identifies known weaknesses — often automatically and at scale. "
        "Penetration testing simulates an attacker and may exploit flaws to show real impact. "
        "Scans are broader and more frequent; pentests are deeper, authorized simulations that "
        "require rules of engagement."
    )


def _audit_type2(_correct: str, _stem: str) -> str:
    return (
        "A SOC 2 Type II report evaluates whether controls operated effectively over a period of "
        "time — not just whether they were designed properly on a single day. Type I is design "
        "only at a point in time; Type II gives stronger assurance for ongoing vendor due diligence."
    )


def _hot_warm_cold(_correct: str, _stem: str) -> str:
    return (
        "Hot sites are fully operational mirrors ready for immediate failover. Warm sites have "
        "hardware and connectivity but need data restore and configuration. Cold sites provide "
        "facility and infrastructure only — longest recovery, lowest cost. Match the tier to your "
        "RTO and budget."
    )


def _media_sanitization(_correct: str, _stem: str) -> str:
    return (
        "Media sanitization removes data so it cannot be recovered — methods range from overwriting "
        "to physical destruction depending on classification and reuse plans. Deleting files or "
        "reformatting often leaves recoverable data; sensitive media requires a defined sanitization "
        "method matched to the asset's classification."
    )


def _sql_injection(_correct: str, _stem: str) -> str:
    return (
        "SQL injection happens when untrusted input is concatenated into database queries. "
        "Parameterized queries (prepared statements) separate code from data so user input cannot "
        "change query logic. Input validation helps but parameterized queries are the primary "
        "development control against SQL injection."
    )


def _xss(_correct: str, _stem: str) -> str:
    return (
        "Cross-site scripting (XSS) injects malicious scripts into content viewed by other users. "
        "Output encoding, content security policy, and validating input before it is reflected "
        "in pages reduce XSS risk. Patching alone does not fix flawed input handling in the application."
    )


def _phishing(_correct: str, _stem: str) -> str:
    return (
        "Phishing uses deceptive messages to trick users into revealing credentials or running "
        "malware. Technical controls help, but user awareness training and reporting procedures "
        "are essential because the attack targets human judgment, not just software flaws."
    )


def _dlp(_correct: str, _stem: str) -> str:
    return (
        "Data Loss Prevention monitors and blocks sensitive data from leaving authorized channels — "
        "e-mail, cloud uploads, removable media. It enforces classification handling rules in "
        "real time. Encryption protects data at rest or in transit; DLP focuses on preventing "
        "improper exfiltration."
    )


def _classification_handling(_correct: str, _stem: str) -> str:
    return (
        "Data classification drives how information must be handled — who may access it, how it "
        "may be stored, transmitted, and destroyed. You classify first, then apply controls. "
        "Skipping classification and jumping to a technical control often violates policy for "
        "sensitive data."
    )


def _bcp_vs_drp(_correct: str, _stem: str) -> str:
    return (
        "Business Continuity Planning keeps critical business functions running during disruption. "
        "Disaster Recovery focuses on restoring IT systems and infrastructure. BCP is broader "
        "and business-facing; DRP is a subset that supports BCP when technology fails."
    )


def _change_management(_correct: str, _stem: str) -> str:
    return (
        "Change management ensures modifications are reviewed, approved, tested, and documented "
        "before production — reducing outages and unauthorized drift. Emergency changes still "
        "need retrospective review. Patching or deploying without a controlled process creates "
        "avoidable operational and security risk."
    )


def _static_dynamic_test(_correct: str, _stem: str) -> str:
    return (
        "Static application security testing reviews source code or binaries without running the "
        "program — good for finding flaws early. Dynamic testing exercises the running application "
        "and can find runtime issues static analysis misses. Both belong in a balanced SDLC program."
    )


def _digital_signature(_correct: str, _stem: str) -> str:
    return (
        "A digital signature uses asymmetric cryptography to prove who signed data and whether "
        "it changed after signing — supporting integrity and nonrepudiation. Encryption alone "
        "does not prove origin; hashing alone does not prove who produced the hash."
    )


def _certificate_purpose(_correct: str, _stem: str) -> str:
    return (
        "Digital certificates bind a public key to an identity, verified by a trusted Certificate "
        "Authority. They enable trusted TLS connections and code signing. Self-signed certificates "
        "lack third-party validation and are inappropriate for production trust chains unless "
        "explicitly managed in a private PKI."
    )


def _vlan_purpose(_correct: str, _stem: str) -> str:
    return (
        "VLANs logically segment broadcast domains on a switch — limiting where traffic flows "
        "without requiring separate physical networks. They support defense in depth and policy "
        "enforcement but are not encryption and do not replace firewalls for all traffic control."
    )


def _ids_ips(_correct: str, _stem: str) -> str:
    return (
        "An IDS detects suspicious activity and alerts — it does not block by default. An IPS sits "
        "inline and can block or drop traffic when policy triggers. Detection versus prevention "
        "is the key distinction; both need tuning to balance false positives and missed attacks."
    )


def _tokenization(_correct: str, _stem: str) -> str:
    return (
        "Tokenization replaces sensitive data with a non-sensitive surrogate token — the original "
        "is stored securely elsewhere. Unlike encryption, tokens are not mathematically reversible "
        "without the token vault. It reduces PCI and PII exposure in downstream systems."
    )


def _privacy_gdpr_theme(_correct: str, _stem: str) -> str:
    return (
        "Privacy regulations emphasize lawful basis for processing, data minimization, purpose "
        "limitation, and individual rights such as access and erasure. Security controls support "
        "privacy but compliance also requires governance, notices, and documented processing — "
        "not encryption alone."
    )


def _ai_governance(_correct: str, _stem: str) -> str:
    return (
        "AI and machine learning systems need governance like any high-impact technology — "
        "defined acceptable use, training data boundaries, human oversight for critical decisions, "
        "and monitoring for drift or abuse. Model accuracy alone does not satisfy security and "
        "risk management obligations."
    )


def _self_replicate_malware(_correct: str, _stem: str) -> str:
    return _worm_trojan(_correct, _stem)


# (all keywords must appear in combined stem + correct + topic text)
CONCEPT_RULES: list[ConceptRule] = [
    (("worm", "trojan"), _worm_trojan),
    (("self-replicat", "trojan"), _worm_trojan),
    (("self-replicat", "does not"), _self_replicate_malware),
    (("security testing", "experiment"), _security_testing_not),
    (("testing schedule", "experiment"), _security_testing_not),
    (("planning a security testing", "should not"), _security_testing_not),
    (("nonrepudiation", "sender"), _nonrepudiation_sender),
    (("convince", "actually the sender"), _nonrepudiation_sender),
    (("recovery point objective", "rpo"), _rpo_meaning),
    (("rpo", "24 hour"), _rpo_meaning),
    (("recovery time objective", "rto"), _rto_meaning),
    (("multifactor", "something you know"), _mfa_factors),
    (("multifactor", "authenticator"), _mfa_factors),
    (("rules of engagement", "penetration"), _rules_of_engagement),
    (("rules of engagement", "scope"), _rules_of_engagement),
    (("ransomware", "first"), _contain_first),
    (("malware", "first"), _contain_first),
    (("contain", "spread"), _contain_first),
    (("risk accept", "document"), _risk_acceptance),
    (("residual risk", "accept"), _risk_acceptance),
    (("due diligence", "vendor"), _due_diligence_vendor),
    (("third party", "before sharing"), _due_diligence_vendor),
    (("zero trust", "verify"), _zero_trust),
    (("zero trust", "least privilege"), _zero_trust),
    (("shared responsibility", "cloud"), _shared_responsibility),
    (("cloud", "customer responsibility"), _shared_responsibility),
    (("least privilege", "access"), _least_privilege),
    (("separation of duties", "fraud"), _separation_of_duties),
    (("segregation of duties",), _separation_of_duties),
    (("hash", "password"), _hashing_vs_encryption),
    (("one-way", "hash"), _hashing_vs_encryption),
    (("symmetric", "asymmetric"), _symmetric_vs_asymmetric),
    (("vulnerability scan", "penetration"), _vuln_scan_vs_pentest),
    (("soc 2", "type ii"), _audit_type2),
    (("type ii", "operating effectiveness"), _audit_type2),
    (("hot site", "warm"), _hot_warm_cold),
    (("disaster recovery site", "cold"), _hot_warm_cold),
    (("sanitiz", "media"), _media_sanitization),
    (("sql injection", "parameter"), _sql_injection),
    (("cross-site scripting",), _xss),
    (("xss",), _xss),
    (("phishing", "awareness"), _phishing),
    (("data loss prevention",), _dlp),
    (("classification", "handling"), _classification_handling),
    (("business continuity", "disaster recovery"), _bcp_vs_drp),
    (("change management", "production"), _change_management),
    (("static", "dynamic"), _static_dynamic_test),
    (("digital signature",), _digital_signature),
    (("certificate authority",), _certificate_purpose),
    (("vlan", "segment"), _vlan_purpose),
    (("intrusion detection", "intrusion prevention"), _ids_ips),
    (("tokenization", "pci"), _tokenization),
    (("gdpr", "privacy"), _privacy_gdpr_theme),
    (("data subject", "right"), _privacy_gdpr_theme),
    (("machine learning", "governance"), _ai_governance),
    (("generative ai", "acceptable use"), _ai_governance),
]


def _not_question_fallback(correct: str, stem: str, core: str) -> str:
    if core and len(core) > 40:
        return (
            f"The other options reflect legitimate risk-based planning factors for this decision. "
            f"{core.strip()}"
        )
    return (
        "The other options tie to risk, sensitivity, exposure, feasibility, or due care — "
        "factors a manager should weigh. "
        f"{correct.strip()} is not a professional basis for this decision and should not drive "
        "the schedule or approach."
    )


def _first_question_fallback(correct: str, core: str) -> str:
    lead = core.strip() if core else ""
    if lead:
        return (
            f"{lead} "
            f"That is why {correct.strip()} comes before technical fixes, broad communication, "
            "or external escalation in this scenario."
        )
    return (
        f"{correct.strip()} establishes the foundation the rest of the response depends on — "
        "ownership, scope, or containment before deeper recovery steps."
    )


def _best_question_fallback(correct: str, core: str) -> str:
    if core and len(core) > 40:
        return (
            f"{core.strip()} "
            f"{correct.strip()} is the answer you could defend to leadership, legal, and auditors."
        )
    return (
        f"{correct.strip()} best balances security obligations with business continuity and "
        "managerial accountability in this scenario."
    )


def _generic_fallback(correct: str, core: str) -> str:
    if core and len(core) > 60:
        return core.strip()
    if core:
        return (
            f"{core.strip()} "
            f"That is why {correct.strip()} is the best fit for what the question asks."
        )
    return (
        f"{correct.strip()} directly addresses the requirement in the stem — it reflects sound "
        "CISSP judgment rather than a partial or out-of-sequence response."
    )


def lookup_concept_explanation(
    *,
    stem: str,
    correct_text: str,
    source_topic: str = "",
    domain: int = 1,
    action: str | None = None,
    stored_explanation: str = "",
) -> str:
    """Return a human, CBK-grounded explanation for why the correct choice is right."""
    combined = _norm(f"{stem} {correct_text} {source_topic} domain-{domain}")

    for needles, builder in CONCEPT_RULES:
        if _has_all(combined, *needles):
            result = builder(correct_text, stem)
            if result:
                return result

    core = stored_explanation.strip()
    correct = correct_text.strip()

    if action == "NOT":
        return _not_question_fallback(correct, stem, core)
    if action == "FIRST":
        return _first_question_fallback(correct, core)
    if action in ("BEST", "PRIMARY", "NEXT", "LEAST"):
        return _best_question_fallback(correct, core)
    return _generic_fallback(correct, core)
