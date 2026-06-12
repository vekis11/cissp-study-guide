interface ProgressRingProps {
  value: number;
  max: number;
  label: string;
  sublabel?: string;
  size?: number;
}

export function ProgressRing({ value, max, label, sublabel, size = 120 }: ProgressRingProps) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  const r = (size - 12) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;

  return (
    <div className="progress-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="progress-ring-track"
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth="6"
        />
        <circle
          className="progress-ring-fill"
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth="6"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="progress-ring-label">
        <span className="progress-ring-value">{pct}%</span>
        <span className="progress-ring-text">{label}</span>
        {sublabel && <span className="progress-ring-sub">{sublabel}</span>}
      </div>
    </div>
  );
}
