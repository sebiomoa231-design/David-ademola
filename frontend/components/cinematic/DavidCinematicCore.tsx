"use client";

import { Activity, AudioLines, Check, CircleAlert, Cpu, LockKeyhole, Mic, Orbit, Radio, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { cinematicPhaseLabels, type DavidCinematicPhase } from "./types";

const phaseIcons: Record<DavidCinematicPhase, typeof Sparkles> = {
  idle: Orbit,
  listening: Mic,
  thinking: Cpu,
  planning: Activity,
  approval: LockKeyhole,
  executing: Zap,
  verifying: ShieldCheck,
  speaking: AudioLines,
  complete: Check,
  degraded: CircleAlert,
};

const phaseDescriptions: Record<DavidCinematicPhase, string> = {
  idle: "Ready for an objective",
  listening: "Microphone channel is active",
  thinking: "Interpreting the request",
  planning: "Constructing a governed plan",
  approval: "Waiting for explicit authorization",
  executing: "A permitted action is in progress",
  verifying: "Checking the result and provenance",
  speaking: "Preparing a response",
  complete: "The current cycle is complete",
  degraded: "A dependency needs attention",
};

export type DavidCinematicCoreProps = {
  phase?: DavidCinematicPhase;
  size?: "hero" | "compact";
  label?: string;
  subtitle?: string;
  metric?: string;
  onActivate?: () => void;
  showControls?: boolean;
};

export function DavidCinematicCore({ phase = "idle", size = "hero", label = "DAVID CORE", subtitle, metric = "VISUAL CHANNEL ONLINE", onActivate, showControls = true }: DavidCinematicCoreProps) {
  const [pulse, setPulse] = useState(0.5);
  const Icon = phaseIcons[phase];
  const phaseLabel = cinematicPhaseLabels[phase];
  const isActive = phase !== "idle" && phase !== "complete";
  const bars = useMemo(() => Array.from({ length: 28 }, (_, index) => {
    const wave = Math.abs(Math.sin(index * 0.82 + pulse * 4));
    const height = 16 + Math.round(wave * (isActive ? 52 : 25));
    return { height, delay: `${(index % 7) * 0.07}s` };
  }), [isActive, pulse]);

  useEffect(() => {
    const timer = window.setInterval(() => setPulse((current) => (current + 0.08) % 1), 120);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <section className={`david-cinematic david-cinematic-${size} david-phase-${phase}`} aria-label={`${label} ${phaseLabel}`}>
      <div className="david-cinematic-scan" />
      <div className="david-cinematic-header">
        <div>
          <p className="david-cinematic-kicker"><Radio size={12} /> {label}</p>
          <p className="david-cinematic-subtitle">{subtitle || phaseDescriptions[phase]}</p>
        </div>
        <span className="david-cinematic-readout">{metric}</span>
      </div>

      <div className="david-core-stage">
        <div className="david-orbit david-orbit-outer" />
        <div className="david-orbit david-orbit-middle" />
        <div className="david-orbit david-orbit-inner" />
        <div className="david-core-crosshair david-crosshair-horizontal" />
        <div className="david-core-crosshair david-crosshair-vertical" />
        <div className="david-core-glow" />
        <button type="button" className="david-core-nucleus" onClick={onActivate} aria-label={`Activate ${label}`}>
          <span className="david-core-nucleus-ring" />
          <span className="david-core-nucleus-ring david-ring-delayed" />
          <Icon className="david-core-icon" size={size === "hero" ? 30 : 21} />
          <span className="david-core-nucleus-label">{phaseLabel}</span>
        </button>
        <div className="david-core-scan-beam" />
        <div className="david-core-particles" aria-hidden="true">
          {Array.from({ length: 12 }, (_, index) => <span key={index} style={{ "--particle-index": index } as React.CSSProperties} />)}
        </div>
      </div>

      <div className="david-cinematic-wave" aria-hidden="true">
        {bars.map((bar, index) => <span key={index} style={{ height: `${bar.height}%`, animationDelay: bar.delay }} />)}
      </div>

      <div className="david-cinematic-footer">
        <span><Sparkles size={12} /> {phaseDescriptions[phase]}</span>
        {showControls && <span className="david-cinematic-control">{onActivate ? "CORE READY · CLICK TO ACTIVATE" : "LIVE VISUAL TELEMETRY"}</span>}
      </div>
    </section>
  );
}
