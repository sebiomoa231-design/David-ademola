import { describe, expect, it, vi } from "vitest";
import { runOperatorStream } from "./operatorStreamController";

function sseResponse(events: string[]) {
  const encoder = new TextEncoder();
  return new Response(new ReadableStream({ start(controller) { events.forEach((event) => controller.enqueue(encoder.encode(event))); controller.close(); } }), { status: 200 });
}

function dependencies() {
  return { beginReasoning: vi.fn(), finishReasoning: vi.fn(), setCoreState: vi.fn(), setLifecycleSummary: vi.fn(), onToken: vi.fn(), onRunEvent: vi.fn(), onComplete: vi.fn() };
}

describe("David AI Operator live request stream", () => {
  it("enters reasoning, applies streamed hub evidence, and exits reasoning on completion", async () => {
    const callbacks = dependencies();
    const fetchImpl = vi.fn().mockResolvedValue(sseResponse([
      "event: run_event\ndata: {\"state\":\"thinking\",\"summary\":\"Model selected\"}\n\n",
      "event: token\ndata: {\"token\":\"Hello\"}\n\n",
      "event: complete\ndata: {\"conversationId\":\"c-1\"}\n\n",
    ]));

    await runOperatorStream({ ...callbacks, message: "Hello", memoryIds: [], fetchImpl });

    expect(callbacks.beginReasoning).toHaveBeenCalledOnce();
    expect(callbacks.setCoreState).toHaveBeenCalledWith("listening");
    expect(callbacks.setLifecycleSummary).toHaveBeenCalledWith("GOAL RECEIVED — PREPARING DAVID AI RUN");
    expect(callbacks.onRunEvent).toHaveBeenCalledWith(expect.objectContaining({ state: "thinking", summary: "Model selected" }));
    expect(callbacks.onToken).toHaveBeenCalledWith("Hello");
    expect(callbacks.onComplete).toHaveBeenCalledWith(expect.objectContaining({ conversationId: "c-1" }));
    expect(callbacks.finishReasoning).toHaveBeenCalledOnce();
  });

  it("exits reasoning and marks the hub degraded when the live stream fails", async () => {
    const callbacks = dependencies();
    const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 503 }));

    await expect(runOperatorStream({ ...callbacks, message: "Hello", memoryIds: [], fetchImpl })).rejects.toThrow("stream could not be opened");

    expect(callbacks.setCoreState).toHaveBeenCalledWith("degraded");
    expect(callbacks.setLifecycleSummary).toHaveBeenCalledWith("RUN DEGRADED — REVIEW THE RESPONSE FOR DETAILS");
    expect(callbacks.finishReasoning).toHaveBeenCalledOnce();
  });
});
