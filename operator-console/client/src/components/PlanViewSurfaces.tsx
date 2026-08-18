import React from "react";
import { PlanEvidenceList } from "./PlanEvidenceList";

type Plan = { steps: string[] };

export function ConversationPlanSurface({ plan }: { plan: Plan | null }) {
  return <div className="surface-card detail-card"><p className="eyebrow-small">ACTIVE RESPONSE PLAN</p>{plan ? <PlanEvidenceList label="Active David AI Operator response plan" className="chat-plan-list" steps={plan.steps} /> : <p className="technical-copy">David will persist a response plan when the next request begins.</p>}</div>;
}

export function RunPlanSurface({ plan }: { plan: Plan | null }) {
  return plan ? <PlanEvidenceList label="David AI Operator response plan" steps={plan.steps} /> : null;
}

export function ExecutionPlanSurface({ plan }: { plan: Plan | null }) {
  return plan ? <div className="theater-plan"><p className="eyebrow-small">STRUCTURED PLAN</p><PlanEvidenceList label="Structured David AI Operator execution plan" steps={plan.steps} /></div> : null;
}
