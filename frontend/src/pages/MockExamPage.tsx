import { useState } from "react";

interface MockExamPageProps {
  onStart: (count: number) => void;
}

export function MockExamPage({ onStart }: MockExamPageProps) {
  const [count, setCount] = useState(125);

  return (
    <div className="card">
      <h2>Mock CISSP CAT Exam</h2>
      <p className="sub">
        ISC2 April 2024 CAT simulation: 125–150 adaptive questions, 3-hour limit, domain-weighted selection, difficulty adapts to your answers, deferred grading until submit.
      </p>
      <ul style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1rem", paddingLeft: "1.25rem" }}>
        <li>Questions added one-at-a-time — difficulty increases when you answer correctly</li>
        <li>Stops at 125+ when pass/fail confidence reached, or continues to 150 max</li>
        <li>Scenario-based manager questions — think leadership, not implementation</li>
        <li>CISSP scaled score 0–1000 (pass = 700) — harder items weighted more</li>
        <li>Study simulation only — not the official Pearson VUE IRT engine</li>
      </ul>
      <div className="form-group">
        <label htmlFor="mock-count">Target question cap</label>
        <select id="mock-count" value={count} onChange={(e) => setCount(Number(e.target.value))}>
          <option value={125}>125 (minimum CAT length)</option>
          <option value={150}>150 (maximum CAT length)</option>
        </select>
      </div>
      <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
        Current practice mode will be overridden to <strong>exam</strong> for this session.
      </p>
      <button type="button" className="btn btn-primary" onClick={() => onStart(count)}>
        Begin Mock Exam
      </button>
    </div>
  );
}
