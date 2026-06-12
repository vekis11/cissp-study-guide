import type { ReactNode } from "react";
import type { Page } from "../types";
import { IconBook, IconChart, IconExam, IconHome, IconSettings } from "./ui/Icons";

interface BottomNavProps {
  page: Page;
  onNavigate: (page: Page) => void;
}

const ITEMS: { page: Page; label: string; icon: ReactNode }[] = [
  { page: "home", label: "Home", icon: <IconHome size={20} /> },
  { page: "study", label: "Guide", icon: <IconBook size={20} /> },
  { page: "mock", label: "Exam", icon: <IconExam size={20} /> },
  { page: "analysis", label: "Stats", icon: <IconChart size={20} /> },
  { page: "settings", label: "More", icon: <IconSettings size={20} /> },
];

const HIDE_ON: Page[] = ["practice", "review", "privacy", "terms"];

export function BottomNav({ page, onNavigate }: BottomNavProps) {
  if (HIDE_ON.includes(page)) return null;

  return (
    <nav className="bottom-nav" aria-label="Main navigation">
      <div className="bottom-nav-inner">
        {ITEMS.map(({ page: p, label, icon }) => {
          const active = page === p || (p === "home" && page === "daily");
          return (
            <button
              key={p}
              type="button"
              className={`bottom-nav-item ${active ? "active" : ""}`}
              onClick={() => onNavigate(p)}
            >
              <span className="bottom-nav-icon">{icon}</span>
              <span className="bottom-nav-label">{label}</span>
              {active && <span className="bottom-nav-indicator" aria-hidden />}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
