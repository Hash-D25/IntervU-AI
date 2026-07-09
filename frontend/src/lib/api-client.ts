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

type AuthHandlers = {
  getAccessToken: () => string | null;
  refreshSession: () => Promise<boolean>;
  onSessionExpired: () => void;
};

let authHandlers: AuthHandlers = {
  getAccessToken: () => null,
  refreshSession: async () => false,
  onSessionExpired: () => undefined,
};

export function configureApiAuth(handlers: AuthHandlers): void {
  authHandlers = handlers;
}

export async function parseApiErrorResponse(response: Response, fallback: string): Promise<string> {
  const body = (await response.json().catch(() => null)) as { detail?: string } | null;
  return body?.detail ?? fallback;
}

function buildHeaders(init?: RequestInit, accessToken?: string | null): Headers {
  const headers = new Headers(init?.headers);

  if (!headers.has("Content-Type") && !(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  return headers;
}

async function executeRequest(path: string, init?: RequestInit, accessToken?: string | null): Promise<Response> {
  return fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: buildHeaders(init, accessToken),
  });
}

async function request<TResponse>(
  path: string,
  init?: RequestInit,
  options?: { authenticated?: boolean },
): Promise<TResponse> {
  const authenticated = options?.authenticated ?? false;
  let accessToken = authenticated ? authHandlers.getAccessToken() : null;

  if (authenticated && !accessToken) {
    throw new ApiError(401, "Not authenticated");
  }

  let response = await executeRequest(path, init, accessToken);

  if (authenticated && response.status === 401) {
    const refreshed = await authHandlers.refreshSession();
    if (refreshed) {
      accessToken = authHandlers.getAccessToken();
      response = await executeRequest(path, init, accessToken);
    }
    if (response.status === 401) {
      authHandlers.onSessionExpired();
      throw new ApiError(401, "Session expired. Please sign in again.");
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseApiErrorResponse(response, `Request to ${path} failed`));
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return (await response.json()) as TResponse;
}

export const apiClient = {
  get: <TResponse>(path: string): Promise<TResponse> => request<TResponse>(path),

  post: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),

  authGet: <TResponse>(path: string): Promise<TResponse> =>
    request<TResponse>(path, undefined, { authenticated: true }),

  authPost: <TResponse>(path: string, body?: unknown): Promise<TResponse> =>
    request<TResponse>(
      path,
      {
        method: "POST",
        body: body === undefined ? undefined : JSON.stringify(body),
      },
      { authenticated: true },
    ),

  authFetch: (path: string, init?: RequestInit): Promise<Response> => {
    const accessToken = authHandlers.getAccessToken();
    if (!accessToken) {
      return Promise.reject(new ApiError(401, "Not authenticated"));
    }

    return (async () => {
      let response = await executeRequest(path, init, accessToken);

      if (response.status === 401) {
        const refreshed = await authHandlers.refreshSession();
        if (refreshed) {
          response = await executeRequest(path, init, authHandlers.getAccessToken());
        }
        if (response.status === 401) {
          authHandlers.onSessionExpired();
          throw new ApiError(401, "Session expired. Please sign in again.");
        }
      }

      return response;
    })();
  },
} as const;
