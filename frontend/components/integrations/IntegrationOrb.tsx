"use client";

import { useEffect, useMemo, useState } from "react";

type OrbState = "IDLE" | "PROCESSING" | "RESPONDING" | "ERROR";

const STATE_LABEL: Record<OrbState, string> = {
  IDLE: "Ready",
  PROCESSING: "Processing",
  RESPONDING: "Responding",
  ERROR: "Needs attention",
};

const STATE_TONE: Record<OrbState, string> = {
  IDLE: "border-cyan-400/50 text-cyan-300",
  PROCESSING: "border-violet-400/70 text-violet-300",
  RESPONDING: "border-emerald-400/70 text-emerald-300",
  ERROR: "border-rose-400/70 text-rose-300",
};

const PARTICLES = Array.from({ length: 12 }, (_, index) => ({
  index,
  angle: index * 30,
  distance: 55 + (index % 3) * 4,
}));

export function IntegrationOrb({ state = "IDLE" }: { state?: OrbState }) {
  const [pulse, setPulse] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);
  const tone = STATE_TONE[state];
  const status = STATE_LABEL[state];

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (reducedMotion) {
      setPulse(0);
      return;
    }
    const timer = window.setInterval(() => setPulse((value) => (value + 1) % 4), 650);
    return () => window.clearInterval(timer);
  }, [reducedMotion]);

  const motionClass = reducedMotion ? "" : "transition-all duration-500";

  return (
    <div
      className="relative flex h-48 w-48 items-center justify-center"
      role="img"
      aria-live="polite"
      aria-label={`David integration core: ${status}`}
      data-state={state}
    >
      <div
        className={`absolute inset-3 rounded-full border border-dashed ${tone} opacity-50 ${motionClass} ${state === "PROCESSING" && !reducedMotion ? "rotate-180 scale-105" : "rotate-0"}`}
      />
      <div
        className={`absolute inset-8 rounded-full border-2 ${tone} opacity-80 shadow-[0_0_45px_rgba(34,211,238,0.22)] ${motionClass} ${state === "RESPONDING" && !reducedMotion ? "scale-110" : "scale-100"}`}
      />
      <div className="absolute inset-[28%] rounded-full bg-gradient-to-br from-cyan-300/80 via-violet-500/70 to-slate-950 shadow-[0_0_50px_rgba(139,92,246,0.4)]" />
      {PARTICLES.map(({ index, angle, distance }) => (
        <span
          key={index}
          className={`absolute left-1/2 top-1/2 h-1.5 w-1.5 rounded-full ${index % 2 ? "bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.9)]" : "bg-violet-300"}`}
          style={{
            transform: `rotate(${angle}deg) translateY(-${distance + (reducedMotion ? 0 : pulse * 2)}px)`,
          }}
        />
      ))}
      <div className="relative z-10 text-center">
        <div className="text-[10px] font-semibold uppercase tracking-[0.32em] text-white/80">David AI</div>
        <div className={`mt-1 text-[10px] uppercase tracking-[0.18em] ${tone.split(" ").at(-1)}`}>{status}</div>
      </div>
    </div>
  );
}
