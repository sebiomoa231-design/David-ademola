"use client";

import { ArrowRight, BarChart3, GitBranch, Layers3, Play, Sparkles, Waypoints } from "lucide-react";
import { useMemo, useState } from "react";

import type { VisualExplanationSpec } from "./types";

const toneClass = {
  cyan: "david-node-cyan",
  violet: "david-node-violet",
  amber: "david-node-amber",
  green: "david-node-green",
  muted: "david-node-muted",
};

export type VisualExplanationCanvasProps = {
  spec?: VisualExplanationSpec;
  compact?: boolean;
  mode?: "flow" | "timeline" | "architecture";
  onPresent?: () => void;
};

const defaultSpec: VisualExplanationSpec = {
  eyebrow: "VISUAL EXPLANATION CANVAS",
  title: "How David turns intent into verified action",
  description: "The explanation is rendered as a visual sequence so the user can follow the reasoning boundary, approvals, tools, and verification step.",
  activeNode: "plan",
  nodes: [
    { id: "intent", label: "Intent", detail: "What you asked", tone: "cyan" },
    { id: "plan", label: "Plan", detail: "Ordered and bounded", tone: "violet" },
    { id: "approval", label: "Approval", detail: "User remains in control", tone: "amber" },
    { id: "tools", label: "Tools", detail: "Permitted providers", tone: "cyan" },
    { id: "verify", label: "Verify", detail: "Evidence and result", tone: "green" },
  ],
};

export function VisualExplanationCanvas({ spec = defaultSpec, compact = false, mode: initialMode = "flow", onPresent }: VisualExplanationCanvasProps) {
  const [mode, setMode] = useState(initialMode);
  const activeIndex = Math.max(0, spec.nodes.findIndex((node) => node.id === spec.activeNode));
  const progress = useMemo(() => `${Math.max(1, activeIndex + 1)} / ${spec.nodes.length}`, [activeIndex, spec.nodes.length]);

  return (
    <section className={`david-visual-canvas ${compact ? "david-visual-canvas-compact" : ""}`} aria-label="Visual explanation canvas">
      <div className="david-visual-canvas-header">
        <div>
          <p className="david-cinematic-kicker"><Sparkles size={12} /> {spec.eyebrow || "VISUAL EXPLANATION"}</p>
          <h3>{spec.title}</h3>
          {spec.description && <p className="david-visual-description">{spec.description}</p>}
        </div>
        <div className="david-visual-actions">
          <span className="david-visual-progress">FRAME {progress}</span>
          {onPresent && <button type="button" className="david-visual-present" onClick={onPresent}><Play size={13} /> Present</button>}
        </div>
      </div>

      <div className="david-visual-tabs" role="tablist" aria-label="Explanation view">
        <button type="button" className={mode === "flow" ? "is-active" : ""} onClick={() => setMode("flow")}><Waypoints size={13} /> Flow</button>
        <button type="button" className={mode === "timeline" ? "is-active" : ""} onClick={() => setMode("timeline")}><BarChart3 size={13} /> Timeline</button>
        <button type="button" className={mode === "architecture" ? "is-active" : ""} onClick={() => setMode("architecture")}><GitBranch size={13} /> Map</button>
      </div>

      {mode === "flow" && <div className="david-visual-flow" role="list">
        {spec.nodes.map((node, index) => <div className="david-visual-flow-item" role="listitem" key={node.id}>
          <div className={`david-visual-node ${toneClass[node.tone || "cyan"]} ${node.id === spec.activeNode ? "is-active" : ""}`}>
            <span className="david-visual-node-index">0{index + 1}</span>
            <span className="david-visual-node-copy"><strong>{node.label}</strong><small>{node.detail}</small></span>
          </div>
          {index < spec.nodes.length - 1 && <ArrowRight className="david-visual-arrow" size={16} aria-hidden="true" />}
        </div>)}
      </div>}

      {mode === "timeline" && <div className="david-visual-timeline" role="list">
        {spec.nodes.map((node, index) => <div className={`david-timeline-row ${index <= activeIndex ? "is-reached" : ""}`} role="listitem" key={node.id}><span className="david-timeline-marker">{index <= activeIndex ? "✓" : "·"}</span><span><strong>{node.label}</strong><small>{node.detail}</small></span><em>{index <= activeIndex ? "visible" : "queued"}</em></div>)}
      </div>}

      {mode === "architecture" && <div className="david-visual-map" role="list">
        <div className="david-map-column"><span className="david-map-label">INPUT</span>{spec.nodes.slice(0, 1).map((node) => <div className="david-map-card" key={node.id}>{node.label}<small>{node.detail}</small></div>)}</div>
        <div className="david-map-connector"><span /> <span /> <span /></div>
        <div className="david-map-column"><span className="david-map-label">DAVID PLANE</span>{spec.nodes.slice(1, -1).map((node) => <div className="david-map-card" key={node.id}>{node.label}<small>{node.detail}</small></div>)}</div>
        <div className="david-map-connector"><span /> <span /> <span /></div>
        <div className="david-map-column"><span className="david-map-label">EVIDENCE</span>{spec.nodes.slice(-1).map((node) => <div className="david-map-card david-map-card-final" key={node.id}>{node.label}<small>{node.detail}</small></div>)}</div>
      </div>}

      {!compact && <div className="david-visual-footnote"><Layers3 size={13} /> Every visual frame is an explanation surface; it can be populated by a plan, diagram, chart, storyboard, or provider result.</div>}
    </section>
  );
}
