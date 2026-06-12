import { useState } from "react";
import { CountdownBanner } from "../components/CountdownBanner";
import type { Page, Settings } from "../types";

interface SettingsPageProps {
  settings: Settings;
  onUpdate: (patch: Partial<Settings>) => Promise<Settings>;
  onNavigate: (page: Page) => void;
}

const STUDY_PLANS = [
  { value: "just_trying", label: "Just Trying — 50% target" },
  { value: "pass_exam", label: "Pass the Exam — 70% target" },
  { value: "high_score", label: "Get a High Score — 80% target" },
  { value: "expert", label: "Become an Expert — 90% target" },
];

export function SettingsPage({ settings, onUpdate, onNavigate }: SettingsPageProps) {
  const [saved, setSaved] = useState(false);
  const [local, setLocal] = useState(settings);

  const save = async (patch: Partial<Settings>) => {
    const updated = await onUpdate(patch);
    setLocal(updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <>
      <CountdownBanner settings={local} />
      <div className="card">
        <h2>Settings</h2>
        {saved && <p style={{ color: "var(--success)", marginBottom: "1rem" }}>Settings saved.</p>}

        <h3 style={{ marginTop: "1rem", marginBottom: "0.75rem" }}>Practice Mode</h3>
        <div className="form-group">
          <label htmlFor="practice-mode">Mode</label>
          <select
            id="practice-mode"
            value={local.practice_mode}
            onChange={(e) => {
              const v = e.target.value as Settings["practice_mode"];
              setLocal({ ...local, practice_mode: v });
              save({ practice_mode: v });
            }}
          >
            <option value="newbie">Newbie — manager brief + approach tips after each answer</option>
            <option value="fast">Fast — quick feedback, auto-advance</option>
            <option value="exam">Exam — no feedback until submit</option>
          </select>
        </div>

        <h3 style={{ marginTop: "1.5rem", marginBottom: "0.75rem" }}>Daily Practice</h3>
        <div className="grid-2">
          <div className="form-group">
            <label htmlFor="daily-min">Minutes per day</label>
            <input
              id="daily-min"
              type="number"
              min={5}
              max={240}
              value={local.daily_minutes}
              onChange={(e) => setLocal({ ...local, daily_minutes: Number(e.target.value) })}
              onBlur={() => save({ daily_minutes: local.daily_minutes })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="daily-q">Default questions</label>
            <input
              id="daily-q"
              type="number"
              min={5}
              max={100}
              value={local.daily_questions}
              onChange={(e) => setLocal({ ...local, daily_questions: Number(e.target.value) })}
              onBlur={() => save({ daily_questions: local.daily_questions })}
            />
          </div>
        </div>

        <h3 style={{ marginTop: "1.5rem", marginBottom: "0.75rem" }}>Study Plan</h3>
        <div className="form-group">
          <select
            value={local.study_plan}
            onChange={(e) => {
              const v = e.target.value as Settings["study_plan"];
              setLocal({ ...local, study_plan: v });
              save({ study_plan: v });
            }}
          >
            {STUDY_PLANS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <h3 style={{ marginTop: "1.5rem", marginBottom: "0.75rem" }}>Exam Date</h3>
        <div className="form-group">
          <label htmlFor="exam-date">Target exam date (countdown on home)</label>
          <input
            id="exam-date"
            type="date"
            value={local.exam_date ?? ""}
            onChange={(e) => {
              const v = e.target.value || null;
              setLocal({ ...local, exam_date: v });
              save({ exam_date: v });
            }}
          />
        </div>
        <div className="toggle-row">
          <span>Exam countdown alert</span>
          <button
            type="button"
            className={`toggle ${local.exam_alert_enabled ? "on" : ""}`}
            onClick={() => {
              const v = !local.exam_alert_enabled;
              setLocal({ ...local, exam_alert_enabled: v });
              save({ exam_alert_enabled: v });
            }}
            aria-label="Toggle exam alert"
          />
        </div>

        <h3 style={{ marginTop: "1.5rem", marginBottom: "0.75rem" }}>Appearance</h3>
        <div className="toggle-row">
          <span>{local.theme === "dark" ? "Dark mode" : "Light mode"}</span>
          <button
            type="button"
            className={`toggle ${local.theme === "dark" ? "on" : ""}`}
            onClick={() => {
              const v = local.theme === "dark" ? "light" : "dark";
              setLocal({ ...local, theme: v });
              save({ theme: v });
            }}
            aria-label="Toggle theme"
          />
        </div>

        <h3 style={{ marginTop: "1.5rem", marginBottom: "0.75rem" }}>Legal</h3>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button type="button" className="btn btn-secondary" onClick={() => onNavigate("privacy")}>
            Privacy Policy
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => onNavigate("terms")}>
            Terms of Use
          </button>
        </div>
      </div>
    </>
  );
}
