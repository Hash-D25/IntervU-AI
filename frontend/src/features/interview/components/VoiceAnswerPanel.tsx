"use client";

import { FormEvent, useState } from "react";

import { ErrorBanner } from "@/components/ErrorBanner";
import { GlassCard } from "@/components/GlassCard";
import { submitInterviewAnswer } from "@/features/interview/api";
import type { ExecutionSnapshot } from "@/features/interview/types";
import { MicrophoneRecorder } from "@/features/voice/components/MicrophoneRecorder";
import { getErrorMessage } from "@/lib/get-error-message";

interface VoiceAnswerPanelProps {
  interviewId: string;
  questionText: string;
  disabled?: boolean;
  onSubmitted: (snapshot: ExecutionSnapshot) => void;
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
      const snapshot = await submitInterviewAnswer(interviewId, transcript.trim());
      onSubmitted(snapshot);
    } catch (err) {
      setError(getErrorMessage(err, "Could not submit answer."));
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

        {error ? <ErrorBanner message={error} /> : null}

        <button
          type="submit"
          disabled={disabled || isSubmitting}
          className="btn-success disabled:opacity-50"
        >
          {isSubmitting ? "Evaluating your answer…" : "Submit answer"}
        </button>
      </form>
    </GlassCard>
  );
}
