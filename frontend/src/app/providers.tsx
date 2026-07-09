"use client";

import type { ReactNode } from "react";

import { AuthProvider } from "@/features/auth";
import { GoogleAuthProvider } from "@/components/GoogleSignInButton";
import { SnakeScrollbar } from "@/components/SnakeScrollbar";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <GoogleAuthProvider>
      <AuthProvider>
        {children}
        <SnakeScrollbar />
      </AuthProvider>
    </GoogleAuthProvider>
  );
}
