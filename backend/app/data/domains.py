DOMAIN_NAMES = {
    1: "Security and Risk Management",
    2: "Asset Security",
    3: "Security Architecture and Engineering",
    4: "Communication and Network Security",
    5: "Identity and Access Management",
    6: "Security Assessment and Testing",
    7: "Security Operations",
    8: "Software Development Security",
}

DOMAIN_WEIGHTS = {1: 0.16, 2: 0.10, 3: 0.13, 4: 0.13, 5: 0.13, 6: 0.12, 7: 0.13, 8: 0.10}

PASS_SCALED = 700
MAX_SCALED = 1000
BANK_VERSION = 7
MIN_QUESTION_COUNT = 800


def get_domain_info():
    return [
        {"id": d, "name": DOMAIN_NAMES[d], "weight": DOMAIN_WEIGHTS[d]}
        for d in sorted(DOMAIN_NAMES)
    ]
