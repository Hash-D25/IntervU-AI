"use client";

import Link from "next/link";

import { AppIcon } from "@/components/AppIcon";
import { GlassCard } from "@/components/GlassCard";
import { useAuth } from "@/features/auth";

function displayFirstName(fullName: string, email: string): string {
  const trimmed = fullName.trim();
  if (trimmed && trimmed.toLowerCase() !== "string") {
    return trimmed.split(/\s+/)[0] ?? trimmed;
  }
  return email.split("@")[0] ?? "there";
}

const FEATURES = [
  {
    title: "Questions from your resume",
    description:
      "We read your background first - so you get asked about the work you have actually done, not random trivia.",
    accent: "cyan" as const,
  },
  {
    title: "Answer out loud",
    description:
      "Talk through your responses like you would in the room. Transcripts are saved so you can tighten phrasing later.",
    accent: "violet" as const,
  },
  {
    title: "See what to fix next",
    description:
      "Each session leaves you with clear notes on what landed, what did not, and what to practice before the next one.",
    accent: "green" as const,
  },
];

export function LandingContent() {
  const { user, isAuthenticated, isLoading } = useAuth();

  return (
    <>
      <section className="text-center">
        <div className="flex flex-col items-center gap-3">
          <AppIcon size={88} priority />
          <p className="text-sm font-medium uppercase tracking-[0.25em] text-cyan-400/70">
            IntervU
          </p>
        </div>
        <h1 className="mt-6 text-4xl font-semibold leading-tight tracking-tight text-slate-100 sm:text-5xl lg:text-6xl">
          The interview room,
          <span className="mt-2 block neon-gradient-text">before the real one.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-slate-400 sm:text-lg">
          Run mock interviews at your own pace - with follow-ups that push back when your answer
          stays vague, and a dashboard that shows whether you are actually improving.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : isAuthenticated && user ? (
            <>
              <p className="w-full text-sm text-slate-500">
                Hey {displayFirstName(user.full_name, user.email)} - pick up where you left off.
              </p>
              <Link href="/interviews/new" className="btn-neon px-6 py-2.5">
                Start a mock interview
              </Link>
              <Link href="/dashboard" className="btn-glass px-6 py-2.5">
                See your progress
              </Link>
            </>
          ) : (
            <>
              <Link href="/login" className="btn-neon px-6 py-2.5">
                Try a mock interview
              </Link>
              <Link href="/login" className="btn-glass px-6 py-2.5">
                I already have an account
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {FEATURES.map((feature) => (
          <GlassCard key={feature.title} accent={feature.accent} className="text-left">
            <h2 className="text-base font-semibold text-slate-100">{feature.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500">{feature.description}</p>
          </GlassCard>
        ))}
      </section>

      {!isLoading && isAuthenticated ? (
        <section className="text-center">
          <p className="text-sm text-slate-600">
            Updated your resume? Upload the latest version from{" "}
            <Link href="/resumes" className="text-cyan-400/80 hover:text-cyan-300">
              Resumes
            </Link>{" "}
            so your next interview stays in sync.
          </p>
        </section>
      ) : !isLoading ? (
        <GlassCard accent="cyan" className="mx-auto max-w-xl text-center">
          <h2 className="text-lg font-semibold text-slate-100">Three steps, no setup drama</h2>
          <ol className="mt-4 space-y-3 text-left text-sm text-slate-400">
            <li>
              <span className="font-medium text-cyan-300/90">1.</span> Sign up and drop in your
              resume - we parse it automatically.
            </li>
            <li>
              <span className="font-medium text-cyan-300/90">2.</span> Choose a role and start
              talking; follow-ups kick in when you skim past the details.
            </li>
            <li>
              <span className="font-medium text-cyan-300/90">3.</span> Check your dashboard to spot
              patterns before your next attempt.
            </li>
          </ol>
        </GlassCard>
      ) : null}

      <p className="text-center text-sm text-slate-600">
        Something broken, or an idea we should hear?{" "}
        <Link href="/contact" className="text-cyan-400/80 hover:text-cyan-300">
          Say hello
        </Link>
      </p>
    </>
  );
}
