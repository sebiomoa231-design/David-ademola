import type { AgentRunState, GoalPlan, RunDetails } from "./types";

export type ExecutionPhase =
  | "idle"
  | "planning"
  | "awaiting_approval"
  | "executing"
  | "verifying"
  | "completed"
  | "degraded"
  | "cancelled";

export type ExecutionStepState = "pending" | "active" | "complete" | "blocked" | "failed";

export interface ExecutionStepView {
  id: string;
  title: string;
  detail: string;
  state: ExecutionStepState;
  capability?: string;
}

export interface ExecutionSnapshot {
  phase: ExecutionPhase;
  objective: string;
  message: string;
  goalId?: string;
  runId?: string;
  selectedCapability?: string;
  steps: ExecutionStepView[];
  events?: Array<{ label: string; detail?: string; state: ExecutionStepState }>;
}

export const baseExecutionSteps: ExecutionStepView[] = [
  { id: "intent", title: "Understand the objective", detail: "Extract the goal and relevant workspace context.", state: "pending" },
  { id: "plan", title: "Build a governed plan", detail: "Sequence capabilities, providers, and approval points.", state: "pending" },
  { id: "execute", title: "Execute approved work", detail: "Run only the actions allowed by the workspace policy.", state: "pending" },
  { id: "verify", title: "Verify and report", detail: "Check the result, record evidence, and write back the outcome.", state: "pending" },
];

export function phaseFromRunStatus(status?: string, approved?: boolean): ExecutionPhase {
  const normalized = String(status || "").toLowerCase();
  if (["completed", "complete", "success", "succeeded"].includes(normalized)) return "completed";
  if (["failed", "error", "degraded"].includes(normalized)) return "degraded";
  if (["cancelled", "canceled"].includes(normalized)) return "cancelled";
  if (["waiting", "paused", "approval", "awaiting_approval", "needs_approval"].includes(normalized) || approved === false) {
    return "awaiting_approval";
  }
  if (["verifying", "verification"].includes(normalized)) return "verifying";
  if (["executing", "running", "retrying", "in_progress"].includes(normalized)) return "executing";
  return "planning";
}

export function stepsForPhase(phase: ExecutionPhase, plan?: GoalPlan, details?: RunDetails): ExecutionStepView[] {
  const plannedSteps = (plan?.steps || []).slice(0, 6).map((step, index) => {
    const capability = String(step.capability || step.skill || step.tool || "capability");
    return {
      id: `plan-${index}`,
      title: capability.replace(/[-_]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
      detail: [step.agent, step.provider].filter(Boolean).join(" · ") || "Planned capability",
      capability,
      state: "pending" as ExecutionStepState,
    };
  });

  if (plannedSteps.length) {
    const activeIndex = phase === "planning" ? 0 : phase === "awaiting_approval" ? Math.min(1, plannedSteps.length - 1) : phase === "executing" ? Math.min(2, plannedSteps.length - 1) : phase === "verifying" ? plannedSteps.length - 1 : phase === "completed" ? plannedSteps.length - 1 : 0;
    return plannedSteps.map((step, index) => ({
      ...step,
      state: phase === "completed" ? "complete" : phase === "degraded" ? (index === activeIndex ? "failed" : index < activeIndex ? "complete" : "pending") : phase === "awaiting_approval" && index === activeIndex ? "blocked" : index < activeIndex ? "complete" : index === activeIndex ? "active" : "pending",
    }));
  }

  const detailEvents = (details?.events || []).slice(-4).map((event, index) => ({
    id: `event-${index}`,
    title: String(event.type || event.event_type || "Execution event").replace(/[-_]/g, " "),
    detail: String(event.message || "Recorded by David's execution trace."),
    state: "complete" as ExecutionStepState,
  }));
  if (detailEvents.length) return detailEvents;

  const activeIndex = phase === "idle" ? -1 : phase === "planning" ? 1 : phase === "awaiting_approval" ? 2 : phase === "executing" ? 2 : phase === "verifying" ? 3 : 3;
  return baseExecutionSteps.map((step, index) => ({
    ...step,
    state: phase === "completed" ? "complete" : phase === "degraded" ? (index === activeIndex ? "failed" : index < activeIndex ? "complete" : "pending") : phase === "awaiting_approval" && index === activeIndex ? "blocked" : index < activeIndex ? "complete" : index === activeIndex ? "active" : "pending",
  }));
}

export function stateFromAgentRun(state: AgentRunState): ExecutionPhase {
  return phaseFromRunStatus(state);
}
