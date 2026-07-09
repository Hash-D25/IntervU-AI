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
        <span className="font-medium text-slate-300">{isActive ? message : "Ready"}</span>
        <span className="tabular-nums text-slate-500">{clamped}%</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full border border-white/5 bg-white/5">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${
            isActive
              ? "bg-gradient-to-r from-cyan-400/90 to-violet-400/90"
              : "bg-gradient-to-r from-emerald-400/90 to-cyan-400/90"
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
