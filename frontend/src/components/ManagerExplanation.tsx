import { useEffect, useState } from "react";
import { formatChoiceLabel } from "../utils/questionFormat";
import type { WrongChoiceNote } from "../types";

interface ManagerExplanationProps {
  isCorrect: boolean;
  correctChoice?: string;
  selectedChoice?: string | null;
  isMultiSelect?: boolean;
  managerBrief: string;
  approachTips: string[];
  wrongChoiceNotes?: WrongChoiceNote[];
  fallbackExplanation?: string;
  /** When true, content is hidden until the user expands it. */
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export function ManagerExplanation({
  isCorrect,
  correctChoice,
  selectedChoice,
  isMultiSelect = false,
  managerBrief,
  approachTips,
  wrongChoiceNotes = [],
  fallbackExplanation,
  collapsible = false,
  defaultExpanded = false,
}: ManagerExplanationProps) {
  const brief = managerBrief || fallbackExplanation || "";
  const tips = approachTips.length > 0 ? approachTips.slice(0, 2) : [];
  const wrongNotes = wrongChoiceNotes.length > 0 ? wrongChoiceNotes : [];
  const [expanded, setExpanded] = useState(defaultExpanded);

  useEffect(() => {
    setExpanded(defaultExpanded);
  }, [brief, correctChoice, isCorrect, defaultExpanded, wrongNotes.length]);

  if (!brief && tips.length === 0 && wrongNotes.length === 0) return null;

  const body = (
    <div className={`manager-explanation ${isCorrect ? "correct-msg" : "incorrect-msg"}`}>
      <div className="manager-explanation-header">
        {isCorrect ? (
          <strong>Correct — manager-level reasoning</strong>
        ) : (
          <strong>
            Correct answer{isMultiSelect ? "s" : ""}: {formatChoiceLabel(correctChoice ?? "")}
            {selectedChoice && selectedChoice !== correctChoice && (
              <span className="explanation-your-pick">
                {" "}
                · You chose {formatChoiceLabel(selectedChoice)}
              </span>
            )}
          </strong>
        )}
      </div>

      {brief && (
        <section className="manager-explanation-section">
          <h4>Manager brief</h4>
          <p>{brief}</p>
        </section>
      )}

      {wrongNotes.length > 0 && (
        <section className="manager-explanation-section">
          <h4>Why the other options are wrong</h4>
          <ul className="wrong-choice-notes">
            {wrongNotes.map((note) => (
              <li
                key={note.choice}
                className={selectedChoice === note.choice ? "wrong-choice-your-pick" : undefined}
              >
                <span className="wrong-choice-label">
                  <strong>{note.choice}.</strong> {note.text}
                </span>
                <span className="wrong-choice-reason">{note.why_wrong}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {tips.length > 0 && (
        <section className="manager-explanation-section manager-explanation-tips-compact">
          <h4>Quick tip</h4>
          <ul className="manager-approach-tips">
            {tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );

  if (!collapsible) return body;

  return (
    <div className="manager-explanation-wrap">
      <button
        type="button"
        className={`explanation-toggle ${expanded ? "expanded" : ""}`}
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span>{expanded ? "Hide explanation" : "See explanation"}</span>
        <span className="explanation-toggle-icon" aria-hidden="true">
          {expanded ? "▲" : "▼"}
        </span>
      </button>
      {expanded && body}
    </div>
  );
}
