"""Additional CISSP scenario templates — distinct topics, manager-level reasoning."""

from app.data.scenario_generator import _make, _scenario


def _d1_extended():
    def security_awareness_program(org, role, action, pressure=""):
        ctx = (
            "Phishing click rates remain high despite email filtering. "
            "Executives want measurable improvement without blocking business email. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Security awareness", stem,
            "Implement a continuous awareness program with role-based training, simulated phishing metrics, and executive reporting",
            [
                "Terminate employees who fail one simulation",
                "Disable external email for all users",
                "Deploy a second email gateway without changing training",
            ],
            "Sustained human-risk reduction requires ongoing awareness with metrics—not punishment or blocking alone.",
            "medium", "awareness,scenario", stem, action,
        )

    def intellectual_property(org, role, action, pressure=""):
        ctx = (
            "Engineering teams share source code with offshore contractors under NDAs, "
            "but data loss prevention alerts show code in personal cloud storage. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Intellectual property", stem,
            "Review contractual controls, enforce handling requirements, and align DLP with data classification policy",
            [
                "Trust NDAs alone without technical or process enforcement",
                "Block all cloud storage company-wide without business review",
                "Publish the source code internally to reduce external sharing",
            ],
            "IP protection combines legal agreements with classification, DLP, and governance—not trust alone.",
            "medium", "ip,governance,scenario", stem, action,
        )

    def business_continuity_plan(org, role, action, pressure=""):
        ctx = (
            "The BCP has not been updated since a major cloud migration. "
            "Last year's tabletop exercise failed because contact lists were outdated. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "BCP maintenance", stem,
            "Update the BCP, validate contact and dependency data, and schedule tested exercises aligned to critical processes",
            [
                "Store the old BCP in a shared drive and hope staff remember it",
                "Purchase generator fuel without reviewing process priorities",
                "Defer BCP work until after the next real disaster",
            ],
            "BCP value requires current plans, validated contacts, and tested exercises.",
            "medium", "bcp,scenario", stem, action,
        )

    def threat_modeling_program(org, role, action, pressure=""):
        ctx = (
            "The board asks how security prioritization is justified for new digital products. "
            "Teams currently react to findings after release. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            1, "Threat modeling governance", stem,
            "Establish enterprise risk assessment and threat modeling requirements before major system deployment",
            [
                "Run annual penetration tests only and skip design-phase review",
                "Accept vendor SOC 2 reports as sufficient for all products",
                "Block all new features until a single tool scan passes",
            ],
            "Governance-level risk assessment and threat modeling justify controls before deployment.",
            "hard", "risk,threat-model,scenario", stem, action,
        )

    return [
        (security_awareness_program, "standard"),
        (intellectual_property, "standard"),
        (business_continuity_plan, "standard"),
        (threat_modeling_program, "standard"),
    ]


def _d2_extended():
    def data_retention(org, role, action, pressure=""):
        ctx = (
            "Legal requires seven-year retention for financial records, "
            "but operations wants indefinite storage 'for analytics.' "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Retention", stem,
            "Define retention schedules by classification with legal hold exceptions and secure disposal at end of life",
            [
                "Keep all data forever in the data lake",
                "Delete records whenever storage costs increase",
                "Let each team set retention informally",
            ],
            "Retention follows legal and business requirements with defined disposal—not unlimited hoarding.",
            "medium", "retention,scenario", stem, action,
        )

    def tokenization(org, role, action, pressure=""):
        ctx = (
            "The payment team wants to reduce PCI scope on a custom billing application "
            "that currently stores primary account numbers in the application database. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Tokenization", stem,
            "Use tokenization or point-to-point encryption so sensitive card data is not stored in the application environment",
            [
                "Encrypt PANs in the same database with a static key",
                "Mask PANs on screen only while keeping full values in the database",
                "Move PAN storage to a spreadsheet on a secured share",
            ],
            "Scope reduction requires not storing CHD—or using validated tokenization/P2PE—not display masking alone.",
            "hard", "pci,tokenization,scenario", stem, action,
        )

    def media_destruction(org, role, action, pressure=""):
        ctx = (
            "A data center decommission includes magnetic tapes labeled 'Confidential — HR.' "
            "Facilities plans to sell the tape library to a recycler. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            2, "Media destruction", stem,
            "Verify sanitization or destruction methods against classification policy and obtain a certificate of destruction",
            [
                "Sell tapes to the highest bidder after a quick erase command",
                "Relabel tapes as unclassified and reuse internally",
                "Store tapes in a locked closet indefinitely",
            ],
            "Sensitive media requires verified destruction with documentation per sanitization standards.",
            "medium", "sanitization,scenario", stem, action,
        )

    return [
        (data_retention, "standard"),
        (tokenization, "standard"),
        (media_destruction, "standard"),
    ]


