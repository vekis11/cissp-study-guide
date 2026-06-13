"""Make distractors plausible CISSP-style options — almost right, but not the BEST."""

from __future__ import annotations

import hashlib
import re

# Obvious / extreme distractors that fail CISSP realism
_EXTREME = re.compile(
    r"\b("
    r"ignore|without any|block all|disable all|shut down|fire\b|terminate all|"
    r"ban\b|prohibit all|skip all|never\b|always deploy|immediately without|"
    r"delete all|no encryption|shared password|root account for everyone"
    r")\b",
    re.I,
)

_PLAUSIBLE_BY_DOMAIN: dict[int, list[str]] = {
    1: [
        "Issue an interim policy memo while deferring board approval until after integration.",
        "Require business units to self-certify compliance without independent validation.",
        "Prioritize contractual indemnification over documented control assurance from the partner.",
        "Accept the risk informally at the director level without a formal exception register.",
        "Commission a point-in-time assessment but delay remediation tracking until the next quarter.",
        "Mandate a technical control standard before defining enterprise risk appetite and ownership.",
    ],
    2: [
        "Apply the corporate classification scheme only to new data created after go-live.",
        "Encrypt data in transit but rely on operating-system defaults for data at rest.",
        "Assign custodianship to IT operations without formal data-owner sign-off on handling rules.",
        "Sanitize media using the fastest method available without verifying method against sensitivity.",
        "Extend retention indefinitely to avoid accidental loss during the migration window.",
    ],
    3: [
        "Deploy a single-vendor security stack to simplify operations across all business units.",
        "Harden production systems first and backfill architecture standards documentation later.",
        "Use encryption for regulated data only, leaving other assets to departmental discretion.",
        "Approve the design based on vendor assurance letters without independent design review.",
        "Implement network segmentation in one region as a pilot before enterprise standards exist.",
    ],
    4: [
        "Enable TLS for customer-facing apps while leaving internal management traffic unencrypted temporarily.",
        "Consolidate VLANs to reduce operational overhead during the network refresh.",
        "Deploy a new firewall rule set globally before change-advisory board review completes.",
        "Allow remote access via VPN without enforcing device posture checks during rollout.",
        "Standardize on one wireless vendor solution without updating the enterprise wireless policy.",
    ],
    5: [
        "Grant privileged access with time limits but skip periodic access recertification.",
        "Deploy MFA for administrators only, leaving standard users on password-only authentication.",
        "Centralize identity in a new directory without reconciling orphaned accounts from legacy systems.",
        "Implement role-based access using department titles rather than least-privilege job functions.",
        "Issue shared break-glass credentials to the operations team for faster incident response.",
    ],
    6: [
        "Run automated vulnerability scans monthly without tying results to asset criticality ranking.",
        "Treat a clean penetration test report as evidence that production controls are effective long term.",
        "Remediate critical findings in production first and document exceptions afterward.",
        "Rely on vendor SOC reports without mapping controls to internal policy requirements.",
        "Perform code review only on externally facing applications to meet the release deadline.",
    ],
    7: [
        "Contain the incident by isolating affected hosts before notifying legal and communications.",
        "Restore the most critical service from backup before verifying backup integrity and scope.",
        "Escalate to senior leadership after technical eradication steps are complete.",
        "Preserve disk images on affected servers but continue production processing on identical builds.",
        "Engage external counsel after public disclosure requirements have been assessed internally.",
    ],
    8: [
        "Add dynamic application testing to the release pipeline but skip threat modeling for legacy modules.",
        "Remediate findings in the current sprint while deferring secure SDLC gate updates.",
        "Mandate secure coding training once without embedding checks in CI/CD workflows.",
        "Accept third-party library risk based on popularity scores rather than composition analysis.",
        "Deploy a web application firewall in production as the primary control for input validation.",
    ],
}


def _seed_index(seed: str, modulo: int) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest(), 16) % modulo


def _too_extreme(text: str) -> bool:
    return bool(_EXTREME.search(text))


def _pick_plausible(domain: int, seed: str, exclude: set[str]) -> str:
    pool = [p for p in _PLAUSIBLE_BY_DOMAIN.get(domain, _PLAUSIBLE_BY_DOMAIN[1]) if p not in exclude]
    if not pool:
        pool = _PLAUSIBLE_BY_DOMAIN[1]
    return pool[_seed_index(seed, len(pool))]


def _derive_almost_right(correct: str, seed: str) -> str:
    """Build a second-best option by narrowing scope or reversing sequence emphasis."""
    templates = [
        f"Proceed with the same initiative but limit scope to the highest-risk business unit first.",
        f"Adopt a similar control approach after the current project phase completes.",
        f"Apply the recommended measure to new systems only, exempting legacy environments temporarily.",
        f"Implement the control with vendor guidance while internal policy is still being revised.",
        f"Use the same strategy for internal users first, extending to third parties in a later phase.",
    ]
    base = templates[_seed_index(seed, len(templates))]
    if len(correct) > 40:
        return base
    return f"{base} This addresses part of the requirement but not the full governance expectation."


def polish_wrong_options(
    correct: str,
    wrong: list[str],
    domain: int,
    seed: str,
) -> list[str]:
    """Return three plausible distractors; none should be obviously absurd."""
    exclude = {correct.strip().lower()}
    polished: list[str] = []
    source = wrong[:3] if wrong else []

    for i in range(3):
        item_seed = f"{seed}-wrong-{i}"
        if i < len(source):
            item = source[i].strip()
            if _too_extreme(item) or len(item) < 25:
                item = _pick_plausible(domain, item_seed, exclude)
            elif item.lower() in exclude:
                item = _derive_almost_right(correct, item_seed)
            else:
                item = re.sub(r"\b(only|never|always|all|immediately)\b", "primarily", item, flags=re.I)
        else:
            item = _pick_plausible(domain, item_seed, exclude)

        if item.lower() in exclude:
            item = _derive_almost_right(correct, f"{item_seed}-alt")

        polished.append(item)
        exclude.add(item.lower())

    if not any(len(p) > 50 for p in polished):
        idx = _seed_index(f"{seed}-inject", 3)
        polished[idx] = _derive_almost_right(correct, f"{seed}-inject")

    return polished[:3]
