"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGuard } from "@/components/AuthGuard";
import { useAuth } from "@/features/auth";
import { LiveInterviewRoom } from "@/features/live-interview";
import type { RoomHeaderInfo } from "@/features/live-interview";
import { getInterview } from "@/features/interview/api";

const FALLBACK_HEADER: RoomHeaderInfo = {
  companyName: null,
  targetRole: "Practice interview",
};

export default function LiveInterviewPage() {
  const params = useParams<{ id: string }>();
  const interviewId = params.id;
  const { isAuthenticated } = useAuth();

  const [header, setHeader] = useState<RoomHeaderInfo>(FALLBACK_HEADER);

  const loadHeader = useCallback(async () => {
    const interview = await getInterview(interviewId);
    setHeader({
      companyName: interview.company_name,
      targetRole: interview.target_role,
    });
  }, [interviewId]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    // Header is non-critical for the room shell; fall back silently on error.
    void loadHeader().catch(() => setHeader(FALLBACK_HEADER));
  }, [isAuthenticated, loadHeader]);

  return (
    <AuthGuard
      title="Live interview"
      subtitle="Sign in to join the live interview room."
    >
      <div className="relative min-h-screen bg-[#0a0e17] text-slate-100">
        <div className="pointer-events-none absolute inset-0 bg-dashboard-mesh" aria-hidden />
        <div className="relative">
          <LiveInterviewRoom interviewId={interviewId} header={header} />
        </div>
      </div>
    </AuthGuard>
  );
}
