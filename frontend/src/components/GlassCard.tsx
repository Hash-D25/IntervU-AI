import type { ReactNode } from "react";

type GlassCardProps = {
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  accent?: "cyan" | "violet" | "pink" | "green" | "none";
};

const accentBorder: Record<NonNullable<GlassCardProps["accent"]>, string> = {
  cyan: "border-t-cyan-400/40",
  violet: "border-t-violet-400/40",
  pink: "border-t-pink-400/40",
  green: "border-t-emerald-400/40",
  none: "border-t-white/5",
};

export function GlassCard({
  title,
  description,
  action,
  children,
  className = "",
  accent = "none",
}: GlassCardProps) {
  const hasHeader = title || description || action;

  return (
    <section className={`glass-panel border-t p-6 ${accentBorder[accent]} ${className}`}>
      {hasHeader ? (
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            {title ? (
              <h2 className="text-lg font-semibold tracking-tight text-slate-100">{title}</h2>
            ) : null}
            {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
          </div>
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}
