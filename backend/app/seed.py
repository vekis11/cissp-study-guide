from sqlalchemy import text
from sqlalchemy.orm import Session

from app.data.domains import BANK_VERSION, MIN_QUESTION_COUNT
from app.data.scenario_generator import get_all_questions
from app.database import SessionLocal, engine
from app.models import Base, Question


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
    sample = db.query(Question).filter(Question.tags.contains("bank-v7")).first()
    if not sample:
        return True
    return False


def seed_database(force: bool = False) -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _ensure_columns(db)
        if needs_reseed(db) or force:
            db.query(Question).delete()
            db.commit()
            print(f"Seeding question bank v{BANK_VERSION} (800+ diverse scenario questions)...")
            batch = []
            for q in get_all_questions():
                batch.append(Question(**q))
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
