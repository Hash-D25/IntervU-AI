"use client";

import { transcribeAudio } from "@/features/voice/api";
import { useMicrophone } from "@/features/voice/hooks/useMicrophone";

interface MicrophoneRecorderProps {
  token: string;
  interviewId?: string;
  disabled?: boolean;
  onTranscript: (transcript: string) => void;
  onError?: (message: string) => void;
}

export function MicrophoneRecorder({
  token,
  interviewId,
  disabled = false,
  onTranscript,
  onError,
}: MicrophoneRecorderProps) {
  const { state, error, startRecording, stopRecording, reset } = useMicrophone();

  async function handleToggleRecording() {
    if (state === "recording") {
      const audio = await stopRecording();
      if (!audio) {
        onError?.("No audio captured. Try speaking closer to the microphone.");
        return;
      }
      try {
        const result = await transcribeAudio(token, audio, "answer.webm", interviewId);
        onTranscript(result.transcript);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Transcription failed.";
        onError?.(message);
      }
      return;
    }

    reset();
    await startRecording();
  }

  const isBusy = disabled || state === "processing";
  const label =
    state === "recording"
      ? "Stop & transcribe"
      : state === "processing"
        ? "Transcribing..."
        : "Record answer";

  return (
    <div className="space-y-2">
      <button
        type="button"
        disabled={isBusy}
        onClick={() => void handleToggleRecording()}
        className={`rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-60 ${
          state === "recording" ? "bg-red-600 hover:bg-red-700" : "bg-indigo-600 hover:bg-indigo-700"
        }`}
      >
        {label}
      </button>
      {(error || state === "recording") && (
        <p className="text-sm text-gray-600">
          {error ?? "Recording... click stop when you finish your answer."}
        </p>
      )}
    </div>
  );
}
