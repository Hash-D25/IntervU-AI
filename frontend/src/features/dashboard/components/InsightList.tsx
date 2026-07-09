type InsightListProps = {
  title: string;
  items: string[];
  tone: "strength" | "weakness";
  emptyMessage: string;
};

export function InsightList({ title, items, tone, emptyMessage }: InsightListProps) {
  const toneClasses =
    tone === "strength"
      ? "border-emerald-400/20 bg-emerald-400/[0.06] text-slate-300 hover:border-emerald-400/35"
      : "border-amber-400/20 bg-amber-400/[0.06] text-slate-300 hover:border-amber-400/35";

  return (
    <div>
      <h3
        className={`text-sm font-medium uppercase tracking-wide ${
          tone === "strength" ? "text-emerald-400/90" : "text-amber-400/90"
        }`}
      >
        {title}
      </h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">{emptyMessage}</p>
      ) : (
        <ul className="mt-4 space-y-2.5">
          {items.map((item) => (
            <li
              key={item}
              className={`rounded-xl border px-4 py-3 text-sm leading-relaxed backdrop-blur-sm transition ${toneClasses}`}
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
