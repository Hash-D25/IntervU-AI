import { env } from "@/env";
import type { AuthTokens, ParseProgressEvent, ParsedProfile, Resume } from "@/features/resume/types";
import { ApiError } from "@/lib/api-client";

const TOKEN_KEY = "interviewerai_access_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return sessionStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function login(email: string, password: string): Promise<AuthTokens> {
  const response = await fetch(`${env.apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Login failed");
  }
  return (await response.json()) as AuthTokens;
}

export async function listResumes(token: string): Promise<Resume[]> {
  const response = await fetch(`${env.apiBaseUrl}/resumes/`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Failed to list resumes");
  }
  return (await response.json()) as Resume[];
}

export async function uploadResume(token: string, file: File): Promise<Resume> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${env.apiBaseUrl}/resumes/upload`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Upload failed");
  }
  return (await response.json()) as Resume;
}

export async function parseResumeWithProgress(
  token: string,
  resumeId: string,
  onProgress: (event: ParseProgressEvent) => void,
): Promise<ParsedProfile> {
  const response = await fetch(`${env.apiBaseUrl}/resumes/${resumeId}/parse/stream`, {
    method: "POST",
    headers: authHeaders(token),
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

export async function getParsedProfile(
  token: string,
  resumeId: string,
): Promise<ParsedProfile> {
  const response = await fetch(`${env.apiBaseUrl}/resumes/${resumeId}/parsed`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? "No parsed profile found");
  }
  return (await response.json()) as ParsedProfile;
}
