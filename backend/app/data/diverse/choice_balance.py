"""Balance A–D choice lengths so the correct answer is not obvious by length."""

from __future__ import annotations

import hashlib
import random
import re

from app.data.diverse.distractor_polish import polish_wrong_options

_EXPANSION_SUFFIXES = [
    " with defined ownership, measurable criteria, and executive accountability.",
    " subject to documented risk acceptance and periodic independent assurance.",
    " aligned to regulatory obligations and the organization's stated risk appetite.",
    " including coordination with legal, audit, and affected business stakeholders.",
    " after formal governance review and approval by designated risk owners.",
    " with escalation paths, exception tracking, and board-visible reporting.",
    " consistent with enterprise policy hierarchy and business continuity requirements.",
]

_EXPANSION_PREFIXES = [
    "Formally ",
    "Require the business to ",
    "Direct leadership to ",
    "Mandate that teams ",
]


def _seed_index(seed: str, modulo: int) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest(), 16) % modulo


def _char_len(text: str) -> int:
    return len(text.strip())


def _expand_option(text: str, min_len: int, seed: str) -> str:
    out = text.strip()
    if not out.endswith("."):
        out += "."
    rng = random.Random(seed)
    suffixes = _EXPANSION_SUFFIXES[:]
    rng.shuffle(suffixes)
    guard = 0
    while _char_len(out) < min_len and guard < 8:
        suffix = suffixes[guard % len(suffixes)]
        if suffix.strip(".") not in out:
            out = out.rstrip(".") + suffix
        guard += 1
    if _char_len(out) < min_len and _char_len(text) < 40:
        prefix = _EXPANSION_PREFIXES[_seed_index(seed, len(_EXPANSION_PREFIXES))]
        body = text.strip()
        if body:
            body = body[0].upper() + body[1:]
        out = prefix + body
        if not out.endswith("."):
            out += "."
    return out


def _trim_option(text: str, max_len: int) -> str:
    out = text.strip()
    if _char_len(out) <= max_len:
        return out
    parts = re.split(r",\s+", out)
    if len(parts) >= 2:
        candidate = parts[0].strip()
        if not candidate.endswith("."):
            candidate += "."
        if _char_len(candidate) <= max_len:
            return candidate
        m = re.match(r"^(.+?[.!?])", out)
        if m and _char_len(m.group(1)) <= max_len:
            return m.group(1).strip()
    if _char_len(out) > max_len:
        trimmed = out[: max_len - 1].rsplit(" ", 1)[0]
        if not trimmed.endswith("."):
            trimmed += "."
        return trimmed
    return out


def balance_choice_set(
    correct: str,
    wrong: list[str],
    domain: int,
    seed: str,
) -> tuple[str, list[str]]:
    """Return correct + three wrong options with similar length."""
    polished = polish_wrong_options(correct, wrong, domain, seed)
    rng = random.Random(seed)

    stats_correct = _char_len(correct)
    avg_wrong = sum(_char_len(w) for w in polished) / len(polished) if polished else stats_correct
    target = int(round((stats_correct + avg_wrong * 3) / 4))
    target = max(target, 85)
    band_low = int(target * 0.82)
    band_high = int(target * 1.12)

    balanced_wrong: list[str] = []
    for i, w in enumerate(polished):
        item = w
        if _char_len(item) < band_low:
            item = _expand_option(item, band_low, f"{seed}-exp-{i}")
        if _char_len(item) > band_high + 30:
            item = _trim_option(item, band_high + 10)
        balanced_wrong.append(item)

    balanced_correct = correct.strip()
    if not balanced_correct.endswith("."):
        balanced_correct += "."

    wrong_max = max(_char_len(w) for w in balanced_wrong)
    correct_len = _char_len(balanced_correct)

    if correct_len > wrong_max + 18:
        if rng.random() < 0.55:
            balanced_correct = _trim_option(balanced_correct, wrong_max + rng.randint(0, 12))
        else:
            idx = max(range(3), key=lambda i: _char_len(balanced_wrong[i]))
            balanced_wrong[idx] = _expand_option(
                balanced_wrong[idx],
                correct_len - rng.randint(0, 8),
                f"{seed}-pad-{idx}",
            )

    if rng.random() < 0.35:
        idx = rng.randint(0, 2)
        longest = max([_char_len(balanced_correct)] + [_char_len(w) for w in balanced_wrong])
        balanced_wrong[idx] = _expand_option(
            balanced_wrong[idx],
            longest + rng.randint(5, 25),
            f"{seed}-decoy-{idx}",
        )

    all_lens = [_char_len(balanced_correct)] + [_char_len(w) for w in balanced_wrong]
    median = sorted(all_lens)[2]
    floor = int(median * 0.78)
    for i, w in enumerate(balanced_wrong):
        if _char_len(w) < floor:
            balanced_wrong[i] = _expand_option(w, floor, f"{seed}-floor-{i}")

    return balanced_correct, balanced_wrong


def is_length_giveaway(correct: str, wrong: list[str]) -> bool:
    c = _char_len(correct)
    if not wrong:
        return False
    wrong_lens = [_char_len(w) for w in wrong]
    avg = sum(wrong_lens) / len(wrong_lens)
    return c > avg * 1.35 and c > max(wrong_lens) + 15
