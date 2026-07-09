import type { ParseProgressEvent, ParsedProfile, Resume } from "@/features/resume/types";
import { apiClient } from "@/lib/api-client";
import { throwIfNotOk } from "@/lib/api-response";
import { readSseJsonStream } from "@/lib/sse";

export async function listResumes(): Promise<Resume[]> {
  return apiClient.authGet<Resume[]>("/resumes/");
}

export async function uploadResume(file: File): Promise<Resume> {
  const form = new FormData();
  form.append("file", file);
  const response = await apiClient.authFetch("/resumes/upload", {
    method: "POST",
    body: form,
  });
  await throwIfNotOk(response, "Upload failed");
  return (await response.json()) as Resume;
}

export async function parseResumeWithProgress(
  resumeId: string,
  onProgress: (event: ParseProgressEvent) => void,
): Promise<ParsedProfile> {
  const response = await apiClient.authFetch(`/resumes/${resumeId}/parse/stream`, {
    method: "POST",
  });
  await throwIfNotOk(response, "Parse request failed");

  return readSseJsonStream<ParseProgressEvent, ParsedProfile>(response, onProgress, {
    emptyStreamMessage: "No progress stream returned",
    incompleteStreamMessage: "Parse stream ended without a result",
  });
}

export async function getParsedProfile(resumeId: string): Promise<ParsedProfile> {
  return apiClient.authGet<ParsedProfile>(`/resumes/${resumeId}/parsed`);
}
