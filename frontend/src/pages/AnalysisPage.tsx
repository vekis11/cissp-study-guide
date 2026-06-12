import { useEffect, useState } from "react";
import { api } from "../api";
import { readinessClass } from "../hooks/useSettings";
import { ScoreGauge } from "../components/charts/ScoreGauge";
import { DomainRadar } from "../components/charts/DomainRadar";
import { DomainBarChart } from "../components/charts/DomainBarChart";
import { DomainProgressMap } from "../components/charts/DomainProgressMap";
import { SessionTrendChart } from "../components/charts/SessionTrendChart";
import { TemTechLogo } from "../components/TemTechLogo";
import { COMPANY_TAGLINE } from "../constants/branding";
import { scoreColor } from "../utils/chartColors";
import type { Analytics } from "../types";

export function AnalysisPage() {
  const [data, setData] = useState<Analytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"map" | "bars" | "radar">("map");

  useEffect(() => {
    api.analytics()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-msg">{error}</div>;
  if (!data) return <div className="loading shimmer">Loading analytics...</div>;

  const passClass = data.overall_pass_rate >= data.exam_pass_threshold ? "pass" : "fail";
  const avgScaled = Math.round((data.overall_pass_rate / 100) * 1000);

  return (
    <div className="analysis-page">
      <header className="analysis-hero glass-card">
        <div className="analysis-hero-top">
          <div>
            <p className="eyebrow">Performance Intelligence</p>
            <h1>Exam Readiness Dashboard</h1>
            <p className="sub">
              Live progress across all 8 ISC2 domains · CISSP scaled benchmark · {COMPANY_TAGLINE}
            </p>
          </div>
          <TemTechLogo size={52} showLabel />
        </div>

        <div className="analysis-hero-grid">
          <div className="analysis-gauge-block">
            <ScoreGauge
              value={avgScaled}
              max={1000}
              passAt={700}
              label="Estimated scaled score"
              sublabel="700 required to pass"
              size={220}
              variant="scaled"
            />
            <span className={`readiness-badge lg ${readinessClass(data.overall_readiness)}`}>
              {data.overall_readiness}
            </span>
          </div>

          <div className="analysis-kpi-stack">
            <div className={`kpi-card ${passClass}`}>
              <span className="kpi-label">Overall accuracy</span>
              <span className="kpi-value" style={{ color: scoreColor(data.overall_pass_rate, data.exam_pass_threshold) }}>
                {data.overall_pass_rate.toFixed(1)}%
              </span>
              <span className="kpi-hint">Study benchmark {data.exam_pass_threshold}%</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-label">Questions answered</span>
              <span className="kpi-value">{data.total_questions_answered.toLocaleString()}</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-label">Completed sessions</span>
              <span className="kpi-value">{data.total_sessions}</span>
            </div>
            <div className="kpi-card accent">
              <span className="kpi-label">Domains tracked</span>
              <span className="kpi-value">8 / 8</span>
              <span className="kpi-hint">April 2024 outline</span>
            </div>
          </div>
        </div>
      </header>

      <section className="glass-card chart-section">
        <div className="section-head">
          <div>
            <h2>Domain Mastery Map</h2>
            <p className="sub">Visual progress across every CISSP domain — ring fill shows pass rate, color shows readiness tier.</p>
          </div>
          <div className="view-toggle">
            {(["map", "bars", "radar"] as const).map((v) => (
              <button
                key={v}
                type="button"
                className={`view-toggle-btn ${view === v ? "active" : ""}`}
                onClick={() => setView(v)}
              >
                {v === "map" ? "Progress Map" : v === "bars" ? "Bar Chart" : "Radar"}
              </button>
            ))}
          </div>
        </div>
        {view === "map" && <DomainProgressMap domains={data.domains} passThreshold={data.exam_pass_threshold} />}
        {view === "bars" && <DomainBarChart domains={data.domains} passThreshold={data.exam_pass_threshold} />}
        {view === "radar" && <DomainRadar domains={data.domains} />}
      </section>

      <section className="glass-card chart-section">
        <div className="section-head">
          <div>
            <h2>Session Performance Trend</h2>
            <p className="sub">Recent submitted sessions — track momentum toward the 700/1000 pass line.</p>
          </div>
        </div>
        <SessionTrendChart sessions={data.recent_sessions} />
      </section>

      {data.recent_sessions.length > 0 && (
        <section className="glass-card">
          <h2>Recent Sessions</h2>
          <div className="session-table">
            {data.recent_sessions.map((s) => {
              const scaled = s.scaled_score ?? (s.score_percent ?? 0) * 10;
              return (
                <div key={s.id} className="session-table-row">
                  <div className="session-table-type">{s.session_type.replace("_", " ")}</div>
                  <div className="session-table-meta">{s.total_questions} questions · {s.correct_count} correct</div>
                  <div className="session-table-scores">
                    <span className="session-scaled">{scaled.toFixed(0)}</span>
                    <span className="session-raw">{s.score_percent?.toFixed(1)}% raw</span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
