type StatCardProps = {
  label: string;
  value: string;
  hint?: string;
  accent?: "cyan" | "violet" | "pink" | "green";
};

const accentTopLine: Record<NonNullable<StatCardProps["accent"]>, string> = {
  cyan: "from-cyan-400/50 to-transparent",
  violet: "from-violet-400/50 to-transparent",
  pink: "from-pink-400/50 to-transparent",
  green: "from-emerald-400/50 to-transparent",
};

export function StatCard({ label, value, hint, accent = "cyan" }: StatCardProps) {
  return (
    <div className="glass-panel-strong relative overflow-hidden p-5">
      <div
        className={`pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r ${accentTopLine[accent]}`}
        aria-hidden
      />
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums text-slate-100">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-600">{hint}</p> : null}
    </div>
  );
}
