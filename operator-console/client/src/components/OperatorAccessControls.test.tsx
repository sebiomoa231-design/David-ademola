// @vitest-environment jsdom
import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CurrentTaskAccess, MemoryRemoveControl, OperatorActivityAccess, TranscriptClearControl } from "./OperatorAccessControls";

describe("David AI Operator workspace access controls", () => {
  it("opens the local activity ledger and a persisted current task only when one exists", () => {
    const openActivity = vi.fn();
    const openTask = vi.fn();
    render(<><OperatorActivityAccess onOpen={openActivity} /><CurrentTaskAccess taskTitle="Prepare launch outline" onOpen={openTask} /></>);
    fireEvent.click(screen.getByLabelText(/local operator activity ledger/i));
    fireEvent.click(screen.getByLabelText(/current task: Prepare launch outline/i));
    expect(openActivity).toHaveBeenCalledOnce();
    expect(openTask).toHaveBeenCalledOnce();
  });

  it("disables missing task access and requires confirmation before memory removal", () => {
    const onRemove = vi.fn();
    const confirm = vi.spyOn(window, "confirm").mockReturnValueOnce(false).mockReturnValueOnce(true);
    render(<><CurrentTaskAccess onOpen={vi.fn()} /><MemoryRemoveControl onRemove={onRemove} /></>);
    expect(screen.getByLabelText(/no active persisted task/i)).toHaveProperty("disabled", true);
    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    expect(onRemove).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    expect(onRemove).toHaveBeenCalledOnce();
    confirm.mockRestore();
  });

  it("clears the most recent voice transcript through the explicit local control", () => {
    const onClear = vi.fn();
    render(<TranscriptClearControl onClear={onClear} />);
    fireEvent.click(screen.getByLabelText(/clear most recent voice transcript/i));
    expect(onClear).toHaveBeenCalledOnce();
  });
});
