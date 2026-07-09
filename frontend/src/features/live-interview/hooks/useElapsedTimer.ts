"use client";

import { useEffect, useState } from "react";

/**
 * Counts elapsed whole seconds while `active` is true. Resets to 0 whenever it
 * transitions from inactive to active.
 */
export function useElapsedTimer(active: boolean): number {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (!active) {
      return;
    }
    setSeconds(0);
    const startedAt = Date.now();
    const interval = window.setInterval(() => {
      setSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(interval);
  }, [active]);

  return seconds;
}

export function formatElapsed(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}
