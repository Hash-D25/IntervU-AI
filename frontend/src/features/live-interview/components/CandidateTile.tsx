"use client";

import { VideoSurface } from "@/features/live-interview/components/VideoSurface";
import { IconCameraOff, IconMicOff } from "@/features/live-interview/icons";
import type { CameraState } from "@/features/live-interview/types";

type CandidateTileProps = {
  stream: MediaStream | null;
  cameraOn: boolean;
  micOn: boolean;
  cameraState: CameraState;
  name?: string;
};

function CameraPlaceholder({ name, denied }: { name: string; denied: boolean }) {
  const initial = name.trim().charAt(0).toUpperCase() || "Y";
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/10 bg-white/[0.05] text-2xl font-semibold text-slate-200">
        {initial}
      </div>
      <p className="flex items-center gap-1.5 text-sm text-slate-400">
        <IconCameraOff className="h-4 w-4" />
        {denied ? "Camera blocked" : "Camera off"}
      </p>
    </div>
  );
}

export function CandidateTile({
  stream,
  cameraOn,
  micOn,
  cameraState,
  name = "You",
}: CandidateTileProps) {
  const showVideo = cameraOn && stream && cameraState === "active";

  return (
    <div className="group relative aspect-video w-full overflow-hidden rounded-2xl border border-white/10 bg-slate-900/60 shadow-[0_4px_24px_rgba(0,0,0,0.35)]">
      {showVideo ? (
        <VideoSurface stream={stream} label="Your camera" />
      ) : (
        <CameraPlaceholder name={name} denied={cameraState === "denied"} />
      )}

      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 bg-gradient-to-t from-black/60 to-transparent px-3 py-2">
        <span className="rounded-md bg-black/40 px-2 py-0.5 text-xs font-medium text-slate-100 backdrop-blur-sm">
          {name}
        </span>
        {!micOn ? (
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-rose-500/80 text-white">
            <IconMicOff className="h-3.5 w-3.5" />
          </span>
        ) : null}
      </div>
    </div>
  );
}
