import { useId, type CSSProperties } from "react";
import { COMPANY_NAME, COMPANY_SHORT_NAME, COMPANY_TAGLINE } from "../constants/branding";
import { TemTechMarkSvg } from "./TemTechMarkSvg";

export type TemTechLogoVariant = "mark" | "lockup" | "stacked";

interface TemTechLogoProps {
  size?: number;
  className?: string;
  showLabel?: boolean;
  variant?: TemTechLogoVariant;
}

export function TemTechLogo({
  size = 40,
  className = "",
  showLabel = false,
  variant = "mark",
}: TemTechLogoProps) {
  const gradientId = useId().replace(/:/g, "");
  const resolvedVariant = showLabel ? "lockup" : variant;

  if (resolvedVariant === "mark") {
    return (
      <span
        className={`temtech-logo-wrap temtech-logo-wrap--mark ${className}`}
        style={{ "--logo-size": `${size}px` } as CSSProperties}
        title={COMPANY_NAME}
      >
        <TemTechMarkSvg size={size} gradientId={gradientId} className="temtech-logo-svg" />
      </span>
    );
  }

  if (resolvedVariant === "stacked") {
    return (
      <span
        className={`temtech-logo-wrap temtech-logo-wrap--stacked ${className}`}
        style={{ "--logo-size": `${size}px` } as CSSProperties}
      >
        <TemTechMarkSvg size={size} gradientId={gradientId} className="temtech-logo-svg" />
        <span className="temtech-wordmark temtech-wordmark--stacked">
          <span className="temtech-wordmark-name">{COMPANY_SHORT_NAME}</span>
          <span className="temtech-wordmark-tag">{COMPANY_TAGLINE}</span>
        </span>
      </span>
    );
  }

  return (
    <span
      className={`temtech-logo-wrap temtech-logo-wrap--lockup ${className}`}
      style={{ "--logo-size": `${size}px` } as CSSProperties}
    >
      <TemTechMarkSvg size={size} gradientId={gradientId} className="temtech-logo-svg" />
      <span className="temtech-wordmark">
        <span className="temtech-wordmark-name">{COMPANY_SHORT_NAME}</span>
        <span className="temtech-wordmark-solutions">Solutions</span>
      </span>
    </span>
  );
}
