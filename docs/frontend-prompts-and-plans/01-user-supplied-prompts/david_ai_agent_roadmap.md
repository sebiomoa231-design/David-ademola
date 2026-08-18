# David AI Multi-Task Agent Roadmap

## Goal

Transform **David AI** from a chat interface that returns one response at a time into a dependable personal AI agent that can accept several goals, create step-by-step execution plans, carry out approved work through real capabilities, retain useful context, and show the user exactly what is happening at every stage.

The first implementation should be a **safe, durable agent workspace** inside the existing David AI application. It will not pretend to have completed an action. Every task, tool call, artifact, approval, pause, retry, and failure will be saved and visible to the user.

> **Core principle:** David AI may plan and work autonomously within an approved boundary, but it must never send, publish, delete, buy, share sensitive data, or make an external commitment without the user’s explicit approval at the moment it matters.

## Current Baseline and Gap

David AI already has the correct foundations: authenticated user accounts, a per-user database, projects, tasks, memories, chat history, content generation, a website workspace, a multi-provider AI router, encrypted provider settings, storage, and scheduled one-step automations. The current automation runner performs one prompt and saves one result; chat similarly produces one response at a time. There is not yet a durable **agent run**, execution plan, dependency graph, approval record, tool invocation history, or multi-run scheduler.

| Existing capability | How the agent will reuse it | Missing layer to add |
|---|---|---|
| Chat and multi-provider AI routing | Understanding goals, creating structured plans, writing task outputs | Planning and step orchestration |
| Projects, tasks, and memories | Context, task ownership, long-term preferences | Agent-specific run and artifact records |
| Website, content, media, and connector modules | First real actions David AI can take | A controlled tool registry and permissions |
| Current scheduled automations | Future triggers for agent runs | Durable queueing, retries, approvals, and progress |
| Encrypted provider settings and OAuth | Secure user-scoped access | Per-tool authorization and audit records |

## Architectural Options

The plan retains two viable delivery paths. The first path is recommended for the first release because it builds on the current application, provides visible control, and does not require moving David AI to a separate platform.

| Approach | What the user experiences | Trade-offs | Setup complexity |
|---|---|---|---|
| **Durable agent workspace inside David AI** | Submit several tasks; each shows a plan, progress, approvals, outputs, and retry controls. Work progresses through a database-backed queue and scheduled worker. | Best for controlled personal productivity and existing David AI features. Long-running or very high-volume workloads will be intentionally bounded. | Moderate; uses the present app, database, authentication, and provider router. |
| **Always-on orchestration service** | Faster near-real-time task dispatch and persistent live execution for more concurrent work. | Requires a continuously running service and ongoing operational oversight; should only be selected if the first approach cannot meet actual latency or scale requirements. | Higher. |
| **External specialist execution service** | David AI can hand exceptional workloads to a separate execution environment. | More integration, credentials, and audit surface. It should be introduced only for a specific capability that the main app cannot safely or reliably provide. | Highest. |

The initial build should use the **durable agent workspace**. It will support multiple active jobs through controlled concurrency, while preserving complete state in the database so a restart never loses a task or repeats an external action.

## Proposed Agent Model

Each user request becomes an **Agent Run**. An Agent Run is a durable, observable work item rather than a chat reply. David AI first creates a structured execution plan, then processes only the next eligible step. Independent runs can progress concurrently up to a defined per-user and global limit; dependent steps within one run remain ordered.

| Run state | Meaning | User control |
|---|---|---|
| Draft | Goal captured but not started | Edit, discard, or start |
| Planning | David AI is preparing a structured task plan | Cancel |
| Awaiting approval | A consequential action needs permission | Approve, reject, or revise scope |
| Queued | Ready to run, waiting for available capacity | Reprioritize or cancel |
| Running | A bounded step is currently executing | Pause or cancel after the active safe boundary |
| Blocked | Missing information, authorization, connector, or prerequisite | Provide input or resolve the block |
| Completed / Failed / Cancelled | Terminal outcome with history and artifacts retained | Retry failed safe steps or archive |

The executor will use a database lease for each active run, idempotency keys for every external-capable action, bounded retries with clear error classification, and an append-only event log. These controls prevent two workers from doing the same job or an interrupted process from silently losing progress.

