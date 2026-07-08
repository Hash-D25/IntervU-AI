"use client";

import { FormEvent, useState } from "react";

import { submitInterviewAnswer } from "@/features/interview/api";
import { MicrophoneRecorder } from "@/features/voice/components/MicrophoneRecorder";

interface VoiceAnswerPanelProps {
  token: string;
  interviewId: string;
  questionText: string;
  disabled?: boolean;
  onSubmitted: () => void;
}

export function VoiceAnswerPanel({
  token,
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
      await submitInterviewAnswer(token, interviewId, transcript.trim());
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
    <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4 rounded-lg border p-4">
      <div>
        <h2 className="text-lg font-semibold">Current question</h2>
        <p className="mt-2 text-sm text-gray-700">{questionText}</p>
      </div>

      <MicrophoneRecorder
        token={token}
        interviewId={interviewId}
        disabled={disabled || isSubmitting}
        onTranscript={(value) => {
          setTranscript(value);
          setError(null);
        }}
        onError={setError}
      />

      <label className="block text-sm font-medium text-gray-700" htmlFor="answer-transcript">
        Transcript (edit before submitting)
      </label>
      <textarea
        id="answer-transcript"
        value={transcript}
        onChange={(event) => setTranscript(event.target.value)}
        rows={6}
        disabled={disabled || isSubmitting}
        className="w-full rounded-md border px-3 py-2 text-sm"
        placeholder="Your spoken answer will appear here after transcription."
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={disabled || isSubmitting}
        className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
      >
        {isSubmitting ? "Submitting..." : "Submit answer"}
      </button>
    </form>
  );
}
