import { daysUntilExam } from "../hooks/useSettings";
import type { Settings } from "../types";

interface CountdownBannerProps {
  settings: Settings;
}

export function CountdownBanner({ settings }: CountdownBannerProps) {
  if (!settings.exam_date || !settings.exam_alert_enabled) return null;

  const days = daysUntilExam(settings.exam_date);
  if (days === null) return null;

  const urgent = days <= 14 && days >= 0;
  const past = days < 0;

  return (
    <div className={`countdown-banner ${urgent ? "urgent" : ""}`}>
      <div>
        <strong>Exam Countdown</strong>
        <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
          Target: {new Date(settings.exam_date + "T00:00:00").toLocaleDateString()}
        </div>
      </div>
      <div style={{ textAlign: "right" }}>
        {past ? (
          <span className="countdown-days">Exam day passed — good luck!</span>
        ) : (
          <>
            <div className="countdown-days">{days}</div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              day{days !== 1 ? "s" : ""} remaining
            </div>
          </>
        )}
      </div>
    </div>
  );
}
