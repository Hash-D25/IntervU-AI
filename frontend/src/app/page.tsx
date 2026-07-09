import { AppShell } from "@/components/AppShell";
import { LandingContent } from "@/components/LandingContent";

export default function HomePage() {
  return (
    <AppShell>
      <main className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center gap-14 px-6 py-16 sm:gap-16 sm:px-8 sm:py-20">
        <LandingContent />
      </main>
    </AppShell>
  );
}
