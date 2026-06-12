import type { Page } from "../types";
import { TemTechLogo } from "./TemTechLogo";

interface NavBarProps {
  page: Page;
  onNavigate: (page: Page) => void;
}

const NAV_ITEMS: { page: Page; label: string }[] = [
  { page: "home", label: "Home" },
  { page: "daily", label: "Daily" },
  { page: "missed", label: "Missed" },
  { page: "mock", label: "Mock Exam" },
  { page: "domain", label: "Domain Test" },
  { page: "study", label: "Study Guide" },
  { page: "analysis", label: "Analysis" },
  { page: "settings", label: "Settings" },
];

export function NavBar({ page, onNavigate }: NavBarProps) {
  return (
    <header className="topbar">
      <button className="logo" onClick={() => onNavigate("home")} type="button">
        <TemTechLogo size={36} />
        <span className="logo-text-wrap">
          <span className="logo-text">CISSP Study</span>
          <span className="logo-sub">by TemTech</span>
        </span>
      </button>
      <nav className="nav nav-desktop">
        {NAV_ITEMS.map(({ page: p, label }) => (
          <button
            key={p}
            type="button"
            className={`nav-btn ${page === p ? "active" : ""}`}
            onClick={() => onNavigate(p)}
          >
            {label}
          </button>
        ))}
      </nav>
    </header>
  );
}