const ACCESS_TOKEN_KEY = "interviewerai_access_token";
const REFRESH_TOKEN_KEY = "interviewerai_refresh_token";

function canUseStorage(): boolean {
  return typeof window !== "undefined";
}

export function getStoredAccessToken(): string | null {
  if (!canUseStorage()) {
    return null;
  }
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  if (!canUseStorage()) {
    return null;
  }
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function storeTokens(accessToken: string, refreshToken: string): void {
  if (!canUseStorage()) {
    return;
  }
  sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearStoredTokens(): void {
  if (!canUseStorage()) {
    return;
  }
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
}
