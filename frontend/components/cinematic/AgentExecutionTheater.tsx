"use client";

import { Check, CircleAlert, Clock3, Loader2, LockKeyhole, Radio, ShieldCheck, X } from "lucide-react";

import type { ExecutionEvent, ExecutionStep } from "./types";

export type AgentExecutionTheaterProps = {
  steps: ExecutionStep[];
  events?: ExecutionEvent[];
  title?: string;
  subtitle?: string;
  live?: boolean;
  compact?: boolean;
};

const stepIcons = {
  pending: Clock3,
  active: Loader2,
  complete: Check,
  blocked: LockKeyhole,
  error: X,
};

export function AgentExecutionTheater({ steps, events = [], title = "Agent execution theater", subtitle = "A visual trace of the plan, approval boundary, and verification evidence.", live = false, compact = false }: AgentExecutionTheaterProps) {
  return (
    <section className={`david-execution-theater ${compact ? "david-execution-theater-compact" : ""}`} aria-label="Agent execution theater">
      <div className="david-execution-header">
        <div>
          <p className="david-cinematic-kicker"><Radio size={12} /> {live ? "LIVE EXECUTION TRACE" : "EXECUTION PREVIEW"}</p>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <ShieldCheck size={18} className="david-execution-shield" />
      </div>

      <div className="david-execution-rail" role="list" aria-label="Execution steps">
        {steps.map((step, index) => {
          const Icon = stepIcons[step.state];
          return <div className={`david-execution-step david-step-${step.state}`} role="listitem" key={step.id}>
            <div className="david-execution-node"><Icon size={14} /></div>
            <div className="david-execution-step-copy"><strong>{step.label}</strong><small>{step.detail || step.state}</small></div>
            {index < steps.length - 1 && <span className="david-execution-connector" aria-hidden="true" />}
          </div>;
        })}
      </div>

      <div className="david-execution-events">
        <div className="david-execution-events-heading"><span>EVENT STREAM</span><span>{events.length ? `${events.length} events` : "Awaiting events"}</span></div>
        {events.length ? events.slice(-5).map((event) => <div className={`david-execution-event david-event-${event.tone || "muted"}`} key={event.id}><span className="david-event-dot" /><span className="david-event-time">{event.time || "--:--"}</span><span className="david-event-label">{event.label}</span><span className="david-event-detail">{event.detail}</span></div>) : <div className="david-execution-empty"><CircleAlert size={14} /> No live events yet. Plan an objective to populate this theater with backend lifecycle events.</div>}
      </div>
    </section>
  );
}
