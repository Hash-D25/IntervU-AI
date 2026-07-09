import Link from "next/link";



import { formatDate, formatScore, formatStatus, scoreTone } from "@/features/dashboard/format";

import type { InterviewHistoryItem } from "@/features/dashboard/types";



type InterviewHistoryListProps = {

  items: InterviewHistoryItem[];

};



export function InterviewHistoryList({ items }: InterviewHistoryListProps) {

  if (items.length === 0) {

    return (

      <p className="text-sm text-slate-500">

        No interviews yet.{" "}

        <Link href="/interviews/new" className="text-cyan-400/80 hover:text-cyan-300">

          Start your first interview

        </Link>

        .

      </p>

    );

  }



  return (

    <ul className="space-y-3">

      {items.map((item) => (

        <li

          key={item.id}

          className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-4 backdrop-blur-sm transition hover:border-violet-400/30 hover:bg-white/[0.07]"

        >

          <div className="min-w-0 flex-1">

            <p className="truncate font-medium text-white">

              {item.company_name ?? "Practice interview"} - {item.target_role}

            </p>

            <p className="mt-1 text-xs text-slate-500">

              {formatDate(item.created_at)} ·{" "}

              <span className="text-slate-400">{formatStatus(item.status)}</span> ·{" "}

              {item.answered_count} answered

              {item.has_feedback ? (

                <span className="text-cyan-400/80"> · feedback ready</span>

              ) : null}

            </p>

          </div>

          <div className="flex items-center gap-3">

            {item.overall_score !== null ? (

              <span

                className={`rounded-full border px-3 py-1 text-sm font-semibold tabular-nums ${scoreTone(item.overall_score)}`}

              >

                {formatScore(item.overall_score)}

              </span>

            ) : (

              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-slate-500">

                No score

              </span>

            )}

            <Link href={`/interviews/${item.id}`} className="btn-neon px-3 py-1.5">

              Open

            </Link>

          </div>

        </li>

      ))}

    </ul>

  );

}


