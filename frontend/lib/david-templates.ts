export type DavidTemplate = {
  id: string;
  name: string;
  category: "Operations" | "Creative" | "Knowledge" | "Growth";
  description: string;
  objective: string;
  steps: string[];
  approvalRequired: boolean;
};

export const davidTemplates: DavidTemplate[] = [
  {
    id: "weekly-business-review",
    name: "Weekly business review",
    category: "Operations",
    description: "Review current projects, tasks, risks, and next actions in one governed run.",
    objective: "Review my active projects and tasks, identify risks, and recommend the next three actions for this week.",
    steps: ["Read live workspace", "Analyze progress", "Identify risks", "Return next actions"],
    approvalRequired: false,
  },
  {
    id: "launch-campaign",
    name: "Product launch system",
    category: "Growth",
    description: "Turn a launch objective into a structured plan with visible approval boundaries.",
    objective: "Create a governed product launch plan covering positioning, campaign assets, channels, owners, and approval points.",
    steps: ["Capture objective", "Sequence work", "Assign capabilities", "Request approvals"],
    approvalRequired: true,
  },
  {
    id: "knowledge-brief",
    name: "Knowledge brief",
    category: "Knowledge",
    description: "Search connected workspace knowledge and return a traceable decision brief.",
    objective: "Search my connected knowledge for the most relevant context, summarize the findings, and cite the source records used.",
    steps: ["Search memory", "Rank context", "Synthesize findings", "Show evidence"],
    approvalRequired: false,
  },
  {
    id: "website-brief",
    name: "Website build brief",
    category: "Creative",
    description: "Prepare a real website-generation brief before any external artifact or publish action.",
    objective: "Prepare a conversion-focused website build brief with structure, copy direction, responsive requirements, and a review gate before publishing.",
    steps: ["Define audience", "Plan structure", "Route website capability", "Hold for review"],
    approvalRequired: true,
  },
  {
    id: "content-pipeline",
    name: "Content pipeline",
    category: "Creative",
    description: "Plan a repeatable content workflow while keeping generation and publishing behind verification.",
    objective: "Plan a content pipeline for the next month with topics, formats, owners, provider requirements, and approval checkpoints.",
    steps: ["Set content goal", "Build calendar", "Route production", "Validate outputs"],
    approvalRequired: true,
  },
  {
    id: "customer-signal-review",
    name: "Customer signal review",
    category: "Growth",
    description: "Turn customer context into an evidence-based set of product or service actions.",
    objective: "Review available customer context and return the strongest recurring signals, opportunities, and recommended follow-up actions.",
    steps: ["Read available context", "Cluster signals", "Assess opportunities", "Return recommendations"],
    approvalRequired: false,
  },
];