def _d3_extended():
    def side_channel(org, role, action, pressure=""):
        ctx = (
            "A crypto review notes potential side-channel exposure in a custom HSM integration. "
            "Developers suggest ignoring it because TLS protects data in transit. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Side-channel risk", stem,
            "Assess implementation against validated modules and address side-channel weaknesses in the cryptographic design",
            [
                "Rely on TLS alone and skip HSM implementation review",
                "Replace AES with a proprietary algorithm",
                "Disable HSM logging to reduce audit findings",
            ],
            "Side-channel and implementation flaws are architectural—TLS in transit does not fix weak crypto implementation.",
            "hard", "crypto,scenario", stem, action,
        )

    def secure_sdlc_gates(org, role, action, pressure=""):
        ctx = (
            "Production releases bypass architecture review when deadlines slip. "
            "Two outages traced to unsigned configuration changes. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Secure architecture governance", stem,
            "Require architecture and security sign-off with exception tracking before production promotion",
            [
                "Remove reviews entirely to meet sprint velocity",
                "Allow developers to self-approve all architecture changes",
                "Scan production weekly instead of reviewing design",
            ],
            "Governance gates enforce accountability before production—not post-incident scanning alone.",
            "medium", "architecture,governance,scenario", stem, action,
        )

    def physical_cloud(org, role, action, pressure=""):
        ctx = (
            "You colocate equipment in a provider facility. "
            "Audit finds vendor staff can access your cage without dual control during maintenance windows. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            3, "Physical security — colocation", stem,
            "Contractually require escorted access, logging, and alignment with your physical security policy for colocation",
            [
                "Accept vendor verbal assurance that access is monitored",
                "Remove all servers from the cage to avoid the issue",
                "Rely on encryption and ignore physical access gaps",
            ],
            "Physical controls at colocation remain your governance responsibility via contract and verification.",
            "medium", "physical,cloud,scenario", stem, action,
        )

    return [
        (side_channel, "standard"),
        (secure_sdlc_gates, "standard"),
        (physical_cloud, "standard"),
    ]


def _d4_extended():
    def dns_security(org, role, action, pressure=""):
        ctx = (
            "Customers report redirects to look-alike domains during online checkout. "
            "DNS changes were not detected by monitoring. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            4, "DNS security", stem,
            "Implement DNSSEC where feasible, monitor authoritative DNS changes, and use registrar locks with MFA",
            [
                "Increase TTL values to reduce DNS query load only",
                "Block all DNS traffic at the firewall",
                "Rotate web server TLS certificates only",
            ],
            "DNS integrity and hijack detection require DNS-specific controls—not generic TLS or firewall changes.",
            "hard", "dns,scenario", stem, action,
        )

    def remote_access_vpn(org, role, action, pressure=""):
        ctx = (
            "Remote engineers use split tunnel VPN. "
            "IR found malware on home networks pivoting through VPN sessions to internal tools. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            4, "Remote access", stem,
            "Reassess VPN posture with device health checks, least-privilege access, and monitoring for anomalous session behavior",
            [
                "Disable VPN permanently without remote work alternatives",
                "Grant full internal network access to speed troubleshooting",
                "Remove MFA because VPN already encrypts traffic",
            ],
            "Remote access risk is managed through posture assessment and least privilege—not unlimited tunnel trust.",
            "medium", "vpn,remote,scenario", stem, action,
        )

    return [
        (dns_security, "standard"),
        (remote_access_vpn, "standard"),
    ]


def _d5_extended():
    def rbac_abac(org, role, action, pressure=""):
        ctx = (
            "Static RBAC roles multiply as partners onboard. "
            "Help desk spends hours mapping exceptions for contractors with time-bound project access. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "RBAC vs ABAC", stem,
            "Evaluate attribute-based or policy-driven access for dynamic contexts while retaining RBAC for stable roles",
            [
                "Create a unique role for every individual user permanently",
                "Grant domain admin to contractors for speed",
                "Disable access reviews to reduce help desk tickets",
            ],
            "Dynamic access needs policy/attribute models—role explosion is a governance failure.",
            "medium", "iam,rbac,scenario", stem, action,
        )

    def biometric_enrollment(org, role, action, pressure=""):
        ctx = (
            "Facilities wants fingerprint readers at data center doors. "
            "Privacy office raises concerns about template storage and false acceptance rates. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            5, "Biometrics", stem,
            "Define biometric use policy, template protection, FAR/FRR requirements, and enrollment/revocation procedures",
            [
                "Store raw fingerprint images in a shared folder for backup",
                "Deploy readers without privacy or accuracy review",
                "Use biometrics as the only factor for privileged access with no fallback controls",
            ],
            "Biometric programs require policy, template security, and accuracy thresholds—not deployment alone.",
            "medium", "biometric,physical,scenario", stem, action,
        )

    return [
        (rbac_abac, "standard"),
        (biometric_enrollment, "standard"),
    ]


