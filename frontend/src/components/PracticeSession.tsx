import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { api } from "../api";

import { ManagerExplanation } from "./ManagerExplanation";

import {
  isMultiSelectQuestion,
  parseChoiceLetters,
  serializeChoices,
} from "../utils/questionFormat";

import type { AnswerResult, Question, SubmitResult } from "../types";



const CHOICES = ["A", "B", "C", "D"] as const;



interface PracticeSessionProps {

  sessionId: number;

  mode: string;

  onComplete: (result: SubmitResult) => void;

  onExit: () => void;

}



export function PracticeSession({ sessionId, mode, onComplete, onExit }: PracticeSessionProps) {

  const [index, setIndex] = useState(1);

  const [total, setTotal] = useState(0);

  const [question, setQuestion] = useState<Question | null>(null);

  const [selected, setSelected] = useState<string | null>(null);

  const [selectedMulti, setSelectedMulti] = useState<Set<string>>(new Set());

  const [flagged, setFlagged] = useState(false);

  const [result, setResult] = useState<AnswerResult | null>(null);

  const [loading, setLoading] = useState(true);

  const [submitting, setSubmitting] = useState(false);

  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  const [error, setError] = useState<string | null>(null);

  const [examReadyToSubmit, setExamReadyToSubmit] = useState(false);

  const [showExitModal, setShowExitModal] = useState(false);

  const [exitProgress, setExitProgress] = useState<{ answered: number } | null>(null);

  const [isTimedChallenge, setIsTimedChallenge] = useState(false);

  const [wrongCount, setWrongCount] = useState(0);

  const [maxWrongAllowed, setMaxWrongAllowed] = useState<number | null>(null);

  const [confidence, setConfidence] = useState(3);

  const [passLikelihood, setPassLikelihood] = useState<number | null>(null);

  const questionLoadedAt = useRef<number>(Date.now());
  const sessionStartedAt = useRef<number>(Date.now());
  const [questionElapsed, setQuestionElapsed] = useState(0);
  const [sessionElapsed, setSessionElapsed] = useState(0);



  const isExam = mode === "exam";

  const isFast = mode === "fast";

  const isMulti = question ? isMultiSelectQuestion(question) : false;

  const selectCount = question?.select_count ?? (isMulti ? 2 : 1);



  const finishWithReview = useCallback(async () => {

    const review = await api.sessions.review(sessionId);

    onComplete({

      session: review.session,

      scaled_score: review.scaled_score,

      score_percent: review.session.score_percent ?? 0,

      passed: review.passed,

      grade_label: review.passed ? "Pass" : "Needs Improvement",

      pass_threshold_scaled: review.pass_threshold_scaled,

      pass_likelihood: review.session.pass_likelihood ?? undefined,

    });

  }, [sessionId, onComplete]);



  const loadCurrent = useCallback(async () => {

    setLoading(true);

    setError(null);

    try {

      const data = await api.sessions.current(sessionId);

      if (data.complete) {

        if (data.session?.submitted) {

          await finishWithReview();

          return;

        }

        if (isExam) {

          setExamReadyToSubmit(true);

          setTotal(data.total ?? data.session?.total_questions ?? 0);

          setQuestion(null);

          setLoading(false);

          return;

        }

        await finishWithReview();

        return;

      }

      setExamReadyToSubmit(false);

      setIndex(data.index!);

      setTotal(data.total!);

      setQuestion(data.question!);

      questionLoadedAt.current = Date.now();

      setConfidence(3);

      setSelected(null);

      setSelectedMulti(new Set());

      setResult(null);

      setFlagged(data.flagged ?? false);

      setIsTimedChallenge(data.is_timed_challenge ?? false);

      setWrongCount(data.wrong_count ?? 0);

      setMaxWrongAllowed(data.max_wrong_allowed ?? null);

      if (data.pass_likelihood != null) setPassLikelihood(data.pass_likelihood);

      if (data.seconds_remaining != null) {

        setTimeLeft(data.seconds_remaining);

      } else if (data.time_limit_seconds != null && timeLeft === null) {

        setTimeLeft(data.time_limit_seconds);

      }

    } catch (e) {

      setError(e instanceof Error ? e.message : "Failed to load question");

    } finally {

      setLoading(false);

    }

  }, [sessionId, isExam, finishWithReview, timeLeft]);



  useEffect(() => {

    loadCurrent();

  }, [loadCurrent]);



  useEffect(() => {
    if (loading || !question) return;
    const tick = () => {
      setQuestionElapsed(Math.max(0, Math.floor((Date.now() - questionLoadedAt.current) / 1000)));
      setSessionElapsed(Math.max(0, Math.floor((Date.now() - sessionStartedAt.current) / 1000)));
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [loading, question, index]);



  useEffect(() => {

    if (timeLeft === null || timeLeft <= 0) return;

    const t = setInterval(() => setTimeLeft((s) => (s !== null && s > 0 ? s - 1 : 0)), 1000);

    return () => clearInterval(t);

  }, [timeLeft]);



  useEffect(() => {

    if (!isTimedChallenge || timeLeft !== 0 || loading || submitting) return;

    void loadCurrent();

  }, [isTimedChallenge, timeLeft, loading, submitting, loadCurrent]);



  const formatTime = (s: number) => {

    const h = Math.floor(s / 3600);

    const m = Math.floor((s % 3600) / 60);

    const sec = s % 60;

    return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;

  };

  const formatShortTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${String(sec).padStart(2, "0")}`;
  };



  const getChoiceText = (q: Question, letter: string) => {

    const map: Record<string, string> = {

      A: q.choice_a,

      B: q.choice_b,

      C: q.choice_c,

      D: q.choice_d,

    };

    return map[letter];

  };



  const handleToggleFlag = async () => {
    if (!question) return;
    const next = !flagged;
    setFlagged(next);
    if (selected) {
      try {
        await api.sessions.setFlag(sessionId, question.id, next);
      } catch (e) {
        setFlagged(!next);
        setError(e instanceof Error ? e.message : "Could not update flag");
      }
    }
  };



  const submitAnswer = async (choicePayload: string) => {

    if (!question || loading) return;

    setLoading(true);

    setError(null);

    try {

      const elapsed = Math.max(1, Math.round((Date.now() - questionLoadedAt.current) / 1000));

      const res = await api.sessions.answer(sessionId, {

        question_id: question.id,

        selected_choice: choicePayload,

        flagged,

        time_spent_seconds: elapsed,

        confidence,

      });

      setSelected(choicePayload);

      if (isTimedChallenge && !res.is_correct) {

        setWrongCount((w) => w + 1);

      }

      if (isExam) {

        if (res.session_complete) {

          setExamReadyToSubmit(true);

          setQuestion(null);

        } else if (isFast) {

          setTimeout(() => loadCurrent(), 300);

        } else {

          await loadCurrent();

        }

      } else {

        setResult(res);

      }

    } catch (e) {

      setError(e instanceof Error ? e.message : "Failed to submit answer");

      setSelected(null);

      setSelectedMulti(new Set());

    } finally {

      setLoading(false);

    }

  };



  const handleSelectSingle = (choice: string) => {

    if (!question || loading || (selected && !isExam)) return;

    void submitAnswer(choice);

  };



  const handleToggleMulti = (choice: string) => {

    if (!question || loading || (selected && !isExam)) return;

    setSelectedMulti((prev) => {

      const next = new Set(prev);

      if (next.has(choice)) next.delete(choice);

      else if (next.size < selectCount) next.add(choice);

      return next;

    });

  };



  const handleSubmitMulti = () => {

    if (selectedMulti.size !== selectCount) return;

    void submitAnswer(serializeChoices(selectedMulti));

  };



  const handleNext = async () => {

    if (result?.session_complete) {

      await finishWithReview();

    } else {

      loadCurrent();

    }

  };



  const handleSubmitExam = async () => {

    setSubmitting(true);

    try {

      const submitResult = await api.sessions.submit(sessionId);

      onComplete(submitResult);

    } catch (e) {

      setError(e instanceof Error ? e.message : "Submit failed");

    } finally {

      setSubmitting(false);

    }

  };



  const handleExitClick = async () => {

    try {

      const progress = await api.sessions.progress(sessionId);

      if (progress.answered === 0) {

        onExit();

        return;

      }

      setExitProgress({ answered: progress.answered });

      setShowExitModal(true);

    } catch {

      onExit();

    }

  };



  const correctLetters = useMemo(

    () => (result ? parseChoiceLetters(result.correct_choice) : new Set<string>()),

    [result]

  );

  const userLetters = useMemo(

    () => parseChoiceLetters(selected),

    [selected]

  );



  const exitModal = showExitModal && exitProgress && (

    <div className="modal-overlay">

      <div className="modal modal-grade">

        <h3>Submit session for grading?</h3>

        <p>

          You have answered <strong>{exitProgress.answered}</strong> question

          {exitProgress.answered !== 1 ? "s" : ""}. Submit now for CISSP-style scoring (pass = 700/1000). Your score

          is hidden until you submit.

        </p>

        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>

          <button type="button" className="btn btn-primary" onClick={handleSubmitExam} disabled={submitting}>

            {submitting ? "Grading..." : "Submit for Grading"}

          </button>

          <button type="button" className="btn btn-secondary" onClick={() => setShowExitModal(false)}>

            Continue Session

          </button>

          <button type="button" className="btn btn-secondary" onClick={onExit}>

            Exit Without Saving

          </button>

        </div>

      </div>

    </div>

  );



  if (examReadyToSubmit) {

    return (

      <>

        {exitModal}

        <div className="card">

          <h2>CAT Session Complete</h2>

          <p className="sub">

            The adaptive engine has enough data or you reached the question cap. Submit for CISSP scaled scoring

            (700/1000 pass).

          </p>

          <button type="button" className="btn btn-primary" onClick={handleSubmitExam} disabled={submitting}>

            {submitting ? "Submitting..." : "Submit for Grading"}

          </button>

          {!isExam && (
          <button type="button" className="btn btn-secondary" style={{ marginTop: "0.75rem" }} onClick={handleExitClick}>

            Exit Session
          </button>
          )}

        </div>

      </>

    );

  }



  if (loading && !question) {

    return <div className="loading">Loading question...</div>;

  }



  if (error && !question) {

    return (

      <div className="card">

        <div className="error-msg">{error}</div>

        <button type="button" className="btn btn-secondary" onClick={onExit}>

          Back

        </button>

      </div>

    );

  }



  if (!question) return null;



  const progressPct = total > 0 ? (index / total) * 100 : 0;

  const showFeedback = result && !isExam;

  const answered = !!selected;



  return (

    <>

      {exitModal}

      <div className="card practice-card">

        <div className="practice-header">

          <div className="practice-progress-label">

            <span className="practice-q-num">

              {index}

              <span className="practice-q-total"> / {total}</span>

            </span>

            {isExam && <span className="practice-cat-badge">CAT adaptive</span>}

            {isTimedChallenge && <span className="practice-cat-badge">Timed challenge</span>}

          </div>

          <div className="practice-header-stats">

            {isTimedChallenge && maxWrongAllowed != null && (

              <span className={`practice-wrongs ${wrongCount > maxWrongAllowed ? "practice-wrongs--over" : ""}`}>

                Wrongs {wrongCount}/{maxWrongAllowed}

              </span>

            )}

            {isExam && passLikelihood != null && (

              <span className="practice-pass-est">Est. pass {passLikelihood.toFixed(0)}%</span>

            )}

            {timeLeft !== null && <span className="timer timer-countdown">{formatTime(timeLeft)}</span>}

            <span className="timer timer-question" title="Time on this question">
              Q {formatShortTime(questionElapsed)}
            </span>

            <span className="timer timer-session" title="Total session time">
              Session {formatShortTime(sessionElapsed)}
            </span>

          </div>

        </div>



        <div className="progress-bar progress-bar--modern">

          <div className="progress-fill" style={{ width: `${progressPct}%` }} />

        </div>



        <div className="question-meta">

          <span className="tag tag-domain">Domain {question.domain}</span>

          <span className="tag">{question.difficulty}</span>

          <span className="tag">{question.tags.includes("knowledge-check") ? "Knowledge check" : "Scenario"}</span>

          {isMulti && <span className="tag tag-multi">Select {selectCount}</span>}

        </div>



        <p className="stem practice-stem">{question.stem}</p>



        {isMulti && !answered && (

          <p className="multi-select-hint">

            Select exactly <strong>{selectCount}</strong> answers, then submit.

          </p>

        )}



        {!isExam && !answered && (

          <div className="confidence-picker">

            <span className="confidence-label">Confidence</span>

            {[1, 2, 3, 4, 5].map((n) => (

              <button

                key={n}

                type="button"

                className={`confidence-btn ${confidence === n ? "active" : ""}`}

                onClick={() => setConfidence(n)}

              >

                {n}

              </button>

            ))}

          </div>

        )}



        {error && <div className="error-msg" style={{ marginBottom: "0.75rem" }}>{error}</div>}



        <div style={{ display: "flex", gap: "0.75rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>

          <button
            type="button"
            className={`btn btn-secondary ${flagged ? "btn-primary" : ""}`}
            onClick={() => void handleToggleFlag()}
            disabled={loading}
          >
            {flagged ? "Flagged for review" : "Flag for review"}
          </button>

        </div>



        <div className={`choice-list ${isMulti ? "choice-list--multi" : ""}`}>

          {CHOICES.map((letter) => {

            let cls = "choice-btn";

            const isSelected = isMulti ? selectedMulti.has(letter) : selected === letter;



            if (isSelected) cls += " selected";

            if (isMulti) cls += " choice-btn--multi";



            if (showFeedback) {

              if (correctLetters.has(letter)) cls += " correct";

              else if (userLetters.has(letter)) cls += " incorrect";

            }



            return (

              <button

                key={letter}

                type="button"

                className={cls}

                disabled={answered && !isExam}

                onClick={() => (isMulti ? handleToggleMulti(letter) : handleSelectSingle(letter))}

              >

                <span className={`choice-letter ${isMulti ? "choice-check" : ""}`}>

                  {isMulti ? (isSelected ? "☑" : "☐") : `${letter}.`}

                </span>
                <span>{getChoiceText(question, letter)}</span>

              </button>

            );

          })}

        </div>



        {isMulti && !answered && (

          <button

            type="button"

            className="btn btn-primary"

            style={{ marginTop: "0.75rem" }}

            disabled={selectedMulti.size !== selectCount || loading}

            onClick={handleSubmitMulti}

          >

            Submit answer ({selectedMulti.size}/{selectCount})

          </button>

        )}



        {isExam && (

          <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem", flexWrap: "wrap" }}>

            <button type="button" className="btn btn-secondary" onClick={() => loadCurrent()} disabled={!answered}>

              Next

            </button>

            <button type="button" className="btn btn-danger" onClick={handleSubmitExam} disabled={submitting}>

              {submitting ? "Submitting..." : "End & Submit for Grading"}

            </button>

          </div>

        )}



        {showFeedback && (

          <div className="practice-next-row">

            <button type="button" className="btn btn-primary" onClick={handleNext}>

              {result!.session_complete ? "View Results" : isFast ? "Next →" : "Next Question"}

            </button>

            <button type="button" className="btn btn-secondary" onClick={handleExitClick}>

              Exit Session

            </button>

          </div>

        )}



        {showFeedback && question.reference && (

          <p className="question-reference sub">

            <strong>Reference:</strong> {question.reference}

          </p>

        )}



        {showFeedback && (

          <ManagerExplanation

            collapsible

            isCorrect={result!.is_correct}

            correctChoice={result!.correct_choice}

            selectedChoice={selected}

            isMultiSelect={isMulti}

            managerBrief={result!.manager_brief ?? result!.explanation}

            explanationSections={result!.explanation_sections}

            referenceSections={result!.reference_sections}

            trap={result!.trap}

            approachTips={result!.approach_tips ?? []}

          />

        )}



        {!showFeedback && !isExam && (

          <button type="button" className="btn btn-secondary" style={{ marginTop: "1rem" }} onClick={handleExitClick}>

            Exit Session

          </button>

        )}

      </div>

    </>

  );

}


