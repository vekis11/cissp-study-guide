from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from app.config import ADMIN_API_KEY, CORS_ORIGINS, FRONTEND_DIST
from app.database import get_db
from app.data.domains import get_domain_info, PASS_SCALED
from app.models import Attempt, Question, SessionRecord, UserSettings
from app.data.cheat_sheet.catalog import CHEAT_SHEET
from app.schemas import (
    AnalyticsOut,
    AnswerRequest,
    FlagUpdateRequest,
    AnswerResult,
    DomainInfo,
    DomainModuleOut,
    FlashcardOut,
    QuestionOut,
    SessionOut,
    SessionProgress,
    SettingsOut,
    SettingsUpdate,
    StartSessionRequest,
    StudyGuideOut,
    StudyPlanOut,
    SubmitResult,
)
from app.seed import seed_database
from app.services.analytics import build_analytics, export_analytics_csv
from app.services.flashcards import build_flashcards
from app.services.irt_cat import THETA_START, pass_likelihood, should_stop_theta, update_theta
from app.services.spaced_repetition import update_review
from app.services.cat_engine import (
    CAT_MAX_QUESTIONS,
    CAT_MIN_QUESTIONS,
    CAT_TIME_SECONDS,
    compute_score,
    get_bank_coverage,
    get_flagged_question_ids,
    get_missed_question_ids,
    pick_next_cat_question,
    select_daily_questions,
    select_questions,
    session_domain_counts,
    should_stop_cat,
)
from app.services.answer_key import (
    grade_answer,
    parse_choices,
    question_type_for,
    validate_submission,
)
from app.services.grading import compute_cissp_scaled, grade_label, passed_cissp
from app.services.manager_explanation import build_manager_feedback
from app.services.study_guide import (
    build_study_guide_payload,
    select_guide_drill_questions,
    select_topic_drill_questions,
)
from app.services.study_plan import build_study_plan
from app.static_files import mount_frontend
from app.user_context import get_user_id

