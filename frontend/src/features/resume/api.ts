import type { ParseProgressEvent, ParsedProfile, Resume } from "@/features/resume/types";
import { ApiError, apiClient } from "@/lib/api-client";

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
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Upload failed");
  }
  return (await response.json()) as Resume;
}

export async function parseResumeWithProgress(
  resumeId: string,
  onProgress: (event: ParseProgressEvent) => void,
): Promise<ParsedProfile> {
  const response = await apiClient.authFetch(`/resumes/${resumeId}/parse/stream`, {
    method: "POST",
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Parse request failed");
  }

  if (!response.body) {
    throw new Error("No progress stream returned");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";

    for (const chunk of chunks) {
      const line = chunk.trim();
      if (!line.startsWith("data: ")) {
        continue;
      }

      const event = JSON.parse(line.slice(6)) as ParseProgressEvent;
      onProgress(event);

      if (event.stage === "error") {
        throw new ApiError(422, event.message);
      }
      if (event.stage === "done" && event.result) {
        return event.result;
      }
    }
  }

  throw new Error("Parse stream ended without a result");
}

export async function getParsedProfile(resumeId: string): Promise<ParsedProfile> {
  return apiClient.authGet<ParsedProfile>(`/resumes/${resumeId}/parsed`);
}
