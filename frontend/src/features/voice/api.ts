import type { TranscribeResponse } from "@/features/voice/types";
import { apiClient } from "@/lib/api-client";
import { throwIfNotOk } from "@/lib/api-response";

export async function transcribeAudio(
  audio: Blob,
  filename = "answer.webm",
  interviewId?: string,
): Promise<TranscribeResponse> {
  const form = new FormData();
  form.append("file", audio, filename);
  const query = interviewId ? `?interview_id=${encodeURIComponent(interviewId)}` : "";
  const response = await apiClient.authFetch(`/voice/transcribe${query}`, {
    method: "POST",
    body: form,
  });
  await throwIfNotOk(response, "Transcription failed");
  return (await response.json()) as TranscribeResponse;
}