app = FastAPI(
    title="CISSP Study Companion",
    description="CAT-style mock exams, daily practice, and domain mastery for all 8 CISSP domains.",
    version="3.0.0",
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


def _get_settings(db: Session, user_id: str) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
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


def _wrong_count(attempts: list[Attempt]) -> int:
    return sum(1 for a in attempts if a.selected_choice and a.is_correct is False)


def _seconds_remaining(session: SessionRecord) -> int | None:
    if not session.time_limit_seconds:
        return None
    elapsed = (datetime.utcnow() - session.started_at).total_seconds()
    return max(0, int(session.time_limit_seconds - elapsed))


def _time_expired(session: SessionRecord) -> bool:
    remaining = _seconds_remaining(session)
    return remaining is not None and remaining <= 0


def _timed_limits_hit(session: SessionRecord, attempts: list[Attempt]) -> bool:
    if session.session_type != "timed_challenge":
        return False
    if _time_expired(session):
        return True
    if session.max_wrong_allowed is not None and _wrong_count(attempts) > session.max_wrong_allowed:
        return True
    return False


def _session_to_out(db: Session, session: SessionRecord) -> SessionOut:
    session = (
        db.query(SessionRecord)
        .options(joinedload(SessionRecord.attempts).joinedload(Attempt.question))
        .filter(SessionRecord.id == session.id)
        .first()
    )
    out = SessionOut.model_validate(session)
    out.wrong_count = _wrong_count(session.attempts)
    return out


def _question_out(q: Question) -> QuestionOut:
    parsed = parse_choices(q.correct_choice)
    return QuestionOut(
        id=q.id,
        domain=q.domain,
        domain_name=q.domain_name,
        difficulty=q.difficulty,
        difficulty_level=q.difficulty_level,
        topic_id=q.topic_id,
        reference=q.reference,
        tags=q.tags,
        stem=q.stem,
        choice_a=q.choice_a,
        choice_b=q.choice_b,
        choice_c=q.choice_c,
        choice_d=q.choice_d,
        source_topic=q.source_topic,
        question_type=question_type_for(q.correct_choice),
        select_count=len(parsed) if parsed else 1,
    )


def _grade_and_finalize(db: Session, session: SessionRecord) -> SubmitResult:
    attempts = _session_attempts(db, session.id)
    for a in attempts:
        if a.selected_choice and a.is_correct is None and a.question:
            a.is_correct = grade_answer(a.selected_choice, a.question.correct_choice)

    if session.mode == "exam":
        for a in attempts:
            if a.selected_choice and a.is_correct is not None:
                update_review(db, session.user_id, a.question_id, bool(a.is_correct), a.confidence)

    scaled, percent, correct, answered = compute_cissp_scaled(attempts)
    session.correct_count = correct
    session.score_percent = percent
    session.scaled_score = scaled
    session.total_questions = len([a for a in attempts if a.selected_choice])
    session.submitted = True
    session.completed_at = datetime.utcnow()
    if session.theta_proxy is not None:
        session.pass_likelihood = pass_likelihood(session.theta_proxy)
    db.commit()

    passed = passed_cissp(scaled)
    return SubmitResult(
        session=_session_to_out(db, session),
        scaled_score=scaled,
        score_percent=percent,
        passed=passed,
        grade_label=grade_label(scaled),
        pass_threshold_scaled=PASS_SCALED,
        pass_likelihood=session.pass_likelihood,
    )


def _append_cat_question(db: Session, session: SessionRecord, attempts: list[Attempt], last: Attempt) -> bool:
    answered = [a for a in attempts if a.selected_choice]
    correct = sum(1 for a in answered if a.is_correct)
    theta = session.theta_proxy if session.theta_proxy is not None else THETA_START
    if last.question:
        level = last.question.difficulty_level or 3
        session.theta_proxy = update_theta(theta, bool(last.is_correct), level)
        session.pass_likelihood = pass_likelihood(session.theta_proxy)

    if (
        should_stop_cat(len(answered), correct)
        or should_stop_theta(len(answered), session.theta_proxy or THETA_START)
        or len(answered) >= session.total_questions
    ):
        db.commit()
        return True

    exclude = {a.question_id for a in attempts}
    domain_counts = session_domain_counts(answered)
    last_diff = last.question.difficulty if last.question else "medium"
    last_level = last.question.difficulty_level if last.question and last.question.difficulty_level else 3
    is_correct = bool(last.is_correct)
    next_q = pick_next_cat_question(
        db,
        exclude,
        last_diff,
        is_correct,
        domain_counts,
        theta=session.theta_proxy or THETA_START,
        last_difficulty_level=last_level,
    )
    if not next_q:
        db.commit()
        return True
    db.add(Attempt(session_id=session.id, question_id=next_q.id))
    db.commit()
    return False


def _verify_session_owner(session: SessionRecord, user_id: str) -> None:
    if session.user_id != user_id:
        raise HTTPException(404, "Session not found")


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "alive",
        "questions": db.query(Question).count(),
        "domains": 8,
        "pass_scaled": PASS_SCALED,
        "cat_min": CAT_MIN_QUESTIONS,
        "cat_max": CAT_MAX_QUESTIONS,
        "cat_hours": CAT_TIME_SECONDS // 3600,
        "pwa": Path(FRONTEND_DIST).is_dir(),
        "installable": True,
        "version": "3.0.0",
    }


@app.get("/api/domains", response_model=list[DomainInfo])
def list_domains():
    return [DomainInfo(**d) for d in get_domain_info()]


