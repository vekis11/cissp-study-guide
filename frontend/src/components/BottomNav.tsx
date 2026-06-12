import type { Page } from "../types";

interface BottomNavProps {
  page: Page;
  onNavigate: (page: Page) => void;
}

const ITEMS: { page: Page; label: string; icon: string }[] = [
  { page: "home", label: "Home", icon: "⌂" },
  { page: "daily", label: "Daily", icon: "◉" },
  { page: "missed", label: "Missed", icon: "✗" },
  { page: "mock", label: "Exam", icon: "▣" },
  { page: "analysis", label: "Stats", icon: "▤" },
  { page: "settings", label: "Settings", icon: "⚙" },
];

const HIDE_ON: Page[] = ["practice", "review", "privacy", "terms"];

export function BottomNav({ page, onNavigate }: BottomNavProps) {
  if (HIDE_ON.includes(page)) return null;

  return (
    <nav className="bottom-nav" aria-label="Main navigation">
      {ITEMS.map(({ page: p, label, icon }) => (
        <button
          key={p}
          type="button"
          className={`bottom-nav-item ${page === p || (p === "daily" && page === "home") ? "active" : ""}`}
          onClick={() => onNavigate(p)}
        >
          <span className="bottom-nav-icon" aria-hidden>
            {icon}
          </span>
          <span className="bottom-nav-label">{label}</span>
        </button>
      ))}
    </nav>
  );
}
