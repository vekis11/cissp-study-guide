import { useState, type ReactNode } from "react";
import { Watermark } from "./components/Watermark";
import { NavBar } from "./components/NavBar";
import { BottomNav } from "./components/BottomNav";
import { InstallPrompt } from "./components/InstallPrompt";
import { ServerWakeUp } from "./components/ServerWakeUp";
import { PracticeSession } from "./components/PracticeSession";
import { useSettings } from "./hooks/useSettings";
import { api } from "./api";
import { HomePage } from "./pages/HomePage";
import { MockExamPage } from "./pages/MockExamPage";
import { DomainTestPage } from "./pages/DomainTestPage";
import { MissedPage } from "./pages/MissedPage";
import { FlaggedPage } from "./pages/FlaggedPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ReviewPage } from "./pages/ReviewPage";
import { StudyGuidePage } from "./pages/StudyGuidePage";
import { TimedChallengePage } from "./pages/TimedChallengePage";
import type { ImportanceTier, Page, SubmitResult, SessionType } from "./types";

function LegalPage({ title, children, onBack }: { title: string; children: ReactNode; onBack: () => void }) {
  return (
    <div className="card legal-content">
      <h2>{title}</h2>
      {children}
      <button type="button" className="btn btn-secondary" style={{ marginTop: "1.5rem" }} onClick={onBack}>
        Back to Settings
      </button>
    </div>
  );
}

export default function App() {
  const [serverReady, setServerReady] = useState(false);
  const { settings, loading, updateSettings } = useSettings(serverReady);
  const [page, setPage] = useState<Page>("home");
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [sessionMode, setSessionMode] = useState("newbie");
  const [startError, setStartError] = useState<string | null>(null);

  const startSession = async (
    type: SessionType,
    count: number,
    domain?: number,
    topicId?: string,
    importance?: ImportanceTier,
    durationMinutes?: number,
    maxWrong?: number
  ) => {
    setStartError(null);
    try {
      const session = await api.sessions.start({
        session_type: type,
        count,
        domain,
        topic_id: topicId,
        importance,
        duration_minutes: durationMinutes,
        max_wrong: maxWrong,
      });
      setSessionId(session.id);
      setSessionMode(session.mode);
      setPage("practice");
    } catch (e) {
      setStartError(e instanceof Error ? e.message : "Failed to start session");
    }
  };

  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);

  const handleComplete = (result: SubmitResult) => {
    setSessionId(result.session.id);
    setSubmitResult(result);
    setPage("review");
  };

  const handleExitPractice = () => {
    setSessionId(null);
    setPage("home");
  };

  if (!serverReady) {
    return <ServerWakeUp onReady={() => setServerReady(true)} />;
  }

  if (loading || !settings) {
    return (
      <div className="app-loading">
        <div className="app-loading-card">
          <div className="app-loading-spinner" aria-hidden />
          <p>Loading CISSP Study Companion…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Watermark />
      <NavBar page={page} onNavigate={setPage} />
      <InstallPrompt />
      <main className="main">
        {startError && page !== "practice" && <div className="error-msg">{startError}</div>}

        {page === "home" && (
          <HomePage
            settings={settings}
            onNavigate={(p) => setPage(p as Page)}
            onStartDaily={(count) => startSession("daily", count)}
          />
        )}

        {page === "daily" && (
          <HomePage
            settings={settings}
            onNavigate={(p) => setPage(p as Page)}
            onStartDaily={(count) => startSession("daily", count)}
          />
        )}

        {page === "missed" && <MissedPage onStart={(count) => startSession("missed", count)} />}

        {page === "flagged" && <FlaggedPage onStart={(count) => startSession("flagged", count)} />}

        {page === "mock" && <MockExamPage onStart={(count) => startSession("mock_exam", count)} />}

        {page === "timed" && (
          <TimedChallengePage
            onStart={(minutes, maxWrong) => startSession("timed_challenge", 0, undefined, undefined, undefined, minutes, maxWrong)}
          />
        )}

        {page === "domain" && (
          <DomainTestPage onStart={(domain, count) => startSession("domain_test", count, domain)} />
        )}

        {page === "study" && (
          <StudyGuidePage
            onStartGuideQuiz={(importance, domain, questionCount) =>
              startSession("guide_drill", questionCount ?? 50, domain, undefined, importance)
            }
          />
        )}

        {page === "analysis" && <AnalysisPage />}

        {page === "settings" && (
          <SettingsPage settings={settings} onUpdate={updateSettings} onNavigate={setPage} />
        )}

        {page === "practice" && sessionId && (
          <PracticeSession
            sessionId={sessionId}
            mode={sessionMode}
            onComplete={handleComplete}
            onExit={handleExitPractice}
          />
        )}

        {page === "review" && sessionId && (
          <ReviewPage
            sessionId={sessionId}
            submitResult={submitResult}
            onDone={() => {
              setSessionId(null);
              setSubmitResult(null);
              setPage("home");
            }}
          />
        )}

        {page === "privacy" && (
          <LegalPage title="Privacy Policy" onBack={() => setPage("settings")}>
            <p>Last updated: June 2026</p>
            <h3>Data Storage</h3>
            <p>
              When hosted on a cloud server (e.g. Render), your study progress is stored in a SQLite database on that server, scoped to an anonymous profile ID in your browser. The same ID on phone and PC keeps progress in sync.
            </p>
            <p>
              When run locally, data is stored in <code>backend/cissp_study.db</code> on your machine.
            </p>
            <h3>What We Store</h3>
            <p>
              Question attempts, session scores, practice settings, exam date, flagged items, and bank coverage — tied to your anonymous study profile ID, not your name or email.
            </p>
            <h3>Third Parties</h3>
            <p>
              No third-party analytics or advertising. Google Fonts may load when online for typography.
            </p>
            <h3>Your Control</h3>
            <p>
              Export progress from Analysis as CSV. Clear browser storage to start a new anonymous profile. Contact your host administrator to reset server-side data.
            </p>
          </LegalPage>
        )}

        {page === "terms" && (
          <LegalPage title="Terms of Use" onBack={() => setPage("settings")}>
            <p>Last updated: June 2026</p>
            <h3>Educational Purpose</h3>
            <p>
              CISSP Study Companion is an unofficial study tool. It is not affiliated with, endorsed by, or connected to ISC2 or Pearson VUE. Questions are original content aligned to the public CISSP exam outline.
            </p>
            <h3>No Guarantee</h3>
            <p>
              Performance in this app does not guarantee passing the actual CISSP exam. The real exam uses proprietary adaptive scoring not replicated here.
            </p>
            <h3>CAT Simulation</h3>
            <p>
              Mock exams follow the April 2024 outline: 125–150 questions, 3-hour limit, domain-weighted adaptive difficulty, and deferred grading. This is a study simulation — not the official Pearson VUE engine.
            </p>
            <h3>Acceptable Use</h3>
            <p>
              Use this tool for personal CISSP exam preparation. Do not redistribute question content commercially without permission.
            </p>
          </LegalPage>
        )}
      </main>
      <BottomNav page={page} onNavigate={setPage} />
    </div>
  );
}
