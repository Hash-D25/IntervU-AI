import type { ReactNode } from "react";

import { GlassCard } from "@/components/GlassCard";
import type { ParsedProfile } from "@/features/resume/types";

type ParsedProfileReviewProps = {
  profile: ParsedProfile;
};

function countFilled(profile: ParsedProfile): number {
  let count = 0;
  if (profile.skills.length > 0) count += 1;
  if (profile.technologies.length > 0) count += 1;
  if (profile.projects.length > 0) count += 1;
  if (profile.experience.length > 0) count += 1;
  if (profile.education.length > 0) count += 1;
  if (profile.achievements.length > 0) count += 1;
  return count;
}

export function ParsedProfileReview({ profile }: ParsedProfileReviewProps) {
  const filled = countFilled(profile);
  const isComplete = profile.parse_status === "completed";

  return (
    <GlassCard
      title="Parsed profile review"
      description="Compare each section below against your original PDF."
      accent="green"
      action={
        <div className="flex flex-wrap gap-2">
          <span className={isComplete ? "badge-success" : "badge-warning"}>
            {profile.parse_status}
          </span>
          <span className="badge-muted">parser: {profile.parser_name}</span>
        </div>
      }
    >
      <div className="space-y-6">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-sm font-medium text-slate-300">Verification checklist</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-500">
            <CheckItem ok={profile.skills.length > 0} label="Skills extracted" />
            <CheckItem ok={profile.technologies.length > 0} label="Technologies extracted" />
            <CheckItem ok={profile.experience.length > 0} label="Work experience found" />
            <CheckItem ok={profile.projects.length > 0} label="Projects found" />
            <CheckItem ok={profile.education.length > 0} label="Education found" />
            <CheckItem ok={profile.achievements.length > 0} label="Achievements found" />
          </ul>
          <p className="mt-3 text-xs text-slate-600">
            {filled}/6 sections populated. Open your PDF side-by-side and confirm names, dates, and
            companies match.
          </p>
        </div>

        <ReviewBlock
          title="Skills"
          empty="No skills extracted - check the Skills section in your PDF."
          hasContent={profile.skills.length > 0}
        >
          <TagList items={profile.skills} />
        </ReviewBlock>

        <ReviewBlock
          title="Technologies"
          empty="No technologies extracted - may appear under Skills or Tech Stack."
          hasContent={profile.technologies.length > 0}
        >
          <TagList items={profile.technologies} />
        </ReviewBlock>

        <ReviewBlock
          title="Experience"
          empty="No experience entries - verify PDF text is selectable."
          hasContent={profile.experience.length > 0}
        >
          <ul className="space-y-3">
            {profile.experience.map((entry, index) => (
              <li
                key={`${entry.title}-${index}`}
                className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-sm"
              >
                <p className="font-medium text-slate-200">{entry.title}</p>
                {entry.company ? <p className="text-slate-400">{entry.company}</p> : null}
                {entry.duration ? <p className="text-xs text-slate-600">{entry.duration}</p> : null}
                {entry.description ? (
                  <p className="mt-1 text-slate-500">{entry.description}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </ReviewBlock>

        <ReviewBlock title="Projects" empty="No projects found." hasContent={profile.projects.length > 0}>
          <ul className="space-y-3">
            {profile.projects.map((project, index) => (
              <li
                key={`${project.name}-${index}`}
                className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-sm"
              >
                <p className="font-medium text-slate-200">{project.name}</p>
                {project.description ? (
                  <p className="mt-1 text-slate-500">{project.description}</p>
                ) : null}
                {project.technologies && project.technologies.length > 0 ? (
                  <p className="mt-1 text-xs text-slate-600">{project.technologies.join(", ")}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </ReviewBlock>

        <ReviewBlock
          title="Achievements"
          empty="No achievements found - check Awards, Honors, or Certifications in your PDF."
          hasContent={profile.achievements.length > 0}
        >
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-400">
            {profile.achievements.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ReviewBlock>

        <ReviewBlock
          title="Education"
          empty="No education entries found."
          hasContent={profile.education.length > 0}
        >
          <ul className="space-y-3">
            {profile.education.map((entry, index) => (
              <li
                key={`${entry.institution}-${index}`}
                className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-sm"
              >
                <p className="font-medium text-slate-200">{entry.institution}</p>
                {entry.degree ? <p className="text-slate-400">{entry.degree}</p> : null}
                {entry.year ? <p className="text-xs text-slate-600">{entry.year}</p> : null}
              </li>
            ))}
          </ul>
        </ReviewBlock>

        {profile.parse_error ? (
          <p className="text-sm text-rose-400/90">Parse error: {profile.parse_error}</p>
        ) : null}
      </div>
    </GlassCard>
  );
}

function CheckItem({ ok, label }: { ok: boolean; label: string }) {
  return (
    <li className="flex items-center gap-2">
      <span className={ok ? "text-emerald-400/90" : "text-amber-400/90"}>{ok ? "✓" : "○"}</span>
      <span>{label}</span>
    </li>
  );
}

function ReviewBlock({
  title,
  empty,
  children,
  hasContent,
}: {
  title: string;
  empty: string;
  children: ReactNode;
  hasContent: boolean;
}) {
  return (
    <div>
      <h3 className="text-sm font-medium uppercase tracking-wide text-slate-500">{title}</h3>
      <div className="mt-2">
        {hasContent ? children : <p className="text-sm text-slate-600">{empty}</p>}
      </div>
    </div>
  );
}

function TagList({ items }: { items: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className="tag-glass">
          {item}
        </span>
      ))}
    </div>
  );
}
