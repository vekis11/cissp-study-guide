import type { DomainStats } from "../../types";
import { DOMAIN_COLORS } from "../../utils/chartColors";

interface DomainRadarProps {
  domains: DomainStats[];
  size?: number;
}

export function DomainRadar({ domains, size = 320 }: DomainRadarProps) {
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size * 0.36;
  const levels = [25, 50, 75, 100];
  const n = domains.length;

  const point = (index: number, value: number) => {
    const angle = (Math.PI * 2 * index) / n - Math.PI / 2;
    const r = (Math.min(100, Math.max(0, value)) / 100) * maxR;
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  };

  const dataPoints = domains.map((d, i) => point(i, d.pass_rate));
  const polygon = dataPoints.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className="chart-radar-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="chart-radar">
        {levels.map((lvl) => {
          const pts = domains
            .map((_, i) => {
              const p = point(i, lvl);
              return `${p.x},${p.y}`;
            })
            .join(" ");
          return (
            <polygon
              key={lvl}
              points={pts}
              fill="none"
              stroke="var(--chart-grid)"
              strokeWidth="1"
              opacity={0.35 + lvl / 400}
            />
          );
        })}
        {domains.map((d, i) => {
          const outer = point(i, 100);
          const label = point(i, 118);
          return (
            <g key={d.domain}>
              <line x1={cx} y1={cy} x2={outer.x} y2={outer.y} stroke="var(--chart-grid)" strokeWidth="1" />
              <circle cx={dataPoints[i].x} cy={dataPoints[i].y} r="5" fill={DOMAIN_COLORS[i]} />
              <text
                x={label.x}
                y={label.y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="radar-label"
              >
                D{d.domain}
              </text>
            </g>
          );
        })}
        <polygon points={polygon} fill="rgba(59, 130, 246, 0.25)" stroke="var(--accent)" strokeWidth="2" />
      </svg>
      <div className="radar-legend">
        {domains.map((d, i) => (
          <span key={d.domain} className="radar-legend-item">
            <span className="radar-dot" style={{ background: DOMAIN_COLORS[i] }} />
            D{d.domain}: {d.pass_rate.toFixed(0)}%
          </span>
        ))}
      </div>
    </div>
  );
}
