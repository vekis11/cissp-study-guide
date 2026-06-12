import type { ReactNode } from "react";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  children?: ReactNode;
  align?: "left" | "center";
}

export function PageHeader({ eyebrow, title, subtitle, children, align = "left" }: PageHeaderProps) {
  return (
    <header className={`page-header page-header--${align}`}>
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
      {children}
    </header>
  );
}
