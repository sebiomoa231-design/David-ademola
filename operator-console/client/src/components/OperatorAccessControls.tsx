import React from "react";
import { Bell, Target } from "lucide-react";

export function OperatorActivityAccess({ onOpen }: { onOpen: () => void }) {
  return <button className="icon-button" title="Open local operator activity ledger" aria-label="Open local operator activity ledger; external notifications are unavailable" onClick={onOpen}><Bell size={17} /></button>;
}

export function CurrentTaskAccess({ taskTitle, onOpen }: { taskTitle?: string; onOpen: () => void }) {
  return <button className="icon-button" title={taskTitle ? `Open current task: ${taskTitle}` : "No active persisted task"} aria-label={taskTitle ? `Open current task: ${taskTitle}` : "No active persisted task"} disabled={!taskTitle} onClick={onOpen}><Target size={17} /></button>;
}

export function MemoryRemoveControl({ onRemove }: { onRemove: () => void }) {
  return <button className="row-action" onClick={() => { if (window.confirm("Remove this saved memory permanently? This action cannot be undone from David AI Operator.")) onRemove(); }}>Remove</button>;
}

export function TranscriptClearControl({ onClear }: { onClear: () => void }) {
  return <button className="text-action" aria-label="Clear most recent voice transcript" onClick={onClear}>Clear transcript</button>;
}
