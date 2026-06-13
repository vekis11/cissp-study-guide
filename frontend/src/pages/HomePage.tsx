import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { CountdownBanner } from "../components/CountdownBanner";
import { TemTechLogo } from "../components/TemTechLogo";
import { FeatureCard } from "../components/ui/FeatureCard";
import {
  IconBook,
  IconChart,
  IconExam,
  IconFlag,
  IconMissed,
  IconSettings,
  IconDaily,
  IconSpark,
  IconTarget,
} from "../components/ui/Icons";
import { ProgressRing } from "../components/ui/ProgressRing";
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

  const bankTotal = typeof counts.total === "number" ? counts.total : 0;
  const bankAnswered =
    typeof counts.bank_answered_unique === "number" ? counts.bank_answered_unique : 0;

  const modeLabel = useMemo(() => {
    const labels: Record<string, string> = {
      newbie: "Guided",
      fast: "Fast feedback",
      exam: "Exam simulation",
    };
    return labels[settings.practice_mode] ?? settings.practice_mode;
  }, [settings.practice_mode]);

  return (
    <div className="home-page page-enter">
      <CountdownBanner settings={settings} />

      <section className="home-hero">
        <div className="home-hero-orb home-hero-orb--1" aria-hidden />
        <div className="home-hero-orb home-hero-orb--2" aria-hidden />
        <div className="home-hero-inner">
          <div className="home-hero-copy">
            <div className="home-brand-row">
              <TemTechLogo size={56} variant="stacked" />
            </div>
            <p className="eyebrow">CISSP Study Companion</p>
            <h1 className="home-title">
              Think like a <span className="text-gradient">security leader</span>
            </h1>
            <p className="home-lead">
              Manager-style scenarios across all 8 domains — daily drills, adaptive mock CAT exams,
              cheat-sheet topic quizzes, and readiness analytics.
            </p>
          </div>

          <div className="home-hero-stats">
            <ProgressRing
              value={bankAnswered}
              max={bankTotal || 1}
              label="Bank explored"
              sublabel={bankTotal ? `${bankAnswered} / ${bankTotal}` : undefined}
              size={128}
            />
            <div className="metric-stack">
              <div className="metric-chip">
                <span className="metric-chip-value">{bankTotal || "—"}</span>
                <span className="metric-chip-label">Questions</span>
              </div>
              <div className="metric-chip">
                <span className="metric-chip-value">8</span>
                <span className="metric-chip-label">Domains</span>
              </div>
              <div className="metric-chip metric-chip--accent">
                <span className="metric-chip-value">700</span>
                <span className="metric-chip-label">Pass score</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="card card-spotlight quick-start-card">
        <div className="quick-start-grid">
          <div>
            <div className="quick-start-label">
              <IconSpark size={18} />
              Today&apos;s session
            </div>
            <h2>Daily practice</h2>
            <p className="sub">
              Unseen-first selection · weak-domain bias · {modeLabel} mode · ~{settings.daily_minutes}{" "}
              min target
            </p>
          </div>
          <div className="quick-start-actions">
            <div className="form-group quick-start-count">
              <label htmlFor="daily-count">Questions</label>
              <input
                id="daily-count"
                type="number"
                min={5}
                max={50}
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
              />
            </div>
            <button type="button" className="btn btn-primary btn-lg" onClick={() => onStartDaily(questionCount)}>
              Start session
              <span className="btn-shine" aria-hidden />
            </button>
          </div>
        </div>
      </section>

      {plan && (
        <section className="card study-plan-card">
          <div className="study-plan-header">
            <div>
              <p className="eyebrow">Personalized plan</p>
              <h2>Your study rhythm</h2>
            </div>
            {plan.days_until_exam !== null && (
              <div className="study-plan-days">
                <span className="study-plan-days-value">{plan.days_until_exam}</span>
                <span className="study-plan-days-label">days left</span>
              </div>
            )}
          </div>
          <p className="sub">{plan.message}</p>
          <div className="grid-2">
            <div className="stat-box stat-box--glow">
              <div className="value">{plan.recommended_daily_questions}</div>
              <div className="label">Suggested / day</div>
            </div>
            <div className="stat-box stat-box--glow">
              <div className="value">{plan.bank_coverage_percent.toFixed(0)}%</div>
              <div className="label">Bank coverage</div>
            </div>
          </div>
        </section>
      )}

      <section className="home-section">
        <div className="section-heading">
          <h2>Study modes</h2>
          <p>Pick your path — every mode uses the same manager-first question bank.</p>
        </div>
        <div className="bento-grid">
          <FeatureCard
            title="Mock CAT Exam"
            description="125–150 adaptive questions · 3-hour timer · scaled scoring"
            icon={<IconExam size={22} />}
            variant="primary"
            size="featured"
            badge="CAT"
            onClick={() => onNavigate("mock")}
          />
          <FeatureCard
            title="Timed Challenge"
            description="Custom minutes · wrong-answer limit · hidden live score"
            icon={<IconDaily size={22} />}
            variant="accent"
            onClick={() => onNavigate("timed")}
          />
          <FeatureCard
            title="Domain Modules"
            description="8 domains · lessons · flashcards · mini-quizzes"
            icon={<IconTarget size={22} />}
            variant="violet"
            onClick={() => onNavigate("domain")}
          />
          <FeatureCard
            title="Study Guide"
            description="70 cheat-sheet topics with scenario drills"
            icon={<IconBook size={22} />}
            variant="accent"
            size="wide"
            badge="New"
            onClick={() => onNavigate("study")}
          />
          <FeatureCard
            title="Analysis"
            description="Readiness dashboard & CSV export"
            icon={<IconChart size={22} />}
            variant="success"
            onClick={() => onNavigate("analysis")}
          />
          <FeatureCard
            title="Missed Questions"
            description="Review what you got wrong"
            icon={<IconMissed size={22} />}
            onClick={() => onNavigate("missed")}
          />
          <FeatureCard
            title="Flagged Review"
            description="Items you marked for later"
            icon={<IconFlag size={22} />}
            onClick={() => onNavigate("flagged")}
          />
          <FeatureCard
            title="Settings"
            description="Exam date, practice mode & profile"
            icon={<IconSettings size={22} />}
            onClick={() => onNavigate("settings")}
          />
        </div>
      </section>
    </div>
  );
}
