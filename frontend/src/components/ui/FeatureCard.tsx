import type { ReactNode } from "react";
import { IconArrow } from "./Icons";

type FeatureVariant = "default" | "primary" | "accent" | "success" | "violet";

interface FeatureCardProps {
  title: string;
  description?: string;
  icon: ReactNode;
  onClick: () => void;
  variant?: FeatureVariant;
  size?: "default" | "wide" | "featured";
  badge?: string;
}

export function FeatureCard({
  title,
  description,
  icon,
  onClick,
  variant = "default",
  size = "default",
  badge,
}: FeatureCardProps) {
  return (
    <button
      type="button"
      className={`feature-card feature-card--${variant} feature-card--${size}`}
      onClick={onClick}
    >
      <div className="feature-card-glow" aria-hidden />
      <div className="feature-card-top">
        <span className="feature-card-icon">{icon}</span>
        {badge && <span className="feature-card-badge">{badge}</span>}
      </div>
      <div className="feature-card-body">
        <span className="feature-card-title">{title}</span>
        {description && <span className="feature-card-desc">{description}</span>}
      </div>
      <span className="feature-card-arrow" aria-hidden>
        <IconArrow size={16} />
      </span>
    </button>
  );
}
