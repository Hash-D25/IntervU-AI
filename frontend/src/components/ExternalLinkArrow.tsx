import { IconExternalArrow } from "@/components/icons";

type ExternalLinkArrowProps = {
  href: string;
  label: string;
};

export function ExternalLinkArrow({ href, label }: ExternalLinkArrowProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`Open ${label} in new tab`}
      className="external-link-arrow flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-cyan-400/30 bg-cyan-400/[0.06] text-cyan-300 transition hover:border-cyan-400/55 hover:bg-cyan-400/12"
    >
      <IconExternalArrow className="h-4 w-4" />
    </a>
  );
}
