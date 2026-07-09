"use client";

import { ControlButton } from "@/features/live-interview/components/ControlButton";
import { DevicePicker } from "@/features/live-interview/components/DevicePicker";
import {
  IconCamera,
  IconCameraOff,
  IconCaptions,
  IconEndCall,
  IconMic,
  IconMicOff,
} from "@/features/live-interview/icons";
import type { MediaDeviceOption } from "@/features/live-interview/types";

type ControlBarProps = {
  micOn: boolean;
  cameraOn: boolean;
  captionsOn: boolean;
  onToggleMic: () => void;
  onToggleCamera: () => void;
  onToggleCaptions: () => void;
  onEnd: () => void;
  cameras: MediaDeviceOption[];
  microphones: MediaDeviceOption[];
  selectedCameraId: string | null;
  selectedMicrophoneId: string | null;
  onSelectCamera: (deviceId: string) => void;
  onSelectMicrophone: (deviceId: string) => void;
};

export function ControlBar({
  micOn,
  cameraOn,
  captionsOn,
  onToggleMic,
  onToggleCamera,
  onToggleCaptions,
  onEnd,
  cameras,
  microphones,
  selectedCameraId,
  selectedMicrophoneId,
  onSelectCamera,
  onSelectMicrophone,
}: ControlBarProps) {
  return (
    <div className="flex items-center justify-center gap-2 border-t border-white/[0.06] px-4 py-3 sm:gap-3 sm:py-4">
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
      <ControlButton
        icon={<IconCaptions />}
        label={captionsOn ? "Hide live captions" : "Show live captions"}
        onClick={onToggleCaptions}
        pressed={captionsOn}
        variant={captionsOn ? "active" : "neutral"}
      />
      <DevicePicker
        cameras={cameras}
        microphones={microphones}
        selectedCameraId={selectedCameraId}
        selectedMicrophoneId={selectedMicrophoneId}
        onSelectCamera={onSelectCamera}
        onSelectMicrophone={onSelectMicrophone}
      />
      <div className="mx-1 h-8 w-px bg-white/10" aria-hidden />
      <ControlButton
        icon={<IconEndCall />}
        label="End interview"
        onClick={onEnd}
        variant="danger"
      />
    </div>
  );
}
