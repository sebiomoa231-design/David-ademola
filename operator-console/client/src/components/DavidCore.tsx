import type { CSSProperties } from "react";
import { cn } from "@/lib/utils";
import type { OperatorCoreState } from "@/lib/operatorRequestRuntime";

export type DavidCoreProps = {
  state: OperatorCoreState;
  amplitude?: number;
  detail: string;
};

const particleCount = 18;

function stateLabel(state: OperatorCoreState) {
  return state === "idle" ? "STANDBY" : state.toUpperCase();
}

function voiceModeLabel(state: OperatorCoreState) {
  if (state === "listening") return "INPUT LIVE";
  if (state === "speaking") return "OUTPUT LIVE";
  if (["thinking", "processing", "planning", "executing", "generating", "verifying"].includes(state)) return "COMPUTE ACTIVE";
  return "STANDING BY";
}

export function DavidCore({ state, amplitude = 0, detail }: DavidCoreProps) {
  const label = stateLabel(state);
  const normalizedAmplitude = Math.max(0, Math.min(1, amplitude));

  return (
    <div
      className={cn("core-stage", `core-${state}`)}
      data-core-state={state}
      style={{ "--voice-amplitude": String(normalizedAmplitude) } as CSSProperties}
      aria-label={`David AI Operator core state: ${label}`}
    >
      <div className="core-grid" aria-hidden="true" />
      <div className="core-aura" aria-hidden="true" />
      <div className="core-particle-field" aria-hidden="true">
        {Array.from({ length: particleCount }, (_, index) => (
          <i key={index} style={{ "--particle-index": String(index), "--particle-angle": `${index * 20}deg`, "--particle-radius": `${112 + (index % 4) * 20}px` } as CSSProperties} />
        ))}
      </div>
      <div className="core-energy-arc core-energy-arc-a" aria-hidden="true" />
      <div className="core-energy-arc core-energy-arc-b" aria-hidden="true" />
      <div className="core-ring core-ring-a" aria-hidden="true" />
      <div className="core-ring core-ring-b" aria-hidden="true" />
      <div className="core-ring core-ring-c" aria-hidden="true" />
      <div className="core-orb">
        <span className="core-orb-inner" />
        <span className="core-orb-glint" />
      </div>
      <div className="core-readout top">DAVID AI OPERATOR // {label}</div>
      <div className="core-waveform" aria-hidden="true">
        {Array.from({ length: 21 }, (_, index) => (
          <i key={index} style={{ "--wave-index": String(index), "--voice-amplitude": String(normalizedAmplitude) } as CSSProperties} />
        ))}
      </div>
      <div className="core-readout bottom" role="status" aria-live="polite">{detail}</div>
      <div className="core-coordinate left">VOICE / {voiceModeLabel(state)}</div>
      <div className="core-coordinate right">OS CORE / GOVERNED</div>
    </div>
  );
}
