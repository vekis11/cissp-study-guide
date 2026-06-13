from sqlalchemy import text
from sqlalchemy.orm import Session

from app.data.domains import BANK_VERSION, MIN_QUESTION_COUNT
from app.data.scenario_generator import get_all_questions
from app.data.cheat_sheet.topic_mapping import TOPIC_SCENARIO_MAP
from app.database import SessionLocal, engine
from app.models import Base, Question

QUESTION_FIELDS = {c.name for c in Question.__table__.columns}


def _question_from_dict(q: dict) -> Question:
    return Question(**{k: v for k, v in q.items() if k in QUESTION_FIELDS})

from app.services.cissp_exam_rules import DIFFICULTY_TO_BLOOM

DIFFICULTY_TO_LEVEL = DIFFICULTY_TO_BLOOM
DOMAIN_REFERENCES = {
    1: "ISC2 CBK Domain 1; NIST SP 800-30; ISO 27001",
    2: "ISC2 CBK Domain 2; NIST SP 800-88",
    3: "ISC2 CBK Domain 3; NIST SP 800-53",
    4: "ISC2 CBK Domain 4; NIST SP 800-207",
    5: "ISC2 CBK Domain 5; NIST SP 800-63",
    6: "ISC2 CBK Domain 6; ISO 27001 A.8",
    7: "ISC2 CBK Domain 7; NIST SP 800-61",
    8: "ISC2 CBK Domain 8; OWASP ASVS",
}


def _tag_to_topic_id() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for topic_id, cfg in TOPIC_SCENARIO_MAP.items():
        for tag in cfg.get("tags", []):
            mapping[tag] = topic_id
    return mapping


def _backfill_question_metadata(db: Session) -> None:
    tag_map = _tag_to_topic_id()
    updated = False
    for q in db.query(Question).all():
        changed = False
        if not q.topic_id:
            for part in q.tags.split(","):
                tag = part.strip()
                if tag in tag_map:
                    q.topic_id = tag_map[tag]
                    changed = True
                    break
            if not q.topic_id and q.source_topic:
                q.topic_id = q.source_topic[:64]
                changed = True
        if not q.difficulty_level:
            q.difficulty_level = DIFFICULTY_TO_LEVEL.get(q.difficulty, 3)
            changed = True
        if not q.reference:
            q.reference = DOMAIN_REFERENCES.get(q.domain, "ISC2 CBK")
            changed = True
        if changed:
            updated = True
    if updated:
        db.commit()


def _add_column_if_missing(db: Session, table: str, column: str, ddl: str) -> None:
    try:
        db.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
    except Exception:
        db.rollback()
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
            db.commit()
        except Exception:
            db.rollback()


def _ensure_columns(db: Session) -> None:
    """Migrate existing SQLite DBs."""
    _add_column_if_missing(db, "sessions", "scaled_score", "FLOAT")
    _add_column_if_missing(db, "sessions", "user_id", "VARCHAR(64) DEFAULT 'legacy'")
    _add_column_if_missing(db, "user_settings", "user_id", "VARCHAR(64)")
    _add_column_if_missing(db, "user_settings", "daily_prioritize_unseen", "BOOLEAN DEFAULT 1")
    _add_column_if_missing(db, "user_settings", "daily_weak_domain_bias", "BOOLEAN DEFAULT 1")
    _add_column_if_missing(db, "user_settings", "daily_avoid_repeats", "BOOLEAN DEFAULT 1")
    _add_column_if_missing(db, "sessions", "time_limit_seconds", "INTEGER")
    _add_column_if_missing(db, "sessions", "max_wrong_allowed", "INTEGER")
    _add_column_if_missing(db, "sessions", "theta_proxy", "FLOAT")
    _add_column_if_missing(db, "sessions", "pass_likelihood", "FLOAT")
    _add_column_if_missing(db, "questions", "difficulty_level", "INTEGER")
    _add_column_if_missing(db, "questions", "topic_id", "VARCHAR(64)")
    _add_column_if_missing(db, "questions", "reference", "VARCHAR(256)")
    _add_column_if_missing(db, "attempts", "time_spent_seconds", "INTEGER")
    _add_column_if_missing(db, "attempts", "confidence", "INTEGER")
    try:
        db.execute(text("UPDATE sessions SET user_id = 'legacy' WHERE user_id IS NULL OR user_id = ''"))
        db.execute(text("UPDATE user_settings SET user_id = 'legacy' WHERE user_id IS NULL OR user_id = ''"))
        db.commit()
    except Exception:
        db.rollback()


def needs_reseed(db: Session) -> bool:
    count = db.query(Question).count()
    if count < MIN_QUESTION_COUNT:
        return True
    sample = db.query(Question).filter(Question.tags.contains("bank-v12")).first()
    if not sample:
        return True
    return False


def seed_database(force: bool = False) -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _ensure_columns(db)
        _backfill_question_metadata(db)
        if needs_reseed(db) or force:
            db.query(Question).delete()
            db.commit()
            print(f"Seeding question bank v{BANK_VERSION} ({MIN_QUESTION_COUNT}+ scenario questions)...")
            batch = []
            for q in get_all_questions():
                batch.append(_question_from_dict(q))
                if len(batch) >= 200:
                    db.add_all(batch)
                    db.commit()
                    batch = []
            if batch:
                db.add_all(batch)
                db.commit()
        return db.query(Question).count()
    finally:
        db.close()
