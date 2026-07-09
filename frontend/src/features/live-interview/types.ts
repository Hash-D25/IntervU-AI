// Types for the Meet-style live interview room (UI shell).
// Realtime transport wiring lands in later iterations; for now these describe
// both the real local-media state and the mocked session state.

export type CameraState = "idle" | "requesting" | "active" | "denied" | "error";

export type ConnectionStatus =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected";

// Whose turn it is in the conversation. Driven by a mock in this iteration.
export type TurnState =
  | "idle"
  | "interviewer_speaking"
  | "listening"
  | "processing";

export type CaptionSpeaker = "interviewer" | "candidate";

export interface CaptionEntry {
  id: string;
  speaker: CaptionSpeaker;
  text: string;
  /** Interim captions render greyed; final captions render solid. */
  isFinal: boolean;
}

export interface MediaDeviceOption {
  deviceId: string;
  label: string;
}

export interface InterviewPhaseInfo {
  /** Human-readable phase label, e.g. "Behavioral". */
  label: string;
  /** 1-based position of the current phase. */
  index: number;
  total: number;
}

export interface RoomHeaderInfo {
  companyName: string | null;
  targetRole: string;
}
