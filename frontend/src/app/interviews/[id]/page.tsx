"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { GlassCard } from "@/components/GlassCard";
import { PageHeader } from "@/components/PageHeader";
import { useAuth } from "@/features/auth";
import {
  generateInterviewFeedback,
  getInterviewFeedback,
} from "@/features/dashboard/api";
import { formatDate, formatStatus } from "@/features/dashboard/format";
import { InterviewFeedbackPanel } from "@/features/interview/components/InterviewFeedbackPanel";
import { VoiceAnswerPanel } from "@/features/interview/components/VoiceAnswerPanel";
import {
  getExecutionSnapshot,
  getInterview,
  startInterviewExecution,
} from "@/features/interview/api";
import type { ExecutionSnapshot, Interview } from "@/features/interview/types";
import type { FeedbackResult } from "@/features/dashboard/types";
import { ApiError } from "@/lib/api-client";

export default function InterviewPage() {
  const params = useParams<{ id: string }>();
  const interviewId = params.id;
  const { isAuthenticated } = useAuth();

  const [interview, setInterview] = useState<Interview | null>(null);
  const [snapshot, setSnapshot] = useState<ExecutionSnapshot | null>(null);
  const [feedback, setFeedback] = useState<FeedbackResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isGeneratingFeedback, setIsGeneratingFeedback] = useState(false);

  const loadInterview = useCallback(async () => {
    const [interviewData, executionData] = await Promise.all([
      getInterview(interviewId),
      getExecutionSnapshot(interviewId),
    ]);
    setInterview(interviewData);
    setSnapshot(executionData);

    if (interviewData.status === "completed") {
      const feedbackData = await getInterviewFeedback(interviewId);
      setFeedback(feedbackData);
    } else {
      setFeedback(null);
    }
  }, [interviewId]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    setIsLoading(true);
    setError(null);
    void loadInterview()
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Could not load interview.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [isAuthenticated, loadInterview]);

  async function handleStart() {
    setIsStarting(true);
    setError(null);
    try {
      const next = await startInterviewExecution(interviewId);
      setSnapshot(next);
      if (interview) {
        setInterview({ ...interview, status: "in_progress" });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start interview.");
    } finally {
      setIsStarting(false);
    }
  }

  async function handleGenerateFeedback() {
    setIsGeneratingFeedback(true);
    setError(null);
    try {
      const result = await generateInterviewFeedback(interviewId);
      setFeedback(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not generate feedback.");
    } finally {
      setIsGeneratingFeedback(false);
    }
  }

  const currentQuestion = snapshot?.current_question;
  const isCompleted = snapshot?.status === "completed" || interview?.status === "completed";
  const isNotStarted = snapshot?.status === "not_started";
  const title = interview
    ? `${interview.company_name ?? "Practice interview"} - ${interview.target_role}`
    : "Interview session";

  return (
    <AuthGuard
      title="Interview session"
      subtitle="Sign in to record and submit voice answers."
    >
      <AppShell>
        <main className="mx-auto max-w-5xl space-y-6 p-6 sm:p-8">
          <PageHeader
            eyebrow="Interview"
            title={title}
            description={
              interview
                ? `${formatDate(interview.created_at)} · ${formatStatus(interview.status)}`
                : "Loading interview details…"
            }
          />

          {isLoading ? (
            <p className="text-sm text-slate-500">Loading session…</p>
          ) : null}

          {!isLoading && interview ? (
            <GlassCard title="Session overview" accent="violet">
              <div className="flex flex-wrap items-center gap-3 text-sm text-slate-400">
                <span className="tag-glass capitalize">{interview.interview_type ?? "mixed"}</span>
                <span>{formatStatus(interview.status)}</span>
                {snapshot?.phase ? <span>Phase: {snapshot.phase.replaceAll("_", " ")}</span> : null}
              </div>
            </GlassCard>
          ) : null}

          {!isLoading && isNotStarted ? (
            <GlassCard title="Ready to begin" accent="cyan">
              <p className="text-sm text-slate-400">
                Start the session when you are ready. Questions will be tailored to your resume and
                target role.
              </p>
              <button
                type="button"
                onClick={() => void handleStart()}
                disabled={isStarting}
                className="btn-neon mt-4 disabled:opacity-50"
              >
                {isStarting ? "Starting…" : "Start interview"}
              </button>
            </GlassCard>
          ) : null}

          {!isLoading && snapshot && !isNotStarted && !isCompleted ? (
            <GlassCard title="Session status" accent="violet">
              <p className="text-sm text-slate-400">
                Phase: <span className="text-slate-200">{snapshot.phase ?? "-"}</span> · Status:{" "}
                <span className="text-slate-200">{snapshot.status}</span>
              </p>
            </GlassCard>
          ) : null}

          {!isLoading && currentQuestion && !isCompleted ? (
            <VoiceAnswerPanel
              interviewId={interviewId}
              questionText={currentQuestion.text}
              onSubmitted={() => {
                void loadInterview().catch(() => {
                  setError("Answer submitted, but refresh failed.");
                });
              }}
            />
          ) : null}

          {!isLoading && snapshot && snapshot.previous_questions.length > 0 ? (
            <GlassCard title="Previous answers" accent="green">
              <ul className="space-y-3">
                {snapshot.previous_questions.map((question) => (
                  <li
                    key={`${question.position}-${question.text}`}
                    className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  >
                    <p className="text-sm font-medium text-slate-200">{question.text}</p>
                    {question.answer_transcript ? (
                      <p className="mt-2 text-sm text-slate-500">{question.answer_transcript}</p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </GlassCard>
          ) : null}

          {!isLoading && isCompleted ? (
            <>
              {feedback ? (
                <InterviewFeedbackPanel feedback={feedback} />
              ) : (
                <GlassCard title="Feedback" accent="pink">
                  <p className="text-sm text-slate-400">
                    Generate a feedback report for this completed interview.
                  </p>
                  <button
                    type="button"
                    onClick={() => void handleGenerateFeedback()}
                    disabled={isGeneratingFeedback}
                    className="btn-neon mt-4 disabled:opacity-50"
                  >
                    {isGeneratingFeedback ? "Generating…" : "Generate feedback"}
                  </button>
                </GlassCard>
              )}

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="btn-glass">
                  Back to dashboard
                </Link>
                <Link href="/interviews/new" className="btn-neon">
                  Start new interview
                </Link>
              </div>
            </>
          ) : null}

          {error ? (
            <p className="rounded-lg border border-rose-400/20 bg-rose-400/5 px-4 py-3 text-sm text-rose-300/90">
              {error}
            </p>
          ) : null}
        </main>
      </AppShell>
    </AuthGuard>
  );
}
