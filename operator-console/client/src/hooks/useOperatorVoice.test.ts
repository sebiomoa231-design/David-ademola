import { describe, expect, it } from "vitest";
import { beginReasoningVoiceState, finishReasoningVoiceState, isProcessingVoiceState, OPERATOR_VOICE_STATES } from "./useOperatorVoice";

describe("David AI Operator voice runtime states", () => {
  it("includes the explicit reasoning state and classifies it as processing", () => {
    expect(OPERATOR_VOICE_STATES).toContain("reasoning");
    expect(isProcessingVoiceState("reasoning")).toBe(true);
    expect(isProcessingVoiceState("speaking")).toBe(false);
  });

  it("enters reasoning for a request and returns to standby when processing finishes", () => {
    expect(beginReasoningVoiceState("idle")).toBe("reasoning");
    expect(finishReasoningVoiceState("reasoning")).toBe("idle");
    expect(beginReasoningVoiceState("speaking")).toBe("speaking");
    expect(finishReasoningVoiceState("degraded")).toBe("degraded");
  });
});
