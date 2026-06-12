"""CISSP cheat sheet catalog for study and simulation."""

CHEAT_SHEET = {
    "version": "2024",
    "exam_format": {
        "cat_min": 125,
        "cat_max": 150,
        "hours": 3,
        "pass_scaled": 700,
        "note": "ISC2 April 2024 CAT; study simulation uses 125-150/3hr",
    },
    "how_to_use": (
        "Use the importance marker on each topic to prioritize study time: "
        "master all MUST topics first, then HIGH topics, then use GOOD topics "
        "for reinforcement and edge-case readiness."
    ),
    "importance_legend": [
        {
            "marker": "must",
            "label": "Must Know",
            "priority": 1,
            "description": "Core exam concepts that appear frequently and drive managerial decisions.",
        },
        {
            "marker": "high",
            "label": "High Value",
            "priority": 2,
            "description": "Commonly tested supporting concepts and practical applications.",
        },
        {
            "marker": "good",
            "label": "Good to Reinforce",
            "priority": 3,
            "description": "Helpful depth, exceptions, and operational details for tougher questions.",
        },
    ],
    "domain_weights": [
        {"domain": 1, "name": "Security and Risk Management", "weight_percent": 16},
        {"domain": 2, "name": "Asset Security", "weight_percent": 10},
        {"domain": 3, "name": "Security Architecture and Engineering", "weight_percent": 13},
        {"domain": 4, "name": "Communication and Network Security", "weight_percent": 13},
        {"domain": 5, "name": "Identity and Access Management", "weight_percent": 13},
        {"domain": 6, "name": "Security Assessment and Testing", "weight_percent": 12},
        {"domain": 7, "name": "Security Operations", "weight_percent": 13},
        {"domain": 8, "name": "Software Development Security", "weight_percent": 10},
    ],
    "manager_mindset": (
        "Choose risk-informed, policy-aligned, and business-supportive actions first. "
        "Prefer governance, due diligence, and repeatable controls over ad hoc technical fixes."
    ),
    "final_reminders": [
        "Read questions as a manager: safety of people, business continuity, legal duty, then technology.",
        "Eliminate answers that bypass policy, skip authorization, or ignore chain of custody.",
        "When choices are close, prefer preventive and formally approved controls over detective-only responses.",
        "Translate technical detail into confidentiality, integrity, availability, and mission impact.",
    ],
    "quick_reference": {
        "formulas": [
            "SLE = Asset Value x Exposure Factor",
            "ALE = SLE x Annualized Rate of Occurrence",
            "ARO = expected frequency per year",
            "MTD >= RTO + WRT",
            "RPO defines acceptable data loss window",
        ],
        "acronyms": [
            {"acronym": "ALE", "name": "Annualized Loss Expectancy"},
            {"acronym": "BIA", "name": "Business Impact Analysis"},
            {"acronym": "DR", "name": "Disaster Recovery"},
            {"acronym": "DLP", "name": "Data Loss Prevention"},
            {"acronym": "IAM", "name": "Identity and Access Management"},
            {"acronym": "IR", "name": "Incident Response"},
            {"acronym": "MFA", "name": "Multi-Factor Authentication"},
            {"acronym": "PAM", "name": "Privileged Access Management"},
            {"acronym": "RPO", "name": "Recovery Point Objective"},
            {"acronym": "RTO", "name": "Recovery Time Objective"},
            {"acronym": "SASE", "name": "Secure Access Service Edge"},
            {"acronym": "SOAR", "name": "Security Orchestration, Automation, and Response"},
        ],
        "domain_weights_table": [
            {"domain": 1, "weight_percent": 16},
            {"domain": 2, "weight_percent": 10},
            {"domain": 3, "weight_percent": 13},
            {"domain": 4, "weight_percent": 13},
            {"domain": 5, "weight_percent": 13},
            {"domain": 6, "weight_percent": 12},
            {"domain": 7, "weight_percent": 13},
            {"domain": 8, "weight_percent": 10},
        ],
    },
    "domains": [
        {
            "domain": 1,
            "name": "Security and Risk Management",
            "weight_percent": 16,
            "exam_tips": [
                "Default to governance and policy before technology.",
                "Quantify risk where possible, then justify treatment choice.",
                "Tie all recommendations to legal, regulatory, and ethical obligations.",
            ],
            "sections": [
                {
                    "topic_id": "d1-cia-five-pillars",
                    "importance": "must",
                    "title": "CIA Triad and Extended Security Objectives",
                    "content": (
                        "CIA remains foundational: confidentiality, integrity, and availability. "
                        "Extended objectives include authenticity and non-repudiation. "
                        "Map controls to business requirements, not tool preference."
                    ),
                    "scenarios": [{"prompt": "A payroll report is altered without authorization. Which pillar is primarily violated?", "answer": "Integrity is primarily violated."}],
                },
                {
                    "topic_id": "d1-risk-formulas-ale",
                    "importance": "must",
                    "title": "Risk Formulas and Loss Calculations",
                    "content": (
                        "- SLE = Asset Value x Exposure Factor\n"
                        "- ALE = SLE x ARO\n"
                        "Use quantitative analysis when reliable data exists; otherwise use qualitative scales."
                    ),
                    "scenarios": [{"prompt": "Asset value is 200,000, EF is 0.25, ARO is 0.4. What is ALE?", "answer": "SLE is 50,000 and ALE is 20,000."}],
                },
                {
                    "topic_id": "d1-risk-treatment-options",
                    "importance": "must",
                    "title": "Risk Treatment Choices",
                    "content": (
                        "Treatment options are avoid, mitigate, transfer, or accept. "
                        "Selection depends on cost-benefit, appetite, and residual risk tolerance."
                    ),
                    "scenarios": [{"prompt": "Buying cyber insurance is which risk treatment?", "answer": "Transfer, because financial impact is shifted to a third party."}],
                },
                {
                    "topic_id": "d1-governance-due-care-diligence",
                    "importance": "must",
                    "title": "Governance, Due Care, and Due Diligence",
                    "content": (
                        "Due care is doing the right thing; due diligence is proving it through ongoing oversight. "
                        "Governance sets direction, policy, accountability, and measurable objectives."
                    ),
                    "scenarios": [{"prompt": "Which is due diligence: writing policy once or auditing compliance quarterly?", "answer": "Auditing compliance quarterly is due diligence."}],
                },
                {
                    "topic_id": "d1-frameworks-standards",
                    "importance": "high",
                    "title": "Frameworks, Standards, and Control Baselines",
                    "content": (
                        "Common references include ISO 27001/27002, NIST CSF, COBIT, and SABSA. "
                        "Frameworks guide strategy; standards define mandatory requirements."
                    ),
                    "scenarios": [{"prompt": "A team needs board-level risk communication language. Which type of artifact helps most?", "answer": "A governance framework such as NIST CSF or COBIT."}],
                },
                {
                    "topic_id": "d1-bcp-bia-rpo-rto",
                    "importance": "must",
                    "title": "BCP, BIA, RPO, and RTO",
                    "content": (
                        "BIA identifies critical processes, dependencies, and impact over time. "
                        "RTO is max downtime; RPO is max acceptable data loss window. "
                        "BCP uses these values to define recovery strategy and priorities."
                    ),
                    "scenarios": [{"prompt": "If an app can lose only 15 minutes of data, which metric is 15 minutes?", "answer": "RPO."}],
                },
                {
                    "topic_id": "d1-legal-regulatory",
                    "importance": "must",
                    "title": "Legal and Regulatory Concepts",
                    "content": (
                        "Understand criminal, civil, administrative, and contractual exposure. "
                        "Know jurisdiction, privacy obligations, breach notification, and cross-border transfer constraints."
                    ),
                    "scenarios": [{"prompt": "A contract requires 24-hour incident notice to partner firms. What governs this duty?", "answer": "Contractual obligation."}],
                },
                {
                    "topic_id": "d1-code-of-ethics-canons",
                    "importance": "high",
                    "title": "Ethics and ISC2 Canons",
                    "content": (
                        "Canon order matters in dilemmas: protect society and common good first, then act honorably, "
                        "serve principals diligently, and advance the profession."
                    ),
                    "scenarios": [{"prompt": "A manager requests concealment of a breach. What should lead your decision?", "answer": "Protect society and the common good; reject concealment."}],
                },
                {
                    "topic_id": "d1-investigations-evidence-chain",
                    "importance": "high",
                    "title": "Investigations and Chain of Custody",
                    "content": (
                        "Document who collected evidence, when, where, and how integrity was preserved. "
                        "Use least invasive methods first and maintain legal admissibility."
                    ),
                    "scenarios": [{"prompt": "Why is a signed chain-of-custody form critical?", "answer": "It supports evidence integrity and admissibility."}],
                },
                {
                    "topic_id": "d1-personnel-security-ip",
                    "importance": "high",
                    "title": "Personnel Security and Intellectual Property",
                    "content": (
                        "Personnel lifecycle controls include background checks, onboarding agreements, role changes, and termination. "
                        "IP protection covers copyrights, patents, trade secrets, and licensing terms."
                    ),
                    "scenarios": [{"prompt": "An engineer leaves and keeps proprietary source code. Which IP category is most relevant?", "answer": "Trade secret protection, supported by agreements and policy."}],
                },
                {
                    "topic_id": "d1-threat-modeling-supply-import-export",
                    "importance": "high",
                    "title": "Threat Modeling and Import/Export Controls",
                    "content": (
                        "Use structured threat modeling (for example STRIDE) to identify abuse paths early. "
                        "Supply chain and cryptographic products may be constrained by import/export laws and sanctions."
                    ),
                    "scenarios": [{"prompt": "A product team plans to ship strong encryption globally. What nontechnical review is required?", "answer": "Import/export and sanctions compliance review."}],
                },
            ],
        },
        {
            "domain": 2,
            "name": "Asset Security",
            "weight_percent": 10,
            "exam_tips": [
                "Tie handling rules to data classification and owner direction.",
                "Differentiate owner accountability from custodian operations.",
                "Know secure destruction and remanence controls by media type.",
            ],
            "sections": [
                {
                    "topic_id": "d2-classification-labeling",
                    "importance": "must",
                    "title": "Classification and Labeling",
                    "content": (
                        "Classification is driven by business impact if data is disclosed, altered, or unavailable. "
                        "Labels and handling standards must remain consistent across lifecycle stages."
                    ),
                    "scenarios": [{"prompt": "Who is accountable for assigning data classification?", "answer": "The data owner."}],
                },
                {
                    "topic_id": "d2-data-states",
                    "importance": "must",
                    "title": "Data States",
                    "content": (
                        "Protect data at rest, in transit, and in use with context-appropriate controls. "
                        "Examples: encryption at rest, TLS in transit, memory/runtime protections in use."
                    ),
                    "scenarios": [{"prompt": "Which state is most associated with TLS?", "answer": "Data in transit."}],
                },
                {
                    "topic_id": "d2-roles-owners-stewards-custodians",
                    "importance": "high",
                    "title": "Data Roles and Responsibilities",
                    "content": (
                        "Owner sets classification and access rules; custodian implements controls; "
                        "steward ensures quality and policy alignment; user follows handling procedures."
                    ),
                    "scenarios": [{"prompt": "A storage admin configures backup encryption keys. Which role is this?", "answer": "Custodian role."}],
                },
                {
                    "topic_id": "d2-lifecycle-handling",
                    "importance": "high",
                    "title": "Data Lifecycle Governance",
                    "content": (
                        "Lifecycle phases include create, store, use, share, archive, and destroy. "
                        "Apply least privilege and minimum necessary use at each phase."
                    ),
                    "scenarios": [{"prompt": "Where should legal hold checks occur most reliably?", "answer": "Before archival or destruction phases."}],
                },
                {
                    "topic_id": "d2-retention-ediscovery-legal-hold",
                    "importance": "must",
                    "title": "Retention, eDiscovery, and Legal Hold",
                    "content": (
                        "Retention schedules balance legal obligations, business value, and risk reduction. "
                        "Legal hold overrides normal destruction until release by counsel."
                    ),
                    "scenarios": [{"prompt": "Can records under legal hold follow normal purge windows?", "answer": "No, legal hold suspends routine destruction."}],
                },
                {
                    "topic_id": "d2-destruction-remanence",
                    "importance": "must",
                    "title": "Destruction and Data Remanence",
                    "content": (
                        "Sanitization methods include clearing, purging, and destroying based on media sensitivity. "
                        "Remanence risk is higher when methods do not match media characteristics."
                    ),
                    "scenarios": [{"prompt": "For highly sensitive failed SSDs, what is safest final action?", "answer": "Physical destruction per approved process."}],
                },
                {
                    "topic_id": "d2-dlp-drm-watermark",
                    "importance": "high",
                    "title": "DLP, DRM, and Watermarking",
                    "content": (
                        "DLP detects and blocks unauthorized data movement; DRM enforces usage restrictions; "
                        "watermarking aids traceability and deterrence."
                    ),
                    "scenarios": [{"prompt": "A user emails customer data to personal webmail. Which control best stops this automatically?", "answer": "DLP policy enforcement."}],
                },
                {
                    "topic_id": "d2-casb-cloud-governance",
                    "importance": "high",
                    "title": "CASB and Cloud Data Governance",
                    "content": (
                        "CASB provides visibility, policy enforcement, and threat protection across cloud services. "
                        "Use API-mode and proxy-mode capabilities based on monitoring and control needs."
                    ),
                    "scenarios": [{"prompt": "Shadow SaaS discovery across many teams is best supported by which platform?", "answer": "A CASB with cloud activity visibility."}],
                },
            ],
        },
        {
            "domain": 3,
            "name": "Security Architecture and Engineering",
            "weight_percent": 13,
            "exam_tips": [
                "Know model intent (confidentiality vs integrity) before comparing models.",
                "Choose cryptographic controls by data sensitivity and key lifecycle.",
                "Treat physical and environmental design as part of architecture.",
            ],
            "sections": [
                {
                    "topic_id": "d3-security-models-blp-biba-clarkwilson",
                    "importance": "must",
                    "title": "Security Models",
                    "content": (
                        "- Bell-LaPadula focuses confidentiality (no read up, no write down)\n"
                        "- Biba focuses integrity (no read down, no write up)\n"
                        "- Clark-Wilson uses well-formed transactions and separation of duties"
                    ),
                    "scenarios": [{"prompt": "Which model is most integrity-centric for commercial systems?", "answer": "Clark-Wilson."}],
                },
                {
                    "topic_id": "d3-architecture-principles",
                    "importance": "must",
                    "title": "Architecture Principles",
                    "content": (
                        "Use trust boundaries, defense in depth, fail-safe defaults, and secure-by-design decisions. "
                        "Document assumptions and dependencies so risk owners can make informed tradeoffs."
                    ),
                    "scenarios": [{"prompt": "What principle limits blast radius by isolating components?", "answer": "Segmentation with clear trust boundaries."}],
                },
                {
                    "topic_id": "d3-secure-design-principles",
                    "importance": "high",
                    "title": "Core Secure Design Principles",
                    "content": (
                        "Least privilege, least functionality, economy of mechanism, open design, and complete mediation "
                        "are recurring exam anchors for architecture questions."
                    ),
                    "scenarios": [{"prompt": "Disabling unused services on a server applies which principle?", "answer": "Least functionality."}],
                },
                {
                    "topic_id": "d3-crypto-basics-symmetric-asymmetric",
                    "importance": "must",
                    "title": "Cryptography Fundamentals",
                    "content": (
                        "Symmetric crypto is fast and best for bulk data; asymmetric crypto supports key exchange, "
                        "digital signatures, and scalable trust with PKI."
                    ),
                    "scenarios": [{"prompt": "Which approach is most efficient for encrypting large backups?", "answer": "Symmetric encryption for bulk data."}],
                },
                {
                    "topic_id": "d3-crypto-pki-key-management",
                    "importance": "must",
                    "title": "PKI and Key Management Lifecycle",
                    "content": (
                        "Strong crypto fails if key generation, storage, rotation, revocation, and destruction are weak. "
                        "Protect private keys with hardware-backed controls where possible."
                    ),
                    "scenarios": [{"prompt": "A compromised private key should trigger what immediate PKI action?", "answer": "Certificate revocation and key replacement."}],
                },
                {
                    "topic_id": "d3-crypto-attacks",
                    "importance": "high",
                    "title": "Cryptographic Attack Patterns",
                    "content": (
                        "Know brute force, replay, downgrade, side-channel, and birthday/collision concepts. "
                        "Prefer modern suites and protocol hardening to reduce exploitable weakness."
                    ),
                    "scenarios": [{"prompt": "Forcing legacy ciphers during negotiation is what type of attack?", "answer": "A downgrade attack."}],
                },
                {
                    "topic_id": "d3-evaluation-models-common-criteria",
                    "importance": "high",
                    "title": "Evaluation and Assurance Models",
                    "content": (
                        "Common Criteria uses Protection Profiles and Evaluation Assurance Levels (EAL). "
                        "Understand assurance evidence versus operational security reality."
                    ),
                    "scenarios": [{"prompt": "Does a higher EAL guarantee secure deployment in every environment?", "answer": "No, it indicates assurance level under evaluated conditions."}],
                },
                {
                    "topic_id": "d3-quantum-post-quantum",
                    "importance": "good",
                    "title": "Quantum and Post-Quantum Readiness",
                    "content": (
                        "Plan crypto agility now: inventory cryptographic dependencies and support algorithm migration. "
                        "Long-lived confidential data is most exposed to harvest-now-decrypt-later risk."
                    ),
                    "scenarios": [{"prompt": "What capability best supports post-quantum transition?", "answer": "Cryptographic agility with replaceable algorithms and key plans."}],
                },
                {
                    "topic_id": "d3-facility-site-design",
                    "importance": "high",
                    "title": "Facility and Site Security Design",
                    "content": (
                        "Layer physical controls: perimeter, entry, internal zones, and critical rooms. "
                        "Address fire suppression, power quality, HVAC, and life safety in design."
                    ),
                    "scenarios": [{"prompt": "Which site feature most directly supports continuous operations during utility failure?", "answer": "UPS plus generator strategy with tested maintenance."}],
                },
            ],
        },
        {
            "domain": 4,
            "name": "Communication and Network Security",
            "weight_percent": 13,
            "exam_tips": [
                "Map controls to OSI/TCP-IP layer behavior.",
                "Differentiate network segmentation goals from traffic filtering goals.",
                "Expect secure remote access and cloud edge architecture questions.",
            ],
            "sections": [
                {
                    "topic_id": "d4-osi-tcpip-models",
                    "importance": "must",
                    "title": "OSI and TCP/IP Models",
                    "content": (
                        "Understand layer responsibilities and where controls apply. "
                        "Exam questions often test troubleshooting logic and control placement by layer."
                    ),
                    "scenarios": [{"prompt": "At which OSI layer does a traditional router primarily operate?", "answer": "Layer 3 (Network)."}],
                },
                {
                    "topic_id": "d4-network-protocols-core",
                    "importance": "must",
                    "title": "Core Network Protocols",
                    "content": (
                        "Know secure and insecure protocol variants: HTTP/HTTPS, FTP/SFTP, Telnet/SSH, DNS/DNSSEC. "
                        "Protocol choice affects confidentiality, integrity, and authentication."
                    ),
                    "scenarios": [{"prompt": "Which protocol replacement best removes plaintext remote admin risk?", "answer": "Use SSH instead of Telnet."}],
                },
                {
                    "topic_id": "d4-routing-switching-basics",
                    "importance": "high",
                    "title": "Routing and Switching Security Basics",
                    "content": (
                        "Secure control planes, use authenticated routing where supported, and protect against VLAN hopping "
                        "through hardened trunk and access port configurations."
                    ),
                    "scenarios": [{"prompt": "What hardening action helps prevent unauthorized trunk negotiation?", "answer": "Disable dynamic trunking and set explicit port mode."}],
                },
                {
                    "topic_id": "d4-firewalls-proxies-waf",
                    "importance": "must",
                    "title": "Firewalls, Proxies, and WAF",
                    "content": (
                        "Packet filters, stateful inspection, NGFW, proxies, and WAF each provide different depth. "
                        "Use layered enforcement for network and application traffic."
                    ),
                    "scenarios": [{"prompt": "Which control is best positioned to inspect and block SQL injection patterns in web traffic?", "answer": "A web application firewall (WAF)."}],
                },
                {
                    "topic_id": "d4-network-attacks",
                    "importance": "must",
                    "title": "Network Attack Patterns",
                    "content": (
                        "Common attacks include spoofing, MITM, DoS/DDoS, ARP poisoning, and DNS manipulation. "
                        "Pair prevention with monitoring and response playbooks."
                    ),
                    "scenarios": [{"prompt": "Intercepting traffic between two hosts while relaying packets describes what?", "answer": "Man-in-the-middle attack."}],
                },
                {
                    "topic_id": "d4-vpn-secure-tunnels",
                    "importance": "high",
                    "title": "VPN and Secure Tunneling",
                    "content": (
                        "Use IPSec or TLS-based VPNs with strong authentication and endpoint posture checks. "
                        "Select split tunnel versus full tunnel based on risk and performance needs."
                    ),
                    "scenarios": [{"prompt": "Which VPN mode best keeps internet-bound traffic under enterprise inspection?", "answer": "Full tunneling."}],
                },
                {
                    "topic_id": "d4-sase-ztna-sdwan",
                    "importance": "high",
                    "title": "SASE, ZTNA, and SD-WAN",
                    "content": (
                        "SASE converges networking and security services at the edge. "
                        "ZTNA emphasizes identity- and context-based access instead of broad network trust."
                    ),
                    "scenarios": [{"prompt": "What access principle does ZTNA enforce most directly?", "answer": "Per-session least-privilege access based on identity and context."}],
                },
                {
                    "topic_id": "d4-wireless-security",
                    "importance": "high",
                    "title": "Wireless Security",
                    "content": (
                        "Prefer WPA3 where possible, enforce strong authentication, and monitor for rogue APs and evil twins. "
                        "Separate guest and corporate wireless with strict policy controls."
                    ),
                    "scenarios": [{"prompt": "A fake hotspot impersonating a trusted SSID is known as what?", "answer": "An evil twin access point."}],
                },
                {
                    "topic_id": "d4-segmentation-microsegmentation",
                    "importance": "must",
                    "title": "Segmentation and Microsegmentation",
                    "content": (
                        "Segmentation reduces lateral movement and limits incident blast radius. "
                        "Microsegmentation adds workload-level policy enforcement in modern environments."
                    ),
                    "scenarios": [{"prompt": "What is the primary security benefit of microsegmentation?", "answer": "Fine-grained east-west traffic control to reduce lateral movement."}],
                },
            ],
        },
        {
            "domain": 5,
            "name": "Identity and Access Management",
            "weight_percent": 13,
            "exam_tips": [
                "Start with identity proofing, then authentication, then authorization, then accountability.",
                "Pick access control models by business context and sensitivity.",
                "Favor centralized, auditable privileged access controls.",
            ],
            "sections": [
                {
                    "topic_id": "d5-auth-factors-mfa",
                    "importance": "must",
                    "title": "Authentication Factors and MFA",
                    "content": (
                        "Factors include something you know, have, are, do, or where you are. "
                        "True MFA requires distinct factor categories."
                    ),
                    "scenarios": [{"prompt": "Password plus PIN is MFA or not?", "answer": "Not MFA; both are knowledge factors."}],
                },
                {
                    "topic_id": "d5-authn-protocols-basics",
                    "importance": "high",
                    "title": "Authentication Protocol Basics",
                    "content": (
                        "Know where PAP/CHAP/MS-CHAP, RADIUS, and TACACS+ fit operationally. "
                        "Prefer modern, encrypted, and centrally managed protocol choices."
                    ),
                    "scenarios": [{"prompt": "Which protocol is commonly used for centralized network access AAA?", "answer": "RADIUS (or TACACS+ depending use case)."}],
                },
                {
                    "topic_id": "d5-access-control-models",
                    "importance": "must",
                    "title": "Access Control Models",
                    "content": (
                        "Models include DAC, MAC, RBAC, ABAC, and rule-based approaches. "
                        "ABAC improves dynamic decisions through attributes and context."
                    ),
                    "scenarios": [{"prompt": "Access based on role title and department policy is typically which model?", "answer": "RBAC, potentially combined with ABAC attributes."}],
                },
                {
                    "topic_id": "d5-aaa-accounting",
                    "importance": "must",
                    "title": "AAA Foundations",
                    "content": (
                        "Authentication verifies identity, authorization grants rights, and accounting records actions. "
                        "Without accounting, non-repudiation and forensic timelines weaken."
                    ),
                    "scenarios": [{"prompt": "Which AAA function provides audit trail evidence of user actions?", "answer": "Accounting."}],
                },
                {
                    "topic_id": "d5-sso-kerberos",
                    "importance": "must",
                    "title": "Single Sign-On and Kerberos",
                    "content": (
                        "Kerberos uses symmetric keys and ticketing through KDC components. "
                        "Time synchronization is critical; ticket misuse can become a lateral movement vector."
                    ),
                    "scenarios": [{"prompt": "What infrastructure dependency is essential for Kerberos reliability?", "answer": "Accurate time synchronization across participants."}],
                },
                {
                    "topic_id": "d5-saml-oauth-oidc",
                    "importance": "must",
                    "title": "SAML, OAuth, and OIDC",
                    "content": (
                        "SAML is assertion-based federation, often enterprise web SSO. "
                        "OAuth delegates authorization; OIDC adds identity layer on OAuth 2.0."
                    ),
                    "scenarios": [{"prompt": "Which protocol family is mainly about delegated authorization to APIs?", "answer": "OAuth 2.0."}],
                },
                {
                    "topic_id": "d5-federation-trust",
                    "importance": "high",
                    "title": "Federation and Trust Relationships",
                    "content": (
                        "Federation extends identity across organizational boundaries via trust agreements. "
                        "Claims mapping, token validation, and lifecycle governance are key risks."
                    ),
                    "scenarios": [{"prompt": "What is the biggest governance risk in federation misconfiguration?", "answer": "Granting inappropriate access through incorrect claim-to-role mapping."}],
                },
                {
                    "topic_id": "d5-biometrics",
                    "importance": "high",
                    "title": "Biometrics and Error Metrics",
                    "content": (
                        "Understand FAR, FRR, and CER tradeoffs. "
                        "Use liveness detection and fallback processes to balance security and usability."
                    ),
                    "scenarios": [{"prompt": "What point reflects balance between false accept and false reject rates?", "answer": "Crossover Error Rate (CER)." }],
                },
                {
                    "topic_id": "d5-pam-secrets-management",
                    "importance": "must",
                    "title": "Privileged Access Management",
                    "content": (
                        "PAM controls privileged credentials through vaulting, rotation, just-in-time access, and session recording. "
                        "Remove standing privilege whenever possible."
                    ),
                    "scenarios": [{"prompt": "Which PAM practice best reduces risk of long-lived admin credentials?", "answer": "Just-in-time elevation with automatic expiration."}],
                },
            ],
        },
        {
            "domain": 6,
            "name": "Security Assessment and Testing",
            "weight_percent": 12,
            "exam_tips": [
                "Differentiate discovery activities from exploit activities.",
                "Scope, authorization, and evidence quality are as important as tooling.",
                "Map findings to remediation owners and retest plans.",
            ],
            "sections": [
                {
                    "topic_id": "d6-vuln-assessment-vs-pentest",
                    "importance": "must",
                    "title": "Vulnerability Assessment vs Penetration Testing",
                    "content": (
                        "Vulnerability assessment identifies and prioritizes weaknesses broadly. "
                        "Pen testing actively exploits authorized targets to demonstrate impact."
                    ),
                    "scenarios": [{"prompt": "Which activity is generally safer for frequent enterprise-wide baseline checks?", "answer": "Vulnerability assessment."}],
                },
                {
                    "topic_id": "d6-pentest-types",
                    "importance": "high",
                    "title": "Penetration Test Approaches",
                    "content": (
                        "Black box, white box, and gray box describe tester knowledge. "
                        "Internal and external perspectives reveal different attack paths."
                    ),
                    "scenarios": [{"prompt": "Which test type best simulates an outside attacker with minimal prior knowledge?", "answer": "Black-box external test."}],
                },
                {
                    "topic_id": "d6-audit-programs-controls",
                    "importance": "must",
                    "title": "Audits and Control Validation",
                    "content": (
                        "Audits assess conformity to policy, standards, and regulatory obligations. "
                        "Evidence quality, sampling, and repeatability matter for defensibility."
                    ),
                    "scenarios": [{"prompt": "What is the primary purpose of an internal security audit?", "answer": "Assess control compliance and effectiveness against defined criteria."}],
                },
                {
                    "topic_id": "d6-sast-dast-iast-sca",
                    "importance": "must",
                    "title": "Application Security Testing Methods",
                    "content": (
                        "- SAST: static source/bytecode review\n"
                        "- DAST: dynamic runtime black-box testing\n"
                        "- IAST: instrumented runtime analysis\n"
                        "- SCA: third-party dependency risk and licensing"
                    ),
                    "scenarios": [{"prompt": "Which testing method best finds vulnerable open-source components quickly?", "answer": "Software Composition Analysis (SCA)."}],
                },
                {
                    "topic_id": "d6-soc-reports",
                    "importance": "high",
                    "title": "SOC Reports and Third-Party Assurance",
                    "content": (
                        "SOC 1 focuses financial reporting controls; SOC 2 covers trust service criteria; "
                        "Type II includes operating effectiveness over time."
                    ),
                    "scenarios": [{"prompt": "A customer asks for evidence that security controls operated effectively over months. Which report is most relevant?", "answer": "SOC 2 Type II."}],
                },
                {
                    "topic_id": "d6-metrics-kri-kpi",
                    "importance": "good",
                    "title": "Security Metrics and Reporting",
                    "content": (
                        "Use KRIs for risk trend signals and KPIs for performance targets. "
                        "Metrics must be decision-useful, not merely easy to collect."
                    ),
                    "scenarios": [{"prompt": "Rising critical unpatched vulnerabilities is best categorized as what?", "answer": "A Key Risk Indicator (KRI)."}],
                },
                {
                    "topic_id": "d6-continuous-monitoring",
                    "importance": "high",
                    "title": "Continuous Monitoring",
                    "content": (
                        "Continuous monitoring integrates logs, telemetry, config drift, and threat intelligence. "
                        "It shortens detection time and supports risk-based prioritization."
                    ),
                    "scenarios": [{"prompt": "What operational outcome improves most when continuous monitoring matures?", "answer": "Mean time to detect potential incidents."}],
                },
                {
                    "topic_id": "d6-reporting-remediation-validation",
                    "importance": "high",
                    "title": "Remediation and Validation Cycles",
                    "content": (
                        "Findings should include severity, business impact, owner, and due date. "
                        "Retesting verifies closure and avoids paper-only remediation."
                    ),
                    "scenarios": [{"prompt": "Why is retesting required after a critical fix?", "answer": "To validate the vulnerability is actually remediated and not reintroduced."}],
                },
            ],
        },
        {
            "domain": 7,
            "name": "Security Operations",
            "weight_percent": 13,
            "exam_tips": [
                "Follow the incident lifecycle in order unless immediate containment demands otherwise.",
                "Preserve evidence integrity while restoring business operations safely.",
                "Treat change, backup, and recovery as integrated governance practices.",
            ],
            "sections": [
                {
                    "topic_id": "d7-incident-response-steps",
                    "importance": "must",
                    "title": "Incident Response Lifecycle",
                    "content": (
                        "Core stages: preparation, identification, containment, eradication, recovery, and lessons learned. "
                        "Pre-approved playbooks reduce response confusion under pressure."
                    ),
                    "scenarios": [{"prompt": "After identifying malware spread, what generally comes next?", "answer": "Containment to limit further impact."}],
                },
                {
                    "topic_id": "d7-evidence-volatility-order",
                    "importance": "must",
                    "title": "Evidence Handling and Order of Volatility",
                    "content": (
                        "Collect most volatile data first (for example memory, network connections) before powering down systems. "
                        "Use documented procedures to maintain forensic integrity."
                    ),
                    "scenarios": [{"prompt": "Why acquire memory before disk imaging on a live host?", "answer": "Memory is more volatile and may be lost quickly."}],
                },
                {
                    "topic_id": "d7-disaster-recovery-sites",
                    "importance": "high",
                    "title": "Disaster Recovery Site Strategies",
                    "content": (
                        "Cold sites are cheapest but slowest; warm sites balance cost and speed; hot sites are fastest and most expensive. "
                        "Select strategy based on BIA-defined RTO/RPO."
                    ),
                    "scenarios": [{"prompt": "Which site type generally offers near-immediate failover capability?", "answer": "Hot site."}],
                },
                {
                    "topic_id": "d7-backup-strategies",
                    "importance": "must",
                    "title": "Backup and Recovery Patterns",
                    "content": (
                        "Use full, differential, and incremental backups with tested restoration. "
                        "Apply 3-2-1 style resilience and protect backup integrity from ransomware tampering."
                    ),
                    "scenarios": [{"prompt": "What is the most overlooked backup control in many programs?", "answer": "Routine restore testing to prove recoverability."}],
                },
                {
                    "topic_id": "d7-change-management-configuration",
                    "importance": "high",
                    "title": "Change and Configuration Management",
                    "content": (
                        "Formal change management reduces outages and unauthorized drift. "
                        "Emergency changes require expedited approval with post-implementation review."
                    ),
                    "scenarios": [{"prompt": "A critical patch is applied overnight without CAB meeting. What must follow?", "answer": "Documented emergency change review and approval record."}],
                },
                {
                    "topic_id": "d7-soar-siem-soc-operations",
                    "importance": "high",
                    "title": "SOC, SIEM, and SOAR Operations",
                    "content": (
                        "SIEM centralizes detection analytics; SOAR automates triage and response workflows. "
                        "Automation should reduce analyst toil while preserving oversight."
                    ),
                    "scenarios": [{"prompt": "Auto-disabling compromised accounts based on validated playbooks is an example of what?", "answer": "SOAR-driven response automation."}],
                },
                {
                    "topic_id": "d7-control-categories",
                    "importance": "must",
                    "title": "Control Categories and Functions",
                    "content": (
                        "Controls may be administrative, technical, or physical; and preventive, detective, corrective, deterrent, compensating, or recovery. "
                        "Exam questions often ask for best category fit."
                    ),
                    "scenarios": [{"prompt": "A mandatory vacation policy primarily represents which control type?", "answer": "Administrative detective/deterrent control."}],
                },
                {
                    "topic_id": "d7-lessons-learned-exercises",
                    "importance": "good",
                    "title": "Lessons Learned and Exercises",
                    "content": (
                        "Tabletop and simulation exercises validate plans before real incidents. "
                        "Lessons learned should produce tracked, measurable improvements."
                    ),
                    "scenarios": [{"prompt": "What is the key output of a mature post-incident review?", "answer": "Actionable improvement items with owners and deadlines."}],
                },
            ],
        },
        {
            "domain": 8,
            "name": "Software Development Security",
            "weight_percent": 10,
            "exam_tips": [
                "Shift security left but keep runtime monitoring and feedback loops.",
                "Treat dependencies and APIs as first-class attack surfaces.",
                "Apply threat modeling and secure coding throughout SDLC phases.",
            ],
            "sections": [
                {
                    "topic_id": "d8-sdlc-phases-security",
                    "importance": "must",
                    "title": "SDLC Security Integration",
                    "content": (
                        "Integrate security requirements, threat modeling, testing, and review into every SDLC phase. "
                        "Security gates should align to risk and release cadence."
                    ),
                    "scenarios": [{"prompt": "Where is fixing design-level auth flaws typically cheapest?", "answer": "Early SDLC phases such as requirements and architecture."}],
                },
                {
                    "topic_id": "d8-dev-models-agile-devsecops",
                    "importance": "high",
                    "title": "Development Models and DevSecOps",
                    "content": (
                        "Waterfall, iterative, agile, and spiral each influence when assurance occurs. "
                        "DevSecOps emphasizes automation, shared ownership, and rapid secure feedback."
                    ),
                    "scenarios": [{"prompt": "What practice best matches DevSecOps principles?", "answer": "Automated security testing in CI/CD with developer-visible feedback."}],
                },
                {
                    "topic_id": "d8-owasp-top-10",
                    "importance": "must",
                    "title": "OWASP Top 10 Mindset",
                    "content": (
                        "Prioritize common web risks such as broken access control, cryptographic failures, and injection. "
                        "Use secure design patterns and verification to prevent recurring classes of flaws."
                    ),
                    "scenarios": [{"prompt": "An endpoint exposes other users' records by ID tampering. Which OWASP class is this?", "answer": "Broken access control."}],
                },
                {
                    "topic_id": "d8-secure-coding-practices",
                    "importance": "must",
                    "title": "Secure Coding Fundamentals",
                    "content": (
                        "Apply input validation, output encoding, parameterized queries, robust error handling, and least privilege. "
                        "Avoid storing secrets in code or insecure configuration."
                    ),
                    "scenarios": [{"prompt": "Which coding pattern most directly reduces SQL injection risk?", "answer": "Parameterized queries and prepared statements."}],
                },
                {
                    "topic_id": "d8-database-security",
                    "importance": "high",
                    "title": "Database Security Controls",
                    "content": (
                        "Use strong authentication, role separation, encryption, activity monitoring, and backup protection. "
                        "Limit direct production access and track privileged queries."
                    ),
                    "scenarios": [{"prompt": "What is the primary purpose of database activity monitoring?", "answer": "Detect and audit suspicious or unauthorized data access behavior."}],
                },
                {
                    "topic_id": "d8-api-security",
                    "importance": "must",
                    "title": "API Security Essentials",
                    "content": (
                        "Enforce strong authn/authz, schema validation, rate limiting, and secure token handling. "
                        "Monitor for abuse patterns such as credential stuffing and excessive data exposure."
                    ),
                    "scenarios": [{"prompt": "What control best limits automated API abuse bursts?", "answer": "Rate limiting with anomaly-aware throttling."}],
                },
                {
                    "topic_id": "d8-sbom-supply-chain",
                    "importance": "high",
                    "title": "SBOM and Software Supply Chain",
                    "content": (
                        "SBOM improves visibility into dependencies, versions, and transitive risk. "
                        "Pair SBOM with signing, provenance checks, and vulnerability response workflows."
                    ),
                    "scenarios": [{"prompt": "A critical CVE is announced. How does SBOM help first?", "answer": "It quickly identifies affected applications and dependency paths."}],
                },
                {
                    "topic_id": "d8-ai-ml-security",
                    "importance": "good",
                    "title": "AI/ML Security Considerations",
                    "content": (
                        "Protect training data, model artifacts, and inference endpoints from poisoning, theft, and prompt abuse. "
                        "Govern model drift, explainability, and policy constraints for safe deployment."
                    ),
                    "scenarios": [{"prompt": "What is a key risk when adversaries manipulate model training data?", "answer": "Data poisoning that degrades or biases model outcomes."}],
                },
            ],
        },
    ],
}
