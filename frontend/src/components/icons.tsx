import Image from "next/image";

type IconProps = {
  className?: string;
};

export function IconAppMark({ className = "h-6 w-6" }: IconProps) {
  return (
    <span className={`relative inline-block shrink-0 ${className}`} aria-hidden>
      <Image
        src="/app-icon-transparent.png"
        alt=""
        fill
        className="object-contain"
        sizes="32px"
      />
    </span>
  );
}

export function IconHome({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 10.5 12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5H15v-5.5H9V20.5H5.5A1.5 1.5 0 0 1 4 19v-8.5Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconDashboard({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect
        x="4"
        y="4.75"
        width="6.5"
        height="3.25"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.75"
      />
      <path
        d="M12.25 7.25V6.1a1.35 1.35 0 0 1 1.35-1.35h4.35a1.65 1.65 0 0 1 1.65 1.65v4.75a1.65 1.65 0 0 1-1.65 1.65h-4.35a1.35 1.35 0 0 1-1.35-1.35V8.75"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M4.5 14.75V13.6a1.35 1.35 0 0 1 1.35-1.35h4.35a1.65 1.65 0 0 1 1.65 1.65v4.75a1.65 1.65 0 0 1-1.65 1.65H5.85a1.35 1.35 0 0 1-1.35-1.35V16.25"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect
        x="13.5"
        y="16.5"
        width="6.5"
        height="3.25"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.75"
      />
    </svg>
  );
}

export function IconResume({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M8 3.5h8l3.5 3.5V19.5A1.5 1.5 0 0 1 18 21H6a1.5 1.5 0 0 1-1.5-1.5v-15A1.5 1.5 0 0 1 6 3.5Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path d="M16 3.5V8H20" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
      <path d="M8 12h8M8 16h5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

export function IconInterview({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      {/* Left person */}
      <circle cx="5.25" cy="6.75" r="2" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M5.25 8.75c-1.85.45-2.85 2.35-2.55 4.65.2 1.55 1.15 2.85 2.55 2.85"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path d="M3 16.25h4.75" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      <path d="M3.5 16.25V18.25M6.75 16.25V18.25" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />

      {/* Speech bubbles */}
      <path
        d="M8.75 4.75h3.25a.9.9 0 0 1 .9.9v2.1a.9.9 0 0 1-.9.9H10l-1.25 1.1V8.65a.9.9 0 0 1-.9-.9V5.65a.9.9 0 0 1 .9-.9Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M11.75 9.25h3.25a.9.9 0 0 1 .9.9v2.1a.9.9 0 0 1-.9.9h-1.5l-1.25 1.1v-1.1a.9.9 0 0 1-.9-.9v-2.1a.9.9 0 0 1 .9-.9Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />

      {/* Right person */}
      <circle cx="18.75" cy="6.75" r="2" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M18.75 8.75c1.85.45 2.85 2.35 2.55 4.65-.2 1.55-1.15 2.85-2.55 2.85"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path d="M16.25 16.25h4.75" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      <path d="M16.75 16.25V18.25M20 16.25V18.25" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

export function IconContact({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 11.5V10a8 8 0 0 1 16 0v1.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <rect x="3" y="11.5" width="3.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
      <rect x="17.5" y="11.5" width="3.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M7 17v.75a5 5 0 0 0 10 0V17"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconLogin({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M10 7.5V6a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-5a2 2 0 0 1-2-2v-1.5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      <path d="M14 12H4m0 0 2.5-2.5M4 12l2.5 2.5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconLogout({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M10 7.5V6a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-5a2 2 0 0 1-2-2v-1.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path
        d="M14 12H4m0 0 2.5-2.5M4 12l2.5 2.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconExternalArrow({ className = "h-4 w-4" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M8 16 16 8M11 8h5v5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconChevron({ expanded, className = "h-3.5 w-3.5" }: IconProps & { expanded: boolean }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      style={{ transform: expanded ? "rotate(180deg)" : "none" }}
    >
      <path
        d="M10 7l5 5-5 5"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
