import type { FeedbackResult } from "@/features/dashboard/types";
import { formatScore } from "@/features/dashboard/format";
import { GlassCard } from "@/components/GlassCard";

type InterviewFeedbackPanelProps = {
  feedback: FeedbackResult;
};

export function InterviewFeedbackPanel({ feedback }: InterviewFeedbackPanelProps) {
  return (
    <GlassCard title="Interview feedback" accent="green">
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm leading-relaxed text-slate-300">{feedback.summary}</p>
          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-sm font-semibold text-emerald-300">
            {formatScore(feedback.overall_score)} / 10
          </span>
        </div>

        {feedback.strengths.length > 0 ? (
          <div>
            <h3 className="text-sm font-medium text-slate-400">Strengths</h3>
            <ul className="mt-2 space-y-1 text-sm text-slate-300">
              {feedback.strengths.map((item) => (
                <li key={item}>▸ {item}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {feedback.weaknesses.length > 0 ? (
          <div>
            <h3 className="text-sm font-medium text-slate-400">Areas to improve</h3>
            <ul className="mt-2 space-y-1 text-sm text-slate-300">
              {feedback.weaknesses.map((item) => (
                <li key={item}>▸ {item}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {feedback.recommendations.length > 0 ? (
          <div>
            <h3 className="text-sm font-medium text-slate-400">Recommendations</h3>
            <ul className="mt-2 space-y-1 text-sm text-slate-300">
              {feedback.recommendations.map((item) => (
                <li key={item}>▸ {item}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </GlassCard>
  );
}
