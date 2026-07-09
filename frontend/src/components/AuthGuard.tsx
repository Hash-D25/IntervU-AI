"use client";

import type { ReactNode } from "react";

import { AppShell } from "@/components/AppShell";
import { AuthPanel } from "@/components/AuthPanel";
import { useAuth } from "@/features/auth";

type AuthGuardProps = {
  title: string;
  subtitle: string;
  eyebrow?: string;
  children: ReactNode;
};

export function AuthGuard({ title, subtitle, eyebrow, children }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <AppShell>
        <main className="mx-auto flex min-h-screen max-w-md items-center justify-center p-8">
          <p className="text-sm text-slate-500">Checking your session…</p>
        </main>
      </AppShell>
    );
  }

  if (!isAuthenticated) {
    return <AuthPanel eyebrow={eyebrow} title={title} subtitle={subtitle} />;
  }

  return <>{children}</>;
}
