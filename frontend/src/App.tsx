import { useState, type ReactNode } from "react";
import { Watermark } from "./components/Watermark";
import { NavBar } from "./components/NavBar";
import { BottomNav } from "./components/BottomNav";
import { InstallPrompt } from "./components/InstallPrompt";
import { PracticeSession } from "./components/PracticeSession";
import { useSettings } from "./hooks/useSettings";
import { api } from "./api";
import { HomePage } from "./pages/HomePage";
import { MockExamPage } from "./pages/MockExamPage";
import { DomainTestPage } from "./pages/DomainTestPage";
import { MissedPage } from "./pages/MissedPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ReviewPage } from "./pages/ReviewPage";
import type { Page, SubmitResult, SessionType } from "./types";

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
  const { settings, loading, updateSettings } = useSettings();
  const [page, setPage] = useState<Page>("home");
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [sessionMode, setSessionMode] = useState("newbie");
  const [startError, setStartError] = useState<string | null>(null);

  const startSession = async (type: SessionType, count: number, domain?: number) => {
    setStartError(null);
    try {
      const session = await api.sessions.start({ session_type: type, count, domain });
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

  if (loading || !settings) {
    return <div className="loading">Loading CISSP Study Companion...</div>;
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

        {page === "mock" && <MockExamPage onStart={(count) => startSession("mock_exam", count)} />}

        {page === "domain" && (
          <DomainTestPage onStart={(domain, count) => startSession("domain_test", count, domain)} />
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
              All study progress, session scores, missed questions, and settings are stored locally in a SQLite database on your machine. No data is transmitted to external servers.
            </p>
            <h3>What We Collect</h3>
            <p>
              The app stores: question attempts, session scores, practice settings, and exam date preferences. This data never leaves your local environment unless you explicitly export it.
            </p>
            <h3>Third Parties</h3>
            <p>
              This application does not integrate third-party analytics or advertising. Google Fonts may load when online for typography.
            </p>
            <h3>Your Control</h3>
            <p>
              Delete the file <code>backend/cissp_study.db</code> to reset all stored data.
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
              Mock exams simulate CAT-style behavior (domain weighting, adaptive difficulty, deferred grading) but are approximations for study purposes only.
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
