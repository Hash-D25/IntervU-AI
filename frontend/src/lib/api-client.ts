import { env } from "@/env";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<TResponse>(path: string, init?: RequestInit): Promise<TResponse> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `Request to ${path} failed with ${response.status}`);
  }

  return (await response.json()) as TResponse;
}

// Minimal, typed HTTP surface. Feature-specific calls build on top of this.
export const apiClient = {
  get: <TResponse>(path: string): Promise<TResponse> => request<TResponse>(path),
  post: <TResponse>(path: string, body: unknown): Promise<TResponse> =>
    request<TResponse>(path, { method: "POST", body: JSON.stringify(body) }),
} as const;
