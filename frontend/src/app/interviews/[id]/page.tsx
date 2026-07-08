"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { VoiceAnswerPanel } from "@/features/interview/components/VoiceAnswerPanel";
import {
  getExecutionSnapshot,
  startInterviewExecution,
} from "@/features/interview/api";
import type { ExecutionSnapshot } from "@/features/interview/types";
import { getStoredToken, login, storeToken } from "@/features/resume/api";

export default function InterviewVoicePage() {
  const params = useParams<{ id: string }>();
  const interviewId = params.id;

  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [snapshot, setSnapshot] = useState<ExecutionSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  const refreshSnapshot = useCallback(async (accessToken: string) => {
    const next = await getExecutionSnapshot(accessToken, interviewId);
    setSnapshot(next);
  }, [interviewId]);

  useEffect(() => {
    if (!token) {
      return;
    }
    void refreshSnapshot(token).catch(() => {
      setError("Could not load interview state.");
    });
  }, [token, refreshSnapshot]);

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const tokens = await login(email, password);
      storeToken(tokens.access_token);
      setToken(tokens.access_token);
      await refreshSnapshot(tokens.access_token);
    } catch {
      setError("Login failed.");
    }
  }

  async function handleStart() {
    if (!token) {
      return;
    }
    setIsStarting(true);
    setError(null);
    try {
      const next = await startInterviewExecution(token, interviewId);
      setSnapshot(next);
    } catch {
      setError("Could not start interview.");
    } finally {
      setIsStarting(false);
    }
  }

  if (!token) {
    return (
      <main className="mx-auto max-w-lg p-6">
        <h1 className="text-2xl font-bold">Interview voice session</h1>
        <form onSubmit={(event) => void handleLogin(event)} className="mt-6 space-y-3">
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            className="w-full rounded-md border px-3 py-2"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            className="w-full rounded-md border px-3 py-2"
            required
          />
          <button type="submit" className="rounded-md bg-indigo-600 px-4 py-2 text-white">
            Sign in
          </button>
        </form>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </main>
    );
  }

  const currentQuestion = snapshot?.current_question;
  const isCompleted = snapshot?.status === "completed";

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Interview voice session</h1>
        <p className="text-sm text-gray-600">
          Record your answer, review the transcript, then submit to the interview engine.
        </p>
      </header>

      {snapshot?.status === "not_started" && (
        <button
          type="button"
          onClick={() => void handleStart()}
          disabled={isStarting}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isStarting ? "Starting..." : "Start interview"}
        </button>
      )}

      {currentQuestion && !isCompleted && token && (
        <VoiceAnswerPanel
          token={token}
          interviewId={interviewId}
          questionText={currentQuestion.text}
          onSubmitted={() => {
            void refreshSnapshot(token).catch(() => {
              setError("Answer submitted, but refresh failed.");
            });
          }}
        />
      )}

      {isCompleted && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          Interview completed. You can generate feedback from the API or dashboard.
        </p>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}
    </main>
  );
}