## Tool Registry and Safety Boundary

David AI will not receive unrestricted access to arbitrary code, browsers, or external accounts. Instead, the system will expose a registry of small, typed tools. Each tool declares its inputs, outputs, required permission level, retry policy, idempotency behavior, and whether it can create an external side effect.

The first release will prioritize tools that already have real backends in David AI: retrieving project/task/memory context, creating or updating project tasks, drafting content, generating a website workspace, modifying an existing website workspace, generating supported media projects, and saving user-approved memories. Every tool call will be validated on the server and logged with redacted inputs where necessary.

| Permission class | Examples | Default policy |
|---|---|---|
| Read-only | Read a project, inspect memories, check connector status | May run automatically within the task’s stated scope |
| Internal change | Create a task, save a draft, update a David AI workspace | Show the planned change; allow automatic execution only when the user started that task and the action stays within the stated scope |
| External communication or publication | Send an email, publish a website, post content, share a file | Requires a specific approval immediately before execution |
| Destructive, financial, or sensitive-data action | Delete data, purchase, transfer funds, alter access, export secrets | Always requires explicit confirmation; never infer consent from an earlier unrelated request |

Provider keys will remain encrypted and server-side. The planner will never receive raw secrets, and tool outputs will be filtered before becoming conversational context or permanent memories.

## Data Model Additions

The agent layer will add new user-scoped tables, each tied to the existing user, project, task, and storage systems where applicable.

| Entity | Purpose | Important fields |
|---|---|---|
| `agent_runs` | One durable goal submitted to David AI | User/project/task links, objective, priority, status, context snapshot, lease, timestamps, outcome summary |
| `agent_steps` | Planned and executed units of work | Run link, order/dependencies, step type, tool identifier, validated inputs, output summary, retry count, status |
| `agent_tool_executions` | Immutable audit log of each actual tool attempt | Step link, redacted request/response, idempotency key, duration, error type, timestamps |
| `agent_approvals` | Evidence of user decisions | Run/step link, requested action and scope, decision, approver, expiry, timestamp |
| `agent_artifacts` | User-visible outputs | Run/step link, type, title, storage reference or workspace reference, preview metadata |
| `agent_events` | Timeline for the live activity feed | Run link, event type, human-readable detail, structured metadata, timestamp |
| `agent_policies` | User-controlled limits | Enabled tools, concurrency limit, default approval preferences, retention choices |

Existing `projects`, `tasks`, `memories`, `contentItems`, `mediaProjects`, `automations`, and website workspaces will stay in place. The agent system will link to them instead of duplicating their data.

## Step-by-Step Implementation Plan

### Phase 1 — Define the first safe agent scope

Create the product rules before adding execution code. The first supported task types will be: research-and-draft work, content creation, website-workspace creation or revision, project/task organization, and memory-assisted planning. External messaging, publishing, financial actions, and destructive actions will be deliberately out of automatic scope.

Define success criteria, a default concurrency cap, maximum steps per run, time and retry limits, artifact retention, and approval language. Add a threat model covering prompt injection from uploaded files, externally sourced content, and tool-output text.

### Phase 2 — Add durable agent-run persistence

Extend the Drizzle schema and database helpers with the agent tables above. Generate and apply a migration, then create user-scoped helpers that enforce ownership on every read, update, cancel, retry, and approval operation.

Implement strict state-transition rules rather than allowing arbitrary status updates. For example, only a valid approval can move an external-action step from `awaiting_approval` to `queued`, and a cancelled run can never be claimed by a worker.

### Phase 3 — Build the planner, tool registry, and executor

Create an `agent` server module with three separate responsibilities: a planner that returns schema-validated JSON, a registry that exposes only approved tools, and an executor that validates and performs one step at a time. The existing resilient provider router will be reused for planning and reasoning, with provider failures recorded as recoverable run events.

Implement real adapters for the first safe tools rather than mock completions. Add input/output schemas, redaction rules, idempotency keys, and deterministic error types for every adapter. The model can suggest a tool call, but server policy will make the final allow/deny decision.

### Phase 4 — Add controlled multi-task dispatch

Create a database-backed job dispatcher that claims queued runs using leases, advances bounded work units, and requeues safe retries. Use the managed application’s background scheduling capability to invoke the dispatcher; do not create a separate always-on system unless measured task volume or latency makes it necessary.

