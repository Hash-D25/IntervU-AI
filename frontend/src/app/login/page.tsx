"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { AuthPanel } from "@/components/AuthPanel";
import { useAuth } from "@/features/auth";

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center justify-center p-8">
        <p className="text-sm text-slate-500">Checking your session…</p>
      </main>
    );
  }

  if (isAuthenticated) {
    return null;
  }

  return (
    <AuthPanel
      title="Welcome back"
      subtitle="Sign in or create an account to start practicing interviews."
    />
  );
}
