interface ManagerExplanationProps {
  isCorrect: boolean;
  correctChoice?: string;
  managerBrief: string;
  approachTips: string[];
  fallbackExplanation?: string;
}

export function ManagerExplanation({
  isCorrect,
  correctChoice,
  managerBrief,
  approachTips,
  fallbackExplanation,
}: ManagerExplanationProps) {
  const brief = managerBrief || fallbackExplanation || "";
  const tips = approachTips.length > 0 ? approachTips : [];

  if (!brief && tips.length === 0) return null;

  return (
    <div className={`manager-explanation ${isCorrect ? "correct-msg" : "incorrect-msg"}`}>
      <div className="manager-explanation-header">
        {isCorrect ? (
          <strong>Correct — manager-level reasoning</strong>
        ) : (
          <strong>Correct answer: {correctChoice}</strong>
        )}
      </div>

      {brief && (
        <section className="manager-explanation-section">
          <h4>Manager brief</h4>
          <p>{brief}</p>
        </section>
      )}

      {tips.length > 0 && (
        <section className="manager-explanation-section">
          <h4>How to approach similar questions</h4>
          <ul className="manager-approach-tips">
            {tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
