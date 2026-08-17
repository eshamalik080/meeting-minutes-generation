import type { ReactNode } from "react";

import { useInView } from "../hooks/useInView";

interface RevealProps {
  children: ReactNode;
  delayMs?: number;
  className?: string;
}

/** Wraps content in a one-shot fade/slide-up reveal that fires when scrolled into view. */
export default function Reveal({ children, delayMs = 0, className = "" }: RevealProps) {
  const { ref, isInView } = useInView<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={`reveal ${isInView ? "reveal-visible" : ""} ${className}`}
      style={{ transitionDelay: isInView ? `${delayMs}ms` : "0ms" }}
    >
      {children}
    </div>
  );
}
