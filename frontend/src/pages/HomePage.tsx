import { useEffect, useState } from "react";
import { api } from "../api";
import { CountdownBanner } from "../components/CountdownBanner";
import { TemTechLogo } from "../components/TemTechLogo";
import type { Settings, StudyPlanAdvice } from "../types";

interface HomePageProps {
  settings: Settings;
  onNavigate: (page: string) => void;
  onStartDaily: (count: number) => void;
}

export function HomePage({ settings, onNavigate, onStartDaily }: HomePageProps) {
  const [counts, setCounts] = useState<Record<string, number | string>>({});
  const [plan, setPlan] = useState<StudyPlanAdvice | null>(null);
  const [questionCount, setQuestionCount] = useState(settings.daily_questions);

  useEffect(() => {
    api.questionCounts().then(setCounts).catch(() => {});
    api.studyPlan().then(setPlan).catch(() => {});
  }, []);

  useEffect(() => {
    setQuestionCount(settings.daily_questions);
  }, [settings.daily_questions]);

  return (
    <>
      <CountdownBanner settings={settings} />
      <div className="hero glass-card">
        <TemTechLogo size={64} />
        <h1>CISSP Study Companion</h1>
        <p>
          Master all 8 domains with daily practice, CAT-style mock exams, domain tests, and analytics aligned to the ISC2 April 2024 outline — including cloud and AI security.
        </p>
        <div className="grid-2" style={{ maxWidth: 520, margin: "0 auto" }}>
          <div className="stat-box">
            <div className="value">{counts.total ?? "—"}</div>
            <div className="label">Question bank</div>
          </div>
          <div className="stat-box">
            <div className="value">
              {typeof counts.bank_answered_unique === "number"
                ? `${counts.bank_answered_unique}/${counts.total ?? "—"}`
                : "—"}
            </div>
            <div className="label">Unique explored</div>
          </div>
        </div>
      </div>

      {plan && (
        <div className="card study-plan-card">
          <h2>Your Study Plan</h2>
          <p className="sub">{plan.message}</p>
          <div className="grid-2">
            <div className="stat-box">
              <div className="value">{plan.recommended_daily_questions}</div>
              <div className="label">Suggested questions/day</div>
            </div>
            <div className="stat-box">
              <div className="value">
                {plan.days_until_exam !== null ? plan.days_until_exam : "—"}
              </div>
              <div className="label">Days until exam</div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Daily Random Practice</h2>
        <p className="sub">
          Fresh mix each session — prioritizes unseen questions, avoids recent repeats, and shuffles domain-weighted items.
          Mode: <strong>{settings.practice_mode}</strong> ({settings.daily_minutes} min target).
        </p>
        <div className="form-group">
          <label htmlFor="daily-count">Questions this session</label>
          <input
            id="daily-count"
            type="number"
            min={5}
            max={50}
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
          />
        </div>
        <button type="button" className="btn btn-primary" onClick={() => onStartDaily(questionCount)}>
          Start Daily Session
        </button>
      </div>

      <div className="action-grid">
        <button type="button" className="action-tile" onClick={() => onNavigate("missed")}>
          <div className="icon">✗</div>
          <div className="title">Missed Questions</div>
        </button>
        <button type="button" className="action-tile" onClick={() => onNavigate("flagged")}>
          <div className="icon">⚑</div>
          <div className="title">Flagged Review</div>
        </button>
        <button type="button" className="action-tile" onClick={() => onNavigate("mock")}>
          <div className="icon">📋</div>
          <div className="title">Mock CAT Exam</div>
        </button>
        <button type="button" className="action-tile" onClick={() => onNavigate("domain")}>
          <div className="icon">🎯</div>
          <div className="title">Domain Test</div>
        </button>
        <button type="button" className="action-tile" onClick={() => onNavigate("analysis")}>
          <div className="icon">📊</div>
          <div className="title">Analysis</div>
        </button>
        <button type="button" className="action-tile" onClick={() => onNavigate("settings")}>
          <div className="icon">⚙</div>
          <div className="title">Settings</div>
        </button>
      </div>
    </>
  );
}
