"use client";

import type { ReactNode } from "react";

type ControlButtonVariant = "neutral" | "active" | "off" | "danger";

type ControlButtonProps = {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  variant?: ControlButtonVariant;
  /** For toggle buttons: reflects the pressed state to assistive tech. */
  pressed?: boolean;
  disabled?: boolean;
};

const variantClasses: Record<ControlButtonVariant, string> = {
  neutral:
    "border-white/10 bg-white/[0.06] text-slate-200 hover:border-white/20 hover:bg-white/[0.1]",
  active:
    "border-cyan-400/40 bg-cyan-400/[0.12] text-cyan-200 hover:border-cyan-400/60 hover:bg-cyan-400/[0.18]",
  off: "border-rose-400/40 bg-rose-400/[0.12] text-rose-200 hover:border-rose-400/60 hover:bg-rose-400/[0.18]",
  danger:
    "border-rose-500/50 bg-rose-500/20 text-rose-100 hover:border-rose-400 hover:bg-rose-500/30",
};

export function ControlButton({
  icon,
  label,
  onClick,
  variant = "neutral",
  pressed,
  disabled = false,
}: ControlButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      aria-pressed={pressed}
      title={label}
      className={`flex h-12 w-12 items-center justify-center rounded-full border backdrop-blur-md transition focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/60 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0e17] disabled:cursor-not-allowed disabled:opacity-40 ${variantClasses[variant]}`}
    >
      {icon}
    </button>
  );
}
