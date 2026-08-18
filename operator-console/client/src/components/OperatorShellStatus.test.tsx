// @vitest-environment jsdom
import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { OperatorShellStatus } from "./OperatorShellStatus";

afterEach(cleanup);

describe("David AI Operator shell status", () => {
  it("shows the persistent demo label while preserving the status-derived external-service signal", () => {
    render(<OperatorShellStatus demoMode externalService="LIMITED" />);
    expect(screen.getByRole("status", { name: /demonstration mode enabled/i }).textContent).toBe("DEMO / PRESENTATION ONLY");
    expect(screen.getByLabelText("External service limited").textContent).toBe("EXT / LIMITED");
  });

  it("keeps the external-service signal available with no demo label when presentation mode is off", () => {
    render(<OperatorShellStatus demoMode={false} externalService="CONNECTED" />);
    expect(screen.queryByRole("status", { name: /demonstration mode enabled/i })).toBeNull();
    expect(screen.getByLabelText("External service connected").textContent).toBe("EXT / CONNECTED");
  });
});
