import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  createConversation: vi.fn(),
  createMessage: vi.fn(),
  createRun: vi.fn(),
  createRunEvent: vi.fn(),
  updateRun: vi.fn(),
  listMessages: vi.fn(),
  listMemoriesByIds: vi.fn(),
  getConversation: vi.fn(),
  createTask: vi.fn(),
  invoke: vi.fn(),
  listModels: vi.fn(),
  stream: vi.fn(),
}));

vi.mock("./db", () => ({
  createDavidConversation: mocks.createConversation,
  createDavidMessage: mocks.createMessage,
  createDavidRun: mocks.createRun,
  createDavidRunEvent: mocks.createRunEvent,
  updateDavidRun: mocks.updateRun,
  listDavidMessages: mocks.listMessages,
  listDavidMemoriesByIds: mocks.listMemoriesByIds,
  getDavidConversation: mocks.getConversation,
  createDavidMemory: vi.fn(),
  createDavidProject: vi.fn(),
  createDavidTask: mocks.createTask,
}));

vi.mock("./_core/llm", () => ({
  invokeLLM: mocks.invoke,
  listLLMModels: mocks.listModels,
  streamLLM: mocks.stream,
}));

import { respondAsDavid, streamAsDavid } from "./davidAgent";

describe("David AI persisted chat run", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getConversation.mockResolvedValue(undefined);
    mocks.listMessages.mockResolvedValue([{ role: "user", content: "Plan the launch" }]);
    mocks.listMemoriesByIds.mockResolvedValue([{ kind: "preference", content: "Use concise summaries" }]);
    mocks.listModels.mockResolvedValue({ data: [{ id: "gpt-5-mini" }] });
    mocks.createConversation.mockResolvedValue(undefined);
    mocks.createMessage.mockResolvedValue(undefined);
    mocks.createRun.mockResolvedValue(undefined);
    mocks.createRunEvent.mockResolvedValue(undefined);
    mocks.updateRun.mockResolvedValue(undefined);
    mocks.createTask.mockResolvedValue(undefined);
    mocks.invoke
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ isMultiStep: true, steps: ["Clarify the goal", "Draft the launch plan"] }) } }] })
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ intent: "none", memoryContent: null, projectName: null, projectDescription: null, taskTitle: null, taskDescription: null, taskPriority: null }) } }] })
      .mockResolvedValueOnce({ choices: [{ message: { content: "Here is a concise launch plan." } }] });
    mocks.stream.mockImplementation(async function* () { yield "Here is "; yield "the streamed plan."; });
  });

  it("stores a structured plan and uses only the selected memory scope", async () => {
    const result = await respondAsDavid({ userId: 7, message: "Plan the launch", memoryIds: ["memory-1"] });

    expect(result.content).toContain("concise launch plan");
    expect(mocks.listMemoriesByIds).toHaveBeenCalledWith(7, ["memory-1"]);
    expect(mocks.updateRun).toHaveBeenCalledWith(7, expect.any(String), expect.objectContaining({
      planData: JSON.stringify({ isMultiStep: true, steps: ["Clarify the goal", "Draft the launch plan"] }),
    }));
    expect(mocks.invoke.mock.calls[2]?.[0]?.messages).toEqual(expect.arrayContaining([
      expect.objectContaining({ content: expect.stringContaining("Use concise summaries") }),
    ]));
    expect(mocks.createMessage).toHaveBeenCalledTimes(2);
  });

  it("continues a persisted conversation without creating a duplicate session", async () => {
    mocks.getConversation.mockResolvedValue({ id: "conversation-1", userId: 7, title: "Launch planning" });

    const result = await respondAsDavid({ userId: 7, conversationId: "conversation-1", message: "Continue the launch plan", memoryIds: [] });

    expect(result.conversationId).toBe("conversation-1");
    expect(mocks.getConversation).toHaveBeenCalledWith(7, "conversation-1");
    expect(mocks.createConversation).not.toHaveBeenCalled();
    expect(mocks.listMessages).toHaveBeenCalledWith(7, "conversation-1");
  });

  it("persists a validated direct task request and reports the confirmed workspace action", async () => {
    mocks.invoke.mockReset();
    mocks.invoke
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ isMultiStep: true, steps: ["Capture the task", "Confirm the saved record"] }) } }] })
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ intent: "create_task", memoryContent: null, projectName: null, projectDescription: null, taskTitle: "Send launch outline", taskDescription: "Prepare the concise version", taskPriority: "high" }) } }] })
      .mockResolvedValueOnce({ choices: [{ message: { content: "The task has been prepared for review." } }] });

    const result = await respondAsDavid({ userId: 7, message: "Create a task to send the launch outline", memoryIds: [] });

    expect(mocks.createTask).toHaveBeenCalledWith(expect.objectContaining({ userId: 7, title: "Send launch outline", description: "Prepare the concise version", status: "todo", priority: "high" }));
    expect(result.content).toContain("Server-confirmed workspace action: created task");
  });

  it("streams authoritative lifecycle events and response tokens for the command center", async () => {
    mocks.invoke
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ isMultiStep: false, steps: ["Answer precisely"] }) } }] })
      .mockResolvedValueOnce({ choices: [{ message: { content: JSON.stringify({ intent: "none", memoryContent: null, projectName: null, projectDescription: null, taskTitle: null, taskDescription: null, taskPriority: null }) } }] });
    const eventTypes: string[] = [];
    const tokens: string[] = [];

    const result = await streamAsDavid({ userId: 7, message: "What is next?", onToken: (token) => tokens.push(token), onEvent: (event) => eventTypes.push(event.type) });

    expect(result.content).toContain("streamed plan");
    expect(tokens.join("")).toContain("streamed plan");
    expect(eventTypes).toEqual(expect.arrayContaining(["goal_received", "plan_created", "model_selected", "response_streaming", "verification_started", "verification_passed"]));
    expect(mocks.createRunEvent.mock.calls.map(([event]) => event.type)).toEqual(expect.arrayContaining(["goal_received", "plan_created", "model_selected", "response_streaming", "verification_started", "verification_passed"]));
  });
});
