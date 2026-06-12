import { scaledColor } from "../../utils/chartColors";

interface ScoreGaugeProps {
  value: number;
  max?: number;
  passAt?: number;
  label?: string;
  sublabel?: string;
  size?: number;
  variant?: "scaled" | "percent";
}

export function ScoreGauge({
  value,
  max = 1000,
  passAt = 700,
  label,
  sublabel,
  size = 200,
  variant = "scaled",
}: ScoreGaugeProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const passPct = (passAt / max) * 100;
  const r = (size - 24) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;
  const color = variant === "scaled" ? scaledColor(value, passAt) : scaledColor((value / 100) * 1000, passAt);

  return (
    <div className="score-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="1" />
            <stop offset="100%" stopColor={color} stopOpacity="0.55" />
          </linearGradient>
          <filter id="gaugeGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--chart-track)"
          strokeWidth="12"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="url(#gaugeGrad)"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          filter="url(#gaugeGlow)"
          className="gauge-arc"
        />
        {variant === "scaled" && (
          <line
            x1={size / 2}
            y1={12}
            x2={size / 2 + r * Math.sin((passPct / 100) * 2 * Math.PI - Math.PI / 2)}
            y2={size / 2 - r * Math.cos((passPct / 100) * 2 * Math.PI - Math.PI / 2)}
            stroke="var(--warning)"
            strokeWidth="2"
            strokeDasharray="4 3"
            opacity="0.85"
          />
        )}
      </svg>
      <div className="score-gauge-center">
        <div className="score-gauge-value" style={{ color }}>
          {variant === "scaled" ? value.toFixed(0) : `${value.toFixed(1)}%`}
        </div>
        {label && <div className="score-gauge-label">{label}</div>}
        {sublabel && <div className="score-gauge-sublabel">{sublabel}</div>}
      </div>
    </div>
  );
}
