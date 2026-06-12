import type { CSSProperties } from "react";
import type { DomainStats } from "../../types";
import { DOMAIN_COLORS, scoreColor } from "../../utils/chartColors";
import { readinessClass } from "../../hooks/useSettings";

interface DomainProgressMapProps {
  domains: DomainStats[];
  passThreshold: number;
}

function masteryLevel(rate: number, attempts: number): string {
  if (attempts === 0) return "unstarted";
  if (rate >= 85) return "mastered";
  if (rate >= 70) return "strong";
  if (rate >= 50) return "developing";
  return "focus";
}

export function DomainProgressMap({ domains, passThreshold }: DomainProgressMapProps) {
  return (
    <div className="progress-map">
      <div className="progress-map-orbit" aria-hidden="true" />
      <div className="progress-map-grid">
        {domains.map((d, i) => {
          const level = masteryLevel(d.pass_rate, d.total_attempts);
          const pct = d.total_attempts === 0 ? 0 : Math.min(100, d.pass_rate);
          return (
            <article
              key={d.domain}
              className={`progress-map-tile level-${level}`}
              style={{ "--domain-color": DOMAIN_COLORS[i], "--fill-pct": `${pct}%` } as CSSProperties}
            >
              <div className="progress-map-ring">
                <svg viewBox="0 0 36 36">
                  <path
                    className="progress-map-ring-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="progress-map-ring-fill"
                    strokeDasharray={`${pct}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    style={{ stroke: DOMAIN_COLORS[i] }}
                  />
                </svg>
                <span className="progress-map-domain">D{d.domain}</span>
              </div>
              <h4 className="progress-map-title">{d.domain_name}</h4>
              <p className="progress-map-rate" style={{ color: scoreColor(d.pass_rate, passThreshold) }}>
                {d.total_attempts === 0 ? "—" : `${d.pass_rate.toFixed(0)}%`}
              </p>
              <span className={`readiness-badge ${readinessClass(d.readiness)}`}>{d.readiness}</span>
              <span className="progress-map-weight">{(d.weight * 100).toFixed(0)}% exam weight</span>
            </article>
          );
        })}
      </div>
      <div className="progress-map-legend">
        <span><i className="legend-dot mastered" /> Mastered 85%+</span>
        <span><i className="legend-dot strong" /> Strong 70%+</span>
        <span><i className="legend-dot developing" /> Building</span>
        <span><i className="legend-dot focus" /> Focus area</span>
        <span><i className="legend-dot unstarted" /> Not started</span>
      </div>
    </div>
  );
}
