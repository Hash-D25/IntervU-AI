// Inline SVG icons for the live room, matching the app's stroke-based icon style
// (currentColor, strokeWidth ~1.75). Kept local to the feature.

type IconProps = {
  className?: string;
};

export function IconMic({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M5.5 11a6.5 6.5 0 0 0 13 0"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path d="M12 17.5V21M9 21h6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

export function IconMicOff({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M15 5a3 3 0 0 0-6 0v5m0 2a3 3 0 0 0 4.5 2.6"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M5.5 11a6.5 6.5 0 0 0 10 5.4M18.5 11a6.4 6.4 0 0 1-.4 2.2"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path d="M12 17.5V21M9 21h6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      <path d="M4 4l16 16" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

export function IconCamera({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="6.5" width="12.5" height="11" rx="2.5" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M15.5 10.5 21 7.5v9l-5.5-3"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconCameraOff({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M3 8.5a2 2 0 0 1 2-2h8.5a2 2 0 0 1 2 2v.5m0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path
        d="M15.5 10.5 21 7.5v9l-3-1.6"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path d="M4 4l16 16" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

export function IconCaptions({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M9.5 10.25a2 2 0 1 0 0 3.5M15.5 10.25a2 2 0 1 0 0 3.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconEndCall({ className = "h-6 w-6" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4.5 14.5c4.5-4 10.5-4 15 0 .8.7.9 1.9.3 2.7l-1.2 1.5c-.5.6-1.3.8-2 .5l-2.3-1a1.6 1.6 0 0 1-1-1.4l-.1-1.2c-1.6-.5-3.3-.5-4.9 0l-.1 1.2a1.6 1.6 0 0 1-1 1.4l-2.3 1c-.7.3-1.5.1-2-.5L1.7 17.2c-.6-.8-.5-2 .3-2.7"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
        transform="rotate(135 12 12)"
      />
    </svg>
  );
}

export function IconSettings({ className = "h-5 w-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M12 3v2.5M12 18.5V21M4.2 7.5l2.2 1.3M17.6 15.2l2.2 1.3M4.2 16.5l2.2-1.3M17.6 8.8l2.2-1.3"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconChevronRight({ className = "h-5 w-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M9 6l6 6-6 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconChevronLeft({ className = "h-5 w-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M15 6l-6 6 6 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
