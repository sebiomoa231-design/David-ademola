import React from "react";
import { cn } from "@/lib/utils";

export function PlanEvidenceList({ steps, label, className }: { steps: string[]; label: string; className?: string }) {
  if (!steps.length) return null;
  return <ol className={cn("run-plan-list", className)} aria-label={label}>{steps.map((step, index) => <li key={`${index}-${step}`}>{step}</li>)}</ol>;
}
