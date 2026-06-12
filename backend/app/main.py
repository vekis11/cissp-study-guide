from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from app.config import CORS_ORIGINS, FRONTEND_DIST
from app.database import get_db
from app.data.domains import get_domain_info, PASS_SCALED
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.schemas import (
    AnalyticsOut,
    AnswerRequest,
    AnswerResult,
    DomainInfo,
    QuestionOut,
    SessionOut,
    SessionProgress,
    SettingsOut,
    SettingsUpdate,
    StartSessionRequest,
    SubmitResult,
)
from app.seed import seed_database
from app.services.analytics import build_analytics
from app.services.cat_engine import (
    CAT_MAX_QUESTIONS,
    CAT_MIN_QUESTIONS,
    CAT_TIME_SECONDS,
    compute_score,
    get_missed_question_ids,
    pick_next_cat_question,
    select_questions,
    session_domain_counts,
    should_stop_cat,
)
from app.services.grading import compute_cissp_scaled, grade_label, passed_cissp
from app.services.manager_explanation import build_manager_feedback
from app.static_files import mount_frontend

app = FastAPI(
    title="CISSP Study Companion",
    description="CAT-style mock exams, daily practice, and domain mastery for all 8 CISSP domains.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == ["*"] else CORS_ORIGINS,
    allow_credentials=CORS_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    count = seed_database()
    print(f"CISSP Study: {count} questions loaded")
    if mount_frontend(app):
        print(f"PWA served from {FRONTEND_DIST} — install via browser on phone or PC")
    else:
        print("PWA static files not found — run: cd frontend && npm run build")


def _get_settings(db: Session) -> UserSettings:
    settings = db.query(UserSettings).first()
    if not settings:
        settings = UserSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _session_attempts(db: Session, session_id: int) -> list[Attempt]:
    return (
        db.query(Attempt)
        .options(joinedload(Attempt.question))
        .filter(Attempt.session_id == session_id)
        .order_by(Attempt.id)
        .all()
    )


def _session_to_out(db: Session, session: SessionRecord) -> SessionOut:
    session = (
        db.query(SessionRecord)
        .options(joinedload(SessionRecord.attempts).joinedload(Attempt.question))
        .filter(SessionRecord.id == session.id)
        .first()
    )
    return SessionOut.model_validate(session)


def _question_out(q: Question) -> QuestionOut:
    return QuestionOut.model_validate(q)


def _grade_and_finalize(db: Session, session: SessionRecord) -> SubmitResult:
    attempts = _session_attempts(db, session.id)
    for a in attempts:
        if a.selected_choice and a.is_correct is None and a.question:
            a.is_correct = a.selected_choice == a.question.correct_choice

    scaled, percent, correct, answered = compute_cissp_scaled(attempts)
    session.correct_count = correct
    session.score_percent = percent
    session.scaled_score = scaled
    session.total_questions = len([a for a in attempts if a.selected_choice])
    session.submitted = True
    session.completed_at = datetime.utcnow()
    db.commit()

    passed = passed_cissp(scaled)
    return SubmitResult(
        session=_session_to_out(db, session),
        scaled_score=scaled,
        score_percent=percent,
        passed=passed,
        grade_label=grade_label(scaled),
        pass_threshold_scaled=PASS_SCALED,
    )


def _append_cat_question(db: Session, session: SessionRecord, attempts: list[Attempt], last: Attempt) -> bool:
    """Add next adaptive question. Returns True if session should end."""
    answered = [a for a in attempts if a.selected_choice]
    correct = sum(1 for a in answered if a.is_correct)
    if should_stop_cat(len(answered), correct) or len(answered) >= session.total_questions:
        return True

    exclude = {a.question_id for a in attempts}
    domain_counts = session_domain_counts(answered)
    last_diff = last.question.difficulty if last.question else "medium"
    is_correct = bool(last.is_correct)
    next_q = pick_next_cat_question(db, exclude, last_diff, is_correct, domain_counts)
    if not next_q:
        return True
    db.add(Attempt(session_id=session.id, question_id=next_q.id))
    db.commit()
    return False


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "alive",
        "questions": db.query(Question).count(),
        "domains": 8,
        "pass_scaled": PASS_SCALED,
        "pwa": Path(FRONTEND_DIST).is_dir(),
        "installable": True,
    }


