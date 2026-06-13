import { useEffect, useState } from "react";
import { api } from "../api";

interface MissedPageProps {
  onStart: (count: number) => void;
}

export function MissedPage({ onStart }: MissedPageProps) {
  const [count, setMissedCount] = useState(0);
  const [sessionCount, setSessionCount] = useState(20);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.missed()
      .then((d) => setMissedCount(d.count))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="card">
      <h2>Missed Questions</h2>
      <p className="sub">
        SM-2 spaced repetition — due reviews surface first, then oldest missed questions.
      </p>
      {error && <div className="error-msg">{error}</div>}
      <div className="stat-box" style={{ marginBottom: "1rem" }}>
        <div className="value">{count}</div>
        <div className="label">Unique missed questions</div>
      </div>
      {count > 0 ? (
        <>
          <div className="form-group">
            <label htmlFor="missed-count">Questions this session</label>
            <input
              id="missed-count"
              type="number"
              min={1}
              max={count}
              value={Math.min(sessionCount, count)}
              onChange={(e) => setSessionCount(Number(e.target.value))}
            />
          </div>
          <button type="button" className="btn btn-primary" onClick={() => onStart(Math.min(sessionCount, count))}>
            Review Missed Questions
          </button>
        </>
      ) : (
        <p style={{ color: "var(--text-muted)" }}>No missed questions yet — complete a practice session first.</p>
      )}
    </div>
  );
}
