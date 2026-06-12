import { useState } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { IconDaily, IconShield } from "../components/ui/Icons";

interface TimedChallengePageProps {
  onStart: (minutes: number, maxWrong: number) => void;
}

const CHALLENGE_FACTS = [
  "Set your own time limit and wrong-answer tolerance",
  "Session ends when time runs out or you exceed your wrong limit",
  "Scores are hidden until you finish — focus on each scenario",
  "Fast feedback after every answer with manager-style briefs",
];

export function TimedChallengePage({ onStart }: TimedChallengePageProps) {
  const [minutes, setMinutes] = useState(30);
  const [maxWrong, setMaxWrong] = useState(5);

  return (
    <div className="page-enter">
      <div className="card card-spotlight exam-intro-card">
        <PageHeader
          eyebrow="Pressure practice"
          title="Timed Challenge"
          subtitle="Race the clock with a personal wrong-answer budget. Great for simulating exam pressure without a full CAT."
        />

        <div className="exam-facts-grid">
          {CHALLENGE_FACTS.map((fact) => (
            <div key={fact} className="exam-fact">
              <IconShield size={16} />
              <span>{fact}</span>
            </div>
          ))}
        </div>

        <div className="exam-config-row timed-config-row">
          <div className="form-group">
            <label htmlFor="challenge-minutes">Challenge duration (minutes)</label>
            <input
              id="challenge-minutes"
              type="number"
              min={5}
              max={180}
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label htmlFor="challenge-wrong">Wrong answers allowed</label>
            <input
              id="challenge-wrong"
              type="number"
              min={0}
              max={50}
              value={maxWrong}
              onChange={(e) => setMaxWrong(Number(e.target.value))}
            />
          </div>
        </div>

        <p className="exam-mode-note">
          Up to <strong>{Math.min(minutes * 2, 100)}</strong> questions will be queued. The session stops early if
          time expires or you miss more than <strong>{maxWrong}</strong> question{maxWrong !== 1 ? "s" : ""}.
        </p>

        <button
          type="button"
          className="btn btn-primary btn-lg btn-block"
          onClick={() => onStart(minutes, maxWrong)}
        >
          <IconDaily size={18} />
          Start timed challenge
        </button>
      </div>
    </div>
  );
}
