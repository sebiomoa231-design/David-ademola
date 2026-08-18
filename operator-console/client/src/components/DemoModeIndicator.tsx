import React from "react";

export function DemoModeIndicator({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  return <span className="demo-mode-indicator" role="status" aria-label="Demonstration mode enabled; live capability status remains evidence-based">DEMO / PRESENTATION ONLY</span>;
}
