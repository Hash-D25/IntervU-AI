"use client";

import { useEffect, useRef } from "react";

type VideoSurfaceProps = {
  stream: MediaStream | null;
  /** Local self-view must be muted to avoid echo. */
  muted?: boolean;
  className?: string;
  /** Mirror the video like a typical self-view. */
  mirrored?: boolean;
  label?: string;
};

export function VideoSurface({
  stream,
  muted = true,
  className = "",
  mirrored = true,
  label = "Your camera preview",
}: VideoSurfaceProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    if (video.srcObject !== stream) {
      video.srcObject = stream;
    }
  }, [stream]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted={muted}
      aria-label={label}
      className={`h-full w-full object-cover ${mirrored ? "-scale-x-100" : ""} ${className}`}
    />
  );
}
