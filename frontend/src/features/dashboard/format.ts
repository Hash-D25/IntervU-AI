const CATEGORY_LABELS: Record<string, string> = {
  dsa: "DSA",
  project: "Projects",
  behavioral: "Behavioral",
  cs_fundamentals: "CS Fundamentals",
};

const DIMENSION_LABELS: Record<string, string> = {
  technical_accuracy: "Technical accuracy",
  completeness: "Completeness",
  communication: "Communication",
  depth: "Depth",
  examples: "Examples",
};

const STATUS_LABELS: Record<string, string> = {
  created: "Created",
  in_progress: "In progress",
  completed: "Completed",
  abandoned: "Abandoned",
};

export function formatCategory(category: string): string {
  return CATEGORY_LABELS[category] ?? category.replaceAll("_", " ");
}

export function formatDimension(dimension: string): string {
  return DIMENSION_LABELS[dimension] ?? dimension.replaceAll("_", " ");
}

export function formatStatus(status: string): string {
  return STATUS_LABELS[status] ?? status.replaceAll("_", " ");
}

export function formatScore(score: number): string {
  return score.toFixed(1);
}

export function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function scoreTone(score: number): string {
  if (score >= 8) {
    return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
  }
  if (score >= 6) {
    return "border-amber-400/30 bg-amber-400/10 text-amber-300";
  }
  return "border-rose-400/30 bg-rose-400/10 text-rose-300";
}

export function barTone(score: number): string {
  if (score >= 8) {
    return "bg-gradient-to-r from-cyan-400/90 to-emerald-400/90";
  }
  if (score >= 6) {
    return "bg-gradient-to-r from-amber-400/90 to-orange-400/90";
  }
  return "bg-gradient-to-r from-rose-400/90 to-pink-400/90";
}
