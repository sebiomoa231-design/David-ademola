// @vitest-environment jsdom
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DemoModeIndicator } from "./DemoModeIndicator";

describe("David AI Operator demo-mode indicator", () => {
  it("labels the shell when presentation mode is enabled without modifying surrounding live status", () => {
    render(<div><DemoModeIndicator enabled /><span data-testid="live-status">EXTERNAL SERVICE CONNECTED</span></div>);
    expect(screen.getByRole("status", { name: /demonstration mode enabled/i }).textContent).toBe("DEMO / PRESENTATION ONLY");
    expect(screen.getByTestId("live-status").textContent).toBe("EXTERNAL SERVICE CONNECTED");
  });

  it("does not render a label when presentation mode is off", () => {
    const { container } = render(<DemoModeIndicator enabled={false} />);
    expect(container.innerHTML).toBe("");
  });
});
