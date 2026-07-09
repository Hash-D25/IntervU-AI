import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/features/auth/types";
import { ApiError, parseApiErrorResponse } from "@/lib/api-client";
import { env } from "@/env";

async function postJson<TResponse>(path: string, body: unknown, fallback: string): Promise<TResponse> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseApiErrorResponse(response, fallback));
  }
  if (response.status === 204) {
    return undefined as TResponse;
  }
  return (await response.json()) as TResponse;
}

export async function loginUser(credentials: LoginRequest): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/login", credentials, "Login failed");
}

export async function loginWithGoogle(idToken: string): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/google", { id_token: idToken }, "Google sign-in failed");
}

export async function registerUser(payload: RegisterRequest): Promise<User> {
  return postJson<User>("/auth/register", payload, "Registration failed");
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/refresh", { refresh_token: refreshToken }, "Session expired");
}

export async function logoutUser(refreshToken: string): Promise<void> {
  await postJson<void>("/auth/logout", { refresh_token: refreshToken }, "Logout failed");
}

export async function fetchCurrentUser(accessToken: string): Promise<User> {
  const response = await fetch(`${env.apiBaseUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseApiErrorResponse(response, "Could not load profile"));
  }
  return (await response.json()) as User;
}
