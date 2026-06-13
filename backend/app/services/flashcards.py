"""Flashcards derived from cheat-sheet catalog topics."""

from app.data.cheat_sheet.catalog import CHEAT_SHEET


def build_flashcards(domain: int | None = None, topic_id: str | None = None) -> list[dict]:
    cards: list[dict] = []
    for dom in CHEAT_SHEET["domains"]:
        d_num = dom["domain"]
        if domain is not None and d_num != domain:
            continue
        for section in dom.get("sections", []):
            tid = section.get("topic_id", "")
            if topic_id and tid != topic_id:
                continue
            importance = section.get("importance", "good")
            front = section.get("title", tid)
            back = section.get("content", "").strip()
            if not back and section.get("scenarios"):
                back = section["scenarios"][0].get("answer", "")
            if not back:
                continue
            cards.append({
                "id": tid,
                "domain": d_num,
                "domain_name": dom["name"],
                "topic_id": tid,
                "importance": importance,
                "front": front,
                "back": back,
            })
    return cards
