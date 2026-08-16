import { afterEach, describe, expect, it, vi } from "vitest";
import { api, toAudioUrl } from "./api";

describe("Command Center API contracts", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("formats a real returned audio payload without substituting a browser voice", () => {
    expect(toAudioUrl("YXVkaW8=", "mp3")).toBe("data:audio/mp3;base64,YXVkaW8=");
  });

  it("sends Voice workspace requests to the existing synthesis endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ audio_available: false, provider: "configured", text_fallback: "Audio unavailable" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await api.synthesize("David, report status");

    expect(response.audio_available).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/voice/synthesize", expect.objectContaining({ method: "POST", body: JSON.stringify({ text: "David, report status", language_mode: "AUTO" }) }));
  });

  it("loads Automation workspace records only from the registered backend workflow contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ workflows: [{ id: "briefing", name: "Daily briefing" }] }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await api.intelligence.workflows();

    expect(response).toEqual({ workflows: [{ id: "briefing", name: "Daily briefing" }] });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/intelligence/workflows", expect.objectContaining({ cache: "no-store" }));
  });

  it("surfaces backend failures instead of inventing a content planning result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("Content planner unavailable", { status: 503, statusText: "Unavailable" })));

    await expect(api.planCreate("Create a launch brief")).rejects.toThrow("Content planner unavailable");
  });
});
