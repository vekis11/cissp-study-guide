import type { DomainStats } from "../../types";
import { DOMAIN_COLORS, scoreColor } from "../../utils/chartColors";
import { readinessClass } from "../../hooks/useSettings";

interface DomainBarChartProps {
  domains: DomainStats[];
  passThreshold: number;
}

export function DomainBarChart({ domains, passThreshold }: DomainBarChartProps) {
  const maxWeight = Math.max(...domains.map((d) => d.weight));

  return (
    <div className="domain-bar-chart">
      {domains.map((d, i) => (
        <div key={d.domain} className="domain-bar-row">
          <div className="domain-bar-meta">
            <span className="domain-bar-id" style={{ color: DOMAIN_COLORS[i] }}>
              D{d.domain}
            </span>
            <span className="domain-bar-name">{d.domain_name}</span>
            <span className={`readiness-badge ${readinessClass(d.readiness)}`}>{d.readiness}</span>
          </div>
          <div className="domain-bar-track-wrap">
            <div className="domain-bar-weight" style={{ width: `${(d.weight / maxWeight) * 100}%` }} title="Exam weight" />
            <div className="domain-bar-track">
              <div
                className="domain-bar-fill"
                style={{
                  width: `${Math.min(100, d.pass_rate)}%`,
                  background: `linear-gradient(90deg, ${DOMAIN_COLORS[i]}, ${DOMAIN_COLORS[i]}99)`,
                  boxShadow: `0 0 12px ${DOMAIN_COLORS[i]}55`,
                }}
              />
              <span
                className="domain-bar-threshold"
                style={{ left: `${passThreshold}%` }}
                title={`Study benchmark ${passThreshold}%`}
              />
            </div>
            <div className="domain-bar-stats">
              <span style={{ color: scoreColor(d.pass_rate, passThreshold), fontFamily: "var(--mono)", fontWeight: 700 }}>
                {d.pass_rate.toFixed(1)}%
              </span>
              <span className="domain-bar-attempts">
                {d.correct_attempts}/{d.total_attempts}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
