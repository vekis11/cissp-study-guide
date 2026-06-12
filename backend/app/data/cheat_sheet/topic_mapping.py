"""Map cheat-sheet topic_ids to scenario-bank tags and search keywords."""

# Each catalog topic maps to scenario tags (from topic_specs) and/or stem keywords.
TOPIC_SCENARIO_MAP: dict[str, dict] = {
    "d1-cia-five-pillars": {
        "tags": ["d1-integrated-risk", "d1-risk-communication"],
        "keywords": ["confidentiality", "integrity", "availability", "non-repudiation", "authenticity", "cia"],
    },
    "d1-risk-formulas-ale": {
        "tags": ["d1-kpi-kri", "d1-risk-communication"],
        "keywords": ["ale", "sle", "aro", "exposure factor", "annualized loss", "quantitative risk"],
    },
    "d1-risk-treatment-options": {
        "tags": ["d1-risk-treatment", "d1-risk-appetite"],
        "keywords": ["mitigate", "transfer", "accept", "avoid", "risk treatment"],
    },
    "d1-governance-due-care-diligence": {
        "tags": ["d1-due-care-diligence", "d1-governance-charter"],
        "keywords": ["due care", "due diligence", "governance"],
    },
    "d1-frameworks-standards": {
        "tags": ["d1-policy-hierarchy", "d1-governance-charter"],
        "keywords": ["iso 27001", "nist csf", "cobit", "sabsa", "framework", "fedramp", "pci"],
    },
    "d1-bcp-bia-rpo-rto": {
        "tags": ["d1-bia-governance"],
        "keywords": ["bcp", "bia", "rpo", "rto", "business continuity", "business impact"],
    },
    "d1-legal-regulatory": {
        "tags": ["d1-jurisdiction-mapping"],
        "keywords": ["gdpr", "ccpa", "criminal law", "civil law", "regulatory", "jurisdiction", "privacy law"],
    },
    "d1-code-of-ethics-canons": {
        "tags": ["d1-ethics-procurement"],
        "keywords": ["canon", "code of ethics", "isc2", "protect society", "common good"],
    },
    "d1-investigations-evidence-chain": {
        "tags": ["d1-jurisdiction-mapping"],
        "keywords": ["investigation", "chain of custody", "administrative", "preponderance", "reasonable doubt"],
    },
    "d1-personnel-security-ip": {
        "tags": ["d1-raci-ownership", "d1-awareness-behavior"],
        "keywords": ["personnel", "termination", "trade secret", "copyright", "patent", "trademark", "onboarding"],
    },
    "d1-threat-modeling-supply-import-export": {
        "tags": ["d1-scrm-tiered", "d1-threat-prioritization"],
        "keywords": ["stride", "dread", "pasta", "threat model", "import", "export", "supply chain", "wassenaar"],
    },
    "d2-classification-labeling": {
        "tags": ["d2-classification-schema"],
        "keywords": ["classification", "top secret", "confidential", "unclassified", "labeling"],
    },
    "d2-data-states": {
        "tags": ["d2-handling-standards", "d2-transmission-policy"],
        "keywords": ["data at rest", "data in transit", "data in use", "encryption", "tls"],
    },
    "d2-roles-owners-stewards-custodians": {
        "tags": ["d2-owner-steward"],
        "keywords": ["data owner", "data custodian", "data steward", "controller", "processor"],
    },
    "d2-lifecycle-handling": {
        "tags": ["d2-lifecycle-rules", "d2-handling-standards"],
        "keywords": ["lifecycle", "create", "store", "archive", "destroy", "handling"],
    },
    "d2-retention-ediscovery-legal-hold": {
        "tags": ["d2-retention-compliance"],
        "keywords": ["retention", "legal hold", "ediscovery", "records"],
    },
    "d2-destruction-remanence": {
        "tags": ["d2-media-sanitization"],
        "keywords": ["degauss", "sanitization", "remanence", "nist 800-88", "crypto-shred", "destruction"],
    },
    "d2-dlp-drm-watermark": {
        "tags": ["d2-dlp-governance"],
        "keywords": ["dlp", "drm", "data loss prevention", "watermark"],
    },
    "d2-casb-cloud-governance": {
        "tags": ["d3-shared-responsibility"],
        "keywords": ["casb", "cloud access", "cloud governance"],
    },
    "d3-security-models-blp-biba-clarkwilson": {
        "tags": ["d3-trust-boundaries", "d3-architecture-principles"],
        "keywords": ["bell-lapadula", "biba", "clark-wilson", "brewer-nash", "chinese wall", "no read up"],
    },
    "d3-architecture-principles": {
        "tags": ["d3-architecture-principles", "d3-defense-depth"],
        "keywords": ["defense in depth", "zero trust", "least privilege", "separation of duties", "fail-safe"],
    },
    "d3-secure-design-principles": {
        "tags": ["d3-secure-defaults", "d3-privacy-engineering"],
        "keywords": ["secure by design", "privacy by design", "secure defaults"],
    },
    "d3-crypto-basics-symmetric-asymmetric": {
        "tags": ["d3-crypto-lifecycle"],
        "keywords": ["symmetric", "asymmetric", "aes", "rsa", "diffie-hellman", "hashing", "sha"],
    },
    "d3-crypto-pki-key-management": {
        "tags": ["d3-crypto-lifecycle"],
        "keywords": ["pki", "certificate", "digital signature", "certificate authority", "key management"],
    },
    "d3-crypto-attacks": {
        "tags": ["d3-crypto-lifecycle"],
        "keywords": ["brute force", "birthday attack", "side-channel", "meet-in-the-middle", "known plaintext"],
    },
    "d3-evaluation-models-common-criteria": {
        "tags": ["d3-arch-review-board"],
        "keywords": ["common criteria", "eal", "orange book", "tcsec", "evaluation"],
    },
    "d3-quantum-post-quantum": {
        "tags": ["d3-crypto-lifecycle"],
        "keywords": ["quantum", "qkd", "post-quantum"],
    },
    "d3-facility-site-design": {
        "tags": ["d3-physical-logical", "d3-ha-fault-tolerance"],
        "keywords": ["cpted", "mantrap", "faraday", "fire suppression", "fm-200", "clean agent", "tempest"],
    },
    "d4-osi-tcpip-models": {
        "tags": ["d4-network-baselines"],
        "keywords": ["osi", "tcp/ip", "layer 7", "layer 4", "application layer", "transport layer"],
    },
    "d4-network-protocols-core": {
        "tags": ["d4-transmission-policy", "d4-remote-access"],
        "keywords": ["ipsec", "esp", "ah", "tls", "ssh", "smtp", "dns", "icmp"],
    },
    "d4-routing-switching-basics": {
        "tags": ["d4-routing-governance", "d4-network-baselines"],
        "keywords": ["router", "switch", "bgp", "ospf", "vlan", "arp"],
    },
    "d4-firewalls-proxies-waf": {
        "tags": ["d4-edge-security", "d4-segmentation-ot-it"],
        "keywords": ["firewall", "stateful", "proxy", "waf", "ngfw", "packet filter"],
    },
    "d4-network-attacks": {
        "tags": ["d4-ddos-resilience", "d4-email-fraud"],
        "keywords": ["mitm", "ddos", "syn flood", "arp poison", "dns poison", "replay", "vlan hopping"],
    },
    "d4-vpn-secure-tunnels": {
        "tags": ["d4-remote-access", "d4-ztna-transition"],
        "keywords": ["vpn", "tunnel", "split tunnel", "ipsec tunnel", "ssl vpn"],
    },
    "d4-sase-ztna-sdwan": {
        "tags": ["d4-ztna-transition", "d4-telemetry-strategy"],
        "keywords": ["sase", "sd-wan", "ztna", "fwaas", "swg"],
    },
    "d4-wireless-security": {
        "tags": ["d4-wireless-program", "d4-nac-governance"],
        "keywords": ["wpa", "wpa2", "wpa3", "wep", "802.1x", "radius", "wireless"],
    },
    "d4-segmentation-microsegmentation": {
        "tags": ["d4-segmentation-ot-it"],
        "keywords": ["dmz", "microsegmentation", "vlan", "segmentation", "sdn"],
    },
    "d5-auth-factors-mfa": {
        "tags": ["d5-proofing-tiered", "d5-adaptive-auth"],
        "keywords": ["mfa", "multi-factor", "something you know", "something you have", "something you are"],
    },
    "d5-authn-protocols-basics": {
        "tags": ["d5-lifecycle-automation"],
        "keywords": ["authentication", "ldap", "active directory", "radius"],
    },
    "d5-access-control-models": {
        "tags": ["d5-authz-governance", "d5-least-privilege"],
        "keywords": ["dac", "mac", "rbac", "abac", "discretionary", "mandatory access"],
    },
    "d5-aaa-accounting": {
        "tags": ["d5-iam-metrics"],
        "keywords": ["authentication", "authorization", "accounting", "aaa"],
    },
    "d5-sso-kerberos": {
        "tags": ["d5-lifecycle-automation"],
        "keywords": ["kerberos", "tgt", "kdc", "single sign-on", "sso"],
    },
    "d5-saml-oauth-oidc": {
        "tags": ["d5-federation-trust"],
        "keywords": ["saml", "oauth", "openid", "oidc", "identity provider"],
    },
    "d5-federation-trust": {
        "tags": ["d5-federation-trust"],
        "keywords": ["federation", "federated identity", "trust", "idp", "service provider"],
    },
    "d5-biometrics": {
        "tags": ["d5-proofing-tiered"],
        "keywords": ["biometric", "far", "frr", "cer", "eer", "false acceptance"],
    },
    "d5-pam-secrets-management": {
        "tags": ["d5-pam-governance", "d5-machine-identity"],
        "keywords": ["pam", "privileged", "just-in-time", "jit", "secrets"],
    },
    "d6-vuln-assessment-vs-pentest": {
        "tags": ["d6-vuln-governance", "d6-assessment-strategy"],
        "keywords": ["vulnerability assessment", "penetration test", "pen test", "exploit"],
    },
    "d6-pentest-types": {
        "tags": ["d6-pentest-lifecycle"],
        "keywords": ["black box", "white box", "gray box", "penetration"],
    },
    "d6-audit-programs-controls": {
        "tags": ["d6-evidence-governance", "d6-assurance-coordination"],
        "keywords": ["audit", "first-party", "second-party", "third-party", "internal audit"],
    },
    "d6-sast-dast-iast-sca": {
        "tags": ["d8-testing-gates", "d6-effectiveness-validation"],
        "keywords": ["sast", "dast", "iast", "sca", "static application", "dynamic application"],
    },
    "d6-soc-reports": {
        "tags": ["d6-third-party-assess"],
        "keywords": ["soc 1", "soc 2", "soc 3", "type i", "type ii", "trust services"],
    },
    "d6-metrics-kri-kpi": {
        "tags": ["d6-testing-metrics", "d1-kpi-kri"],
        "keywords": ["kpi", "kri", "mttd", "mttr", "metric"],
    },
    "d6-continuous-monitoring": {
        "tags": ["d6-continuous-monitoring"],
        "keywords": ["continuous monitoring", "siem", "log management"],
    },
    "d6-reporting-remediation-validation": {
        "tags": ["d6-effectiveness-validation", "d6-vuln-governance"],
        "keywords": ["remediation", "validation", "reporting", "patch compliance"],
    },
    "d7-incident-response-steps": {
        "tags": ["d7-ir-governance", "d7-incident-slos"],
        "keywords": ["incident response", "containment", "eradication", "preparation", "lessons learned"],
    },
    "d7-evidence-volatility-order": {
        "tags": ["d7-forensics-readiness"],
        "keywords": ["order of volatility", "chain of custody", "forensic", "write blocker", "ram"],
    },
    "d7-disaster-recovery-sites": {
        "tags": ["d7-bcdr-operations"],
        "keywords": ["hot site", "warm site", "cold site", "disaster recovery", "mobile site"],
    },
    "d7-backup-strategies": {
        "tags": ["d7-backup-assurance"],
        "keywords": ["full backup", "incremental", "differential", "backup"],
    },
    "d7-change-management-configuration": {
        "tags": ["d7-change-governance"],
        "keywords": ["change management", "configuration management", "baseline"],
    },
    "d7-soar-siem-soc-operations": {
        "tags": ["d7-soc-governance", "d7-monitoring-usecases"],
        "keywords": ["soar", "siem", "soc", "threat intelligence", "threat hunting"],
    },
    "d7-control-categories": {
        "tags": ["d7-monitoring-usecases"],
        "keywords": ["preventive", "detective", "corrective", "deterrent", "compensating"],
    },
    "d7-lessons-learned-exercises": {
        "tags": ["d7-lessons-governance", "d6-tabletop-executive"],
        "keywords": ["lessons learned", "tabletop", "exercise", "mandatory vacation", "job rotation"],
    },
    "d8-sdlc-phases-security": {
        "tags": ["d8-ssdlc-governance", "d8-sec-req-early"],
        "keywords": ["sdlc", "requirements", "design", "deployment", "maintenance"],
    },
    "d8-dev-models-agile-devsecops": {
        "tags": ["d8-devsecops-strategy", "d8-release-governance"],
        "keywords": ["agile", "devsecops", "waterfall", "spiral", "ci/cd"],
    },
    "d8-owasp-top-10": {
        "tags": ["d8-threat-modeling"],
        "keywords": ["owasp", "injection", "xss", "csrf", "broken authentication"],
    },
    "d8-secure-coding-practices": {
        "tags": ["d8-coding-standards", "d8-code-review-risk"],
        "keywords": ["input validation", "output encoding", "parameterized", "secure coding"],
    },
    "d8-database-security": {
        "tags": ["d8-testing-gates"],
        "keywords": ["sql injection", "polyinstantiation", "inference", "aggregation", "database view"],
    },
    "d8-api-security": {
        "tags": ["d8-release-governance"],
        "keywords": ["api security", "rate limiting", "api key", "oauth"],
    },
    "d8-sbom-supply-chain": {
        "tags": ["d8-sbom-governance"],
        "keywords": ["sbom", "software composition", "supply chain", "code signing"],
    },
    "d8-ai-ml-security": {
        "tags": ["d8-defect-governance"],
        "keywords": ["adversarial", "data poisoning", "machine learning", "ai security", "model integrity"],
    },
}
