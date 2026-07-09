import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "IntervU",
  description: "AI-powered mock interview platform",
  icons: {
    icon: "/app-icon-transparent.png",
    apple: "/app-icon-transparent.png",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen scroll-smooth bg-[#0a0e17] text-slate-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
