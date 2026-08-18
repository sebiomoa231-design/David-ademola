// @vitest-environment jsdom
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlanEvidenceList } from "./PlanEvidenceList";

describe("David AI Operator plan evidence", () => {
  it("renders every persisted plan step with an explicit evidence label", () => {
    render(<PlanEvidenceList label="Structured operator response plan" steps={["Clarify the outcome", "Prepare the response"]} />);
    expect(screen.getByLabelText("Structured operator response plan")).toBeTruthy();
    expect(screen.getByText("Clarify the outcome")).toBeTruthy();
    expect(screen.getByText("Prepare the response")).toBeTruthy();
  });

  it("does not render an empty plan artifact", () => {
    const { container } = render(<PlanEvidenceList label="Empty plan" steps={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
