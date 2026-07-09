import { barTone, formatCategory, formatDimension, formatScore } from "@/features/dashboard/format";

type ScoreBarProps = {
  label: string;
  score: number;
  maxScore?: number;
  meta?: string;
};

export function ScoreBar({ label, score, maxScore = 10, meta }: ScoreBarProps) {
  const width = Math.max(4, Math.round((score / maxScore) * 100));
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-medium text-slate-200">{label}</span>
        <span className="tabular-nums text-slate-400">
          <span className="font-semibold text-white">{formatScore(score)}</span>
          {meta ? <span className="text-slate-500"> · {meta}</span> : null}
        </span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full border border-white/5 bg-white/5">
        <div
          className={`h-full rounded-full transition-all duration-500 ${barTone(score)}`}
          style={{ width: `${width}%` }}
          aria-hidden
        />
      </div>
    </div>
  );
}

type CategoryScoresProps = {
  items: Array<{ category: string; average_score: number; answer_count: number }>;
};

export function CategoryScores({ items }: CategoryScoresProps) {
  if (items.length === 0) {
    return <EmptyInsight message="Answer questions to see category scores." />;
  }
  return (
    <div className="space-y-5">
      {items.map((item) => (
        <ScoreBar
          key={item.category}
          label={formatCategory(item.category)}
          score={item.average_score}
          meta={`${item.answer_count} answer${item.answer_count === 1 ? "" : "s"}`}
        />
      ))}
    </div>
  );
}

type DimensionScoresProps = {
  averages: Record<string, number>;
};

export function DimensionScores({ averages }: DimensionScoresProps) {
  const entries = Object.entries(averages);
  if (entries.length === 0) {
    return <EmptyInsight message="Dimension scores appear after evaluated answers." />;
  }
  return (
    <div className="space-y-5">
      {entries.map(([dimension, score]) => (
        <ScoreBar key={dimension} label={formatDimension(dimension)} score={score} />
      ))}
    </div>
  );
}

function EmptyInsight({ message }: { message: string }) {
  return <p className="text-sm text-slate-500">{message}</p>;
}
