"""
CISSP action-word sets — each template only uses compatible phrasing.
Mixing FIRST/NEXT/LEAST with the wrong answer breaks exam realism.
"""

ACTION_BEST = [
    "What is the BEST course of action?",
    "Which action is MOST appropriate?",
    "Which option would a security leader choose as the PRIMARY focus?",
    "Which approach BEST balances security with business continuity?",
    "Which response BEST reduces organizational risk with minimal disruption?",
    "What is the BEST long-term solution rather than a one-time fix?",
    "Which decision BEST demonstrates due care?",
]

ACTION_FIRST = [
    "What should you do FIRST?",
    "What should occur BEFORE any technical remediation?",
    "What should leadership approve BEFORE implementation begins?",
]

ACTION_NEXT = [
    "What is the NEXT step after initial assessment?",
]

ACTION_PRIORITY = [
    "Which response should take PRIORITY?",
    "What is the MOST significant risk to address from a management viewpoint?",
    "What represents the GREATEST need from a governance perspective?",
]

ACTION_LEAST = [
    "Which action is LEAST appropriate in this situation?",
]

ALL_STANDARD = ACTION_BEST + ACTION_FIRST + ACTION_PRIORITY
ALL_WITH_NEXT = ACTION_BEST + ACTION_FIRST + ACTION_NEXT + ACTION_PRIORITY
LEAST_ONLY = ACTION_LEAST
