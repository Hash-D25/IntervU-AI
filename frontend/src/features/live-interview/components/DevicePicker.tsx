"use client";

import { useEffect, useId, useRef, useState } from "react";

import { IconSettings } from "@/features/live-interview/icons";
import type { MediaDeviceOption } from "@/features/live-interview/types";

type DevicePickerProps = {
  cameras: MediaDeviceOption[];
  microphones: MediaDeviceOption[];
  selectedCameraId: string | null;
  selectedMicrophoneId: string | null;
  onSelectCamera: (deviceId: string) => void;
  onSelectMicrophone: (deviceId: string) => void;
  /** Render as a full-width inline block (pre-join) instead of a popover. */
  inline?: boolean;
};

function DeviceSelects({
  cameras,
  microphones,
  selectedCameraId,
  selectedMicrophoneId,
  onSelectCamera,
  onSelectMicrophone,
  idPrefix,
}: Omit<DevicePickerProps, "inline"> & { idPrefix: string }) {
  return (
    <div className="space-y-3">
      <div>
        <label
          htmlFor={`${idPrefix}-camera`}
          className="mb-1 block text-xs font-medium text-slate-400"
        >
          Camera
        </label>
        <select
          id={`${idPrefix}-camera`}
          className="input-glass text-sm"
          value={selectedCameraId ?? ""}
          onChange={(event) => onSelectCamera(event.target.value)}
          disabled={cameras.length === 0}
        >
          {cameras.length === 0 ? <option value="">No cameras found</option> : null}
          {cameras.map((camera) => (
            <option key={camera.deviceId} value={camera.deviceId}>
              {camera.label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label
          htmlFor={`${idPrefix}-mic`}
          className="mb-1 block text-xs font-medium text-slate-400"
        >
          Microphone
        </label>
        <select
          id={`${idPrefix}-mic`}
          className="input-glass text-sm"
          value={selectedMicrophoneId ?? ""}
          onChange={(event) => onSelectMicrophone(event.target.value)}
          disabled={microphones.length === 0}
        >
          {microphones.length === 0 ? <option value="">No microphones found</option> : null}
          {microphones.map((mic) => (
            <option key={mic.deviceId} value={mic.deviceId}>
              {mic.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export function DevicePicker(props: DevicePickerProps) {
  const { inline = false } = props;
  const idPrefix = useId();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }
    const handlePointerDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  if (inline) {
    return <DeviceSelects {...props} idPrefix={idPrefix} />;
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Device settings"
        aria-haspopup="dialog"
        aria-expanded={open}
        title="Device settings"
        className="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/[0.06] text-slate-200 backdrop-blur-md transition hover:border-white/20 hover:bg-white/[0.1] focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/60 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0e17]"
      >
        <IconSettings />
      </button>
      {open ? (
        <div
          role="dialog"
          aria-label="Select devices"
          className="glass-panel-strong absolute bottom-full right-0 mb-3 w-72 p-4"
        >
          <p className="mb-3 text-sm font-medium text-slate-200">Devices</p>
          <DeviceSelects {...props} idPrefix={idPrefix} />
        </div>
      ) : null}
    </div>
  );
}
