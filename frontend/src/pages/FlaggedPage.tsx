import { useEffect, useState } from "react";
import { api } from "../api";

interface FlaggedPageProps {
  onStart: (count: number) => void;
}

export function FlaggedPage({ onStart }: FlaggedPageProps) {
  const [count, setFlaggedCount] = useState(0);
  const [sessionCount, setSessionCount] = useState(20);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.flagged()
      .then((d) => setFlaggedCount(d.count))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="card">
      <h2>Flagged Questions</h2>
      <p className="sub">Review questions you flagged during daily practice or mock exams.</p>
      {error && <div className="error-msg">{error}</div>}
      <div className="stat-box" style={{ marginBottom: "1rem" }}>
        <div className="value">{count}</div>
        <div className="label">Flagged for review</div>
      </div>
      {count > 0 ? (
        <>
          <div className="form-group">
            <label htmlFor="flagged-count">Questions this session</label>
            <input
              id="flagged-count"
              type="number"
              min={1}
              max={count}
              value={Math.min(sessionCount, count)}
              onChange={(e) => setSessionCount(Number(e.target.value))}
            />
          </div>
          <button type="button" className="btn btn-primary" onClick={() => onStart(Math.min(sessionCount, count))}>
            Review Flagged Questions
          </button>
        </>
      ) : (
        <p style={{ color: "var(--text-muted)" }}>Flag questions during practice to build a personal review list.</p>
      )}
    </div>
  );
}
