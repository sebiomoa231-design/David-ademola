import { describe, expect, it } from "vitest";

describe("David AI Operator project identity", () => {
  it("uses the configured public application title", () => {
    expect(process.env.VITE_APP_TITLE).toBe("David AI Operator");
  });
});
