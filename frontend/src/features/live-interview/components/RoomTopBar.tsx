"use client";

import { ConnectionPill } from "@/features/live-interview/components/ConnectionPill";
import { formatElapsed } from "@/features/live-interview/hooks/useElapsedTimer";
import type {
  ConnectionStatus,
  InterviewPhaseInfo,
  RoomHeaderInfo,
} from "@/features/live-interview/types";

type RoomTopBarProps = {
  header: RoomHeaderInfo;
  phase: InterviewPhaseInfo;
  elapsedSeconds: number;
  connectionStatus: ConnectionStatus;
};

export function RoomTopBar({
  header,
  phase,
  elapsedSeconds,
  connectionStatus,
}: RoomTopBarProps) {
  const title = header.companyName
    ? `${header.companyName} · ${header.targetRole}`
    : header.targetRole;

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] px-4 py-3 sm:px-6">
      <div className="min-w-0">
        <h1 className="truncate text-sm font-semibold text-slate-100 sm:text-base">{title}</h1>
        <p className="text-xs text-slate-500">Live interview</p>
      </div>

      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <span className="badge-muted">
          Phase {phase.index}/{phase.total} · {phase.label}
        </span>
        <span
          className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 font-mono text-xs text-slate-300"
          aria-label={`Elapsed time ${formatElapsed(elapsedSeconds)}`}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-rose-400 motion-safe:animate-pulse" aria-hidden />
          {formatElapsed(elapsedSeconds)}
        </span>
        <ConnectionPill status={connectionStatus} />
      </div>
    </header>
  );
}
