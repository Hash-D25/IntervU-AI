import type {
  CreateInterviewRequest,
  ExecutionSnapshot,
  Interview,
  InterviewSummary,
  SubmitAnswerResponse,
} from "@/features/interview/types";
import { apiClient } from "@/lib/api-client";

type JobDescriptionPdfAnalysisResponse = {
  skills: string[];
  technologies: string[];
  responsibilities: string[];
  seniority_level: string;
  analyzer_name: string;
  extracted_text: string | null;
};

export async function listInterviews(): Promise<InterviewSummary[]> {
  return apiClient.authGet<InterviewSummary[]>("/interviews/");
}

export async function getInterview(interviewId: string): Promise<Interview> {
  return apiClient.authGet<Interview>(`/interviews/${interviewId}`);
}

export async function createInterview(payload: CreateInterviewRequest): Promise<Interview> {
  return apiClient.authPost<Interview>("/interviews/", payload);
}

export async function getExecutionSnapshot(interviewId: string): Promise<ExecutionSnapshot> {
  return apiClient.authGet<ExecutionSnapshot>(`/interviews/${interviewId}/execution`);
}

export async function startInterviewExecution(interviewId: string): Promise<ExecutionSnapshot> {
  return apiClient.authPost<ExecutionSnapshot>(`/interviews/${interviewId}/execution/start`);
}

export async function submitInterviewAnswer(
  interviewId: string,
  transcript: string,
): Promise<SubmitAnswerResponse> {
  return apiClient.authPost<SubmitAnswerResponse>(`/interviews/${interviewId}/execution/answer`, {
    transcript,
  });
}

export async function parseJobDescriptionPdf(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.authFetch("/job-descriptions/analyze/pdf", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Could not parse the job description PDF.");
  }

  const body = (await response.json()) as JobDescriptionPdfAnalysisResponse;
  return body.extracted_text?.trim() ?? "";
}
