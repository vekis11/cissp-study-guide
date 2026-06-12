import type { Session } from "../../types";
import { scaledColor } from "../../utils/chartColors";

interface SessionTrendChartProps {
  sessions: Session[];
  height?: number;
}

export function SessionTrendChart({ sessions, height = 160 }: SessionTrendChartProps) {
  const points = [...sessions].reverse().slice(-10);
  if (points.length === 0) {
    return <p className="chart-empty">Complete sessions to see your performance trend.</p>;
  }

  const w = 600;
  const pad = { t: 20, r: 16, b: 32, l: 40 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;

  const useScaled = points.some((s) => s.scaled_score != null);
  const maxV = useScaled ? 1000 : 100;
  const minV = useScaled ? 400 : 40;

  const coords = points.map((s, i) => {
    const v = s.scaled_score ?? (s.score_percent ?? 0) * (useScaled ? 10 : 1);
    const x = pad.l + (i / Math.max(1, points.length - 1)) * innerW;
    const y = pad.t + innerH - ((v - minV) / (maxV - minV)) * innerH;
    return { x, y, v, session: s };
  });

  const line = coords.map((p) => `${p.x},${p.y}`).join(" ");
  const area = `${pad.l},${pad.t + innerH} ${line} ${coords[coords.length - 1].x},${pad.t + innerH}`;

  const passY = pad.t + innerH - ((700 - minV) / (maxV - minV)) * innerH;

  return (
    <div className="session-trend-chart">
      <svg viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.35" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0, 25, 50, 75, 100].map((g) => {
          const y = pad.t + innerH - (g / 100) * innerH;
          return (
            <line key={g} x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke="var(--chart-grid)" strokeWidth="1" />
          );
        })}
        {useScaled && (
          <>
            <line
              x1={pad.l}
              y1={passY}
              x2={w - pad.r}
              y2={passY}
              stroke="var(--warning)"
              strokeWidth="1.5"
              strokeDasharray="6 4"
            />
            <text x={pad.l + 4} y={passY - 6} className="trend-pass-label">
              Pass 700
            </text>
          </>
        )}
        <polygon points={area} fill="url(#trendFill)" />
        <polyline points={line} fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinejoin="round" />
        {coords.map((p, i) => (
          <g key={p.session.id}>
            <circle cx={p.x} cy={p.y} r="6" fill={scaledColor(p.v, 700)} stroke="var(--bg-card)" strokeWidth="2" />
            <text x={p.x} y={height - 8} textAnchor="middle" className="trend-x-label">
              {i + 1}
            </text>
          </g>
        ))}
      </svg>
      <div className="trend-summary">
        {points.slice(-3).map((s) => (
          <span key={s.id} className="trend-chip">
            {s.session_type.replace("_", " ")} ·{" "}
            {s.scaled_score != null ? `${s.scaled_score.toFixed(0)}/1000` : `${s.score_percent?.toFixed(0)}%`}
          </span>
        ))}
      </div>
    </div>
  );
}
