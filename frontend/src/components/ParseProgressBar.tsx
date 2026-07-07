type ParseProgressBarProps = {
  percent: number;
  message: string;
  isActive: boolean;
};

export function ParseProgressBar({ percent, message, isActive }: ParseProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, percent));

  return (
    <div className="w-full space-y-2" aria-live="polite" aria-busy={isActive}>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700">{isActive ? message : "Ready"}</span>
        <span className="tabular-nums text-slate-500">{clamped}%</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${
            isActive ? "bg-indigo-500" : "bg-emerald-500"
          }`}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
