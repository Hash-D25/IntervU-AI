"use client";

import Link from "next/link";

import { ControlButton } from "@/features/live-interview/components/ControlButton";
import { DevicePicker } from "@/features/live-interview/components/DevicePicker";
import { VideoSurface } from "@/features/live-interview/components/VideoSurface";
import {
  IconCamera,
  IconCameraOff,
  IconMic,
  IconMicOff,
} from "@/features/live-interview/icons";
import type {
  CameraState,
  MediaDeviceOption,
  RoomHeaderInfo,
} from "@/features/live-interview/types";

type PreJoinScreenProps = {
  header: RoomHeaderInfo;
  stream: MediaStream | null;
  cameraState: CameraState;
  cameraError: string | null;
  micError: string | null;
  cameraOn: boolean;
  micOn: boolean;
  onToggleCamera: () => void;
  onToggleMic: () => void;
  cameras: MediaDeviceOption[];
  microphones: MediaDeviceOption[];
  selectedCameraId: string | null;
  selectedMicrophoneId: string | null;
  onSelectCamera: (deviceId: string) => void;
  onSelectMicrophone: (deviceId: string) => void;
  onJoin: () => void;
  backHref: string;
};

function PreviewPlaceholder({ denied }: { denied: boolean }) {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-3 px-6 text-center">
      <IconCameraOff className="h-10 w-10 text-slate-500" />
      <p className="text-sm text-slate-400">
        {denied
          ? "Camera access is blocked. Update your browser permissions to see a preview."
          : "Camera is off. Turn it on to preview your video."}
      </p>
    </div>
  );
}

export function PreJoinScreen({
  header,
  stream,
  cameraState,
  cameraError,
  micError,
  cameraOn,
  micOn,
  onToggleCamera,
  onToggleMic,
  cameras,
  microphones,
  selectedCameraId,
  selectedMicrophoneId,
  onSelectCamera,
  onSelectMicrophone,
  onJoin,
  backHref,
}: PreJoinScreenProps) {
  const showVideo = cameraOn && stream && cameraState === "active";
  const title = header.companyName
    ? `${header.companyName} · ${header.targetRole}`
    : header.targetRole;

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center gap-8 px-4 py-10 lg:flex-row lg:items-center lg:gap-12">
      <div className="flex-1">
        <div className="relative aspect-video w-full overflow-hidden rounded-2xl border border-white/10 bg-slate-900/60 shadow-[0_4px_24px_rgba(0,0,0,0.35)]">
          {showVideo ? (
            <VideoSurface stream={stream} label="Camera preview" />
          ) : (
            <PreviewPlaceholder denied={cameraState === "denied"} />
          )}

          <div className="absolute inset-x-0 bottom-0 flex items-center justify-center gap-3 bg-gradient-to-t from-black/60 to-transparent py-4">
            <ControlButton
              icon={micOn ? <IconMic /> : <IconMicOff />}
              label={micOn ? "Turn off microphone" : "Turn on microphone"}
              onClick={onToggleMic}
              pressed={micOn}
              variant={micOn ? "neutral" : "off"}
            />
            <ControlButton
              icon={cameraOn ? <IconCamera /> : <IconCameraOff />}
              label={cameraOn ? "Turn off camera" : "Turn on camera"}
              onClick={onToggleCamera}
              pressed={cameraOn}
              variant={cameraOn ? "neutral" : "off"}
            />
          </div>
        </div>

        {cameraError ? (
          <p className="mt-3 text-sm text-rose-400/90" role="alert">
            {cameraError}
          </p>
        ) : null}
        {micError ? (
          <p className="mt-2 text-sm text-rose-400/90" role="alert">
            {micError}
          </p>
        ) : null}
      </div>

      <div className="w-full max-w-md lg:w-96">
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-cyan-400/70">
          Ready to join?
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100">{title}</h1>
        <p className="mt-2 text-sm text-slate-500">
          Check your camera and microphone before joining. Your video stays on your device and is
          never uploaded.
        </p>

        <div className="mt-6">
          <DevicePicker
            inline
            cameras={cameras}
            microphones={microphones}
            selectedCameraId={selectedCameraId}
            selectedMicrophoneId={selectedMicrophoneId}
            onSelectCamera={onSelectCamera}
            onSelectMicrophone={onSelectMicrophone}
          />
        </div>

        <button type="button" onClick={onJoin} className="btn-neon mt-6 w-full py-2.5 text-base">
          Join interview
        </button>
        <Link href={backHref} className="btn-glass mt-3 block w-full py-2.5 text-center">
          Cancel
        </Link>
      </div>
    </div>
  );
}
