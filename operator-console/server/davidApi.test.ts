import { describe, expect, it } from "vitest";
import { unavailableResult } from "./davidApi";

describe("David upstream state handling", () => {
  it("keeps an unimplemented upstream route visibly unavailable", () => {
    const result = unavailableResult("/api/chat", 404);
    expect(result).toMatchObject({
      state: "unavailable",
      status: 404,
      data: null,
    });
    expect(result.message).toContain("does not currently expose /api/chat");
  });

  it("marks server-side upstream failures as degraded", () => {
    const result = unavailableResult("/api/intelligence/runs", 503);
    expect(result.state).toBe("degraded");
    expect(result.status).toBe(503);
  });
});
