export function scoreColor(value: number, passThreshold = 70): string {
  if (value >= passThreshold + 10) return "var(--success)";
  if (value >= passThreshold) return "var(--accent)";
  if (value >= passThreshold - 15) return "var(--warning)";
  return "var(--danger)";
}

export function scaledColor(scaled: number, pass = 700): string {
  if (scaled >= pass + 80) return "var(--success)";
  if (scaled >= pass) return "var(--accent)";
  if (scaled >= pass - 120) return "var(--warning)";
  return "var(--danger)";
}

export function readinessHue(label: string): string {
  if (label.includes("Ready") && !label.includes("Near")) return "var(--success)";
  if (label.includes("Near")) return "var(--accent)";
  if (label.includes("Building")) return "var(--warning)";
  return "var(--danger)";
}

export const DOMAIN_COLORS = [
  "#3b82f6",
  "#8b5cf6",
  "#06b6d4",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#ec4899",
  "#6366f1",
];
