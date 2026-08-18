import React from "react";
import { DemoModeIndicator } from "./DemoModeIndicator";

export function OperatorShellStatus({ demoMode, externalService }: { demoMode: boolean; externalService: "CONNECTED" | "LIMITED" | "CHECKING" }) {
  return <div className="operator-shell-status"><DemoModeIndicator enabled={demoMode} /><span className="shell-external-status" aria-label={`External service ${externalService.toLowerCase()}`}>EXT / {externalService}</span></div>;
}