def _d6_extended():
    def compliance_audit(org, role, action, pressure=""):
        ctx = (
            "Internal audit will assess ISO 27001 alignment in six weeks. "
            "Teams have evidence scattered across email and personal drives. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            6, "Audit readiness", stem,
            "Centralize control evidence, assign control owners, and perform a pre-audit gap assessment against the standard",
            [
                "Ask auditors to skip controls with missing evidence",
                "Generate random policy PDFs the night before the audit",
                "Disable logging to reduce findings",
            ],
            "Audit readiness is organized evidence and gap remediation—not last-minute document fabrication.",
            "medium", "audit,compliance,scenario", stem, action,
        )

    def red_team_rules(org, role, action, pressure=""):
        ctx = (
            "Red team testing is scheduled. "
            "Operations fears production impact and wants unlimited scope without notification. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            6, "Red team ROE", stem,
            "Define scope, rules of engagement, communication paths, and stop conditions with executive authorization",
            [
                "Allow unscoped testing anytime without telling operations",
                "Cancel all testing to avoid any business risk",
                "Test only production with live denial-of-service attacks",
            ],
            "Red team exercises require explicit ROE and authorization—uncontrolled testing creates operational and legal risk.",
            "hard", "assessment,red-team,scenario", stem, action,
        )

    return [
        (compliance_audit, "standard"),
        (red_team_rules, "standard"),
    ]


def _d7_extended():
    def soc_triage(org, role, action, pressure=""):
        ctx = (
            "The SOC receives 12,000 alerts daily. "
            "Analysts close tickets without investigation to meet SLA metrics. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "SOC optimization", stem,
            "Tune detection rules, prioritize alerts by asset criticality, and define investigation playbooks with quality metrics",
            [
                "Disable alerting entirely to reach zero backlog",
                "Hire more analysts without changing processes or tuning",
                "Auto-close all medium severity alerts after one hour",
            ],
            "SOC effectiveness requires tuning, prioritization, and playbooks—not volume metrics alone.",
            "medium", "soc,operations,scenario", stem, action,
        )

    def malware_containment(org, role, action, pressure=""):
        ctx = (
            "EDR flags lateral movement on several workstations. "
            "The malware family is unknown and finance systems are on the same subnet. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            7, "Malware containment", stem,
            "Isolate affected segments, preserve evidence, and escalate per IR procedures before mass reimaging",
            [
                "Reimage all company devices immediately without analysis",
                "Ignore EDR alerts until antivirus definitions update",
                "Pay the attacker to obtain a decryption key first",
            ],
            "Containment and evidence preservation precede destructive recovery when lateral movement is suspected.",
            "hard", "malware,ir,scenario", stem, action,
        )

    return [
        (soc_triage, "standard"),
        (malware_containment, "standard"),
    ]


def _d8_extended():
    def supply_chain(org, role, action, pressure=""):
        ctx = (
            "A third-party library in your CI pipeline had a compromised update. "
            "Developers pull dependencies directly from public registries without verification. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "Supply chain", stem,
            "Implement dependency pinning, integrity verification, and approved repository governance in the build pipeline",
            [
                "Ban all open source permanently",
                "Trust package checksums from the public internet without internal mirrors",
                "Scan production only after customer reports issues",
            ],
            "Supply chain security requires verified dependencies in CI/CD—not blind trust or post-release discovery.",
            "hard", "supply-chain,devsecops,scenario", stem, action,
        )

    def api_auth(org, role, action, pressure=""):
        ctx = (
            "Mobile apps call backend APIs with long-lived static keys embedded in the binary. "
            "Pen testers extracted keys and accessed customer data. "
        )
        stem = _scenario(org, role, ctx, action, pressure)
        return _make(
            8, "API authentication", stem,
            "Replace static keys with short-lived tokens, mutual TLS or OAuth flows, and server-side authorization",
            [
                "Obfuscate keys in the mobile binary only",
                "Rotate static keys quarterly without changing the model",
                "Disable API logging to hide abuse",
            ],
            "Embedded long-lived secrets fail CISSP API security—use standard token flows and server-side controls.",
            "hard", "api,owasp,scenario", stem, action,
        )

    return [
        (supply_chain, "standard"),
        (api_auth, "standard"),
    ]


EXTENDED_BY_DOMAIN = {
    1: _d1_extended,
    2: _d2_extended,
    3: _d3_extended,
    4: _d4_extended,
    5: _d5_extended,
    6: _d6_extended,
    7: _d7_extended,
    8: _d8_extended,
}
