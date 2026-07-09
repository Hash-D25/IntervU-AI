"use client";

import { useEffect, useRef } from "react";

import { IconChevronRight } from "@/features/live-interview/icons";
import type { CaptionEntry } from "@/features/live-interview/types";

type CaptionsPanelProps = {
  open: boolean;
  onClose: () => void;
  captionsEnabled: boolean;
  captions: CaptionEntry[];
};

const speakerLabel: Record<CaptionEntry["speaker"], string> = {
  interviewer: "AI Interviewer",
  candidate: "You",
};

const speakerColor: Record<CaptionEntry["speaker"], string> = {
  interviewer: "text-cyan-300",
  candidate: "text-violet-300",
};

export function CaptionsPanel({ open, onClose, captionsEnabled, captions }: CaptionsPanelProps) {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Autoscroll to the newest caption.
  useEffect(() => {
    const node = scrollRef.current;
    if (node) {
      node.scrollTop = node.scrollHeight;
    }
  }, [captions]);

  if (!open) {
    return null;
  }

  return (
    <aside
      aria-label="Live captions and transcript"
      className="glass-panel-strong flex h-full w-full flex-col overflow-hidden rounded-2xl lg:w-80"
    >
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-100">Live captions</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Collapse captions panel"
          title="Collapse"
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-white/[0.06] hover:text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/60"
        >
          <IconChevronRight />
        </button>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
        aria-live="polite"
        aria-atomic="false"
      >
        {!captionsEnabled ? (
          <p className="text-sm text-slate-500">
            Captions are off. Turn on live captions from the control bar to see the transcript.
          </p>
        ) : captions.length === 0 ? (
          <p className="text-sm text-slate-500">Waiting for the conversation to start…</p>
        ) : (
          captions.map((entry) => (
            <div key={entry.id} className="text-sm leading-relaxed">
              <span className={`mr-2 text-xs font-semibold uppercase tracking-wide ${speakerColor[entry.speaker]}`}>
                {speakerLabel[entry.speaker]}
              </span>
              <span className={entry.isFinal ? "text-slate-200" : "text-slate-500 italic"}>
                {entry.text}
              </span>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
