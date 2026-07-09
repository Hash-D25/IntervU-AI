"use client";

import { transcribeAudio } from "@/features/voice/api";
import { useMicrophone } from "@/features/voice/hooks/useMicrophone";

const WAVE_BARS = [0, 1, 2, 3, 4, 5, 6];

interface MicrophoneRecorderProps {
  interviewId?: string;
  disabled?: boolean;
  onTranscript: (transcript: string) => void;
  onError?: (message: string) => void;
}

function RecordingAnimation() {
  return (
    <div
      className="flex items-center gap-4 rounded-xl border border-rose-400/25 bg-rose-400/[0.06] px-4 py-3"
      role="status"
      aria-live="polite"
    >
      <div className="recording-ring flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-rose-400/50 bg-rose-400/15">
        <span className="h-2.5 w-2.5 rounded-full bg-rose-400" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-rose-200">Recording your answer</p>
        <p className="text-xs text-rose-200/60">Speak clearly, then click stop when finished.</p>
        <div className="mt-3 flex h-8 items-end gap-1">
          {WAVE_BARS.map((bar) => (
            <span
              key={bar}
              className="waveform-bar w-1 rounded-full bg-rose-400/80"
              style={{ height: `${10 + (bar % 3) * 8}px`, animationDelay: `${bar * 0.12}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function TranscribingAnimation() {
  return (
    <div
      className="transcribe-shimmer flex items-center gap-4 rounded-xl border border-cyan-400/25 px-4 py-3"
      role="status"
      aria-live="polite"
    >
      <div className="relative flex h-10 w-10 shrink-0 items-center justify-center">
        <div className="transcribe-spinner absolute inset-0 rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />
        <span className="text-xs font-semibold text-cyan-300">AI</span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-cyan-200">Transcribing audio</p>
        <p className="text-xs text-cyan-200/60">Converting your recording into editable text…</p>
        <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-cyan-400/10">
          <div className="transcribe-shimmer h-full w-1/2 rounded-full bg-cyan-400/50" />
        </div>
      </div>
    </div>
  );
}

export function MicrophoneRecorder({
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
        reset();
        onError?.("No audio captured. Try speaking closer to the microphone.");
        return;
      }
      try {
        const result = await transcribeAudio(audio, "answer.webm", interviewId);
        onTranscript(result.transcript);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Transcription failed.";
        onError?.(message);
      } finally {
        reset();
      }
      return;
    }

    reset();
    await startRecording();
  }

  const isRecording = state === "recording";
  const isTranscribing = state === "processing";
  const isBusy = disabled || isTranscribing;

  const label = isRecording ? "Stop & transcribe" : isTranscribing ? "Transcribing…" : "Record answer";

  return (
    <div className="space-y-3">
      {isRecording ? <RecordingAnimation /> : null}
      {isTranscribing ? <TranscribingAnimation /> : null}

      <button
        type="button"
        disabled={isBusy}
        onClick={() => void handleToggleRecording()}
        className={
          isRecording
            ? "btn-danger disabled:opacity-50"
            : isTranscribing
              ? "btn-glass cursor-wait opacity-70"
              : "btn-neon disabled:opacity-50"
        }
      >
        {label}
      </button>

      {error ? <p className="text-sm text-rose-400/90">{error}</p> : null}
    </div>
  );
}
