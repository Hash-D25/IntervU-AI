export interface TranscriptionChunk {
  text: string;
  is_final: boolean;
  start_ms?: number | null;
  end_ms?: number | null;
}

export interface TranscribeResponse {
  transcript: string;
  language?: string | null;
  duration_ms?: number | null;
  transcriber_name: string;
  chunks: TranscriptionChunk[];
  refined?: boolean;
}

export interface TranscriptionStreamEvent {
  stage: "started" | "chunk" | "done" | "error";
  message: string;
  chunk?: TranscriptionChunk;
  result?: TranscribeResponse;
}

export type MicrophoneState = "idle" | "recording" | "processing" | "error";
