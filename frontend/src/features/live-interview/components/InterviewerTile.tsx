"use client";

import type { TurnState } from "@/features/live-interview/types";

type InterviewerTileProps = {
  speaking: boolean;
  turnState: TurnState;
  name?: string;
};

const turnLabel: Record<TurnState, string> = {
  idle: "Waiting…",
  interviewer_speaking: "Speaking…",
  listening: "Listening…",
  processing: "Thinking…",
};

function SpeakingWaveform({ speaking }: { speaking: boolean }) {
  const bars = [0, 1, 2, 3, 4];
  return (
    <div className="flex items-end gap-1" aria-hidden>
      {bars.map((bar) => (
        <span
          key={bar}
          className={`w-1.5 rounded-full bg-cyan-300 ${speaking ? "motion-safe:waveform-bar" : ""}`}
          style={{
            height: speaking ? "1.5rem" : "0.4rem",
            animationDelay: `${bar * 0.12}s`,
          }}
        />
      ))}
    </div>
  );
}

export function InterviewerTile({
  speaking,
  turnState,
  name = "AI Interviewer",
}: InterviewerTileProps) {
  return (
    <div className="relative flex aspect-video w-full flex-col items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-violet-950/40 shadow-[0_4px_24px_rgba(0,0,0,0.35)]">
      <div className="relative flex flex-col items-center gap-4">
        <div className="relative">
          {speaking ? (
            <span
              className="absolute inset-0 rounded-full bg-cyan-400/30 motion-safe:animate-ping"
              aria-hidden
            />
          ) : null}
          <div
            className={`relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400/25 to-violet-500/25 text-3xl font-semibold text-cyan-100 ring-1 transition ${
              speaking ? "ring-cyan-400/70" : "ring-white/10"
            }`}
          >
            AI
          </div>
        </div>
        <SpeakingWaveform speaking={speaking} />
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 bg-gradient-to-t from-black/60 to-transparent px-3 py-2">
        <span className="rounded-md bg-black/40 px-2 py-0.5 text-xs font-medium text-slate-100 backdrop-blur-sm">
          {name}
        </span>
        <span className="rounded-md bg-black/40 px-2 py-0.5 text-xs font-medium text-cyan-200/90 backdrop-blur-sm">
          {turnLabel[turnState]}
        </span>
      </div>
    </div>
  );
}
