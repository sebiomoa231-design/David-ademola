import { describe, expect, it } from "vitest";
import { DAVID_SYSTEM_PROMPT, composeDavidMessages, parsePlanArtifact, parseWorkspaceDecision } from "./davidAgent";

describe("David AI message composition", () => {
  it("keeps the supplied David AI personality and includes approved memory context", () => {
    const messages = composeDavidMessages({ history: [{ role: "user", content: "Plan my launch." }], memories: [{ kind: "preference", content: "Keep updates concise." }] });
    expect(DAVID_SYSTEM_PROMPT).toContain("calm, professional British tone");
    expect(messages[1]?.content).toContain("Keep updates concise.");
    expect(messages.at(-1)?.content).toBe("Plan my launch.");
  });
});

describe("David AI workspace decisions", () => {
  it("accepts only the supported, server-validated internal action shape", () => {
    expect(parseWorkspaceDecision(JSON.stringify({ intent: "create_task", memoryContent: null, projectName: null, projectDescription: null, taskTitle: "Send launch outline", taskDescription: "Prepare a short version", taskPriority: "high" }))).toMatchObject({ intent: "create_task", taskTitle: "Send launch outline", taskPriority: "high" });
    expect(parseWorkspaceDecision("not-json").intent).toBe("none");
  });
});

describe("David AI response plans", () => {
  it("keeps a bounded, readable plan artifact and falls back safely on malformed data", () => {
    expect(parsePlanArtifact(JSON.stringify({ isMultiStep: true, steps: ["Clarify the objective", "Draft the response"] }))).toEqual({ isMultiStep: true, steps: ["Clarify the objective", "Draft the response"] });
    expect(parsePlanArtifact("bad-json").steps).toHaveLength(1);
  });
});
