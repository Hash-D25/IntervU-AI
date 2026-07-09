"use client";

import { useCallback, useEffect, useState } from "react";

import type { MediaDeviceOption } from "@/features/live-interview/types";

interface UseMediaDevicesResult {
  cameras: MediaDeviceOption[];
  microphones: MediaDeviceOption[];
  refresh: () => Promise<void>;
}

function toOptions(devices: MediaDeviceInfo[], kind: MediaDeviceKind, fallbackPrefix: string) {
  return devices
    .filter((device) => device.kind === kind)
    .map((device, index) => ({
      deviceId: device.deviceId,
      // Labels are empty until the user grants permission for that media type.
      label: device.label || `${fallbackPrefix} ${index + 1}`,
    }));
}

/**
 * Enumerates available camera and microphone input devices for the device
 * picker. Device labels only populate after the relevant permission is granted,
 * so refresh after starting the camera/mic.
 */
export function useMediaDevices(): UseMediaDevicesResult {
  const [cameras, setCameras] = useState<MediaDeviceOption[]>([]);
  const [microphones, setMicrophones] = useState<MediaDeviceOption[]>([]);

  const refresh = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      return;
    }
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      setCameras(toOptions(devices, "videoinput", "Camera"));
      setMicrophones(toOptions(devices, "audioinput", "Microphone"));
    } catch {
      // Enumeration can fail on some browsers before any permission; ignore.
    }
  }, []);

  useEffect(() => {
    void refresh();
    const mediaDevices = navigator.mediaDevices;
    if (!mediaDevices?.addEventListener) {
      return;
    }
    const handleChange = () => void refresh();
    mediaDevices.addEventListener("devicechange", handleChange);
    return () => mediaDevices.removeEventListener("devicechange", handleChange);
  }, [refresh]);

  return { cameras, microphones, refresh };
}
