"use client";

import { usePathname } from "next/navigation";
import { type ReactNode } from "react";

import { FloatingEdgeNav } from "@/components/FloatingEdgeNav";
import { ScrollToTopButton } from "@/components/ScrollToTopButton";

type AppShellProps = {
  children: ReactNode;
  showEdgeNav?: boolean;
};

export function AppShell({ children, showEdgeNav = true }: AppShellProps) {
  const pathname = usePathname();
  const hideEdgeNav = !showEdgeNav || pathname === "/login";

  const contentPadding = hideEdgeNav ? "" : "sm:pl-28 pb-24 sm:pb-0";

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0a0e17] text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-dashboard-mesh" aria-hidden />
      <div
        className="pointer-events-none absolute -left-40 top-0 h-96 w-96 rounded-full bg-cyan-500/[0.07] blur-[120px]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-32 top-32 h-80 w-80 rounded-full bg-violet-500/[0.06] blur-[120px]"
        aria-hidden
      />
      {!hideEdgeNav ? <FloatingEdgeNav /> : null}
      <ScrollToTopButton />
      <div className={`relative transition-[padding] duration-300 ease-out ${contentPadding}`}>
        {children}
      </div>
    </div>
  );
}
