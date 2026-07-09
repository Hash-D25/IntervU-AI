"use client";

import { FormEvent, useState } from "react";

import { AppIcon } from "@/components/AppIcon";
import { AppShell } from "@/components/AppShell";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";
import { useAuth } from "@/features/auth";
import { env } from "@/env";
import { getErrorMessage } from "@/lib/get-error-message";

type AuthMode = "login" | "register";

type AuthPanelProps = {
  eyebrow?: string;
  title: string;
  subtitle: string;
};

export function AuthPanel({ eyebrow = "IntervU", title, subtitle }: AuthPanelProps) {
  const { login, loginWithGoogle, register } = useAuth();
  const [mode, setMode] = useState<AuthMode>("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (mode === "login") {
        await login({ email, password });
      } else {
        await register({ email, password, full_name: fullName.trim() });
      }
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          mode === "login" ? "Login failed. Check your email and password." : "Registration failed. Try a different email.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleGoogleSignIn(idToken: string) {
    setError(null);
    setIsSubmitting(true);

    try {
      await loginWithGoogle(idToken);
    } catch (err) {
      setError(getErrorMessage(err, "Google sign-in failed."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AppShell showEdgeNav={false}>
      <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-8 p-8">
        <div className="text-center">
          <AppIcon size={80} priority className="mx-auto" />
          <p className="mt-4 text-sm font-medium uppercase tracking-[0.15em] text-cyan-400/70">
            {eyebrow}
          </p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-100">{title}</h1>
          <p className="mt-3 text-slate-500">{subtitle}</p>
        </div>

        <div className="flex rounded-lg border border-white/10 bg-white/[0.03] p-1">
          <button
            type="button"
            onClick={() => {
              setMode("login");
              setError(null);
            }}
            className={
              mode === "login"
                ? "flex-1 rounded-md border border-cyan-400/35 bg-cyan-400/10 py-2 text-sm font-medium text-cyan-300"
                : "flex-1 rounded-md py-2 text-sm font-medium text-slate-400"
            }
          >
            Sign in
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("register");
              setError(null);
            }}
            className={
              mode === "register"
                ? "flex-1 rounded-md border border-cyan-400/35 bg-cyan-400/10 py-2 text-sm font-medium text-cyan-300"
                : "flex-1 rounded-md py-2 text-sm font-medium text-slate-400"
            }
          >
            Create account
          </button>
        </div>

        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="glass-panel-strong flex flex-col gap-4 p-8"
        >
          {mode === "login" && env.googleClientId ? (
            <>
              <GoogleSignInButton
                disabled={isSubmitting}
                onSuccess={handleGoogleSignIn}
                onError={() => setError("Google sign-in was cancelled or failed.")}
              />
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <span className="h-px flex-1 bg-white/10" />
                or continue with email
                <span className="h-px flex-1 bg-white/10" />
              </div>
            </>
          ) : null}

          {mode === "register" ? (
            <input
              type="text"
              placeholder="Full name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input-glass"
              required
              minLength={1}
              maxLength={255}
            />
          ) : null}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-glass"
            required
            autoComplete="email"
          />
          <input
            type="password"
            placeholder={mode === "register" ? "Password (min 8 characters)" : "Password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-glass"
            required
            minLength={mode === "register" ? 8 : 1}
            maxLength={128}
            autoComplete={mode === "register" ? "new-password" : "current-password"}
          />

          <button type="submit" disabled={isSubmitting} className="btn-neon w-full py-2.5 disabled:opacity-50">
            {isSubmitting
              ? mode === "login"
                ? "Signing in…"
                : "Creating account…"
              : mode === "login"
                ? "Sign in"
                : "Create account"}
          </button>

          {error ? <p className="text-sm text-rose-400/90">{error}</p> : null}
        </form>
      </main>
    </AppShell>
  );
}
