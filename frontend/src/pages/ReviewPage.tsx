import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { ScoreGauge } from "../components/charts/ScoreGauge";
import { ManagerExplanation } from "../components/ManagerExplanation";
import { TemTechLogo } from "../components/TemTechLogo";
import { DOMAIN_COLORS } from "../utils/chartColors";
import type { ReviewItem, Session, SubmitResult } from "../types";

interface ReviewPageProps {
  sessionId: number;
  submitResult: SubmitResult | null;
  onDone: () => void;
}

function domainBreakdown(results: ReviewItem[]) {
  const map = new Map<number, { correct: number; total: number; name: string }>();
  for (const r of results) {
    const d = r.question.domain;
    const cur = map.get(d) ?? { correct: 0, total: 0, name: r.question.domain_name };
    cur.total += 1;
    if (r.is_correct) cur.correct += 1;
    map.set(d, cur);
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]);
}

export function ReviewPage({ sessionId, submitResult, onDone }: ReviewPageProps) {
  const [session, setSession] = useState<Session | null>(submitResult?.session ?? null);
  const [results, setResults] = useState<ReviewItem[]>([]);
  const [scaled, setScaled] = useState(submitResult?.scaled_score ?? 0);
  const [passed, setPassed] = useState(submitResult?.passed ?? false);
  const [gradeLabel, setGradeLabel] = useState(submitResult?.grade_label ?? "");
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    api.sessions
      .review(sessionId)
      .then((d) => {
        setSession(d.session);
        setResults(d.results);
        setScaled(d.scaled_score);
        setPassed(d.passed);
        if (!gradeLabel) setGradeLabel(d.passed ? "Pass" : "Needs Improvement");
      })
      .catch((e) => setError(e.message));
  }, [sessionId, gradeLabel]);

  const breakdown = useMemo(() => domainBreakdown(results), [results]);

  if (error) return <div className="error-msg">{error}</div>;
  if (!session) return <div className="loading shimmer">Loading results...</div>;

  const accuracy = session.score_percent ?? 0;
  const correctPct = session.total_questions > 0 ? (session.correct_count / session.total_questions) * 100 : 0;

  return (
    <div className="review-page">
      <header className={`grade-hero glass-card ${passed ? "grade-pass" : "grade-fail"}`}>
        <div className="grade-hero-glow" aria-hidden="true" />
        <div className="grade-hero-header">
          <div>
            <p className="eyebrow">CISSP Session Grading</p>
            <h1>{passed ? "Strong performance" : "Keep building momentum"}</h1>
            <p className="sub">
              {session.session_type.replace("_", " ")} · {session.correct_count} of {session.total_questions} correct ·
              Pass threshold 700/1000
            </p>
          </div>
          <TemTechLogo size={48} />
        </div>

        <div className="grade-hero-body">
          <ScoreGauge
            value={scaled}
            max={1000}
            passAt={700}
            label={gradeLabel}
            sublabel="Scaled score"
            size={240}
            variant="scaled"
          />

          <div className="grade-stats-panel">
            <div className={`grade-verdict ${passed ? "pass" : "fail"}`}>
              <span className="grade-verdict-icon">{passed ? "✓" : "↗"}</span>
              <div>
                <strong>{gradeLabel}</strong>
                <p>{passed ? "At or above the 700 scaled pass benchmark." : "Focus on weak domains and retry mock CAT sessions."}</p>
              </div>
            </div>
            <div className="grade-stat-grid">
              <div className="grade-stat">
                <span>Raw accuracy</span>
                <strong>{accuracy.toFixed(1)}%</strong>
              </div>
              <div className="grade-stat">
                <span>Correct rate</span>
                <strong>{correctPct.toFixed(1)}%</strong>
              </div>
              <div className="grade-stat">
                <span>Hard items weighted</span>
                <strong>CAT-style</strong>
              </div>
              <div className="grade-stat">
                <span>Domains covered</span>
                <strong>{breakdown.length}</strong>
              </div>
            </div>
            <button type="button" className="btn btn-primary btn-lg" onClick={onDone}>
              Back to Home
            </button>
          </div>
        </div>
      </header>

      {breakdown.length > 0 && (
        <section className="glass-card chart-section">
          <h2>Domain Breakdown</h2>
          <p className="sub">How you performed in each domain this session.</p>
          <div className="review-domain-bars">
            {breakdown.map(([domain, stats], i) => {
              const rate = stats.total > 0 ? (stats.correct / stats.total) * 100 : 0;
              return (
                <div key={domain} className="review-domain-row">
                  <span className="review-domain-label" style={{ color: DOMAIN_COLORS[i % 8] }}>
                    D{domain}
                  </span>
                  <div className="review-domain-track">
                    <div
                      className="review-domain-fill"
                      style={{ width: `${rate}%`, background: DOMAIN_COLORS[i % 8] }}
                    />
                  </div>
                  <span className="review-domain-pct">{rate.toFixed(0)}%</span>
                  <span className="review-domain-count">
                    {stats.correct}/{stats.total}
                  </span>
                </div>
              );
            })}
          </div>
        </section>
      )}

      <section className="glass-card">
        <h2>Question Review</h2>
        <p className="sub">{results.length} questions · tap to expand manager briefs and approach tips</p>
        {results.map((r, i) => (
          <article
            key={r.attempt_id}
            className={`review-question-card ${r.is_correct ? "correct" : "incorrect"} ${expanded === i ? "expanded" : ""}`}
          >
            <button type="button" className="review-question-head" onClick={() => setExpanded(expanded === i ? null : i)}>
              <div className="question-meta">
                <span className="tag">Q{i + 1}</span>
                <span className="tag">Domain {r.question.domain}</span>
                {r.flagged && <span className="tag flagged">Flagged</span>}
              </div>
              <span className={`review-status ${r.is_correct ? "pass" : "fail"}`}>
                {r.is_correct ? "Correct" : "Incorrect"}
              </span>
            </button>
            {expanded === i && (
              <div className="review-question-body">
                <p className="stem">{r.question.stem}</p>
                <p className="review-answers">
                  Your answer: <strong>{r.selected_choice ?? "—"}</strong> · Correct: <strong>{r.correct_choice}</strong>
                </p>
                <ManagerExplanation
                  isCorrect={!!r.is_correct}
                  correctChoice={r.correct_choice}
                  managerBrief={r.manager_brief ?? r.explanation}
                  approachTips={r.approach_tips ?? []}
                />
              </div>
            )}
          </article>
        ))}
      </section>
    </div>
  );
}
