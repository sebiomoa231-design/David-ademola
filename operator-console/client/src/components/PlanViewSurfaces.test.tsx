// @vitest-environment jsdom
import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ConversationPlanSurface, ExecutionPlanSurface, RunPlanSurface } from "./PlanViewSurfaces";

const plan = { steps: ["Clarify the outcome", "Prepare the response"] };

afterEach(cleanup);

describe("David AI Operator persisted-plan view surfaces", () => {
  it("shows an active persisted plan in the Conversation plan panel", () => {
    render(<ConversationPlanSurface plan={plan} />);
    expect(screen.getByLabelText("Active David AI Operator response plan")).toBeTruthy();
    expect(screen.getByText("Clarify the outcome")).toBeTruthy();
  });

  it("shows the plan in run history and Operator Execution Theater surfaces", () => {
    render(<><RunPlanSurface plan={plan} /><ExecutionPlanSurface plan={plan} /></>);
    expect(screen.getByLabelText("David AI Operator response plan")).toBeTruthy();
    expect(screen.getByLabelText("Structured David AI Operator execution plan")).toBeTruthy();
    expect(screen.getAllByText("Prepare the response")).toHaveLength(2);
  });
});
