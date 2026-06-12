import type { CSSProperties } from "react";
import { TEMTECH_LOGO_URL, COMPANY_NAME } from "../constants/branding";

interface TemTechLogoProps {
  size?: number;
  className?: string;
  showLabel?: boolean;
}

export function TemTechLogo({ size = 40, className = "", showLabel = false }: TemTechLogoProps) {
  return (
    <span className={`temtech-logo-wrap ${className}`} style={{ "--logo-size": `${size}px` } as CSSProperties}>
      <img
        src={TEMTECH_LOGO_URL}
        alt={COMPANY_NAME}
        className="temtech-logo-img"
        width={size}
        height={size}
        loading="lazy"
        referrerPolicy="no-referrer"
        crossOrigin="anonymous"
      />
      {showLabel && <span className="temtech-logo-label">{COMPANY_NAME}</span>}
    </span>
  );
}
