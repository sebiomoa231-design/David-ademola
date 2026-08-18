# Recovered David AI Reference Decisions

## Source hierarchy

The recovered master specification is the governing product blueprint. The integrated build prompt supplies the implementation guardrails, while the earlier video task defines the approved visual motion language. The prior web-app task confirms the core navigation and workspace set.

## Product definition

David AI is a persistent personal AI operating system, not a decorative chatbot. Its working loop is **goal → context → plan → approval when required → execute authorized capability → verify → evidence-backed result → controlled memory write-back**. The current build is the first safe slice of that system: authenticated conversation, durable workspace records, LLM reasoning, stored context, visible run status, and explicit failure states.

## Required command-center modules

| Module | Recovered intent | Active implementation direction |
|---|---|---|
| David HUD and Core | A central AI presence that represents actual runtime state, never random decoration. | Retain the approved green/cyan orb; connect it to typed lifecycle events. |
| Reactive Hub State System | Standby, listening, transcribing, thinking, planning, approval required, executing, verifying, speaking, complete, degraded, emergency stop. | Implement the states supported by text chat first; reserve voice-only states until voice is enabled. |
| Conversation Engine | Shared contract for goals, context, responses, plan, tool decisions, and result. | Stream real LLM responses and persist the resulting conversation and run. |
| Persistent workspaces | User-scoped projects, tasks, memory, conversations, and run history. | Use database-backed CRUD and visible ownership-scoped records. |
| Visual Explanation Canvas | Flow, timeline, architecture, chart, storyboard, comparison, and highlight views returned as structured data. | Add a typed visual-response schema after chat/run persistence is stable. |
| Agent Execution Theater | Ordered, evidence-backed plan, approval, tool, provider, verification, rollback, and completion events. | Add durable run events and a real execution rail; label preview events plainly. |
| Governance layer | Permission matrix, approvals, audit, redaction, stop, and rollback controls. | Keep all external actions behind server-side approval and start with no autonomous external actions. |

## Visual language

The user approved the **David AI Reactive Hub State System**: a dark navy command center with teal phosphor lines, cyan-green orb, concentric rings, restrained particles, technical grids, compact monospace telemetry, and a distinct amber degraded state. The motion relationship is also approved: slow breathing on standby; amplitude/ripple response while listening; accelerated segmented rings while thinking; connected planning geometry; active trajectories during execution; scan/check behavior while verifying; a brief emerald completion pulse; and an amber, explanatory degraded state.

## Engineering and safety decisions

1. Preserve working surfaces and extend with typed adapters rather than rewrite the project.
2. Do not claim an action completed, saved, sent, published, or verified without server evidence.
3. Keep provider credentials and external integrations server-side. The model can propose an action but cannot possess unrestricted credentials or raw shell/network access.
4. User data, memory, projects, tasks, and runs remain user-scoped, editable, and auditable.
5. Text is the immediate interaction path. Voice remains planned; microphone UI and voice claims remain disabled until the configured backend capability and safe controls are connected.
6. The legacy Render API remains a secondary adapter because its deployed surface is incomplete. The active project uses the built-in LLM for real conversation now, while retaining a truthful boundary for future provider routing.

## Priority sequence recovered from the handoffs

1. Make the current conversation, memory, project, task, and run data paths genuinely work.
2. Add a typed plan and execution-event model with an approval boundary.
3. Render the event model through the Agent Execution Theater and bind all core states to it.
4. Add structured visual explanations with accessible textual fallbacks.
5. Integrate voice, provider routing, approved connectors, durable background execution, diagnostics, and learning only after their server-side governance contracts exist.

## Reference files recovered

The original materials include the master specification, integrated build prompt, full web build brief, API/type contracts, command-center reference, inspection report, complete build bundles, frontend architecture handoffs, cinematic multimodal source, and frontend prompts/plans bundles. They are preserved as reference material; only compatible, reviewed portions should be merged into this managed project.