@app.get("/api/questions/count")
def question_counts(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    counts = {}
    for d in range(1, 9):
        counts[str(d)] = db.query(Question).filter(Question.domain == d).count()
    counts["total"] = db.query(Question).count()
    counts["scenario"] = db.query(Question).filter(Question.tags.contains("scenario")).count()
    counts.update(get_bank_coverage(db, user_id))
    return counts


@app.get("/api/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    return SettingsOut.model_validate(_get_settings(db, user_id))


@app.put("/api/settings", response_model=SettingsOut)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    settings = _get_settings(db, user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return SettingsOut.model_validate(settings)


@app.get("/api/study-plan", response_model=StudyPlanOut)
def study_plan(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    settings = _get_settings(db, user_id)
    return StudyPlanOut(**build_study_plan(db, settings))


@app.get("/api/study-guide", response_model=StudyGuideOut)
def study_guide(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    return StudyGuideOut(**build_study_guide_payload(db, user_id))


@app.get("/api/study-guide/coverage")
def study_guide_coverage(db: Session = Depends(get_db)):
    payload = build_study_guide_payload(db)
    return {"coverage": payload["coverage"], "summary": payload["summary"]}


@app.get("/api/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    return build_analytics(db, user_id)


@app.get("/api/analytics/export")
def analytics_export(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    csv_data = export_analytics_csv(db, user_id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cissp-progress.csv"},
    )


@app.get("/api/missed")
def missed_questions(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    ids = get_missed_question_ids(db, user_id)
    questions = db.query(Question).filter(Question.id.in_(ids)).all() if ids else []
    qmap = {q.id: q for q in questions}
    return {
        "count": len(ids),
        "questions": [_question_out(qmap[i]).model_dump() for i in ids if i in qmap],
    }


@app.get("/api/flagged")
def flagged_questions(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    ids = get_flagged_question_ids(db, user_id)
    questions = db.query(Question).filter(Question.id.in_(ids)).all() if ids else []
    qmap = {q.id: q for q in questions}
    return {
        "count": len(ids),
        "questions": [_question_out(qmap[i]).model_dump() for i in ids if i in qmap],
    }


@app.get("/api/flashcards", response_model=list[FlashcardOut])
def list_flashcards(domain: int | None = None, topic_id: str | None = None):
    return [FlashcardOut(**c) for c in build_flashcards(domain, topic_id)]


@app.get("/api/domains/{domain_id}/module", response_model=DomainModuleOut)
def domain_module(domain_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    if domain_id not in range(1, 9):
        raise HTTPException(400, "Domain must be 1-8")
    analytics = build_analytics(db, user_id)
    dom_stat = next((d for d in analytics.domains if d.domain == domain_id), None)
    bank = next((b for b in analytics.domain_bank_coverage if b.domain == domain_id), None)
    topics = [
        s for dom in CHEAT_SHEET["domains"] if dom["domain"] == domain_id for s in dom.get("sections", [])
    ]
    cards = build_flashcards(domain_id)
    return DomainModuleOut(
        domain=domain_id,
        domain_name=dom_stat.domain_name if dom_stat else "",
        weight=dom_stat.weight if dom_stat else 0,
        pass_rate=dom_stat.pass_rate if dom_stat else 0,
        readiness=dom_stat.readiness if dom_stat else "Needs Focus",
        topic_count=len(topics),
        flashcard_count=len(cards),
        bank_coverage_percent=bank.bank_coverage_percent if bank else 0,
    )


@app.post("/api/sessions/start", response_model=SessionOut)
def start_session(
    req: StartSessionRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    settings = _get_settings(db, user_id)
    mode = req.practice_mode or settings.practice_mode

    if req.session_type == "mock_exam":
        max_q = min(max(req.count, CAT_MIN_QUESTIONS), CAT_MAX_QUESTIONS)
        mode = "exam"
        first_batch = select_questions(db, 1, cat_mode=True, difficulty="medium")
        if not first_batch:
            raise HTTPException(404, "No questions available")
        session = SessionRecord(
            user_id=user_id,
            mode=mode,
            session_type=req.session_type,
            total_questions=max_q,
            domain_filter=None,
            time_limit_seconds=CAT_TIME_SECONDS,
            theta_proxy=THETA_START,
        )
        db.add(session)
        db.flush()
        db.add(Attempt(session_id=session.id, question_id=first_batch[0].id))
        db.commit()
        return _session_to_out(db, session)

    count = min(req.count, 100)
    questions: list[Question] = []

    if req.session_type == "missed":
        missed_ids = get_missed_question_ids(db, user_id)
        if not missed_ids:
            raise HTTPException(404, "No missed questions yet — keep practicing!")
        pool = db.query(Question).filter(Question.id.in_(missed_ids)).all()
        qmap = {q.id: q for q in pool}
        questions = [qmap[i] for i in missed_ids if i in qmap][:count]
    elif req.session_type == "flagged":
        flagged_ids = get_flagged_question_ids(db, user_id)
        if not flagged_ids:
            raise HTTPException(404, "No flagged questions yet — flag items during practice.")
        pool = db.query(Question).filter(Question.id.in_(flagged_ids)).all()
        qmap = {q.id: q for q in pool}
        questions = [qmap[i] for i in flagged_ids if i in qmap][:count]
    elif req.session_type == "domain_test":
        if not req.domain:
            raise HTTPException(400, "Domain required for domain test")
        questions = select_questions(db, count, domain=req.domain)
    elif req.session_type == "daily":
        questions = select_daily_questions(db, count, user_id, settings)
    elif req.session_type == "topic_drill":
        if not req.topic_id:
            raise HTTPException(400, "topic_id required for topic drill")
        questions = select_topic_drill_questions(db, req.topic_id, min(count, 20))
        if not questions:
            raise HTTPException(404, "No questions available for this study topic")
    elif req.session_type == "guide_drill":
        if not req.importance:
            raise HTTPException(400, "importance required for guide drill (must, high, or good)")
        questions = select_guide_drill_questions(db, req.importance, req.domain)
        if not questions:
            raise HTTPException(404, "No study guide questions for this domain and priority tier")
    elif req.session_type == "timed_challenge":
        if req.duration_minutes is None or req.max_wrong is None:
            raise HTTPException(400, "duration_minutes and max_wrong required for timed challenge")
        minutes = min(max(req.duration_minutes, 5), 180)
        max_wrong = min(max(req.max_wrong, 0), 50)
        pool_size = min(minutes * 2, 100)
        questions = select_daily_questions(db, pool_size, user_id, settings)
        if not questions:
            raise HTTPException(404, "No questions available for timed challenge")
        session = SessionRecord(
            user_id=user_id,
            mode="fast",
            session_type=req.session_type,
            total_questions=len(questions),
            domain_filter=None,
            time_limit_seconds=minutes * 60,
            max_wrong_allowed=max_wrong,
        )
        db.add(session)
        db.flush()
        for q in questions:
            db.add(Attempt(session_id=session.id, question_id=q.id))
        db.commit()
        return _session_to_out(db, session)
    else:
        questions = select_questions(db, count)

    if not questions:
        raise HTTPException(404, "No questions available for this session")

    session = SessionRecord(
        user_id=user_id,
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
def get_session(session_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
    return _session_to_out(db, session)


@app.get("/api/sessions/{session_id}/progress", response_model=SessionProgress)
def session_progress(session_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
    attempts = _session_attempts(db, session_id)
    answered_list = [a for a in attempts if a.selected_choice]
    scaled, percent, _, answered = compute_cissp_scaled(attempts)
    max_q = session.total_questions if session.session_type == "mock_exam" else len(attempts)
    hide_scores = not session.submitted
    return SessionProgress(
        answered=answered,
        total_in_session=len(attempts),
        max_questions=max_q,
        can_submit=answered > 0 and not session.submitted,
        score_percent=0.0 if hide_scores else percent,
        scaled_score=0.0 if hide_scores else scaled,
        passed=passed_cissp(scaled) if not hide_scores else False,
        pass_threshold_scaled=PASS_SCALED,
    )


@app.get("/api/sessions/{session_id}/current")
def get_current_question(session_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)

    attempts = _session_attempts(db, session_id)
    answered = [a for a in attempts if a.selected_choice is not None]
    unanswered = [a for a in attempts if a.selected_choice is None]

    if session.session_type == "mock_exam" and not unanswered and not session.submitted:
        if len(answered) >= CAT_MIN_QUESTIONS:
            return {"complete": True, "session": _session_to_out(db, session), "cat_complete": True}

    if session.session_type == "mock_exam" and not session.submitted and session.time_limit_seconds and _time_expired(session):
        _grade_and_finalize(db, session)
        return {"complete": True, "session": _session_to_out(db, session), "exam_expired": True}

    if session.session_type == "timed_challenge" and not session.submitted and _time_expired(session):
        _grade_and_finalize(db, session)
        return {"complete": True, "session": _session_to_out(db, session), "timed_expired": True}

    if not unanswered:
        return {"complete": True, "session": _session_to_out(db, session)}

    current = unanswered[0]
    time_limit = None
    seconds_remaining = None
    if session.session_type == "mock_exam":
        time_limit = session.time_limit_seconds or CAT_TIME_SECONDS
        seconds_remaining = _seconds_remaining(session) if session.time_limit_seconds else CAT_TIME_SECONDS
        if seconds_remaining is None:
            seconds_remaining = CAT_TIME_SECONDS
    elif session.session_type == "timed_challenge" and session.time_limit_seconds:
        time_limit = session.time_limit_seconds
        seconds_remaining = _seconds_remaining(session)

    return {
        "complete": False,
        "index": len(answered) + 1,
        "total": session.total_questions if session.session_type == "mock_exam" else len(attempts),
        "answered": len(answered),
        "question": _question_out(current.question).model_dump(),
        "attempt_id": current.id,
        "flagged": current.flagged,
        "time_limit_seconds": time_limit,
        "seconds_remaining": seconds_remaining,
        "is_cat": session.session_type == "mock_exam",
        "is_timed_challenge": session.session_type == "timed_challenge",
        "wrong_count": _wrong_count(attempts),
        "max_wrong_allowed": session.max_wrong_allowed,
        "pass_likelihood": session.pass_likelihood,
        "theta_proxy": session.theta_proxy,
    }


@app.post("/api/sessions/{session_id}/answer", response_model=AnswerResult)
def answer_question(
    session_id: int,
    req: AnswerRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
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
    try:
        normalized = validate_submission(req.selected_choice, q.correct_choice)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    is_correct = grade_answer(normalized, q.correct_choice)
    attempt.selected_choice = normalized
    attempt.flagged = req.flagged
    attempt.time_spent_seconds = req.time_spent_seconds
    attempt.confidence = req.confidence
    attempt.answered_at = datetime.utcnow()
    attempt.is_correct = is_correct

    if session.session_type != "mock_exam" and session.mode != "exam":
        update_review(db, user_id, q.id, is_correct, req.confidence)

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
    elif session.session_type == "timed_challenge":
        session_complete = _timed_limits_hit(session, attempts) or len(unanswered) == 0
    else:
        session_complete = len(unanswered) == 0

    if session_complete and not session.submitted and session.mode != "exam":
        _grade_and_finalize(db, session)

    hide_live_score = not session.submitted

    if hide_feedback:
        return AnswerResult(
            is_correct=False,
            correct_choice="",
            explanation="",
            manager_brief="",
            approach_tips=[],
            wrong_choice_notes=[],
            score_percent=0.0,
            session_complete=session_complete,
        )

    feedback = build_manager_feedback(q, normalized, is_correct)
    return AnswerResult(
        is_correct=is_correct,
        correct_choice=q.correct_choice,
        explanation=feedback["explanation"],
        manager_brief=feedback["manager_brief"],
        explanation_sections=feedback.get("explanation_sections", []),
        reference_sections=feedback.get("reference_sections", []),
        trap=feedback.get("trap", ""),
        approach_tips=feedback["approach_tips"],
        wrong_choice_notes=feedback["wrong_choice_notes"],
        score_percent=0.0 if hide_live_score else percent,
        session_complete=session_complete,
    )


@app.patch("/api/sessions/{session_id}/flag")
def update_question_flag(
    session_id: int,
    req: FlagUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
    if session.submitted:
        raise HTTPException(400, "Session already submitted")

    attempt = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id, Attempt.question_id == req.question_id)
        .first()
    )
    if not attempt:
        raise HTTPException(404, "Question not in this session")

    attempt.flagged = req.flagged
    db.commit()
    return {"question_id": req.question_id, "flagged": req.flagged}


@app.post("/api/sessions/{session_id}/submit", response_model=SubmitResult)
def submit_session(session_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
    if session.submitted:
        raise HTTPException(400, "Session already submitted")

    attempts = _session_attempts(db, session_id)
    answered = [a for a in attempts if a.selected_choice]
    if not answered:
        raise HTTPException(400, "No answered questions to grade")

    return _grade_and_finalize(db, session)


@app.get("/api/sessions/{session_id}/review")
def review_session(session_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    session = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    _verify_session_owner(session, user_id)
    if session.mode == "exam" and not session.submitted:
        raise HTTPException(400, "Submit session before reviewing answers")

    attempts = _session_attempts(db, session_id)
    results = []
    for a in attempts:
        if not a.selected_choice:
            continue
        feedback = build_manager_feedback(a.question, a.selected_choice, a.is_correct)
        results.append({
            "attempt_id": a.id,
            "question": _question_out(a.question).model_dump(),
            "selected_choice": a.selected_choice,
            "correct_choice": a.question.correct_choice,
            "is_correct": a.is_correct,
            "explanation": feedback["explanation"],
            "manager_brief": feedback["manager_brief"],
            "explanation_sections": feedback.get("explanation_sections", []),
            "reference_sections": feedback.get("reference_sections", []),
            "trap": feedback.get("trap", ""),
            "approach_tips": feedback["approach_tips"],
            "wrong_choice_notes": feedback["wrong_choice_notes"],
            "flagged": a.flagged,
        })
    return {
        "session": _session_to_out(db, session),
        "results": results,
        "scaled_score": session.scaled_score,
        "passed": passed_cissp(session.scaled_score or 0),
        "pass_threshold_scaled": PASS_SCALED,
    }

