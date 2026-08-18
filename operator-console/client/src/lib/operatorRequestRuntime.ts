export type OperatorCoreState = "idle" | "listening" | "thinking" | "planning" | "executing" | "verifying" | "speaking" | "complete" | "degraded";

type RequestRuntimeDependencies = {
  beginReasoning: () => void;
  finishReasoning: () => void;
  setCoreState: (state: OperatorCoreState) => void;
  setLifecycleSummary: (summary: string) => void;
};

export function beginOperatorRequestRuntime({ beginReasoning, setCoreState, setLifecycleSummary }: RequestRuntimeDependencies) {
  setCoreState("listening");
  setLifecycleSummary("GOAL RECEIVED — PREPARING DAVID AI RUN");
  beginReasoning();
}

export function finishOperatorRequestRuntime({ finishReasoning }: RequestRuntimeDependencies) {
  finishReasoning();
}
