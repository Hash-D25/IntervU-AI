"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { ParseProgressBar } from "@/components/ParseProgressBar";
import { ParsedProfileReview } from "@/components/ParsedProfileReview";
import {
  getParsedProfile,
  getStoredToken,
  listResumes,
  login,
  parseResumeWithProgress,
  storeToken,
  uploadResume,
} from "@/features/resume/api";
import type { ParsedProfile, ParseProgressEvent, Resume } from "@/features/resume/types";

export default function ResumesPage() {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [parsingId, setParsingId] = useState<string | null>(null);
  const [progress, setProgress] = useState<ParseProgressEvent | null>(null);
  const [parsed, setParsed] = useState<ParsedProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const refreshResumes = useCallback(async (accessToken: string) => {
    const items = await listResumes(accessToken);
    setResumes(items);
  }, []);

  useEffect(() => {
    if (token) {
      void refreshResumes(token).catch(() => {
        setError("Could not load resumes.");
      });
    }
  }, [token, refreshResumes]);

  async function handleLogin(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const tokens = await login(email, password);
      storeToken(tokens.access_token);
      setToken(tokens.access_token);
      await refreshResumes(tokens.access_token);
    } catch {
      setError("Login failed. Check your email and password.");
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const form = event.currentTarget;
    const fileInput = form.elements.namedItem("resume") as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (!file) {
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      await uploadResume(token, file);
      await refreshResumes(token);
      form.reset();
    } catch {
      setError("Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleViewParsed(resumeId: string) {
    if (!token) {
      return;
    }
    setError(null);
    try {
      const result = await getParsedProfile(token, resumeId);
      setParsed(result);
      setProgress({ stage: "done", percent: 100, message: "Parse complete" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "No parsed profile yet.");
      setParsed(null);
    }
  }

  async function handleParse(resumeId: string) {
    if (!token) {
      return;
    }

    setParsingId(resumeId);
    setParsed(null);
    setError(null);
    setProgress({ stage: "starting", percent: 0, message: "Starting parse…" });

    try {
      const result = await parseResumeWithProgress(token, resumeId, (event) => {
        setProgress(event);
      });
      setParsed(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed.");
      setProgress(null);
    } finally {
      setParsingId(null);
    }
  }

  if (!token) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-6 p-8">
        <div>
          <h1 className="text-3xl font-bold">InterviewerAI</h1>
          <p className="mt-2 text-slate-600">Sign in to upload and parse your resume.</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-4 rounded-xl border bg-white p-6 shadow-sm">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border px-3 py-2"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border px-3 py-2"
            required
          />
          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
          >
            Sign in
          </button>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </form>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-3xl space-y-8 p-8">
      <header>
        <h1 className="text-3xl font-bold">Resume parsing</h1>
        <p className="mt-2 text-slate-600">Upload a PDF and parse it with live progress.</p>
      </header>

      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Upload</h2>
        <form onSubmit={handleUpload} className="mt-4 flex flex-wrap items-center gap-3">
          <input type="file" name="resume" accept="application/pdf" required />
          <button
            type="submit"
            disabled={isUploading}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {isUploading ? "Uploading…" : "Upload PDF"}
          </button>
        </form>
      </section>

      {(progress || parsingId) && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">Parsing progress</h2>
          <ParseProgressBar
            percent={progress?.percent ?? 0}
            message={
              progress?.percent === 100 && !parsingId
                ? "Parse complete"
                : (progress?.message ?? "Working…")
            }
            isActive={parsingId !== null}
          />
        </section>
      )}

      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your resumes</h2>
          <button
            type="button"
            onClick={() => refreshResumes(token)}
            className="text-sm text-indigo-600 hover:underline"
          >
            Refresh
          </button>
        </div>
        {resumes.length === 0 ? (
          <p className="text-sm text-slate-500">No resumes yet. Upload a PDF above.</p>
        ) : (
          <ul className="divide-y">
            {resumes.map((resume) => (
              <li key={resume.id} className="flex items-center justify-between gap-4 py-3">
                <div>
                  <p className="font-medium">{resume.original_filename}</p>
                  <p className="text-xs text-slate-500">{resume.id}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => handleViewParsed(resume.id)}
                    disabled={parsingId !== null}
                    className="rounded-lg border px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    View parsed
                  </button>
                  <button
                    type="button"
                    onClick={() => handleParse(resume.id)}
                    disabled={parsingId !== null}
                    className="rounded-lg border border-indigo-600 px-3 py-1.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
                  >
                    {parsingId === resume.id ? "Parsing…" : "Re-parse"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {parsed ? <ParsedProfileReview profile={parsed} /> : null}

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </main>
  );
}
