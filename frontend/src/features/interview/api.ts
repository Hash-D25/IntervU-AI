import { env } from "@/env";
import type { ExecutionSnapshot, SubmitAnswerResponse } from "@/features/interview/types";
import { ApiError } from "@/lib/api-client";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function getExecutionSnapshot(
  token: string,
  interviewId: string,
): Promise<ExecutionSnapshot> {
  const response = await fetch(`${env.apiBaseUrl}/interviews/${interviewId}/execution`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Failed to load interview execution state");
  }
  return (await response.json()) as ExecutionSnapshot;
}

export async function startInterviewExecution(
  token: string,
  interviewId: string,
): Promise<ExecutionSnapshot> {
  const response = await fetch(`${env.apiBaseUrl}/interviews/${interviewId}/execution/start`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Failed to start interview");
  }
  return (await response.json()) as ExecutionSnapshot;
}

export async function submitInterviewAnswer(
  token: string,
  interviewId: string,
  transcript: string,
): Promise<SubmitAnswerResponse> {
  const response = await fetch(`${env.apiBaseUrl}/interviews/${interviewId}/execution/answer`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ transcript }),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Failed to submit answer");
  }
  return (await response.json()) as SubmitAnswerResponse;
}
