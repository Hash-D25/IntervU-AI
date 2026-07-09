"use client";

import { useEffect, useState } from "react";

const SCROLL_THRESHOLD = 320;

function ScrollToTopIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path
        d="M8 14.5 12 9.5 16 14.5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="square"
        strokeLinejoin="miter"
      />
    </svg>
  );
}

export function ScrollToTopButton() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    function handleScroll() {
      setVisible(window.scrollY > SCROLL_THRESHOLD);
    }

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <button
      type="button"
      onClick={scrollToTop}
      aria-label="Scroll to top"
      title="Scroll to top"
      className={`fixed bottom-20 right-4 z-50 flex h-11 w-11 items-center justify-center rounded-full border border-cyan-400/40 bg-[#0f172a]/90 text-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.25)] backdrop-blur-md transition-all duration-300 hover:border-cyan-400/60 hover:bg-cyan-400/10 hover:text-cyan-200 hover:shadow-[0_0_22px_rgba(34,211,238,0.45)] sm:bottom-6 sm:right-6 ${
        visible
          ? "translate-y-0 scale-100 opacity-100"
          : "pointer-events-none translate-y-3 scale-90 opacity-0"
      }`}
    >
      <ScrollToTopIcon />
    </button>
  );
}
