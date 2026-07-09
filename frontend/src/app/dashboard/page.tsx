"use client";

import { useCallback, useEffect, useState } from "react";

import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { ErrorBanner } from "@/components/ErrorBanner";
import { PageHeader } from "@/components/PageHeader";
import { getDashboardSummary } from "@/features/dashboard/api";
import { InsightList } from "@/features/dashboard/components/InsightList";
import { InterviewHistoryList } from "@/features/dashboard/components/InterviewHistoryList";
import { ProgressChart } from "@/features/dashboard/components/ProgressChart";
import { CategoryScores, DimensionScores } from "@/features/dashboard/components/ScoreBars";
import { StatCard } from "@/features/dashboard/components/StatCard";
import { DashboardCard } from "@/features/dashboard/components/DashboardCard";
import type { DashboardSummary } from "@/features/dashboard/types";
import { useAuth } from "@/features/auth";
import { getErrorMessage } from "@/lib/get-error-message";

export default function DashboardPage() {
  const { isAuthenticated } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err) {
      setError(getErrorMessage(err, "Could not load dashboard."));
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    void loadDashboard();
  }, [isAuthenticated, loadDashboard]);

  const averageScore =
    summary && summary.progress_over_time.length > 0
      ? (
          summary.progress_over_time.reduce((total, point) => total + point.overall_score, 0) /
          summary.progress_over_time.length
        ).toFixed(1)
      : "-";

  return (
    <AuthGuard
      title="Your dashboard"
      subtitle="Sign in to track interview performance."
    >
      <AppShell>
        <main className="mx-auto min-h-screen max-w-6xl space-y-8 p-6 sm:p-8">
          <PageHeader
            eyebrow="Performance hub"
            title="Dashboard"
            description="Track interview history, strengths, weaknesses, and how your scores change over time."
            actions={
              <button
                type="button"
                onClick={() => void loadDashboard()}
                disabled={isLoading}
                className="btn-neon disabled:opacity-50"
              >
                {isLoading ? "Refreshing…" : "Refresh"}
              </button>
            }
          />

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total interviews"
              value={String(summary?.total_interviews ?? 0)}
              accent="cyan"
            />
            <StatCard
              label="Completed"
              value={String(summary?.completed_interviews ?? 0)}
              accent="violet"
            />
            <StatCard
              label="Average score"
              value={averageScore}
              hint="Across scored sessions"
              accent="green"
            />
            <StatCard
              label="Categories tracked"
              value={String(summary?.category_scores.length ?? 0)}
              hint="Based on answered questions"
              accent="pink"
            />
          </section>

          <div className="grid gap-6 xl:grid-cols-2">
            <DashboardCard
              title="Progress over time"
              description="Overall score for each interview session."
              accent="cyan"
            >
              <ProgressChart points={summary?.progress_over_time ?? []} />
            </DashboardCard>

            <DashboardCard
              title="Category scores"
              description="Average score grouped by question category."
              accent="violet"
            >
              <CategoryScores items={summary?.category_scores ?? []} />
            </DashboardCard>
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <DashboardCard
              title="Strengths"
              description="Recurring themes from feedback reports."
              accent="green"
            >
              <InsightList
                title="What you do well"
                items={summary?.strengths ?? []}
                tone="strength"
                emptyMessage="Generate feedback after interviews to collect strengths."
              />
            </DashboardCard>

            <DashboardCard
              title="Weaknesses"
              description="Areas to improve across sessions."
              accent="pink"
            >
              <InsightList
                title="Where to focus next"
                items={summary?.weaknesses ?? []}
                tone="weakness"
                emptyMessage="Weaknesses appear once feedback reports are generated."
              />
            </DashboardCard>
          </div>

          <DashboardCard
            title="Evaluation dimensions"
            description="Rolling averages across all evaluated answers."
            accent="violet"
          >
            <DimensionScores averages={summary?.dimension_averages ?? {}} />
          </DashboardCard>

          <DashboardCard
            title="Interview history"
            description="Your past and in-progress mock interviews."
            accent="cyan"
            action={
              <Link
                href="/interviews/new"
                className="text-sm font-medium text-cyan-400/80 transition hover:text-cyan-300"
              >
                Start new →
              </Link>
            }
          >
            <InterviewHistoryList items={summary?.interview_history ?? []} />
          </DashboardCard>

          {error ? <ErrorBanner message={error} /> : null}
        </main>
      </AppShell>
    </AuthGuard>
  );
}
