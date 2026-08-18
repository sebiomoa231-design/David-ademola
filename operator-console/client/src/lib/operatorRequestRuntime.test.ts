import { describe, expect, it, vi } from "vitest";
import { beginOperatorRequestRuntime, finishOperatorRequestRuntime } from "./operatorRequestRuntime";

describe("David AI Operator request runtime", () => {
  it("enters reasoning with a truthful hub summary when a request begins", () => {
    const beginReasoning = vi.fn();
    const finishReasoning = vi.fn();
    const setCoreState = vi.fn();
    const setLifecycleSummary = vi.fn();

    beginOperatorRequestRuntime({ beginReasoning, finishReasoning, setCoreState, setLifecycleSummary });

    expect(setCoreState).toHaveBeenCalledWith("listening");
    expect(setLifecycleSummary).toHaveBeenCalledWith("GOAL RECEIVED — PREPARING DAVID AI RUN");
    expect(beginReasoning).toHaveBeenCalledOnce();
  });

  it("exits reasoning after the request lifecycle completes or fails", () => {
    const finishReasoning = vi.fn();
    finishOperatorRequestRuntime({ beginReasoning: vi.fn(), finishReasoning, setCoreState: vi.fn(), setLifecycleSummary: vi.fn() });
    expect(finishReasoning).toHaveBeenCalledOnce();
  });
});
