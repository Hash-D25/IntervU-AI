import type { DashboardSummary, FeedbackResult } from "@/features/dashboard/types";
import { ApiError, apiClient } from "@/lib/api-client";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiClient.authGet<DashboardSummary>("/dashboard/");
}

export async function getInterviewFeedback(interviewId: string): Promise<FeedbackResult | null> {
  const response = await apiClient.authFetch(`/interviews/${interviewId}/feedback`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Failed to load feedback");
  }
  return (await response.json()) as FeedbackResult;
}

export async function generateInterviewFeedback(interviewId: string): Promise<FeedbackResult> {
  return apiClient.authPost<FeedbackResult>(`/interviews/${interviewId}/feedback/generate`);
}
