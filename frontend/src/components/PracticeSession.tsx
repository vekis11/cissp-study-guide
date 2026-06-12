import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { ScoreGauge } from "./charts/ScoreGauge";
import { ManagerExplanation } from "./ManagerExplanation";
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
  const [flagged, setFlagged] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [examReadyToSubmit, setExamReadyToSubmit] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  const [exitProgress, setExitProgress] = useState<{
    answered: number;
    scaled_score: number;
    score_percent: number;
  } | null>(null);

  const isExam = mode === "exam";
  const isFast = mode === "fast";

  const finishWithReview = useCallback(async () => {
    const review = await api.sessions.review(sessionId);
    onComplete({
      session: review.session,
      scaled_score: review.scaled_score,
      score_percent: review.session.score_percent ?? 0,
      passed: review.passed,
      grade_label: review.passed ? "Pass" : "Needs Improvement",
      pass_threshold_scaled: review.pass_threshold_scaled,
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
      setSelected(null);
      setResult(null);
      setFlagged(data.flagged ?? false);
      if (data.time_limit_seconds && timeLeft === null) {
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
    if (timeLeft === null || timeLeft <= 0) return;
    const t = setInterval(() => setTimeLeft((s) => (s !== null && s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [timeLeft]);

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
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

  const handleSelect = async (choice: string) => {
    if (!question || loading) return;
    if (selected && !isExam) return;
    setSelected(choice);
    setLoading(true);
    try {
      const res = await api.sessions.answer(sessionId, {
        question_id: question.id,
        selected_choice: choice,
        flagged,
      });
      setScore(res.score_percent);
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
        // Newbie & fast: always wait for user to click Next — never auto-advance
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit answer");
      setSelected(null);
    } finally {
      setLoading(false);
    }
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
      setExitProgress({
        answered: progress.answered,
        scaled_score: progress.scaled_score,
        score_percent: progress.score_percent,
      });
      setShowExitModal(true);
    } catch {
      onExit();
    }
  };

  const exitModal = showExitModal && exitProgress && (
    <div className="modal-overlay">
      <div className="modal modal-grade">
        <h3>Submit session for grading?</h3>
        <p>
          You have answered <strong>{exitProgress.answered}</strong> question
          {exitProgress.answered !== 1 ? "s" : ""}. Submit now for CISSP-style scoring (pass = 700/1000).
        </p>
        <div className="exit-grade-preview">
          <ScoreGauge
            value={exitProgress.scaled_score}
            max={1000}
            passAt={700}
            label="Current scaled"
            sublabel={`${exitProgress.score_percent.toFixed(1)}% raw`}
            size={180}
            variant="scaled"
          />
        </div>
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
          <button type="button" className="btn btn-secondary" style={{ marginTop: "0.75rem" }} onClick={handleExitClick}>
            Exit Session
          </button>
        </div>
      </>
    );
  }

  if (loading && !question) {
    return <div className="loading">Loading question...</div>;
  }

  if (error) {
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

  return (
    <>
      {exitModal}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <span>
            Question {index} of {total}
            {isExam && <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}> (CAT adaptive)</span>}
          </span>
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            {!isExam && (
              <span style={{ fontFamily: "var(--mono)", color: "var(--accent)" }}>{score.toFixed(1)}%</span>
            )}
            {timeLeft !== null && <span className="timer">{formatTime(timeLeft)}</span>}
          </div>
        </div>

        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progressPct}%` }} />
        </div>

        <div className="question-meta">
          <span className="tag">Domain {question.domain}</span>
          <span className="tag">{question.difficulty}</span>
          <span className="tag">Scenario</span>
        </div>

        <p className="stem">{question.stem}</p>

        <div style={{ display: "flex", gap: "0.75rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
          <button
            type="button"
            className={`btn btn-secondary ${flagged ? "btn-primary" : ""}`}
            onClick={() => setFlagged(!flagged)}
            disabled={!!selected && !isExam && !!result}
          >
            {flagged ? "Flagged for review" : "Flag for review"}
          </button>
        </div>

        <div className="choice-list">
          {CHOICES.map((letter) => {
            let cls = "choice-btn";
            if (selected === letter) cls += " selected";
            if (showFeedback) {
              if (letter === result!.correct_choice) cls += " correct";
              else if (selected === letter && !result!.is_correct) cls += " incorrect";
            }
            return (
              <button
                key={letter}
                type="button"
                className={cls}
                disabled={!!selected && !isExam}
                onClick={() => handleSelect(letter)}
              >
                <span className="choice-letter">{letter}.</span>
                <span>{getChoiceText(question, letter)}</span>
              </button>
            );
          })}
        </div>

        {isExam && (
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem", flexWrap: "wrap" }}>
            <button type="button" className="btn btn-secondary" onClick={() => loadCurrent()} disabled={!selected}>
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

        {showFeedback && (
          <ManagerExplanation
            collapsible
            isCorrect={result!.is_correct}
            correctChoice={result!.correct_choice}
            selectedChoice={selected}
            managerBrief={result!.manager_brief ?? result!.explanation}
            approachTips={result!.approach_tips ?? []}
            wrongChoiceNotes={result!.wrong_choice_notes ?? []}
          />
        )}

        {!showFeedback && (
          <button type="button" className="btn btn-secondary" style={{ marginTop: "1rem" }} onClick={handleExitClick}>
            Exit Session
          </button>
        )}
      </div>
    </>
  );
}
