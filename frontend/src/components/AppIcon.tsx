import Image from "next/image";

const ICON_SRC = "/app-icon-transparent.png";

type AppIconProps = {
  size?: number;
  className?: string;
  priority?: boolean;
  showGlow?: boolean;
};

export function AppIcon({
  size = 64,
  className = "",
  priority = false,
  showGlow = true,
}: AppIconProps) {
  return (
    <div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      {showGlow ? (
        <div
          className="pointer-events-none absolute inset-0 scale-125 bg-cyan-400/15 blur-2xl"
          aria-hidden
        />
      ) : null}
      <Image
        src={ICON_SRC}
        alt="IntervU"
        width={size}
        height={size}
        priority={priority}
        className="relative z-10 h-full w-full object-contain"
      />
    </div>
  );
}
