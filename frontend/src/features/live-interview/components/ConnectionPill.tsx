import type { ConnectionStatus } from "@/features/live-interview/types";

type ConnectionPillProps = {
  status: ConnectionStatus;
};

const config: Record<ConnectionStatus, { label: string; dot: string; text: string; border: string }> = {
  connecting: {
    label: "Connecting…",
    dot: "bg-amber-400",
    text: "text-amber-300",
    border: "border-amber-400/30 bg-amber-400/10",
  },
  connected: {
    label: "Connected",
    dot: "bg-emerald-400",
    text: "text-emerald-300",
    border: "border-emerald-400/30 bg-emerald-400/10",
  },
  reconnecting: {
    label: "Reconnecting…",
    dot: "bg-amber-400",
    text: "text-amber-300",
    border: "border-amber-400/30 bg-amber-400/10",
  },
  disconnected: {
    label: "Disconnected",
    dot: "bg-rose-400",
    text: "text-rose-300",
    border: "border-rose-400/30 bg-rose-400/10",
  },
};

export function ConnectionPill({ status }: ConnectionPillProps) {
  const { label, dot, text, border } = config[status];
  const pulse = status === "connecting" || status === "reconnecting";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${border} ${text}`}
      role="status"
      aria-live="polite"
    >
      <span className={`h-2 w-2 rounded-full ${dot} ${pulse ? "motion-safe:animate-pulse" : ""}`} aria-hidden />
      {label}
    </span>
  );
}
