import type { LearningCurvePoint } from "../../types";

interface LearningCurveChartProps {
  points: LearningCurvePoint[];
  height?: number;
}

const SERIES = [
  { key: "passing" as const, label: "Passing", color: "var(--success)" },
  { key: "security" as const, label: "Security (D1)", color: "var(--accent)" },
  { key: "hazard" as const, label: "Hazard", color: "var(--danger)" },
];

export function LearningCurveChart({ points, height = 200 }: LearningCurveChartProps) {
  if (points.length === 0) {
    return <p className="chart-empty">Complete more sessions to see your learning curve.</p>;
  }

  const w = 600;
  const pad = { t: 24, r: 16, b: 36, l: 44 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const minV = 0;
  const maxV = 100;

  const toY = (v: number) => pad.t + innerH - ((v - minV) / (maxV - minV)) * innerH;

  const coordsFor = (key: "passing" | "security" | "hazard") =>
    points.map((p, i) => {
      const raw = p[key];
      const v = raw ?? (key === "security" ? null : 0);
      if (v === null) return null;
      const x = pad.l + (i / Math.max(1, points.length - 1)) * innerW;
      return { x, y: toY(v), v, i };
    }).filter(Boolean) as { x: number; y: number; v: number; i: number }[];

  const benchmarkY = toY(70);

  return (
    <div className="learning-curve-chart">
      <div className="learning-curve-legend">
        {SERIES.map((s) => (
          <span key={s.key} className="learning-curve-legend-item">
            <span className="learning-curve-swatch" style={{ background: s.color }} />
            {s.label}
          </span>
        ))}
        <span className="learning-curve-legend-item learning-curve-legend-bench">
          <span className="learning-curve-swatch learning-curve-swatch--dashed" />
          70% benchmark
        </span>
      </div>
      <svg viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="xMidYMid meet">
        {[0, 25, 50, 75, 100].map((g) => {
          const y = toY(g);
          return (
            <g key={g}>
              <line x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke="var(--chart-grid)" strokeWidth="1" />
              <text x={pad.l - 6} y={y + 4} textAnchor="end" className="trend-x-label">
                {g}
              </text>
            </g>
          );
        })}
        <line
          x1={pad.l}
          y1={benchmarkY}
          x2={w - pad.r}
          y2={benchmarkY}
          stroke="var(--warning)"
          strokeWidth="1.5"
          strokeDasharray="6 4"
        />
        {SERIES.map((s) => {
          const coords = coordsFor(s.key);
          if (coords.length < 2) return null;
          const line = coords.map((p) => `${p.x},${p.y}`).join(" ");
          return (
            <g key={s.key}>
              <polyline
                points={line}
                fill="none"
                stroke={s.color}
                strokeWidth={s.key === "hazard" ? 2 : 2.5}
                strokeLinejoin="round"
                strokeDasharray={s.key === "hazard" ? "5 4" : undefined}
              />
              {coords.map((p) => (
                <circle
                  key={`${s.key}-${p.i}`}
                  cx={p.x}
                  cy={p.y}
                  r="4"
                  fill={s.color}
                  stroke="var(--bg-card)"
                  strokeWidth="1.5"
                />
              ))}
            </g>
          );
        })}
        {points.map((p, i) => {
          const x = pad.l + (i / Math.max(1, points.length - 1)) * innerW;
          return (
            <text key={p.session_id} x={x} y={height - 8} textAnchor="middle" className="trend-x-label">
              {i + 1}
            </text>
          );
        })}
      </svg>
      <p className="learning-curve-note sub">
        Passing = session score toward 700 scaled · Security = Domain 1 accuracy per session · Hazard = gap below 70%
        study benchmark
      </p>
    </div>
  );
}
