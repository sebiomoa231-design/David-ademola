import { describe, expect, it } from "vitest";

describe("David AI Operator Render connection", () => {
  it("reaches the configured backend voice-status endpoint", async () => {
    const baseUrl = process.env.DAVID_API_BASE_URL;
    expect(baseUrl).toMatch(/^https:\/\//);

    const response = await fetch(`${baseUrl}/api/voice/status`);
    expect(response.ok).toBe(true);

    const status = await response.json() as { tts_configured?: boolean; stt_configured?: boolean; tts_provider?: string; stt_provider?: string };
    expect(status.tts_configured).toBe(true);
    expect(status.stt_configured).toBe(true);
    expect(status.tts_provider).toBeTruthy();
    expect(status.stt_provider).toBeTruthy();
  }, 30_000);
});
