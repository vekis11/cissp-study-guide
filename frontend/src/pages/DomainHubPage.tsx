import { useEffect, useState } from "react";
import { api } from "../api";
import { PageHeader } from "../components/ui/PageHeader";
import { ProgressRing } from "../components/ui/ProgressRing";
import { IconBook, IconChart, IconTarget } from "../components/ui/Icons";
import type { DomainModule } from "../types";

interface DomainHubPageProps {
  domain: number;
  onBack: () => void;
  onStartPractice: (domain: number, count: number) => void;
  onStartFlashcards: (domain: number) => void;
  onOpenStudyGuide: () => void;
}

export function DomainHubPage({
  domain,
  onBack,
  onStartPractice,
  onStartFlashcards,
  onOpenStudyGuide,
}: DomainHubPageProps) {
  const [mod, setMod] = useState<DomainModule | null>(null);
  const [count, setCount] = useState(20);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .domainModule(domain)
      .then(setMod)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load domain"));
  }, [domain]);

  if (error) return <div className="error-msg">{error}</div>;
  if (!mod) return <div className="loading">Loading domain module…</div>;

  return (
    <div className="page-enter">
      <button type="button" className="btn btn-secondary btn-sm" style={{ marginBottom: "1rem" }} onClick={onBack}>
        ← All domains
      </button>

      <div className="card card-spotlight domain-hub-hero">
        <PageHeader
          eyebrow={`Domain ${mod.domain} · ${(mod.weight * 100).toFixed(0)}% exam weight`}
          title={mod.domain_name}
          subtitle="Lessons, flashcards, practice, and analytics for this ISC2 domain."
        />
        <div className="domain-hub-stats">
          <ProgressRing value={mod.pass_rate} max={100} label="Pass rate" size={96} />
          <div className="metric-stack">
            <div className="metric-chip">
              <span className="metric-chip-value">{mod.readiness}</span>
              <span className="metric-chip-label">Readiness</span>
            </div>
            <div className="metric-chip">
              <span className="metric-chip-value">{mod.topic_count}</span>
              <span className="metric-chip-label">Topics</span>
            </div>
            <div className="metric-chip">
              <span className="metric-chip-value">{mod.flashcard_count}</span>
              <span className="metric-chip-label">Flashcards</span>
            </div>
            <div className="metric-chip metric-chip--accent">
              <span className="metric-chip-value">{mod.bank_coverage_percent.toFixed(0)}%</span>
              <span className="metric-chip-label">Bank seen</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bento-grid domain-hub-actions">
        <button type="button" className="feature-card feature-card--primary" onClick={onOpenStudyGuide}>
          <span className="feature-card-icon">
            <IconBook size={22} />
          </span>
          <span className="feature-card-title">Lessons &amp; cheat sheet</span>
          <span className="feature-card-desc">{mod.topic_count} study topics with reference notes</span>
        </button>
        <button type="button" className="feature-card feature-card--accent" onClick={() => onStartFlashcards(domain)}>
          <span className="feature-card-icon">
            <IconChart size={22} />
          </span>
          <span className="feature-card-title">Flashcards</span>
          <span className="feature-card-desc">{mod.flashcard_count} flip cards from cheat-sheet content</span>
        </button>
      </div>

      <div className="card">
        <h3>Domain practice quiz</h3>
        <p className="sub">Scenario questions filtered to Domain {domain} only.</p>
        <div className="form-group" style={{ maxWidth: 200, marginTop: "0.75rem" }}>
          <label htmlFor="hub-count">Questions</label>
          <input
            id="hub-count"
            type="number"
            min={5}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </div>
        <button
          type="button"
          className="btn btn-primary btn-lg"
          style={{ marginTop: "1rem" }}
          onClick={() => onStartPractice(domain, count)}
        >
          <IconTarget size={18} />
          Start domain quiz
        </button>
      </div>
    </div>
  );
}
