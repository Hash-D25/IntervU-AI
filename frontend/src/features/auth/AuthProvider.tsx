"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  refreshTokens,
  registerUser,
} from "@/features/auth/api";
import {
  clearStoredTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
  storeTokens,
} from "@/features/auth/storage";
import type { LoginRequest, RegisterRequest, User } from "@/features/auth/types";
import { ApiError } from "@/lib/api-client";
import { configureApiAuth } from "@/lib/api-client";

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshPromiseRef = useRef<Promise<boolean> | null>(null);

  const clearSession = useCallback(() => {
    clearStoredTokens();
    setUser(null);
  }, []);

  const applyTokens = useCallback(async (accessToken: string, refreshToken: string) => {
    storeTokens(accessToken, refreshToken);
    const profile = await fetchCurrentUser(accessToken);
    setUser(profile);
  }, []);

  const refreshSession = useCallback(async (): Promise<boolean> => {
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }

    const runRefresh = async (): Promise<boolean> => {
      const refreshToken = getStoredRefreshToken();
      if (!refreshToken) {
        clearSession();
        return false;
      }

      try {
        const tokens = await refreshTokens(refreshToken);
        storeTokens(tokens.access_token, tokens.refresh_token);
        const profile = await fetchCurrentUser(tokens.access_token);
        setUser(profile);
        return true;
      } catch {
        clearSession();
        return false;
      }
    };

    refreshPromiseRef.current = runRefresh().finally(() => {
      refreshPromiseRef.current = null;
    });

    return refreshPromiseRef.current;
  }, [clearSession]);

  const bootstrap = useCallback(async () => {
    const accessToken = getStoredAccessToken();
    if (!accessToken) {
      setIsLoading(false);
      return;
    }

    try {
      const profile = await fetchCurrentUser(accessToken);
      setUser(profile);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        await refreshSession();
      } else {
        clearSession();
      }
    } finally {
      setIsLoading(false);
    }
  }, [clearSession, refreshSession]);

  useEffect(() => {
    configureApiAuth({
      getAccessToken: getStoredAccessToken,
      refreshSession,
      onSessionExpired: clearSession,
    });
    void bootstrap();
  }, [bootstrap, clearSession, refreshSession]);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      const tokens = await loginUser(credentials);
      await applyTokens(tokens.access_token, tokens.refresh_token);
    },
    [applyTokens],
  );

  const register = useCallback(
    async (payload: RegisterRequest) => {
      await registerUser(payload);
      await login({ email: payload.email, password: payload.password });
    },
    [login],
  );

  const logout = useCallback(async () => {
    const refreshToken = getStoredRefreshToken();
    clearSession();
    if (refreshToken) {
      try {
        await logoutUser(refreshToken);
      } catch {
        // Local session is already cleared; server revocation is best-effort.
      }
    }
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
