import { AppShell } from "@/components/AppShell";
import { ExternalLinkArrow } from "@/components/ExternalLinkArrow";
import { GlassCard } from "@/components/GlassCard";
import { PageHeader } from "@/components/PageHeader";

const CONTACT_LINKS = [
  {
    label: "LinkedIn",
    value: "harshita-bb9168286",
    href: "https://www.linkedin.com/in/harshita-bb9168286",
    description: "Connect for collaborations, feedback, or professional inquiries.",
    accent: "cyan" as const,
    external: true,
  },
  {
    label: "Email",
    value: "harshita2386@gmail.com",
    href: "mailto:harshita2386@gmail.com",
    description: "Reach out directly - we typically respond within 1–2 business days.",
    accent: "violet" as const,
    external: false,
  },
  {
    label: "Portfolio",
    value: "my-portfolio-beta-orcin-90.vercel.app",
    href: "https://my-portfolio-beta-orcin-90.vercel.app/",
    description: "Explore projects, experience, and more about the builder behind IntervU.",
    accent: "green" as const,
    external: true,
  },
];

export default function ContactPage() {
  return (
    <AppShell>
      <main className="mx-auto min-h-screen max-w-5xl space-y-8 p-6 sm:p-8">
        <PageHeader
          eyebrow="IntervU"
          title="Contact us"
          description="Questions, feedback, or partnership ideas? Reach out through any channel below."
        />

        <div className="space-y-4">
          {CONTACT_LINKS.map((item) => (
            <GlassCard key={item.label} title={item.label} accent={item.accent}>
              <p className="text-sm text-slate-500">{item.description}</p>
              <div className="mt-4 flex items-center justify-between gap-3">
                <a
                  href={item.href}
                  target={item.external ? "_blank" : undefined}
                  rel={item.external ? "noopener noreferrer" : undefined}
                  className="min-w-0 truncate text-sm font-medium text-cyan-300/90 transition hover:text-cyan-200"
                >
                  {item.value}
                </a>
                {item.external ? <ExternalLinkArrow href={item.href} label={item.label} /> : null}
              </div>
            </GlassCard>
          ))}
        </div>

        <p className="text-center text-sm text-slate-600">
          Built with care for interview practice. Thank you for using IntervU.
        </p>
      </main>
    </AppShell>
  );
}
