import type { DashboardSummary, FeedbackResult } from "@/features/dashboard/types";
import { apiClient } from "@/lib/api-client";
import { authGetNullable } from "@/lib/api-response";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiClient.authGet<DashboardSummary>("/dashboard/");
}

export async function getInterviewFeedback(interviewId: string): Promise<FeedbackResult | null> {
  const response = await apiClient.authFetch(`/interviews/${interviewId}/feedback`);
  return authGetNullable<FeedbackResult>(response, "Failed to load feedback");
}

export async function generateInterviewFeedback(interviewId: string): Promise<FeedbackResult> {
  return apiClient.authPost<FeedbackResult>(`/interviews/${interviewId}/feedback/generate`);
}
