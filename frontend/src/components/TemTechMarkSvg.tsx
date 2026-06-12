/**
 * TemTech Solutions — brand mark (shield + monogram).
 * Inline SVG for crisp rendering at any size on mobile and desktop.
 */

interface TemTechMarkSvgProps {
  size?: number;
  className?: string;
  gradientId?: string;
  /** App icon style: filled card background */
  variant?: "default" | "app";
}

export function TemTechMarkSvg({
  size = 40,
  className = "",
  gradientId = "tt-brand-grad",
  variant = "default",
}: TemTechMarkSvgProps) {
  const bgId = `${gradientId}-bg`;
  const glowId = `${gradientId}-glow`;

  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-hidden={variant === "default"}
    >
      <defs>
        <linearGradient id={gradientId} x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse">
          <stop stopColor="#38bdf8" />
          <stop offset="0.45" stopColor="#6366f1" />
          <stop offset="1" stopColor="#a78bfa" />
        </linearGradient>
        <linearGradient id={bgId} x1="32" y1="4" x2="32" y2="60" gradientUnits="userSpaceOnUse">
          <stop stopColor="#161f2e" />
          <stop offset="1" stopColor="#070b12" />
        </linearGradient>
        <radialGradient id={glowId} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(20 16) rotate(45) scale(40)">
          <stop stopColor="#38bdf8" stopOpacity="0.35" />
          <stop offset="1" stopColor="#38bdf8" stopOpacity="0" />
        </radialGradient>
      </defs>

      {variant === "app" && (
        <>
          <rect width="64" height="64" rx="14" fill="url(#bgId)" />
          <rect width="64" height="64" rx="14" fill={`url(#${glowId})`} />
        </>
      )}

      <rect
        x={variant === "app" ? 6 : 3}
        y={variant === "app" ? 6 : 3}
        width={variant === "app" ? 52 : 58}
        height={variant === "app" ? 52 : 58}
        rx={variant === "app" ? 12 : 14}
        fill={variant === "app" ? "transparent" : `url(#${bgId})`}
        stroke={`url(#${gradientId})`}
        strokeWidth="1.5"
        strokeOpacity={variant === "app" ? 0.9 : 0.65}
      />

      {/* Shield silhouette — security */}
      <path
        d="M32 15.5 46.5 22.2V35.2c0 7.2-5.8 12.8-14.5 15.3-8.7-2.5-14.5-8.1-14.5-15.3V22.2L32 15.5Z"
        stroke={`url(#${gradientId})`}
        strokeWidth="2.4"
        strokeLinejoin="round"
        fill={`url(#${gradientId})`}
        fillOpacity="0.12"
      />

      {/* TT monogram — TemTech */}
      <path
        d="M24.5 29.5h15M31.75 29.5V41.5M36.25 29.5V41.5"
        stroke={`url(#${gradientId})`}
        strokeWidth="2.8"
        strokeLinecap="round"
      />

      {/* Network nodes — cloud / platform */}
      <circle cx="32" cy="20" r="2.2" fill="#38bdf8" />
      <circle cx="40.5" cy="25" r="1.6" fill="#818cf8" fillOpacity="0.9" />
      <circle cx="23.5" cy="25" r="1.6" fill="#818cf8" fillOpacity="0.9" />
      <path
        d="M32 22.2v3.8M25.1 25h3.2M35.7 25h3.2"
        stroke="#6366f1"
        strokeWidth="1.2"
        strokeLinecap="round"
        opacity="0.7"
      />
    </svg>
  );
}
