// Mocked/scripted content for the UI shell. Everything here is a placeholder
// until the realtime WebSocket + STT/TTS layers land (iterations 3-6).

import type { CaptionEntry, InterviewPhaseInfo } from "@/features/live-interview/types";

export const MOCK_PHASE: InterviewPhaseInfo = {
  label: "Behavioral",
  index: 2,
  total: 4,
};

/** Seed transcript shown when captions are enabled. */
export const MOCK_TRANSCRIPT: CaptionEntry[] = [
  {
    id: "seed-1",
    speaker: "interviewer",
    text: "Welcome! Let's start with a quick introduction — tell me about yourself.",
    isFinal: true,
  },
  {
    id: "seed-2",
    speaker: "candidate",
    text: "Sure. I'm a frontend engineer with about four years of experience building product UIs.",
    isFinal: true,
  },
  {
    id: "seed-3",
    speaker: "interviewer",
    text: "Great. Can you walk me through a project you're particularly proud of?",
    isFinal: true,
  },
];

/** Scripted lines streamed in over time to simulate live captions. */
export const MOCK_STREAMING_LINES: string[] = [
  "Absolutely. Last year I led a redesign of our checkout flow...",
  "We cut the drop-off rate by roughly thirty percent...",
  "The biggest challenge was coordinating across three teams...",
  "I set up a shared component library to keep things consistent...",
];
