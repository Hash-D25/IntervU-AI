"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { CameraState } from "@/features/live-interview/types";

interface UseCameraResult {
  state: CameraState;
  error: string | null;
  /** Live local video stream. Stays in the browser — never uploaded. */
  stream: MediaStream | null;
  /** Request the camera (optionally a specific device). */
  start: (deviceId?: string) => Promise<void>;
  /** Stop the camera and release the device. */
  stop: () => void;
}

function toCameraError(err: unknown): { state: CameraState; message: string } {
  if (err instanceof DOMException) {
    if (err.name === "NotAllowedError" || err.name === "SecurityError") {
      return {
        state: "denied",
        message: "Camera access was blocked. Allow camera permission and try again.",
      };
    }
    if (err.name === "NotFoundError" || err.name === "OverconstrainedError") {
      return { state: "error", message: "No camera was found on this device." };
    }
    if (err.name === "NotReadableError") {
      return {
        state: "error",
        message: "Your camera is already in use by another application.",
      };
    }
  }
  const message = err instanceof Error ? err.message : "Could not access the camera.";
  return { state: "error", message };
}

/**
 * Manages a local camera `MediaStream` for the candidate self-view.
 * Mirrors the contract of `useMicrophone`: `state`, `error`, and start/stop.
 * The stream is exposed so a consumer can attach it to a `<video>` element.
 */
export function useCamera(): UseCameraResult {
  const [state, setState] = useState<CameraState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setStream(null);
    setState("idle");
  }, []);

  const start = useCallback(async (deviceId?: string) => {
    setError(null);
    setState("requesting");
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Camera access is not supported in this browser.");
      }
      // Release any previous stream before requesting a new one.
      streamRef.current?.getTracks().forEach((track) => track.stop());

      const constraints: MediaStreamConstraints = {
        video: deviceId ? { deviceId: { exact: deviceId } } : true,
        audio: false,
      };
      const next = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = next;
      setStream(next);
      setState("active");
    } catch (err) {
      const { state: nextState, message } = toCameraError(err);
      streamRef.current = null;
      setStream(null);
      setError(message);
      setState(nextState);
    }
  }, []);

  // Ensure tracks are released if the component unmounts while active.
  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    };
  }, []);

  return { state, error, stream, start, stop };
}
