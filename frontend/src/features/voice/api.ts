import { env } from "@/env";
import type { TranscribeResponse, TranscriptionStreamEvent } from "@/features/voice/types";
import { ApiError } from "@/lib/api-client";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function transcribeAudio(
  token: string,
  audio: Blob,
  filename = "answer.webm",
  interviewId?: string,
): Promise<TranscribeResponse> {
  const form = new FormData();
  form.append("file", audio, filename);
  const query = interviewId ? `?interview_id=${encodeURIComponent(interviewId)}` : "";
  const response = await fetch(`${env.apiBaseUrl}/voice/transcribe${query}`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Transcription failed");
  }
  return (await response.json()) as TranscribeResponse;
}

export async function transcribeAudioWithProgress(
  token: string,
  audio: Blob,
  onEvent: (event: TranscriptionStreamEvent) => void,
  filename = "answer.webm",
): Promise<TranscribeResponse> {
  const form = new FormData();
  form.append("file", audio, filename);
  const response = await fetch(`${env.apiBaseUrl}/voice/transcribe/stream`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "Transcription stream failed");
  }
  if (!response.body) {
    throw new Error("No transcription stream returned");
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
      const event = JSON.parse(line.slice(6)) as TranscriptionStreamEvent;
      onEvent(event);
      if (event.stage === "error") {
        throw new ApiError(422, event.message);
      }
      if (event.stage === "done" && event.result) {
        return event.result;
      }
    }
  }

  throw new Error("Transcription stream ended without a result");
}
