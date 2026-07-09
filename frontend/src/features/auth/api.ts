import { env } from "@/env";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/features/auth/types";
import { ApiError } from "@/lib/api-client";

async function parseErrorMessage(response: Response, fallback: string): Promise<string> {
  const body = (await response.json().catch(() => null)) as { detail?: string } | null;
  return body?.detail ?? fallback;
}

export async function loginUser(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${env.apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response, "Login failed"));
  }
  return (await response.json()) as TokenResponse;
}

export async function registerUser(payload: RegisterRequest): Promise<User> {
  const response = await fetch(`${env.apiBaseUrl}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response, "Registration failed"));
  }
  return (await response.json()) as User;
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${env.apiBaseUrl}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response, "Session expired"));
  }
  return (await response.json()) as TokenResponse;
}

export async function logoutUser(refreshToken: string): Promise<void> {
  const response = await fetch(`${env.apiBaseUrl}/auth/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok && response.status !== 204) {
    throw new ApiError(response.status, await parseErrorMessage(response, "Logout failed"));
  }
}

export async function fetchCurrentUser(accessToken: string): Promise<User> {
  const response = await fetch(`${env.apiBaseUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response, "Could not load profile"));
  }
  return (await response.json()) as User;
}
