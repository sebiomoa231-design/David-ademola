import React from "react";
import { OperatorShellStatus } from "./OperatorShellStatus";

type ExternalHealth = { state?: string | null } | undefined;

export function resolveHomeExternalServiceState(health: ExternalHealth): "CONNECTED" | "LIMITED" | "CHECKING" {
  if (health?.state === "ready") return "CONNECTED";
  if (health?.state === "degraded") return "LIMITED";
  return "CHECKING";
}

export function HomeShellStatus({ demoMode, health }: { demoMode: boolean; health: ExternalHealth }) {
  return <OperatorShellStatus demoMode={demoMode} externalService={resolveHomeExternalServiceState(health)} />;
}
