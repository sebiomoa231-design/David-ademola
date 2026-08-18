export type DavidCinematicPhase =
  | "idle"
  | "listening"
  | "thinking"
  | "planning"
  | "approval"
  | "executing"
  | "verifying"
  | "speaking"
  | "complete"
  | "degraded";

export type VisualNode = {
  id: string;
  label: string;
  detail?: string;
  tone?: "cyan" | "violet" | "amber" | "green" | "muted";
};

export type VisualExplanationSpec = {
  title: string;
  eyebrow?: string;
  description?: string;
  nodes: VisualNode[];
  activeNode?: string;
};

export type ExecutionStep = {
  id: string;
  label: string;
  detail?: string;
  state: "pending" | "active" | "complete" | "blocked" | "error";
};

export type ExecutionEvent = {
  id: string;
  time?: string;
  label: string;
  detail?: string;
  tone?: "cyan" | "green" | "amber" | "red" | "muted";
};

export const cinematicPhaseLabels: Record<DavidCinematicPhase, string> = {
  idle: "STANDBY",
  listening: "LISTENING",
  thinking: "THINKING",
  planning: "PLANNING",
  approval: "APPROVAL REQUIRED",
  executing: "EXECUTING",
  verifying: "VERIFYING",
  speaking: "RESPONDING",
  complete: "COMPLETE",
  degraded: "DEGRADED",
};

export function normalizeCinematicPhase(value?: string): DavidCinematicPhase {
  const normalized = String(value || "idle").toLowerCase();
  if (normalized.includes("listen")) return "listening";
  if (normalized.includes("think") || normalized.includes("process")) return "thinking";
  if (normalized.includes("plan")) return "planning";
  if (normalized.includes("approv") || normalized.includes("await")) return "approval";
  if (normalized.includes("execut") || normalized.includes("running")) return "executing";
  if (normalized.includes("verif")) return "verifying";
  if (normalized.includes("speak") || normalized.includes("respond")) return "speaking";
  if (normalized.includes("complete") || normalized.includes("success")) return "complete";
  if (normalized.includes("degrad") || normalized.includes("error") || normalized.includes("offline")) return "degraded";
  return "idle";
}
