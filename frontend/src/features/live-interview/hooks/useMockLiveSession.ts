"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { MOCK_STREAMING_LINES, MOCK_TRANSCRIPT } from "@/features/live-interview/mocks";
import type {
  CaptionEntry,
  ConnectionStatus,
  TurnState,
} from "@/features/live-interview/types";

interface UseMockLiveSessionOptions {
  /** Session becomes active once the candidate joins the room. */
  active: boolean;
  /** Whether the captions/transcript stream is enabled. */
  captionsEnabled: boolean;
}

interface MockLiveSession {
  connectionStatus: ConnectionStatus;
  turnState: TurnState;
  isInterviewerSpeaking: boolean;
  captions: CaptionEntry[];
}

// Placeholder session behavior for the UI shell. Iterations 3-6 replace this
// with a real WebSocket-driven state hook (`useLiveChannel`).
export function useMockLiveSession({
  active,
  captionsEnabled,
}: UseMockLiveSessionOptions): MockLiveSession {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("connecting");
  const [turnState, setTurnState] = useState<TurnState>("idle");
  const [streamedCaptions, setStreamedCaptions] = useState<CaptionEntry[]>([]);
  const lineIndexRef = useRef(0);

  // Fake a brief connection handshake after joining.
  useEffect(() => {
    if (!active) {
      setConnectionStatus("connecting");
      setTurnState("idle");
      return;
    }
    const timer = window.setTimeout(() => {
      setConnectionStatus("connected");
      setTurnState("interviewer_speaking");
    }, 1200);
    return () => window.clearTimeout(timer);
  }, [active]);

  // Cycle the turn state so the speaking indicator has something to show.
  useEffect(() => {
    if (!active || connectionStatus !== "connected") {
      return;
    }
    const cycle: TurnState[] = ["interviewer_speaking", "listening", "processing"];
    let index = 0;
    const interval = window.setInterval(() => {
      index = (index + 1) % cycle.length;
      setTurnState(cycle[index] ?? "listening");
    }, 4000);
    return () => window.clearInterval(interval);
  }, [active, connectionStatus]);

  // Stream scripted caption lines while captions are on.
  useEffect(() => {
    if (!active || !captionsEnabled || connectionStatus !== "connected") {
      return;
    }
    const interval = window.setInterval(() => {
      const line = MOCK_STREAMING_LINES[lineIndexRef.current % MOCK_STREAMING_LINES.length];
      if (!line) {
        return;
      }
      lineIndexRef.current += 1;
      setStreamedCaptions((prev) => [
        ...prev,
        {
          id: `stream-${lineIndexRef.current}`,
          speaker: lineIndexRef.current % 2 === 0 ? "interviewer" : "candidate",
          text: line,
          isFinal: true,
        },
      ]);
    }, 3500);
    return () => window.clearInterval(interval);
  }, [active, captionsEnabled, connectionStatus]);

  const captions = useMemo(
    () => (captionsEnabled ? [...MOCK_TRANSCRIPT, ...streamedCaptions] : []),
    [captionsEnabled, streamedCaptions],
  );

  return {
    connectionStatus,
    turnState,
    isInterviewerSpeaking: turnState === "interviewer_speaking",
    captions,
  };
}
