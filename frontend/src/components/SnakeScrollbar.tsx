"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const SEGMENT_COUNT = 7;
const TRACK_INSET = 16;
const THUMB_MIN_HEIGHT = 52;
const SLITHER_STOP_MS = 320;

type ScrollMetrics = {
  progress: number;
  thumbHeight: number;
  trackHeight: number;
  canScroll: boolean;
};

export function SnakeScrollbar() {
  const [metrics, setMetrics] = useState<ScrollMetrics>({
    progress: 0,
    thumbHeight: THUMB_MIN_HEIGHT,
    trackHeight: 0,
    canScroll: false,
  });
  const [isSlithering, setIsSlithering] = useState(false);
  const slitherTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const isHoveringRef = useRef(false);

  const updateMetrics = useCallback(() => {
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = window.innerHeight;
    const maxScroll = scrollHeight - clientHeight;
    const canScroll = maxScroll > 8;
    const progress = canScroll ? Math.min(1, Math.max(0, window.scrollY / maxScroll)) : 0;
    const trackHeight = Math.max(0, clientHeight - TRACK_INSET * 2);
    const thumbHeight = canScroll
      ? Math.max(THUMB_MIN_HEIGHT, (clientHeight / scrollHeight) * trackHeight)
      : THUMB_MIN_HEIGHT;

    setMetrics({ progress, thumbHeight, trackHeight, canScroll });
  }, []);

  const startSlither = useCallback(() => {
    setIsSlithering(true);
    if (slitherTimeoutRef.current) {
      clearTimeout(slitherTimeoutRef.current);
    }
  }, []);

  const scheduleStopSlither = useCallback(() => {
    if (slitherTimeoutRef.current) {
      clearTimeout(slitherTimeoutRef.current);
    }
    slitherTimeoutRef.current = setTimeout(() => {
      if (!isHoveringRef.current) {
        setIsSlithering(false);
      }
    }, SLITHER_STOP_MS);
  }, []);

  const scrollToTrackY = useCallback(
    (clientY: number) => {
      const track = trackRef.current;
      if (!track || !metrics.canScroll) {
        return;
      }

      const rect = track.getBoundingClientRect();
      const pointerY = clientY - rect.top;
      const travel = Math.max(0, metrics.trackHeight - metrics.thumbHeight);
      const thumbTop = pointerY - metrics.thumbHeight / 2;
      const ratio = travel > 0 ? Math.min(1, Math.max(0, thumbTop / travel)) : 0;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      window.scrollTo({ top: ratio * maxScroll, behavior: "auto" });
    },
    [metrics.canScroll, metrics.thumbHeight, metrics.trackHeight],
  );

  useEffect(() => {
    updateMetrics();

    function handleScroll() {
      updateMetrics();
      startSlither();
      scheduleStopSlither();
    }

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", updateMetrics);

    const observer = new ResizeObserver(updateMetrics);
    observer.observe(document.documentElement);
    observer.observe(document.body);

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", updateMetrics);
      observer.disconnect();
      if (slitherTimeoutRef.current) {
        clearTimeout(slitherTimeoutRef.current);
      }
    };
  }, [scheduleStopSlither, startSlither, updateMetrics]);

  function handleTrackClick(event: React.MouseEvent<HTMLDivElement>) {
    startSlither();
    scrollToTrackY(event.clientY);
    scheduleStopSlither();
  }

  function handleMouseEnter() {
    isHoveringRef.current = true;
    startSlither();
  }

  function handleMouseLeave() {
    isHoveringRef.current = false;
    scheduleStopSlither();
  }

  function handleTrackMouseMove(event: React.MouseEvent<HTMLDivElement>) {
    if (!metrics.canScroll) {
      return;
    }
    startSlither();
    scrollToTrackY(event.clientY);
  }

  if (!metrics.canScroll) {
    return null;
  }

  const thumbOffset = metrics.progress * Math.max(0, metrics.trackHeight - metrics.thumbHeight);

  return (
    <div
      className="snake-scrollbar fixed right-2 top-0 z-[60] hidden h-full w-5 sm:block"
      style={{ paddingTop: TRACK_INSET, paddingBottom: TRACK_INSET }}
      aria-hidden
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div
        ref={trackRef}
        onClick={handleTrackClick}
        onMouseMove={handleTrackMouseMove}
        className="snake-scrollbar-track relative h-full w-full cursor-pointer"
      >
        <div
          className={`snake-scrollbar-thumb absolute left-1/2 w-[7px] ${isSlithering ? "is-slithering" : ""}`}
          style={{
            height: metrics.thumbHeight,
            transform: `translateX(-50%) translateY(${thumbOffset}px)`,
          }}
        >
          {Array.from({ length: SEGMENT_COUNT }, (_, index) => (
            <span
              key={index}
              className={`snake-segment ${index === 0 ? "snake-segment-head" : ""} ${
                index === SEGMENT_COUNT - 1 ? "snake-segment-tail" : ""
              }`}
              style={{ animationDelay: `${index * 0.06}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