Allow several independent Agent Runs to proceed concurrently within a conservative user limit. Tasks from the same run will respect their dependency graph. The scheduler will favor user-selected priority, prevent starvation, pause when approval is required, and recover safely from restarts or provider cooldowns.

### Phase 5 — Build the Agent Runs workspace

Add an **Agent Runs** section to David AI’s command-center navigation. The workspace will contain a goal composer, priority selector, project link, live run list, status filters, capacity indicator, approval inbox, and clear pause/cancel/retry controls.

Each run detail page will show the goal, proposed plan, current step, real-time event timeline, tool calls, errors, artifacts, and approval history. Chat will gain a deliberate hand-off action—such as **“Turn this into an agent task”**—so conversational work does not become autonomous work without the user choosing it.

### Phase 6 — Add memory and approval experiences

At run creation, save a bounded context snapshot drawn from only relevant user memories, project data, and explicitly attached artifacts. At completion, David AI will propose any lasting memory as a reviewable suggestion rather than silently storing every result.

Build focused approval cards that state what David AI will do, where it will act, what information will be sent, and the expected result. Support one-time approval, scoped approval for the current run, rejection with feedback, and expiry of unused approvals.

### Phase 7 — Extend to scheduled and connected work

After the safe manual-run experience is reliable, let existing automations create Agent Runs instead of executing a single prompt. Begin with internal, read-only, or draft-producing scheduled tasks. Each automation will inherit a fixed policy and still pause for approval before consequential external actions.

New connected capabilities—such as email, calendar, cloud storage, or publishing platforms—will be added one at a time only after their user authorization, server-side permission model, and audit records are complete. Webhook-based triggers will be evaluated against the chosen service’s current documentation before implementation; otherwise, low-frequency checks will be scheduled appropriately.

### Phase 8 — Test, observe, and release progressively

Add unit tests for state transitions, tool validation, permission checks, approval expiry, idempotency, retry classification, lease recovery, and per-user isolation. Add integration tests that run two or more independent jobs, enforce step dependencies, simulate provider failure, verify that an unapproved external tool cannot execute, and confirm that real artifacts are persisted.

Complete browser tests for the Agent Runs workspace, mobile layouts, approval flow, cancellation, recovery, and chat-to-agent hand-off. Start with a private preview and the safe tool set. Expand the capability set only after observing successful completion, clear audit history, and correct human-approval behavior.

## First Release: Concrete User Flows

The initial agent release will support several simultaneous, visible workflows such as: “Research three competitors and prepare a content brief,” “Create a website workspace from this product idea,” “Turn these chat notes into project tasks and a priority plan,” and “Create a content draft plus supporting visual brief.” Each workflow produces saved artifacts in David AI; none silently sends or publishes anything outside David AI.

The user will be able to start another task while a first task is working, see which task is waiting or running, pause one task to free capacity, and review every completed deliverable. If David AI lacks a required connection or permission, it will mark the exact step as blocked and explain what is needed rather than inventing success.

## Assumptions and Open Decisions

This roadmap assumes David AI remains a user-authenticated web application with the current database, encrypted provider settings, storage, provider router, and scheduled automation capability. It also assumes the first priority is reliable personal productivity rather than unrestricted autonomous browsing or financial execution.

The safe default is that **all external communications, publishing, purchases, transfers, deletions, and access changes require immediate approval**. The first release will use a conservative concurrency limit, then tune it using observed provider rate limits, response latency, and successful-run data. A continuously running orchestration service will not be introduced unless the database-backed dispatcher proves insufficient for the real workload.

## Acceptance Criteria

The agent capability will be ready for review when a signed-in user can create at least three independent Agent Runs; David AI can plan, execute, pause, resume, cancel, and retry supported runs without losing state; safe tools perform real work and return stored artifacts; approval-required tools cannot run before approval; every action is visible in an audit timeline; a restart does not duplicate tool work; and all existing David AI capabilities, including provider failover and Ryan voice output, continue to pass their regression tests.

## Recommended Next Action

Approve this roadmap, then begin with **Phase 1 and Phase 2 only**: lock the safety policy and add the durable Agent Run data model. That creates the reliable foundation needed before David AI is allowed to execute any multi-step work.
