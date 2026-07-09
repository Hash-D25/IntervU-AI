"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { GlassCard } from "@/components/GlassCard";
import { PageHeader } from "@/components/PageHeader";
import { useAuth } from "@/features/auth";
import { createInterview, parseJobDescriptionPdf } from "@/features/interview/api";
import type { InterviewType } from "@/features/interview/types";
import { listResumes } from "@/features/resume/api";
import type { Resume } from "@/features/resume/types";
import { ApiError } from "@/lib/api-client";

const INTERVIEW_TYPES: { value: InterviewType; label: string }[] = [
  { value: "technical", label: "Technical" },
  { value: "behavioral", label: "Behavioral" },
  { value: "mixed", label: "Mixed" },
];

export default function NewInterviewPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const jobDescriptionFileRef = useRef<HTMLInputElement>(null);

  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [interviewType, setInterviewType] = useState<InterviewType>("technical");
  const [jobDescription, setJobDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoadingResumes, setIsLoadingResumes] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isParsingJobDescription, setIsParsingJobDescription] = useState(false);

  const loadResumes = useCallback(async () => {
    setIsLoadingResumes(true);
    try {
      const items = await listResumes();
      setResumes(items);
      setResumeId((current) => current || items[0]?.id || "");
    } catch {
      setError("Could not load resumes.");
    } finally {
      setIsLoadingResumes(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    void loadResumes();
  }, [isAuthenticated, loadResumes]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!resumeId) {
      setError("Select a resume to continue.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const interview = await createInterview({
        resume_id: resumeId,
        company_name: companyName.trim(),
        target_role: targetRole.trim(),
        interview_type: interviewType,
        job_description: jobDescription.trim() || null,
      });
      router.push(`/interviews/${interview.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create interview.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleJobDescriptionPdfSelected(file: File) {
    setError(null);
    setIsParsingJobDescription(true);
    try {
      const extractedText = await parseJobDescriptionPdf(file);
      if (!extractedText) {
        throw new Error("No readable text was found in the uploaded PDF.");
      }
      setJobDescription(extractedText);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not parse the job description PDF.");
    } finally {
      setIsParsingJobDescription(false);
      if (jobDescriptionFileRef.current) {
        jobDescriptionFileRef.current.value = "";
      }
    }
  }

  return (
    <AuthGuard
      title="Start an interview"
      subtitle="Sign in to create a new mock interview session."
    >
      <AppShell>
        <main className="mx-auto min-h-screen max-w-5xl space-y-8 p-6 sm:p-8">
          <PageHeader
            eyebrow="New session"
            title="Start new interview"
            description="Choose a resume and target role. You'll be taken to the voice session once created."
          />

          {isLoadingResumes ? (
            <p className="text-sm text-slate-500">Loading resumes…</p>
          ) : resumes.length === 0 ? (
            <GlassCard title="Resume required" accent="violet">
              <p className="text-sm text-slate-400">
                Upload and parse a resume before starting an interview.
              </p>
              <Link href="/resumes" className="btn-neon mt-4 inline-block">
                Go to resumes
              </Link>
            </GlassCard>
          ) : (
            <GlassCard title="Interview details" accent="cyan">
              <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
                <label className="block text-sm font-medium text-slate-400" htmlFor="resume-id">
                  Resume
                </label>
                <select
                  id="resume-id"
                  value={resumeId}
                  onChange={(e) => setResumeId(e.target.value)}
                  className="input-glass"
                  required
                >
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.original_filename}
                    </option>
                  ))}
                </select>

                <label className="block text-sm font-medium text-slate-400" htmlFor="company-name">
                  Company
                </label>
                <input
                  id="company-name"
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="e.g. EPAM"
                  className="input-glass"
                  required
                  maxLength={255}
                />

                <label className="block text-sm font-medium text-slate-400" htmlFor="target-role">
                  Target role
                </label>
                <input
                  id="target-role"
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="e.g. SDE intern"
                  className="input-glass"
                  required
                  maxLength={255}
                />

                <label className="block text-sm font-medium text-slate-400" htmlFor="interview-type">
                  Interview type
                </label>
                <select
                  id="interview-type"
                  value={interviewType}
                  onChange={(e) => setInterviewType(e.target.value as InterviewType)}
                  className="input-glass"
                >
                  {INTERVIEW_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>

                <label className="block text-sm font-medium text-slate-400" htmlFor="job-description">
                  Job description (optional)
                </label>
                <div className="flex flex-wrap items-center gap-3">
                  <label
                    htmlFor="job-description-pdf"
                    className={`btn-glass inline-flex cursor-pointer items-center px-3 py-2 ${
                      isParsingJobDescription ? "pointer-events-none opacity-60" : ""
                    }`}
                  >
                    {isParsingJobDescription ? "Parsing PDF…" : "Add PDF"}
                  </label>
                  <input
                    ref={jobDescriptionFileRef}
                    id="job-description-pdf"
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    disabled={isParsingJobDescription}
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) {
                        void handleJobDescriptionPdfSelected(file);
                      }
                    }}
                  />
                  <span className="text-xs text-slate-500">
                    Upload a JD PDF to extract its text into the box below.
                  </span>
                </div>
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={4}
                  placeholder="Paste the job description for more tailored questions."
                  className="textarea-glass"
                  maxLength={50000}
                />

                <div className="flex flex-wrap gap-3 pt-2">
                  <button type="submit" disabled={isSubmitting} className="btn-neon disabled:opacity-50">
                    {isSubmitting ? "Creating…" : "Create & open session"}
                  </button>
                  <Link href="/dashboard" className="btn-glass">
                    Cancel
                  </Link>
                </div>
              </form>
            </GlassCard>
          )}

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
