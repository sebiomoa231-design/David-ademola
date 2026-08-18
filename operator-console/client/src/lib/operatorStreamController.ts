import { beginOperatorRequestRuntime, finishOperatorRequestRuntime, type OperatorCoreState } from "./operatorRequestRuntime";

export type DavidStreamPayload = { token?: string; conversationId?: string; message?: string; state?: OperatorCoreState | "failed"; summary?: string };

type OperatorStreamControllerArgs = {
  message: string;
  conversationId?: string;
  memoryIds: string[];
  token?: string;
  beginReasoning: () => void;
  finishReasoning: () => void;
  setCoreState: (state: OperatorCoreState) => void;
  setLifecycleSummary: (summary: string) => void;
  onToken: (token: string) => void;
  onRunEvent: (payload: DavidStreamPayload) => void;
  onComplete: (payload: DavidStreamPayload) => void;
  fetchImpl?: typeof fetch;
};

export async function runOperatorStream({ message, conversationId, memoryIds, token, beginReasoning, finishReasoning, setCoreState, setLifecycleSummary, onToken, onRunEvent, onComplete, fetchImpl = fetch }: OperatorStreamControllerArgs) {
  beginOperatorRequestRuntime({ beginReasoning, finishReasoning, setCoreState, setLifecycleSummary });
  try {
    const response = await fetchImpl("/api/david/chat-stream", {
      method: "POST",
      credentials: "include",
      headers: { "content-type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify({ message, conversationId, memoryIds }),
    });
    if (!response.ok || !response.body) throw new Error(response.status === 401 ? "Please sign in before starting a David AI Operator conversation." : "The David AI Operator stream could not be opened.");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let finished = false;
    while (!finished) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";
      for (const event of events) {
        const eventName = event.split("\n").find((line) => line.startsWith("event:"))?.slice(6).trim();
        const payloadLine = event.split("\n").find((line) => line.startsWith("data:"));
        if (!payloadLine) continue;
        const payload = JSON.parse(payloadLine.slice(5).trim()) as DavidStreamPayload;
        if (eventName === "token" && payload.token) onToken(payload.token);
        if (eventName === "run_event" && payload.state) onRunEvent(payload);
        if (eventName === "complete") { onComplete(payload); finished = true; }
        if (eventName === "error") throw new Error(payload.message ?? "David AI Operator could not complete this response.");
      }
    }
  } catch (error) {
    setCoreState("degraded");
    setLifecycleSummary("RUN DEGRADED — REVIEW THE RESPONSE FOR DETAILS");
    throw error;
  } finally {
    finishOperatorRequestRuntime({ beginReasoning, finishReasoning, setCoreState, setLifecycleSummary });
  }
}
