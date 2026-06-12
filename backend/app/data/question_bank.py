"""CISSP question bank — ISC2 April 2024 outline + scenario generator."""

from app.data.domains import (
    BANK_VERSION,
    MAX_SCALED,
    MIN_QUESTION_COUNT,
    PASS_SCALED,
    DOMAIN_NAMES,
    DOMAIN_WEIGHTS,
    get_domain_info,
)
from app.data.scenario_generator import generate_all_questions, get_all_questions
