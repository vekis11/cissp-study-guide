"""Cloud Security and AI Security scenario items for the main CISSP exam bank."""

from __future__ import annotations

import hashlib

from app.data.domains import DOMAIN_NAMES
from app.data.diverse.choice_balance import balance_choice_set
from app.data.diverse.stem_formats import shuffle_choices

CLOUD_AI_TAG = "cloud-ai-exam"

CLOUD_AI_ITEMS: list[dict] = [
    {
        "domain": 3,
        "topic_id": "d3-cloud-shared-responsibility",
        "source_topic": "Cloud shared responsibility",
        "difficulty": "medium",
        "stem": (
            "A retailer moved loyalty and pricing workloads to a public cloud before peak season. "
            "After an outage, executives cannot agree on who failed to patch a customer-facing API "
            "or who owns encryption key rotation. Which action is MOST appropriate to reduce "
            "recurring accountability gaps?"
        ),
        "correct": (
            "Document a shared responsibility matrix with control ownership, evidence expectations, "
            "and escalation paths before scaling further"
        ),
        "wrong": [
            "Assume the cloud provider owns all security controls unless contract language says otherwise",
            "Transfer accountability to the vendor's SOC 2 report and stop internal control testing",
            "Disable auto-scaling until every team completes generic cloud awareness training",
        ],
        "explanation": (
            "Shared responsibility must be explicit before incidents expose gaps. A matrix ties "
            "business services to owned controls so leadership can govern risk rather than debate "
            "after an outage."
        ),
    },
    {
        "domain": 5,
        "topic_id": "d5-cloud-iam-misconfig",
        "source_topic": "Cloud IAM",
        "difficulty": "hard",
        "stem": (
            "A fintech startup discovered a storage bucket with sensitive loan records exposed to "
            "anonymous read access after a rushed cloud migration. Developers used long-lived access "
            "keys shared in chat. Which control BEST mitigates the risk described while preserving "
            "delivery speed?"
        ),
        "correct": (
            "Enforce least-privilege IAM roles, eliminate standing keys, and require short-lived "
            "credentials with centralized logging"
        ),
        "wrong": [
            "Rotate the exposed keys monthly while keeping the same broad permissions model",
            "Block all external access to cloud APIs until the next major release cycle",
            "Rely on the cloud provider's default encryption settings without changing access policies",
        ],
        "explanation": (
            "Misconfiguration and shared keys are people-and-process failures as much as technical ones. "
            "Least privilege with ephemeral credentials reduces blast radius while keeping teams productive."
        ),
    },
    {
        "domain": 2,
        "topic_id": "d2-cloud-data-residency",
        "source_topic": "Cloud data residency",
        "difficulty": "medium",
        "stem": (
            "A healthcare SaaS vendor stores patient analytics in multiple regions to improve "
            "performance. Legal counsel warns that cross-border replication may violate contractual "
            "and regulatory constraints. What should the security leader recommend FIRST?"
        ),
        "correct": (
            "Map data flows to classification and residency requirements, then align cloud regions "
            "and replication policies to approved locations"
        ),
        "wrong": [
            "Enable the fastest global replication tier to minimize clinical dashboard latency",
            "Ask each customer to accept all regions in a click-through agreement at signup",
            "Move encryption key management to the provider without reviewing data location controls",
        ],
        "explanation": (
            "Residency decisions start with what data exists, where it may legally reside, and who "
            "owns the risk. Technical replication choices follow that business and legal boundary."
        ),
    },
    {
        "domain": 8,
        "topic_id": "d8-ai-sdlc-governance",
        "source_topic": "AI in the SDLC",
        "difficulty": "hard",
        "stem": (
            "A SaaS company plans to embed a generative AI assistant into its customer support portal. "
            "Product wants to ship in two sprints using a third-party model API. Privacy and legal "
            "have not reviewed training data sources or output liability. Which course of action is BEST?"
        ),
        "correct": (
            "Define AI use policies, data handling boundaries, and human oversight requirements "
            "before production integration"
        ),
        "wrong": [
            "Launch behind a beta flag and collect user feedback before involving governance teams",
            "Rely on the model vendor's terms of service to cover all customer data protection obligations",
            "Disable logging of AI prompts to reduce storage costs during the pilot",
        ],
        "explanation": (
            "AI features inherit SDLC and data-protection obligations. Governance must precede "
            "integration so the business can defend how data is used and how harmful outputs are handled."
        ),
    },
    {
        "domain": 3,
        "topic_id": "d3-ai-model-integrity",
        "source_topic": "AI model integrity",
        "difficulty": "hard",
        "stem": (
            "An insurance firm uses a machine learning model to flag potentially fraudulent claims. "
            "Security learns that an external data feed used for retraining was altered without "
            "integrity checks. Which response is MOST effective given the business constraints?"
        ),
        "correct": (
            "Suspend automated decisions fed by the affected pipeline, validate model integrity, "
            "and retrain only from trusted sources with change control"
        ),
        "wrong": [
            "Continue automated denials because manual review would overwhelm adjusters this quarter",
            "Retrain immediately on all available data to restore model accuracy as fast as possible",
            "Publish the model weights internally so analysts can spot poisoning themselves",
        ],
        "explanation": (
            "Poisoned training data can silently bias business decisions. Containment and verified "
            "retraining protect customers and the firm while preserving auditability."
        ),
    },
    {
        "domain": 7,
        "topic_id": "d7-cloud-incident-response",
        "source_topic": "Cloud incident response",
        "difficulty": "medium",
        "stem": (
            "A multinational enterprise suspects credential theft in its cloud control plane. "
            "Workloads span three providers and a managed SIEM. The CISO needs the NEXT step "
            "after confirming unauthorized API activity."
        ),
        "correct": (
            "Contain active sessions and keys across affected accounts while preserving logs "
            "for coordinated investigation"
        ),
        "wrong": [
            "Rebuild every cloud subscription before determining scope to guarantee cleanliness",
            "Wait for each provider's support ticket response before taking internal containment steps",
            "Notify all customers publicly before the internal team understands impact",
        ],
        "explanation": (
            "Cloud incidents require fast containment across identities and APIs without destroying "
            "evidence. Scope and notification follow once the team stabilizes the environment."
        ),
    },
    {
        "domain": 4,
        "topic_id": "d4-casb-saas-governance",
        "source_topic": "SaaS and CASB",
        "difficulty": "medium",
        "stem": (
            "Employees adopted multiple unsanctioned SaaS file-sharing tools after a merger. "
            "DLP alerts show regulated contract data leaving approved storage. Which control "
            "BEST mitigates the risk described?"
        ),
        "correct": (
            "Implement sanctioned SaaS governance with CASB visibility, policy enforcement, "
            "and approved alternatives for collaboration"
        ),
        "wrong": [
            "Block all HTTPS traffic except the corporate web proxy without offering replacements",
            "Trust user training alone because shadow IT usually declines after one memo",
            "Allow any SaaS vendor that offers encryption marketing claims on its website",
        ],
        "explanation": (
            "Shadow SaaS is a business workflow problem. Visibility plus enforced policy and "
            "approved paths reduce data loss without ignoring how people actually work."
        ),
    },
    {
        "domain": 1,
        "topic_id": "d1-ai-risk-governance",
        "source_topic": "AI risk governance",
        "difficulty": "hard",
        "stem": (
            "A bank's marketing team wants to use an AI system to personalize offers using "
            "transaction history. Compliance is concerned about bias, explainability, and model "
            "drift over time. What is the PRIMARY objective from a security management perspective?"
        ),
        "correct": (
            "Establish governance that defines acceptable use, monitoring, and accountability "
            "for AI-driven decisions affecting customers"
        ),
        "wrong": [
            "Maximize model accuracy regardless of interpretability to beat competitor campaigns",
            "Defer all AI oversight until regulators publish final rules in every jurisdiction",
            "Outsource bias testing entirely to the model vendor without internal validation",
        ],
        "explanation": (
            "AI risk is a governance and accountability problem at CISSP level. Leadership must "
            "define how models are used, monitored, and owned — not only how accurate they are."
        ),
    },
    {
        "domain": 8,
        "topic_id": "d8-llm-prompt-injection",
        "source_topic": "LLM application security",
        "difficulty": "hard",
        "stem": (
            "An enterprise chatbot retrieves internal documents and can trigger workflow actions "
            "when users ask questions. Pen testers showed that crafted prompts can exfiltrate "
            "confidential snippets and approve low-value purchases. Which action is LEAST appropriate?"
        ),
        "correct": (
            "Treat the LLM as fully trusted because it runs inside the corporate network perimeter"
        ),
        "wrong": [
            "Apply input validation, output filtering, and least-privilege integrations for automated actions",
            "Log and monitor high-risk prompts and workflow triggers for anomalous patterns",
            "Segment the chatbot's access to documents and transactions based on user authorization",
        ],
        "explanation": (
            "LLM integrations blur application and data boundaries. Trusting perimeter placement alone "
            "ignores prompt injection and over-privileged automation — the LEAST appropriate stance."
        ),
    },
    {
        "domain": 6,
        "topic_id": "d6-cloud-assurance-testing",
        "source_topic": "Cloud assurance testing",
        "difficulty": "medium",
        "stem": (
            "A security team plans annual testing of production cloud workloads that process "
            "payment data. The cloud provider prohibits certain intrusive tests without notice. "
            "Which factor should NOT be taken into consideration when planning the schedule?"
        ),
        "correct": "Desire to experiment with new testing tools",
        "wrong": [
            "Sensitivity of the information stored on the system",
            "Desirability of the system to attackers",
            "Difficulty of performing the test within provider constraints",
        ],
        "explanation": (
            "Testing schedules should reflect data sensitivity, threat exposure, and feasibility — "
            "not tool experimentation, which is unrelated to risk-based prioritization."
        ),
    },
    {
        "domain": 7,
        "topic_id": "d7-malware-containment-priority",
        "source_topic": "Malware incident response",
        "difficulty": "medium",
        "stem": (
            "A hospital SOC sees two concurrent malware events after a phishing campaign. "
            "One strain spreads to new systems without user interaction; the other appears only "
            "where staff installed a fake PDF tool disguised as IT support software. The incident "
            "commander must brief leadership on containment priorities. Which distinction is MOST "
            "important?"
        ),
        "correct": (
            "One threat self-replicates across the network; the other requires user execution "
            "and does not self-replicate"
        ),
        "wrong": [
            "One threat spreads via e-mail while the other never uses e-mail",
            "One threat is malicious code while the other is not considered malicious",
            "Both threats behave identically once inside the environment",
        ],
        "explanation": (
            "Worms self-replicate and demand network-focused containment urgency. Trojans rely on "
            "deception and user action — the response emphasis differs even though both are malware."
        ),
    },
    {
        "domain": 4,
        "topic_id": "d4-zero-trust-cloud",
        "source_topic": "Zero trust in cloud",
        "difficulty": "hard",
        "stem": (
            "A CISO is modernizing remote access for cloud-hosted applications. Teams assume "
            "corporate VPN entry equals trust for internal APIs. Auditors want reduced lateral "
            "movement after credential theft. Which principle BEST reflects the target architecture?"
        ),
        "correct": (
            "Verify explicitly and grant least privilege for every access request regardless of network location"
        ),
        "wrong": [
            "Trust internal users because they authenticated to the VPN concentrator",
            "Rely on network segmentation alone without continuous authorization checks",
            "Disable logging on east-west traffic to improve cloud performance",
        ],
        "explanation": (
            "Zero trust removes implicit trust based on location. Every request is verified and "
            "scoped — especially critical when applications live outside a traditional perimeter."
        ),
    },
]


def _qid(domain: int, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:12]
    return f"ca-d{domain}-{h}"


def build_cloud_ai_exam_questions() -> list[dict]:
    built: list[dict] = []
    for i, item in enumerate(CLOUD_AI_ITEMS):
        seed = f"cloud-ai-{i}-{item['stem'][:48]}"
        balanced_correct, balanced_wrong = balance_choice_set(
            item["correct"], item["wrong"], item["domain"], seed
        )
        ca, cb, cc, cd, letter = shuffle_choices(
            balanced_correct, balanced_wrong, seed + balanced_correct
        )
        built.append({
            "id": _qid(item["domain"], seed),
            "domain": item["domain"],
            "domain_name": DOMAIN_NAMES[item["domain"]],
            "difficulty": item["difficulty"],
            "stem": item["stem"].strip(),
            "choice_a": ca,
            "choice_b": cb,
            "choice_c": cc,
            "choice_d": cd,
            "correct_choice": letter,
            "explanation": item["explanation"].strip(),
            "source_topic": item["source_topic"],
            "topic_id": item["topic_id"],
            "tags": f"diverse,direct-exam,manager,scenario,{CLOUD_AI_TAG},{item['topic_id']}",
        })
    return built
