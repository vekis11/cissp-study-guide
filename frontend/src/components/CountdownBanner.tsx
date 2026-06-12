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
      <div className="countdown-copy">
        <span className="countdown-eyebrow">Exam countdown</span>
        <strong className="countdown-title">
          {past ? "Your exam date has passed" : `${days} day${days !== 1 ? "s" : ""} to go`}
        </strong>
        <span className="countdown-date">
          Target: {new Date(settings.exam_date + "T00:00:00").toLocaleDateString(undefined, {
            weekday: "short",
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
        </span>
      </div>
      {!past && (
        <div className="countdown-ring-wrap" aria-hidden>
          <span className="countdown-days">{days}</span>
        </div>
      )}
    </div>
  );
}
