interface IconProps {
  size?: number;
  className?: string;
}

const base = (size: number, className?: string) => ({
  width: size,
  height: size,
  className,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.75,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
});

export function IconHome({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-9.5Z" />
    </svg>
  );
}

export function IconDaily({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4l2.5 2.5" />
    </svg>
  );
}

export function IconMissed({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 8 8 8M16 8l-8 8" />
    </svg>
  );
}

export function IconExam({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 8h6M9 12h6M9 16h4" />
    </svg>
  );
}

export function IconChart({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M4 20V10M10 20V4M16 20v-6M22 20H2" />
    </svg>
  );
}

export function IconSettings({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  );
}

export function IconBook({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M5 4h9a3 3 0 0 1 3 3v14a3 3 0 0 0-3-3H5V4Z" />
      <path d="M5 4h8a3 3 0 0 1 3 3v14" />
    </svg>
  );
}

export function IconTarget({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconFlag({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M6 3v18M6 4h11l-2 3 2 3H6" />
    </svg>
  );
}

export function IconSpark({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M12 2 9 9l-7 3 7 3 3 7 3-7 7-3-7-3-3-7Z" />
    </svg>
  );
}

export function IconShield({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6l-7-3Z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

export function IconChevron({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="m6 9 6 6 6-6" />
    </svg>
  );
}

export function IconArrow({ size = 20, className }: IconProps) {
  return (
    <svg {...base(size, className)}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}
