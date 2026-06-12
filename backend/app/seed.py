from sqlalchemy import text
from sqlalchemy.orm import Session

from app.data.domains import BANK_VERSION, MIN_QUESTION_COUNT
from app.data.scenario_generator import get_all_questions
from app.database import SessionLocal, engine
from app.models import Base, Question, UserSettings


def _ensure_columns(db: Session) -> None:
    """Add scaled_score column to existing SQLite DBs."""
    try:
        db.execute(text("SELECT scaled_score FROM sessions LIMIT 1"))
    except Exception:
        db.rollback()
        try:
            db.execute(text("ALTER TABLE sessions ADD COLUMN scaled_score FLOAT"))
            db.commit()
        except Exception:
            db.rollback()


def needs_reseed(db: Session) -> bool:
    count = db.query(Question).count()
    if count < MIN_QUESTION_COUNT:
        return True
    sample = db.query(Question).filter(Question.tags.contains("bank-v4")).first()
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
            print(f"Seeding question bank v{BANK_VERSION} (1000+ scenario questions)...")
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
        if not db.query(UserSettings).first():
            db.add(UserSettings())
            db.commit()
        return db.query(Question).count()
    finally:
        db.close()