@app.get("/api/domains", response_model=list[DomainInfo])
def list_domains():
    return [DomainInfo(**d) for d in get_domain_info()]


@app.get("/api/questions/count")
def question_counts(db: Session = Depends(get_db)):
    counts = {}
    for d in range(1, 9):
        counts[str(d)] = db.query(Question).filter(Question.domain == d).count()
    counts["total"] = db.query(Question).count()
    counts["scenario"] = db.query(Question).filter(Question.tags.contains("scenario")).count()
    return counts


@app.get("/api/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return SettingsOut.model_validate(_get_settings(db))


@app.put("/api/settings", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    settings = _get_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return SettingsOut.model_validate(settings)


@app.get("/api/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)):
    return build_analytics(db)


@app.get("/api/missed")
def missed_questions(db: Session = Depends(get_db)):
    ids = get_missed_question_ids(db)
    questions = db.query(Question).filter(Question.id.in_(ids)).all() if ids else []
    qmap = {q.id: q for q in questions}
    return {
        "count": len(ids),
        "questions": [_question_out(qmap[i]).model_dump() for i in ids if i in qmap],
    }


@app.post("/api/sessions/start", response_model=SessionOut)
def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    settings = _get_settings(db)
    mode = req.practice_mode or settings.practice_mode

    if req.session_type == "mock_exam":
        max_q = min(max(req.count, CAT_MIN_QUESTIONS), CAT_MAX_QUESTIONS)
        mode = "exam"
        first_batch = select_questions(db, 1, cat_mode=True, difficulty="medium")
        if not first_batch:
            raise HTTPException(404, "No questions available")
        session = SessionRecord(
            mode=mode,
            session_type=req.session_type,
            total_questions=max_q,
            domain_filter=None,
        )
        db.add(session)
        db.flush()
        db.add(Attempt(session_id=session.id, question_id=first_batch[0].id))
        db.commit()
        return _session_to_out(db, session)

    count = min(req.count, 100)
    questions: list[Question] = []

    if req.session_type == "missed":
        missed_ids = get_missed_question_ids(db)
        if not missed_ids:
            raise HTTPException(404, "No missed questions yet — keep practicing!")
        pool = db.query(Question).filter(Question.id.in_(missed_ids)).all()
        qmap = {q.id: q for q in pool}
        questions = [qmap[i] for i in missed_ids if i in qmap][:count]
    elif req.session_type == "domain_test":
        if not req.domain:
            raise HTTPException(400, "Domain required for domain test")
        questions = select_questions(db, count, domain=req.domain)
    else:
        questions = select_questions(db, count)

    if not questions:
        raise HTTPException(404, "No questions available for this session")

    session = SessionRecord(
        mode=mode,
        session_type=req.session_type,
        total_questions=len(questions),
        domain_filter=req.domain,
    )
    db.add(session)
    db.flush()
    for q in questions:
        db.add(Attempt(session_id=session.id, question_id=q.id))
    db.commit()
    return _session_to_out(db, session)


@app.get("/api/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    return _session_to_out(db, session)


@app.get("/api/sessions/{session_id}/progress", response_model=SessionProgress)
def session_progress(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    attempts = _session_attempts(db, session_id)
    answered_list = [a for a in attempts if a.selected_choice]
    scaled, percent, _, answered = compute_cissp_scaled(attempts)
    max_q = session.total_questions if session.session_type == "mock_exam" else len(attempts)
    return SessionProgress(
        answered=answered,
        total_in_session=len(attempts),
        max_questions=max_q,
        can_submit=answered > 0 and not session.submitted,
        score_percent=percent,
        scaled_score=scaled,
        passed=passed_cissp(scaled),
        pass_threshold_scaled=PASS_SCALED,
    )


@app.get("/api/sessions/{session_id}/current")
def get_current_question(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")

    attempts = _session_attempts(db, session_id)
    answered = [a for a in attempts if a.selected_choice is not None]
    unanswered = [a for a in attempts if a.selected_choice is None]

    if session.session_type == "mock_exam" and not unanswered and not session.submitted:
        if len(answered) >= CAT_MIN_QUESTIONS:
            return {"complete": True, "session": _session_to_out(db, session), "cat_complete": True}

    if not unanswered:
        return {"complete": True, "session": _session_to_out(db, session)}

    current = unanswered[0]
    return {
        "complete": False,
        "index": len(answered) + 1,
        "total": session.total_questions if session.session_type == "mock_exam" else len(attempts),
        "answered": len(answered),
        "question": _question_out(current.question).model_dump(),
        "attempt_id": current.id,
        "flagged": current.flagged,
        "time_limit_seconds": CAT_TIME_SECONDS if session.session_type == "mock_exam" else None,
        "is_cat": session.session_type == "mock_exam",
    }


@app.post("/api/sessions/{session_id}/answer", response_model=AnswerResult)
def answer_question(session_id: int, req: AnswerRequest, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.submitted:
        raise HTTPException(400, "Session already submitted")

    attempt = (
        db.query(Attempt)
        .options(joinedload(Attempt.question))
        .filter(Attempt.session_id == session_id, Attempt.question_id == req.question_id)
        .first()
    )
    if not attempt:
        raise HTTPException(404, "Question not in this session")

    q = attempt.question
    is_correct = req.selected_choice == q.correct_choice
    attempt.selected_choice = req.selected_choice
    attempt.flagged = req.flagged
    attempt.answered_at = datetime.utcnow()
    attempt.is_correct = is_correct

    hide_feedback = session.mode == "exam" and not session.submitted
    db.commit()

    attempts = _session_attempts(db, session_id)
    scaled, percent, _, answered = compute_cissp_scaled(attempts)

    cat_done = False
    if session.session_type == "mock_exam" and not session.submitted:
        cat_done = _append_cat_question(db, session, attempts, attempt)
        attempts = _session_attempts(db, session_id)

    unanswered = [a for a in attempts if not a.selected_choice]
    if session.session_type == "mock_exam":
        session_complete = cat_done and not unanswered
    else:
        session_complete = len(unanswered) == 0

    if session_complete and not session.submitted and session.mode != "exam":
        _grade_and_finalize(db, session)

    if hide_feedback:
        return AnswerResult(
            is_correct=False,
            correct_choice="",
            explanation="",
            manager_brief="",
            approach_tips=[],
            score_percent=0.0,
            session_complete=session_complete,
        )

    feedback = build_manager_feedback(q)
    return AnswerResult(
        is_correct=is_correct,
        correct_choice=q.correct_choice,
        explanation=feedback["explanation"],
        manager_brief=feedback["manager_brief"],
        approach_tips=feedback["approach_tips"],
        score_percent=percent,
        session_complete=session_complete,
    )


@app.post("/api/sessions/{session_id}/submit", response_model=SubmitResult)
def submit_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.submitted:
        raise HTTPException(400, "Session already submitted")

    attempts = _session_attempts(db, session_id)
    answered = [a for a in attempts if a.selected_choice]
    if not answered:
        raise HTTPException(400, "No answered questions to grade")

    return _grade_and_finalize(db, session)


@app.get("/api/sessions/{session_id}/review")
def review_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.mode == "exam" and not session.submitted:
        raise HTTPException(400, "Submit session before reviewing answers")

    attempts = _session_attempts(db, session_id)
    results = []
    for a in attempts:
        if not a.selected_choice:
            continue
        feedback = build_manager_feedback(a.question)
        results.append({
            "attempt_id": a.id,
            "question": _question_out(a.question).model_dump(),
            "selected_choice": a.selected_choice,
            "correct_choice": a.question.correct_choice,
            "is_correct": a.is_correct,
            "explanation": feedback["explanation"],
            "manager_brief": feedback["manager_brief"],
            "approach_tips": feedback["approach_tips"],
            "flagged": a.flagged,
        })
    return {
        "session": _session_to_out(db, session),
        "results": results,
        "scaled_score": session.scaled_score,
        "passed": passed_cissp(session.scaled_score or 0),
        "pass_threshold_scaled": PASS_SCALED,
    }
