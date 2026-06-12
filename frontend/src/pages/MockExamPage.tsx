import { useState } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { IconExam, IconShield } from "../components/ui/Icons";

interface MockExamPageProps {
  onStart: (count: number) => void;
}

const EXAM_FACTS = [
  "Adaptive difficulty — questions added one at a time",
  "Stops at 125+ when confidence is reached, or continues to 150 max",
  "Manager-style scenarios — leadership decisions, not configs",
  "Scaled score 0–1000 (700 to pass) with deferred grading",
];

export function MockExamPage({ onStart }: MockExamPageProps) {
  const [count, setCount] = useState(125);

  return (
    <div className="page-enter">
      <div className="card card-spotlight exam-intro-card">
        <PageHeader
          eyebrow="Computerized Adaptive Testing"
          title="Mock CISSP CAT Exam"
          subtitle="ISC2 April 2024 simulation — 3-hour limit, domain-weighted selection, and CISSP-style scaled scoring."
        />

        <div className="exam-facts-grid">
          {EXAM_FACTS.map((fact) => (
            <div key={fact} className="exam-fact">
              <IconShield size={16} />
              <span>{fact}</span>
            </div>
          ))}
        </div>

        <div className="exam-config-row">
          <div className="form-group">
            <label htmlFor="mock-count">Question cap</label>
            <select id="mock-count" value={count} onChange={(e) => setCount(Number(e.target.value))}>
              <option value={125}>125 — minimum CAT length</option>
              <option value={150}>150 — maximum CAT length</option>
            </select>
          </div>
          <p className="exam-mode-note">
            Practice mode switches to <strong>exam</strong> for this session.
          </p>
        </div>

        <button type="button" className="btn btn-primary btn-lg btn-block" onClick={() => onStart(count)}>
          <IconExam size={18} />
          Begin mock exam
        </button>
      </div>
    </div>
  );
}
