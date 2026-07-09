import { barTone, formatDate, formatScore } from "@/features/dashboard/format";
import type { ProgressPoint } from "@/features/dashboard/types";

type ProgressChartProps = {
  points: ProgressPoint[];
};

export function ProgressChart({ points }: ProgressChartProps) {
  if (points.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Complete interviews with evaluated answers to track progress over time.
      </p>
    );
  }

  const maxScore = 10;

  return (
    <div className="space-y-5">
      <div className="relative flex h-52 items-end gap-2 rounded-xl border border-white/5 bg-white/[0.03] px-3 pb-3 pt-6">
        <div
          className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[length:100%_25%]"
          aria-hidden
        />
        {points.map((point) => {
          const height = Math.max(14, Math.round((point.overall_score / maxScore) * 100));
          return (
            <div
              key={point.interview_id}
              className="relative z-10 flex min-w-0 flex-1 flex-col items-center gap-2"
            >
              <span className="text-xs font-medium tabular-nums text-cyan-300/90">
                {formatScore(point.overall_score)}
              </span>
              <div className="flex h-32 w-full max-w-14 items-end justify-center">
                <div
                  className={`w-full rounded-t-lg ${barTone(point.overall_score)}`}
                  style={{ height: `${height}%` }}
                  title={`${point.label}: ${formatScore(point.overall_score)}`}
                />
              </div>
              <span className="max-w-full truncate text-center text-[10px] text-slate-500">
                {formatDate(point.recorded_at)}
              </span>
            </div>
          );
        })}
      </div>
      <ul className="space-y-1.5 text-xs text-slate-400">
        {points.map((point) => (
          <li key={`${point.interview_id}-label`} className="truncate">
            <span className="text-slate-500">▸</span> {point.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
