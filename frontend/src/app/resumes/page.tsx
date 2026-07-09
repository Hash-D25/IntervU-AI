"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { GlassCard } from "@/components/GlassCard";
import { PageHeader } from "@/components/PageHeader";
import { ParseProgressBar } from "@/components/ParseProgressBar";
import { ParsedProfileReview } from "@/components/ParsedProfileReview";
import {
  getParsedProfile,
  listResumes,
  parseResumeWithProgress,
  uploadResume,
} from "@/features/resume/api";
import type { ParsedProfile, ParseProgressEvent, Resume } from "@/features/resume/types";
import { useAuth } from "@/features/auth";
import { ApiError } from "@/lib/api-client";

export default function ResumesPage() {
  const { isAuthenticated } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [resumes, setResumes] = useState<Resume[]>([]);
  const [parsingId, setParsingId] = useState<string | null>(null);
  const [progress, setProgress] = useState<ParseProgressEvent | null>(null);
  const [parsed, setParsed] = useState<ParsedProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const refreshResumes = useCallback(async () => {
    const items = await listResumes();
    setResumes(items);
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    void refreshResumes().catch(() => {
      setError("Could not load resumes.");
    });
  }, [isAuthenticated, refreshResumes]);

  const runParse = useCallback(async (resumeId: string) => {
    setParsingId(resumeId);
    setParsed(null);
    setError(null);
    setProgress({ stage: "starting", percent: 0, message: "Starting parse…" });

    try {
      const result = await parseResumeWithProgress(resumeId, (event) => {
        setProgress(event);
      });
      setParsed(result);
      setProgress({ stage: "done", percent: 100, message: "Parse complete" });
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed.");
      setProgress(null);
      throw err;
    } finally {
      setParsingId(null);
    }
  }, []);

  async function handleFileSelected(file: File) {
    setError(null);
    setParsed(null);
    setIsUploading(true);
    setProgress({ stage: "uploading", percent: 5, message: "Uploading PDF…" });

    try {
      const resume = await uploadResume(file);
      await refreshResumes();
      setProgress({ stage: "uploaded", percent: 15, message: "Upload complete. Parsing…" });
      await runParse(resume.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload or parse failed.");
      setProgress(null);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleViewParsed(resumeId: string) {
    setError(null);
    try {
      const result = await getParsedProfile(resumeId);
      setParsed(result);
      setProgress({ stage: "done", percent: 100, message: "Parse complete" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "No parsed profile yet.");
      setParsed(null);
    }
  }

  const isBusy = isUploading || parsingId !== null;
  const showProgress = isBusy || progress !== null;

  return (
    <AuthGuard title="Resume parsing" subtitle="Sign in to upload and parse your resume.">
      <AppShell>
        <main className="mx-auto min-h-screen max-w-5xl space-y-8 p-6 sm:p-8">
          <PageHeader
            eyebrow="Resume"
            title="Parsing"
            description="Upload a PDF - it will be parsed and saved automatically."
          />

          <GlassCard title="Upload" accent="cyan">
            <p className="mb-4 text-sm text-slate-500">
              Select a PDF resume. Upload and parsing start immediately with live progress below.
            </p>
            <label className="flex flex-wrap items-center gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                disabled={isBusy}
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void handleFileSelected(file);
                  }
                }}
                className="max-w-full text-sm text-slate-400 file:mr-3 file:rounded-lg file:border file:border-white/10 file:bg-white/[0.04] file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-300 hover:file:bg-white/[0.08] disabled:opacity-50"
              />
              {isBusy ? (
                <span className="text-sm text-cyan-300/80">
                  {isUploading ? "Uploading…" : "Parsing…"}
                </span>
              ) : null}
            </label>
          </GlassCard>

          {showProgress ? (
            <GlassCard title="Parsing progress" accent="violet">
              <ParseProgressBar
                percent={progress?.percent ?? 0}
                message={progress?.message ?? "Working…"}
                isActive={isBusy}
              />
            </GlassCard>
          ) : null}

          <GlassCard
            title="Your resumes"
            accent="green"
            action={
              <button
                type="button"
                onClick={() => void refreshResumes()}
                className="text-sm font-medium text-cyan-400/80 hover:text-cyan-300"
              >
                Refresh
              </button>
            }
          >
            {resumes.length === 0 ? (
              <p className="text-sm text-slate-500">No resumes yet. Upload a PDF above.</p>
            ) : (
              <ul className="space-y-3">
                {resumes.map((resume) => (
                  <li
                    key={resume.id}
                    className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-slate-200">{resume.original_filename}</p>
                      <p className="text-xs text-slate-600">{resume.id}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => void handleViewParsed(resume.id)}
                        disabled={isBusy}
                        className="btn-glass px-3 py-1.5 disabled:opacity-50"
                      >
                        View parsed
                      </button>
                      <button
                        type="button"
                        onClick={() => void runParse(resume.id)}
                        disabled={isBusy}
                        className="btn-neon px-3 py-1.5 disabled:opacity-50"
                      >
                        {parsingId === resume.id ? "Parsing…" : "Re-parse"}
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </GlassCard>

          {parsed ? <ParsedProfileReview profile={parsed} /> : null}

          {error ? (
            <p className="rounded-lg border border-rose-400/20 bg-rose-400/5 px-4 py-3 text-sm text-rose-300/90">
              {error}
            </p>
          ) : null}
        </main>
      </AppShell>
    </AuthGuard>
  );
}
