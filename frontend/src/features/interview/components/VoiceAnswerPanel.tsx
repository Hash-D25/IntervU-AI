"use client";

import { FormEvent, useState } from "react";

import { GlassCard } from "@/components/GlassCard";
import { submitInterviewAnswer } from "@/features/interview/api";
import { MicrophoneRecorder } from "@/features/voice/components/MicrophoneRecorder";

interface VoiceAnswerPanelProps {
  interviewId: string;
  questionText: string;
  disabled?: boolean;
  onSubmitted: () => void;
}

export function VoiceAnswerPanel({
  interviewId,
  questionText,
  disabled = false,
  onSubmitted,
}: VoiceAnswerPanelProps) {
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!transcript.trim()) {
      setError("Add or record an answer before submitting.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await submitInterviewAnswer(interviewId, transcript.trim());
      setTranscript("");
      onSubmitted();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Could not submit answer.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <GlassCard title="Current question" accent="cyan">
      <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4">
        <p className="text-sm leading-relaxed text-slate-300">{questionText}</p>

        <MicrophoneRecorder
          interviewId={interviewId}
          disabled={disabled || isSubmitting}
          onTranscript={(value) => {
            setTranscript(value);
            setError(null);
          }}
          onError={setError}
        />

        <label className="block text-sm font-medium text-slate-400" htmlFor="answer-transcript">
          Transcript (edit before submitting)
        </label>
        <textarea
          id="answer-transcript"
          value={transcript}
          onChange={(event) => setTranscript(event.target.value)}
          rows={6}
          disabled={disabled || isSubmitting}
          className="textarea-glass"
          placeholder="Your spoken answer will appear here after transcription."
        />

        {error ? <p className="text-sm text-rose-400/90">{error}</p> : null}

        <button
          type="submit"
          disabled={disabled || isSubmitting}
          className="btn-success disabled:opacity-50"
        >
          {isSubmitting ? "Submitting…" : "Submit answer"}
        </button>
      </form>
    </GlassCard>
  );
}
