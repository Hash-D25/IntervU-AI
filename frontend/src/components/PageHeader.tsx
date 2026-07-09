import type { ReactNode } from "react";

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageHeader({ eyebrow, title, description, actions }: PageHeaderProps) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-4">
      <div>
        {eyebrow ? (
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-cyan-400/70">{eyebrow}</p>
        ) : null}
        <h1 className={`font-semibold tracking-tight text-slate-100 ${eyebrow ? "mt-2 text-3xl" : "text-3xl"}`}>
          {title}
        </h1>
        {description ? <p className="mt-2 max-w-2xl text-slate-500">{description}</p> : null}
      </div>
      {actions}
    </header>
  );
}
