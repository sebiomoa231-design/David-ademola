// @vitest-environment jsdom
import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { HomeShellStatus } from "./HomeShellStatus";

afterEach(cleanup);

describe("David AI Operator Home shell status mapping", () => {
  it.each([
    [{ state: "ready" }, "External service connected", "EXT / CONNECTED"],
    [{ state: "degraded" }, "External service limited", "EXT / LIMITED"],
    [undefined, "External service checking", "EXT / CHECKING"],
  ] as const)("maps external health to %s while preserving the persistent demo label", (health, accessibleName, expected) => {
    render(<HomeShellStatus demoMode health={health} />);
    expect(screen.getByRole("status", { name: /demonstration mode enabled/i }).textContent).toBe("DEMO / PRESENTATION ONLY");
    expect(screen.getByLabelText(accessibleName).textContent).toBe(expected);
  });
});
