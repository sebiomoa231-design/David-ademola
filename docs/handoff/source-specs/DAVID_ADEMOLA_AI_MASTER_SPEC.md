# David Ademola AI — Master Specification

## A Personal AI Operating System: Unified Blueprint for an Autonomous, Multi-Modal, Self-Evolving Agent

**Document Version:** 2.0 (Unified Master Specification)
**Status:** Definitive Blueprint — supersedes CORE_ARCHITECTURE.md, MASTER_FEATURES.md, and EVOLUTION_ENGINE_SPEC.md
**Prepared by:** Manus AI
**Date:** 18 August 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Complete Feature Specification](#3-complete-feature-specification)
4. [Frontend Specification](#4-frontend-specification)
5. [Voice System Specification](#5-voice-system-specification)
6. [Multi-Agent Orchestration System](#6-multi-agent-orchestration-system)
7. [Integration & Provider Architecture](#7-integration--provider-architecture)
8. [Security & Governance Framework](#8-security--governance-framework)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Implementation Priority & Phases](#10-implementation-priority--phases)

---

## 1. Executive Summary

**David Ademola AI** is a personal AI operating system — not merely a chatbot, but a persistent, autonomous, multi-modal intelligence layer that lives alongside David Ademola as a business owner and operator. It converses naturally (including via a voice-first, JARVIS-style interface), understands goals, plans multi-step work, executes it across a coordinated fleet of specialized sub-agents, interfaces securely with the external world (email, code, video, social media, payments), remembers everything that matters with a ranked and privacy-filtered memory, observes its own performance, and — under strict human governance — evolves its own capabilities over time.

### 1.1 What This Document Is

This master specification unifies and improves upon three prior artifacts — the existing handoff architecture, a 270-feature capability inventory across 20 categories, and the self-evolution engine specification — into a single, definitive blueprint. It consolidates duplication, resolves gaps and contradictions, expands every feature with concrete implementation notes, and adds new cross-cutting sections (frontend, voice, multi-agent orchestration, security governance, and phased implementation) that the source documents implied but never fully specified.

### 1.2 Vision in One Paragraph

David speaks to the system in natural language or voice; the system detects intent, assembles relevant context from a ranked personal memory, delegates work to the appropriate specialist agents, routes each stage of reasoning to the most capable and cost-effective AI provider, executes external actions only across a hard security boundary that the model can never cross unilaterally, queues long-running work through durable background workers, writes verified results back into memory and project workspaces, notifies David through the voice and UI channels he prefers, and continually measures its own health and quality — all rendered through a JARVIS-style holographic interface with a British, deep male voice.

### 1.3 Design Principles

The system is governed by ten non-negotiable design principles that must survive every implementation decision:

| # | Principle | Meaning in Practice |
|---|-----------|---------------------|
| 1 | **Human sovereignty** | David remains the ultimate authority. No component can remove owner permissions, disable audit logs, bypass approval gates, or grant itself elevated privileges. |
| 2 | **Propose, never act unilaterally** | Models propose structured tool requests; the backend validates, authorizes, and executes. The model never holds unrestricted credentials or raw infrastructure access. |
| 3 | **Controlled evolution, not self-modification** | The self-evolution engine operates inside a sandbox, behind approval gates, with rollback always available. High/critical-risk changes require explicit owner approval. |
| 4 | **Memory is a first-class citizen** | Memory retrieval, ranking, privacy filtering, and write-back are pipeline stages with their own validation — memory is written and read through the same gates as any external service. |
| 5 | **Providers are interchangeable capabilities** | No business logic is hardcoded to a single provider. Every AI service is addressed through the capability → registry → routing → fallback abstraction. |
| 6 | **Durable everything** | Long-running work survives restarts through queues, checkpoints, and job state. Nothing of value exists only in ephemeral memory. |
| 7 | **Observability by default** | Every task, agent, tool call, and provider call is traced with correlation IDs. The system can replay its own executions and generate its own diagnostic reports. |
| 8 | **Voice-first, but not voice-only** | Voice is the primary interaction mode, but every voice capability has an equivalent text/WebSocket path, and vice versa. |
| 9 | **Security boundary over convenience** | Approval gates, spending limits, and the sensitive-action matrix may add friction; that friction is deliberate and configurable, never optional. |
| 10 | **Learning under review** | The learning system adapts preferences and routing behaviour, but never performs unrestricted self-modification. All learned artefacts are reviewable, correctable, and reversible. |

### 1.4 System at a Glance

| Dimension | Summary |
|-----------|---------|
| Platform | Personal AI Operating System (multi-modal autonomous agent) |
| Backend | Python / FastAPI, deployed on Render (`david-ademola.onrender.com`) |
| Frontend | JARVIS-style holographic interface (dark, cyan/teal glow, particle and rotating-orb animations, voice-first) |
| Voice | ElevenLabs TTS (British JARVIS-style, Voice ID `5hZv9mAOcmcMt1TxA5Iz`), deep-male, English and Yoruba support goals |
| AI providers | Gemini, Groq, OpenRouter, OpenAI, Claude, Voyage AI, Hugging Face, Cloudflare, Cerebras, SambaNova |
| External services | YouTube, TikTok, Gmail, GitHub, Supabase, Google Maps, OpenWeather, Paystack; creative providers Runway, ElevenLabs, Gemini/Veo |
| Exclusions | **Facebook is explicitly excluded** from all social integrations |
| Scale of capability | 270 features across 20 categories; 15 prioritized as the "genuinely autonomous OS" core |
| Governance | Owner-approval gates for high/critical risk, emergency stop, audit trail for all sensitive actions |

### 1.5 The Fifteen Capabilities That Define the System

The source materials identify fifteen upgrades whose combination converts "David AI has lots of features" into "David AI is genuinely an autonomous AI operating system." They are treated in this specification as the mandatory core of Phase 1 and Phase 2:

1. Autonomous Agent Core
2. Goal → Plan → Execute → Verify loop
3. Advanced Long-Term Memory
4. Multi-Agent Orchestrator
5. Dynamic Tool Selection
6. Self-Correction & Failure Recovery
7. Coding Agent
8. Research Agent
9. Permission & Human Approval Engine
10. Provider Intelligence / Automatic Fallback
11. Persistent Project Workspaces
12. Background & Scheduled Tasks
13. Self-Diagnostics
14. Agent Observability & Tracing
15. Learning From Corrections

---

## 2. System Architecture

### 2.1 Overview

David Ademola AI is a layered, event-driven system built on a Python/FastAPI backend and deployed on Render. The architecture separates five concerns that must never be conflated: **intelligence** (models and routing), **agency** (agents and execution), **persistence** (memory, projects, state), **integration** (tools and external services), and **governance** (security, approvals, audit). Each concern has its own service boundary, its own failure modes, and its own observability surface.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CLIENTS / CHANNELS                             │
│  JARVIS Web UI (holographic) · Voice channel (WebSocket) · REST API      │
└───────────────┬───────────────────────────────┬──────────────────────────┘
                │                               │
┌───────────────▼───────────────────────────────▼──────────────────────────┐
│  ENTRY LAYER                                                             │
│  Gateway (auth, rate limiting, CORS) → Conversation Engine → Channels    │
│  (text / voice / webhook / email)                                        │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  INTELLIGENCE LAYER                                                      │
│  Context Assembler ◄── Memory Context Service ──► Personal Memory Store  │
│  (short-term, session, projects)            (long-term stores + indexes) │
│  Intent Detection → AI Core → Multi-Model Orchestration                  │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  AGENCY LAYER                                                            │
│  Master Orchestrator Agent                                               │
│  ├── Task/Workflow Planner  (plan, subtasks, DAG of steps)               │
│  ├── Sub-Agent Fleet (23 specialist agents, §6)                          │
│  └── Autonomous Execution Loop (plan → execute → verify, checkpoints)    │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  CAPABILITY & EXECUTION LAYER                                            │
│  Capability Router → Model/Provider Router → Tool Router                 │
│  Tool Security Boundary (validate → authorize → execute → verify)        │
│  Long-Running Work: API → Queue → Workers → Checkpoints → Audit          │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  INTEGRATION LAYER                                                       │
│  External Service Manager · Connector registry · OAuth/credential vault  │
│  Providers: Gemini, Groq, OpenRouter, OpenAI, Claude, Voyage AI, HF,     │
│  Cloudflare, Cerebras, SambaNova · Creative: Runway, ElevenLabs, Veo     │
│  Services: YouTube, TikTok, Gmail, GitHub, Supabase, Maps, OpenWeather,  │
│  Paystack                                                                │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  PERSISTENCE & OBSERVABILITY LAYER                                       │
│  Postgres/Supabase (state, projects, audit) · Object storage             │
│  Vector index (embeddings) · Task/job state · Telemetry & tracing        │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│  GOVERNANCE LAYER (cross-cutting)                                        │
│  Permission Engine · Approval Gates · Audit Log · Self-Diagnostics       │
│  Self-Evolution Engine (sandboxed, gated) · Learning System              │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Request Flow (Improved)

The existing handoff flow is retained and refined. Every user request, regardless of channel, traverses the same pipeline, which guarantees that memory, intent, security, and observability are applied uniformly:

```
User (text or voice)
  → Channel Adapter (voice: STT / text: parser)
  → Conversation Engine (session state, follow-ups, entity resolution)
  → Context Assembly (memory retrieval + ranking + privacy filter)
  → Intent Detection & Goal Extraction
  → AI Core (orchestrator model selects strategy)
  → Task/Workflow Planner (decompose into plan graph with dependencies)
  → Capability Router (capability → eligible provider models)
  → Model/Provider Router (health, credentials, capability, cost/latency/quality)
  → Tool Router (dynamic tool selection, chaining, parallel branches)
  → Tool Security Boundary (proposal → schema validation → policy → authorization)
  → Execution (internal tool or External Service via connector; queue for long jobs)
  → Validation & Verification (output checks, schema checks, retries)
  → Result Synthesis
  → Memory Write-Back (validate → secret-filter → classify → dedupe/conflict → persist → index)
  → Response (text, voice, notification, or webhook per channel preference)
```

Key improvements over the handoff flow: a **Channel Adapter** stage is made explicit so voice, webhook, email, and scheduled-trigger requests enter the same pipeline; **Context Assembly** becomes a documented stage with a context-budgeting contract; the **Task/Workflow Planner** emits a directed-acyclic plan graph (not just a linear list), enabling parallel execution where safe; and **Memory Write-Back** is given the same validation gate as any external service, including secret filtering and conflict detection.

### 2.3 Multi-Model Orchestration

A single user command may become a staged pipeline of AI calls: **planning → research → coding → review → testing → correction → synthesis**. Stages may run sequentially or, where their inputs are independent, in parallel. Each stage receives only the context it needs (least-privilege context), and each stage may be served by a different model family optimized for its job — for example, a frontier reasoning model for planning, a fast high-context model for research, and a coding-specialized model for implementation.

| Stage | Typical Model Profile | Failure Handling |
|-------|----------------------|------------------|
| Planning / intent | High-reasoning frontier model | Retry with expanded context; escalate to orchestrator |
| Research / retrieval | High-context, strong-grounding model | Source-verification pass; secondary provider fallback |
| Coding / generation | Coding-specialized model | Lint, test, and review gates before acceptance |
| Review | Different model family than generation | Cross-model validation reduces correlated error |
| Testing / verification | Deterministic harnesses + model-assisted test generation | Auto-debug loop capped at N attempts |
| Synthesis / response | Voice-profile or user-preference model | Voice/TTS fallback chain (§5) |

Provider selection inside each stage is delegated to the **Model/Provider Router** (§7), which consults health, capability, cost, latency, and quality signals before choosing a primary and pre-computing fallbacks.

### 2.4 Tool Security Boundary (The Non-Negotiable Line)

The model proposes a **structured tool request** (tool name + validated-against-schema arguments). It never receives credentials, shell access, or direct service endpoints. The backend then enforces:

1. **Schema validation** — arguments must satisfy the tool's JSON Schema.
2. **Policy evaluation** — the Permission Engine resolves tool-level permissions, sensitivity class, and required approval level (§8).
3. **Authorization** — OAuth token or secret is retrieved from the credential vault for the exact requested scope; the token is injected server-side only.
4. **Execution** — the tool runs; code execution, when required, happens in a sandbox.
5. **Verification** — result is validated against expected schema and sanity bounds before being exposed back to the model or user.

Any proposal that crosses the boundary (e.g., "give me your Gmail token") is rejected, logged as a security event, and reported.

### 2.5 Memory Architecture (Improved)

Memory flows through a dedicated service chain on read and on write:

- **Read path:** `AI Core → Memory Context Service → Retrieval (vector + keyword + graph) → Ranking (importance × confidence × recency × relevance) → Privacy Filter → Context Assembly (with context budget) → Model`.
- **Write path:** `Agent/Tool → Validation → Secret Filtering → Classification (store, sensitivity, scope) → Duplicate Detection → Conflict Detection → Decision (merge / supersede / reject) → Persistence → Indexes/Embeddings → Audit`.

The memory subsystem is expanded from the handoff's five stores into **nine typed long-term memory stores plus working context** (detailed in §3.2): long-term, short-term/context, episodic, semantic, procedural, preference, project, decision, and relationship memory. Every memory entry carries **importance**, **confidence**, and **relevance** scores, an optional **expiration** (TTL), provenance (which agent/task wrote it), and an immutable audit record. Prompt-injection protection applies to memory writes: entries that contain instructions addressed to the system are flagged and quarantined.

### 2.6 Long-Running Work Pipeline

Anything that cannot complete within a single HTTP request — video generation, deep research, code builds, uploads — is submitted to the durable job pipeline:

```
API (enqueue) → Task Queue (priority, dedupe) → Worker Pool
  → Checkpoint / job-state write (every stage transition)
  → Result + artifact storage → Audit + notification → user-facing status feed
```

Jobs carry a globally unique `job_id`, a machine-readable state (`queued | running | checkpointed | verifying | succeeded | failed | cancelled | resuming`), retry policy with exponential backoff, cancellation tokens, and resumption from the latest checkpoint. A **dead-letter path** captures repeatedly failing jobs for diagnosis rather than silent loss. WebSocket/SSE streams push progress events to the frontend; notifications (§3.16) fire on completion, failure, or required approval.

### 2.7 Self-Evolution Engine (Integration Summary)

The self-evolution engine is specified in full in §8.7 and operates as a governed loop: `observe → detect → analyze → plan → risk assess → authorize → isolate → modify → build/test → security gate → regression → branch/commit/PR → approval → deploy → monitor → verify → rollback if needed → learn`. It is intentionally governed separately from ordinary conversation and API integration: it never removes owner permissions, never disables audit or rollback, and cannot create infinite self-modification loops. The conservative default mode means the engine proposes and proves; it deploys only with approval or within pre-agreed low-risk envelopes.

### 2.8 Cross-Cutting Contracts

Three contracts bind the layers together:

| Contract | Content |
|----------|---------|
| **Correlation ID** | Every request, agent step, tool call, and provider call shares one `trace_id`; all telemetry, logs, and audit rows are queryable by it. |
| **Schema-first tooling** | Every tool, internal or external, is registered with an OpenAPI/JSON-Schema description used for selection, validation, and documentation. |
| **Event bus** | A single internal event bus (task lifecycle, agent events, approval requests, notifications) decouples producers from consumers and powers the real-time UI feed and webhooks. |

---

## 3. Complete Feature Specification

This section expands all 20 capability categories (270 features) into actionable specifications. Each category opens with its purpose and architecture notes, followed by feature groups with implementation guidance. The fifteen priority capabilities (§1.5) are marked **(P)** throughout.

### 3.1 Autonomous Intelligence Core (16 features) — **(P)**

**Purpose.** The engine of agency. This layer converts natural-language intent into persistent, resumable, self-correcting goal-driven behaviour, elevating the system from question-answering to operating-system-level autonomy.

**Architecture notes.** Built as the `Goal Manager` + `Planner` + `Executor` trio inside the Intelligence and Agency layers. Goal state is persisted to the database so that goals survive restarts, interruptions, and channel switches.

| Feature | Implementation Notes |
|---------|---------------------|
| Goal understanding | The Intent Detector maps utterances to structured `Goal` objects: `{id, title, description, owner_intent, desired_outcome, constraints, success_criteria}`. Success criteria must be machine-checkable wherever possible ("upload completes", "PR merged", "video < 5 min"). |
| Intent detection **(P)** | Multi-signal classifier: utterance embedding similarity to known task templates + LLM-based intent parsing + entity/reference resolution against conversation and project context. Returns a confidence score; low confidence triggers a one-question clarification instead of guessing. |
| Goal decomposition | The Planner recursively decomposes a goal into a DAG of subtasks with explicit dependencies, resource estimates, and per-step success criteria. Depth is capped and decomposition quality is evaluated against a checklist before execution begins. |
| Autonomous planning **(P)** | Plans are versioned artefacts (`plan_id`, revision history) that can be displayed to the user, edited by the user, and diffed across revisions. The orchestrator model selects plan granularity based on task risk class. |
| Multi-step task execution **(P)** | The Executor walks the plan graph in topological order, parallelizing independent branches subject to resource and provider limits. Each step emits structured status events consumed by the UI and notification subsystem. |
| Dynamic replanning **(P)** | On step failure or new evidence, the Planner re-plans from the latest checkpoint rather than from scratch. Replan decisions are logged with rationale and, for high-risk tasks, require user confirmation before the new plan executes. |
| Self-correction **(P)** | Every critical step runs a verification function (schema check, unit test, content validator, human-in-the-loop threshold). Failures feed an auto-debug loop: diagnose → patch → retest, capped at a configurable attempt budget before escalation. |
| Failure recovery **(P)** | A `FailurePolicy` per step class: retry (backoff), alternate tool, alternate provider, partial-success branch, or abort. Partial success is reported explicitly — results delivered, residual gaps listed. |
| Task prioritization | The Goal Manager maintains a prioritized queue using urgency (deadline proximity), importance (user-declared or learned), and dependency blocking. Preemptive pause/resume respects the priority order. |
| Dependency management | Plan edges are explicit; blocking dependencies suspend dependents with clear "waiting on X" state visible to the user. Deadlocks (circular waits) are detected at plan time and reported as plan errors. |
| Deadline awareness | Goals carry deadlines; the scheduler issues proactive reminders before deadlines and deprioritizes non-essential steps when a deadline is at risk, escalating with a concrete proposal ("drop X, deliver Y by deadline"). |
| Continuous task execution **(P)** | Execution is never bound to a single HTTP request. The Executor is a state machine persisted in the job pipeline (§2.6); the user can disconnect and return to the same live task. |
| Background tasks **(P)** | Any goal can be explicitly or implicitly backgrounded. Background tasks run on workers with full checkpointing and report via notifications, the live UI feed, or voice when David is listening. |
| Task resumption after interruption | Resumption reads the latest checkpoint, re-validates the plan against current state (e.g., was a dependent PR merged while paused?), and resumes from the exact interrupt point with a status message. |
| Task cancellation | Cancellation is cooperative: a cancellation token is checked at every step boundary, with graceful teardown (release tokens, close files) and a "cancelled with partial results" audit record. |
| Task retry policies **(P)** | Declarative policies per tool/provider class: max attempts, backoff curve, jitter, idempotency requirements, and per-attempt logging. Idempotency keys prevent double actions on resumable operations. |

### 3.2 Advanced Memory System (19 features) — **(P)**

**Purpose.** A persistent, ranked, privacy-filtered personal knowledge base that makes every interaction build on the last. Memory is the differentiator between a tool and a personal operating system.

**Architecture notes.** Nine typed stores over a Postgres core with a vector index (Voyage AI embeddings or equivalent) and an optional knowledge-graph overlay. Each store has its own schema but all entries share the common envelope:

```
MemoryEntry {
  id, store, key, content,
  importance (0-1), confidence (0-1), relevance (0-1),
  created_at, updated_at, expires_at (optional TTL),
  scope (global | project | conversation | relationship),
  sensitivity (public | private | secret_adjacent),
  provenance {agent, task_id, trace_id},
  superseded_by / supersedes (conflict resolution chain),
  audit_row_id
}
```

| Feature | Implementation Notes |
|---------|---------------------|
| Long-term memory **(P)** | Durable Postgres-backed store; vector-indexed for semantic retrieval. Consolidation jobs periodically compress stale entries into summaries. |
| Short-term / context memory **(P)** | Per-session working memory with a strict token budget; context budgeting (§3.3 conversation) decides what rolls into long-term stores versus gets dropped. |
| Episodic memory | Time-ordered records of notable events ("uploaded video X at 14:02", "meeting with Y decided Z"). Supports "what happened with X last week?" queries. Retention TTLs configurable per event class. |
| Semantic memory | Facts about the world and David's business (brand voice, pricing, product facts), de-duplicated and versioned. Fact-level confidence scoring separates "asserted by user" from "verified". |
| Procedural memory | Learned workflows and "how we do X here" patterns (e.g., David's standard YouTube upload checklist). Stored as reviewed workflow artefacts, not raw weights — reviewable and editable. |
| Preference memory | Typed preferences (voice, format, scheduling habits, approval tolerance) with an explicit `learned_at` and revocation path. Preferences drive personalization across all subsystems. |
| Project memory | Scoped to project workspaces (§3.15); each project carries its own memory view so cross-project contamination does not occur. |
| Decision memory | An append-only ledger of decisions with context, alternatives considered, and outcome tracking. Powers "why did we decide X?" retrieval and decision-review sessions. |
| Relationship memory | People and organizations David works with: roles, communication style notes, history of interactions. Strictly private scope; never used in any non-owner context. |
| Importance scoring **(P)** | Composite score: user-declared importance + access frequency + downstream usage + sensitivity weight. High-importance entries resist expiration and consolidation loss. |
| Confidence scoring | Source-weighted: user-stated (high), system-verified (highest), model-inferred (medium), single-observation (low). Low-confidence entries are surfaced with provenance when used. |
| Relevance scoring **(P)** | At retrieval time: query-entry similarity + recency decay + importance + scope match. The Memory Context Service returns the top-k under the context budget. |
| Memory expiration | TTLs per store and per entry class (e.g., session noise expires in 24 h; verified facts persist until superseded). Expiry is a delete-with-audit operation, never silent. |
| Memory conflict detection **(P)** | On write, near-duplicate retrieval checks for contradictions (same subject, divergent content, overlapping validity). Conflicts are surfaced for resolution: merge, supersede with reason, or reject with explanation to the originating agent. |
| Memory consolidation | Scheduled jobs merge related entries, summarize episodic bursts, and re-embed stale vectors. Consolidation preserves the audit chain — summaries reference the entries they compress. |
| Memory summarization | On-demand and scheduled: a model pass produces "state of X" summaries stored as first-class entries, useful for project handoffs and diagnostic reports. |
| Memory correction | Any user or agent can correct an entry; corrections create a new revision linked to the old one (never a silent overwrite). Bulk correction campaigns run via the Review Agent. |
| Memory search | Hybrid search: vector similarity + keyword (tsvector) + structured filters (store, scope, date, sensitivity). The user-facing interface exposes "search David's memory" as a first-class tool. |
| Memory graph **(P)** | An entity-relation overlay (people ↔ projects ↔ decisions ↔ tasks) enabling graph traversal queries ("every decision touching project X involving person Y"). Implemented as tables with a lightweight traversal layer; a dedicated graph DB is a future option if query complexity demands it. |

### 3.3 Conversation & Context

**Purpose.** The user-facing dialogue layer: natural, stateful, multilingual conversation with rigorous context management.

| Feature | Implementation Notes |
|---------|---------------------|
| Natural conversation | Streaming responses via SSE/WebSocket; conversation history persisted per session with summarization for long threads. |
| Follow-up understanding | The Conversation Engine resolves pronouns and implicit references against the last N turns plus project context ("and do the same for the thumbnail" → applies prior action to a new target). |
| Entity / reference resolution | Entities are grounded against memory stores and connected services (which channel? which repository? which video?). Ambiguity triggers targeted clarification, not blind execution. |
| Conversation state | Typed session state machine: `{session_id, channel, active_tasks, active_project, pending_approvals, voice_mode}`. State travels with the user across channels. |
| Active project / task continuity | The active project acts as a context lens: retrieval, tool defaults, and memory scoping bias toward it until the user switches. |
| Current-context management | A `ContextAssembly` service composes {instructions, memory, project files, active task state, tool definitions} under a hard token budget with prioritized slots. |
| Context budgeting | Dynamic allocation: when the budget is threatened, the assembler prefers relevance-ranked memory over raw history, replaces old turns with summaries, and drops redundant tool definitions. |
| Conversation summaries | Automatic rolling summaries at turn thresholds and at session close; summaries are themselves stored as memory entries. |
| Multilingual conversation | English primary; Yoruba supported per the stated goals (§5.8). Language detection is automatic; mixed-language utterances are handled natively, and the response language follows the user's. |
| Multilingual memory | Memory entries carry a `language` tag; retrieval is language-aware but cross-lingual (a Yoruba query can surface English entries and vice versa via shared embeddings). |

### 3.4 AI Provider System

**Purpose.** The abstraction that makes ten providers interchangeable capabilities rather than ten hardcoded API keys. Fully specified in §7.1 — summary here for catalog completeness.

Capabilities covered: central provider registry, model capability registry, health monitoring, availability checks, priority routing, retry with exponential backoff, rate-limit handling (429-aware), full error-code handling (401/402/403/404/408/409/429/5xx), provider fallback, circuit breakers, usage tracking, latency/reliability tracking, user-requested model/provider override, and cost/speed/quality-aware routing.

### 3.5 Tool Intelligence (15 features) — **(P)**

**Purpose.** The runtime that discovers, selects, composes, executes, monitors, and secures all tools — internal and external.

**Architecture notes.** Centered on the **Tool Registry**, a schema-first catalogue where every tool declares: name, description (model-readable for selection), input/output JSON Schemas, capability tags, sensitivity class, permission requirements, timeout, idempotency flag, provider/tool type, and MCP compatibility marker.

| Feature | Implementation Notes |
|---------|---------------------|
| Dynamic tool discovery **(P)** | At planning time, the Capability Router queries the registry by capability tags and returns eligible tools ranked by description fit; the model then proposes from the eligible set — never from a hardcoded list. |
| Tool registry **(P)** | Git-versioned registry source (Python decorators or YAML specs) compiled into a searchable catalogue; registration includes automated contract tests run on CI. |
| Tool capability descriptions | Human-authored descriptions refined by a scheduled review pass that compares descriptions against actual usage outcomes and proposes rewrites. |
| Automatic tool selection **(P)** | Two-stage: tag-based filter → model selection from shortlist. Selections are logged with reasoning for the Learning System. |
| Tool chaining | Chains are explicit DAG nodes in the plan graph; the Executor sequences outputs of one tool into inputs of the next with schema validation at every link. |
| Parallel tool execution | Independent plan branches execute concurrently with a concurrency cap; shared state is synchronized through the checkpoint store, never through in-memory globals. |
| Tool retry | Delegated to per-tool retry policies (§3.1), with per-attempt jittered backoff and idempotency verification before re-executing non-idempotent tools. |
| Tool timeout handling | Hard timeouts per tool class; on timeout, the Executor checks provider health, chooses retry vs. fallback provider/tool, and records the timeout in telemetry. |
| Tool failure recovery | Failure classification (transient vs. permanent vs. argument error) drives the recovery path: retry, re-argument, alternate implementation, or escalate with a human-readable diagnosis. |
| Tool permission system **(P)** | Every invocation is checked against the Permission Engine (§8): per-tool allow/deny, sensitivity tier, approval requirement. Denied calls return structured denials the model can act on (e.g., "request approval"). |
| Tool usage history | Append-only usage log with inputs (sanitized), outputs (truncated), latency, provider, and result status — the raw material for monitoring and learning. |
| Tool performance monitoring | Live aggregates: p50/p95 latency, success rate, cost per call, saturation. Triggers automated "this tool is degrading" diagnostics. |
| MCP support | An MCP client adaptor lets external MCP servers register as tools in the same registry, with the same validation and permission treatment as native tools. |
| External API connector system | Connectors (§7.2) wrap third-party REST/GraphQL APIs behind tool definitions; adding a service is a connector + tool specs, not a code rewrite. |
| Custom tool creation **(P)** | David can describe a tool in natural language; the Coding Agent scaffolds it (spec + implementation + contract tests) into a sandbox, requires review and approval, then registers it. Custom tools are clearly tagged with origin and trust level. |

---

### 3.6 Autonomous Execution (14 features) — **(P)**

**Purpose.** The operational loop that turns plans into verified outcomes without continuous human steering.

**Architecture notes.** Implemented by the `ExecutionLoop` component of the agency layer, backed by the durable job pipeline (§2.6). The loop's contract is "never declare success without verification."

| Feature | Implementation Notes |
|---------|---------------------|
| Plan → Execute → Verify loop **(P)** | Each plan step executes, then a verification function (assertion, test, validator, or secondary-model check) confirms success against the step's criteria before the next step begins. |
| Automatic verification **(P)** | Verification functions are mandatory for write actions (uploads, deploys, payments) and strongly encouraged for generation actions (format checks, content validators). |
| Automatic debugging | On verification failure, a debug pass analyzes the error output and logs, proposes a fix, re-runs verification. Auto-debug budget is capped; exhaustion escalates to the user with full diagnosis. |
| Automatic retry **(P)** | Transient failures retry under the step's retry policy; permanent failures skip retry and invoke the failure-recovery path. |
| Automatic rollback | Destructive or external-facing actions record compensating operations (e.g., delete-after-upload, redeploy-previous-version). Rollback is triggered automatically on post-action verification failure where a compensator exists. |
| Execution checkpoints **(P)** | Checkpoints are written at every step boundary and on long intra-step milestones: plan state, artefacts, and environment snapshot references. Checkpoints are the resumption contract. |
| Progress tracking | Structured progress events (percent, current step, ETA where estimable, blockers) feed the UI live feed, voice status, and notifications. |
| Long-running jobs **(P)** | All jobs exceeding ~30 s are automatically promoted to the queue/worker pipeline; the user never waits on an HTTP connection for them. |
| Background workers **(P)** | Horizontally scalable worker pool consuming the task queue; workers are stateless apart from checkpoint reads/writes, so they can be recycled safely. |
| Scheduled tasks **(P)** | Cron-like schedules persisted in the database (never only in platform cron), with timezone awareness (Africa/Lagos default), pausable schedules, and backfill policy on missed runs. |
| Recurring tasks | Recurring definitions (daily briefing, weekly analytics digest) are first-class objects with run history, drift detection, and easy modification by conversation ("make the briefing weekly instead"). |
| Event-triggered tasks | An event-rule engine subscribes to the internal event bus (job completed, PR merged, payment received, memory written) and fires trigger rules with guard conditions to prevent loops. |
| Task queues **(P)** | Priority queues with weight scheduling: user-facing interactive tasks preempt background digests; dead-letter handling for chronic failures. |
| Task priorities **(P)** | Per-job priority (0–100) combining user-declared priority, deadline urgency, and queue position; preemption decisions are logged. |

### 3.7 Coding & Software Engineering (23 features)

**Purpose.** A full software-engineering partner: understand, generate, test, review, ship, and watch over David's code.

**Architecture notes.** A dedicated **Coding Agent** (§6.3) owns this domain, running inside the same security boundary as all agents. Code execution happens in sandboxed environments; repository operations go through the GitHub connector.

| Feature | Implementation Notes |
|---------|---------------------|
| Repository understanding | Clone/fetch with sparse checkout; build a repo map (directories, key files, dependency graph) before any code action; the map is summarized into context. |
| Codebase indexing | Incremental index (AST symbols, module graph, docstrings) stored per repository; powers "where is X implemented?" queries and precise edit targeting. |
| Code generation | Model generates code in sandboxed scratchspaces with explicit file targets; generated code is always linted and test-run before being offered as a deliverable. |
| Code editing | Diff-based editing (model proposes hunks/patches), never whole-file overwrite; diffs are previewed to the user for reviewable repos. |
| Bug detection | Static analysis + linters + targeted model passes over stack traces and failing tests; findings are ranked by severity with reproduction steps. |
| Bug fixing | Locate → reproduce → patch → retest loop; fixes carry the failing test as permanent regression protection. |
| Refactoring | Small-batch, behaviour-preserving refactorings verified by the existing test suite before and after; large refactorings are proposed as PRs, not applied silently. |
| Dependency analysis | Dependency graph extraction, outdated/vulnerable dependency detection (CVE feeds), upgrade proposals with changelog summaries. |
| Automated testing **(P)** | The Testing Agent runs the repo's suites and generates new tests for changed code; green tests are a gate for accepting any code change. |
| Unit-test generation **(P)** | For generated or changed functions, tests are generated from the spec and executed; coverage deltas are reported. |
| Integration testing | Spins up local services/mocks to test module interactions; integration suites run in CI via the GitHub connector. |
| API testing | Schema contract tests against live staging endpoints (never production writes without explicit approval). |
| Security scanning | SAST pass on changed code (secrets scanning, injection patterns, dependency CVEs); findings block merge until reviewed. |
| Git operations | All Git actions go through the GitHub connector with a dedicated service account; operations are logged with trace IDs. |
| Branch creation | Conventional branch naming tied to goal/task IDs (`feat/GDA-42-youtube-thumbnails`); branches are auto-cleaned after merge. |
| Commit creation | Atomic, well-message commits; commit messages follow a conventional format that links to goals/tasks. |
| Pull-request generation **(P)** | The Coding Agent opens PRs with generated descriptions: summary, risk assessment, test evidence, screenshots where relevant. |
| Code review **(P)** | A Review pass (separate model from the generation model) comments on PRs: logic, style, security, and clarity; blocking comments require human or agent resolution. |
| Build verification | Every branch runs the project build (lint + typecheck + build + test) via CI; build status gates further actions. |
| Deployment **(P)** | Deploys (Render and others) go through the Deployment Agent with environment-aware approvals; production deploys default to requiring owner approval. |
| Deployment monitoring | Post-deploy health probes: endpoint checks, error-rate watch, log tailing for the first N minutes; anomalies trigger the rollback flow. |
| Log analysis | Log ingestion and model-assisted analysis for error spikes and anomalies; recurring errors are filed as diagnosed issues with suggested fixes. |
| Automatic rollback **(P)** | Pre-deploy snapshot of the prior version; on verified deployment failure, automatic redeploy of the previous version with a post-incident report. |

### 3.8 Web Intelligence (14 features)

**Purpose.** David's research department: search, verify, and synthesize the public web into trustworthy, citable knowledge.

**Architecture notes.** A **Research Agent** (§6.2) orchestrates multi-source research through the external search tools and browser automation, with a mandatory citation and verification pass before results are presented.

| Feature | Implementation Notes |
|---------|---------------------|
| Web search | Multi-engine search (provider-backed search tools plus direct engine APIs) with rate-limit-aware fans-out; results de-duplicated by URL normalization. |
| Deep research **(P)** | Multi-round research mode: question decomposition → parallel source sweeps → gap analysis → follow-up sweeps → synthesis report with confidence per claim. |
| Multi-source research | Minimum source-count policy per research task; sources span domains and types (news, docs, forums, official pages) to reduce single-source bias. |
| Source comparison | Side-by-side extraction of competing claims with agreement/disagreement tagging; disagreements are surfaced, not averaged away. |
| Fact verification **(P)** | Claims in deliverables are cross-checked against at least one independent primary source; unverifiable claims are marked as such rather than dropped silently. |
| Citation generation | Every factual statement in reports carries inline citations (source, URL, retrieval date); citation format is configurable (numbered, APA-style, inline). |
| Website reading | Reader-mode extraction (article text, structured data, metadata) with graceful fallback when JavaScript rendering is needed. |
| Webpage extraction | Structured extraction to JSON from pages and documents; schema-driven extraction for repeatable data targets. |
| Browser automation | Headless browser sessions for JS-rendered pages and interactive flows, running in a rate-limited pool with session isolation. |
| Form interaction | Guided form filling within policy bounds; never submits forms that trigger financial or account-modifying actions without explicit approval. |
| Website monitoring | Scheduled snapshot comparisons of target pages (content, price, availability); delta alerts via notification channels. |
| Price monitoring | Numeric extraction with currency normalization; threshold-based alerts ("notify when below ₦X"). |
| News monitoring | Topic subscriptions with dedupe, source-quality weighting, and digest generation (daily/weekly briefings). |
| Research reports **(P)** | Structured report artefacts (markdown/PDF) stored in project workspaces, with executive summary, per-claim citations, confidence annotations, and memory write-back of durable findings. |

### 3.9 Creative Intelligence (14 features)

**Purpose.** A complete creative studio: generate and edit images, video, audio, voice, and music; produce thumbnails, presentations, documents, PDFs, websites, and brand assets — managed as creative projects.

**Architecture notes.** All generation runs as **asynchronous jobs** through the long-running pipeline (§2.6) with provider selection by the creative routing rules in §7.3. Generated assets are persisted to object storage with versions and linked to project workspaces and memory.

| Feature | Implementation Notes |
|---------|---------------------|
| Image generation | Text-to-image via creative providers (Gemini/Imagen, Runway image, HF models); templates per use case (social post, thumbnail base, logo concept); aspect ratios and style presets parameterized. |
| Image editing | Inpainting/outpainting, background removal, upscaling, style transfer; edit requests reference an asset ID and produce a new version of the asset. |
| Video generation **(P)** | Orchestration by the Video Agent (§3.10); scene clips generated per provider capabilities, then assembled. |
| Video editing | Trim, concatenate, transitions, speed, captions overlay via ffmpeg-based worker toolchain; declarative edit scripts versioned per project. |
| Audio generation | Music and sound-effect generation through music-capable providers; licensing-metadata stored per asset (usage rights, model, seed). |
| Voice generation **(P)** | ElevenLabs TTS with the designated British JARVIS voice (§5); cloned/custom voices gated behind owner approval only. |
| Music generation | Template-driven music tasks (intro beds, loops, outro stings) with duration and mood parameters; stems stored when supported. |
| Thumbnail generation **(P)** | Templates combining generated imagery, text overlay, and brand presets; A/B variant sets generated on request for YouTube uploads. |
| Presentation generation | Template-based slide generation (structured content → styled slides), exportable to PDF; consistent with brand presets. |
| Document generation | Structured documents (reports, briefs, proposals) from templates with brand styling; markdown source stored for re-editing. |
| PDF generation | Deterministic PDF rendering of documents and reports; watermarks and metadata per owner settings. |
| Website generation **(P)** | Prompt-to-website and screenshot-to-website pipelines; frontend/backend scaffolds; responsive generation; editing and debugging follow the coding workflow (§3.7). |
| Brand / design generation | Brand kit as a memory-backed object (palette, typography, logo assets, voice guidelines) consumed automatically by all creative templates. |
| Creative project management **(P)** | Creative jobs are organized into creative projects within workspaces: assets, versions, generation history, and approvals tracked per project; the frontend studios surface these (§4). |

### 3.10 Video & YouTube (16 features) — **(P) core**

**Purpose.** An end-to-end YouTube production line: from script to published, monitored video. This is one of the highest-value workflows for David as a content/business owner.

**Architecture notes.** The **Video Agent** (§6) is the orchestrator; each stage is a checkpointed step with its own provider routing and artefact storage. YouTube operations run exclusively through the OAuth connector with published-visibility defaulting to user-approved.

| Feature | Implementation Notes |
|---------|---------------------|
| Video generation orchestration **(P)** | The Video Agent runs the full pipeline as one job: script → storyboard → scene plan → VO/subtitles/thumbnail → scene generation → assembly → review → upload. Every stage checkpointed and resumable. |
| Video-provider selection | Scene clips routed by required duration/quality/provider availability (Runway, Veo, others); fallback provider per scene class; provider decision logged per clip. |
| Script generation | Script artefact with sections, timing estimates, and VO text; reviewed by David or auto-approved under low-risk policy; stored versioned. |
| Storyboard generation | Scene-by-scene visual descriptions generated from the script; each scene card carries image references and duration targets. |
| Scene planning | Scene DAG: parallel-generatable scenes execute concurrently; dependency-aware sequencing (e.g., scene 2 references scene 1's output). |
| Voice-over generation **(P)** | ElevenLabs JARVIS voice (§5) narrates the VO text; pacing aligned to scene durations; re-generation per scene without re-doing the whole track. |
| Subtitle generation | Whisper-class STT over the final mix; timed SRT/VTT artefacts; bilingual subtitles where enabled (English/Yoruba). |
| Thumbnail generation **(P)** | Thumbnail candidates generated per brand templates; David picks or auto-select highest-scoring candidate against historical CTR signals. |
| Video assembly **(P)** | ffmpeg worker pipeline: scenes + VO + music bed + subtitles + transitions; render is checkpointed (per-segment renders) and resumable; final file validated (duration, resolution, loudness). |
| YouTube upload **(P)** | OAuth upload via YouTube connector; resumable upload API for large files; progress events streamed to UI. |
| YouTube metadata generation | Title, description, tags generated by model with SEO heuristics; always presented for approval before publish (default) or auto-published under explicit per-channel policy. |
| Title generation | Multiple title candidates with rationale; CTR-informed scoring from analytics history where available. |
| Description generation | Structured descriptions: hook, summary, chapters, links, hashtags; brand-compliant by template. |
| Tag generation | Tag sets generated per video with channel-historical performance weighting. |
| YouTube analytics **(P)** | Scheduled analytics pulls (views, watch time, CTR, revenue) stored in workspace data; anomaly alerts; periodic performance digests via notification channels. |
| Content scheduling **(P)** | A content calendar (workspace object) plans videos ahead; the Video Agent can queue pipeline runs against calendar dates; rescheduling is conversational. |

---

### 3.11 Voice Agent (12 features) — **(P) core**

**Purpose.** A voice-first interaction layer: David speaks, David AI speaks back, in a natural, interruptible, JARVIS-like conversation — including Yoruba support. Full detail in §5.

| Feature | Implementation Notes |
|---------|---------------------|
| Speech-to-text **(P)** | Low-latency STT (streaming where supported) in the voice channel adapter; automatic language detection; transcripts persisted as memory entries. |
| Text-to-speech **(P)** | ElevenLabs with Voice ID `5hZv9mAOcmcMt1TxA5Iz` (British JARVIS); fallback TTS chain on provider failure (§5.5); streaming audio delivery to minimize first-byte latency. |
| Real-time voice conversation **(P)** | Full-duplex WebSocket pipeline: audio in → STT → intent → response → TTS → audio out, with turn management and voice-activity detection. |
| Voice interruption **(P)** | Barge-in detection halts TTS playback and STT context immediately; the interrupted turn is re-resolved with the new utterance. |
| Wake-word support | Local or server-side wake-word detection; configurable keyword; always-on listening is opt-in with explicit UI indication. |
| Voice commands **(P)** | Intent detection over voice transcripts identical to text path; command grammar learned from corrections ("David, play my analytics" maps to the Analytics digest). |
| Voice confirmation | Sensitive actions confirmed by voice ("Shall I proceed?") with timeout fallback to the UI approval card; confirmations are audit-logged with the audio reference. |
| Voice-controlled tools | Tools expose voice-friendly descriptions; results are rendered as concise spoken summaries, not raw data dumps. |
| Voice memory **(P)** | Spoken preferences and instructions are captured as preference/semantic memory with voice provenance; voice corrections update the same stores as text corrections. |
| Natural conversational responses | Voice responses use a spoken-register style guide (shorter sentences, no markdown, spoken citations); response length budgeted for listening comfort. |
| Multilingual voice **(P)** | STT/TTS language auto-detection and switching mid-conversation; language preference stored per user. |
| Yoruba voice support **(P)** | Yoruba STT/TTS support per stated goals: provider capabilities evaluated per release; mixed English–Yoruba utterances handled natively. Where provider coverage is partial, capability is reported honestly in self-diagnostics (§3.20) rather than silently degrading. |

### 3.12 Security & Permissions (13 features) — **(P)**

**Purpose.** The governance spine of the system, specified in full in §8. Summary follows.

Capabilities covered: permission engine (policy-as-data, owner-overridable), tool-level permissions (per-tool allow/deny/sensitivity tiers), human approval system (in-UI, voice, email approval cards), sensitive-action confirmation, secret protection (vault, never exposed to models), API-key protection (encrypted at rest, scoped tokens, rotation), prompt-injection detection (input, memory-write, and tool-result scanning), malicious-file detection (file-type validation, content scanning, sandboxed opening), command safety (no shell passthrough; allowlisted command patterns in sandbox), data-access controls (scope-based memory and file access), audit logs (append-only, tamper-evident), security monitoring (anomalous-pattern alerts), and credential exposure detection (output scanning for secrets before any response leaves the system).

### 3.13 Testing & Quality (12 features) — **(P) core**

**Purpose.** Quality as a system property, not an afterthought: the system tests itself continuously — providers, tools, memory, agents, and deployments.

**Architecture notes.** Owned by the **Testing Agent** (§6) with a `QualityGate` contract: no release, deploy, or learned artefact crosses a gate without evidence.

| Feature | Implementation Notes |
|---------|---------------------|
| Automatic testing **(P)** | Unit, contract, and property tests run on every change; testing is triggered by commits, deploys, provider changes, and learning updates. |
| Regression testing | Golden-path suites (core flow, 15 priority capabilities) run on every deployment and nightly; regression failures block merge/deploy. |
| Integration testing | End-to-end scenarios across subsystem boundaries (intent → plan → tool → memory → response) executed against staging. |
| Provider testing **(P)** | Per-provider canary suite (auth, model availability, latency, output sanity) run before routing traffic after any config change or health alert. |
| Tool testing | Contract tests per tool: schema round-trip, happy path, error path, idempotency proof where claimed. |
| Memory testing | Retrieval quality probes (known questions, expected answers), conflict-resolution fixtures, privacy-filter tests (secrets must never leak through retrieval). |
| Security testing **(P)** | Scheduled penetration-style self-checks: injection probes, privilege-escalation attempts against own gates, secret-scan of all outputs. Findings route to the owner. |
| Deployment testing | Pre-deploy smoke suite against staging; canary deployment with automated rollback on error-rate regression (§3.7). |
| Output quality evaluation **(P)** | Model-assisted evaluation of generation outputs (relevance, accuracy, style compliance) against rubrics stored per task type; low scores trigger regeneration or human review. |
| Agent evaluation **(P)** | Per-agent scorecards: task success rate, retry rate, cost per task, user-correction rate. Scorecards drive routing weight adjustments in the Learning System. |
| Failure analysis | Post-failure reports with root-cause classification, affected scope, and remediation; chronic failure classes trigger Improvement Planner proposals. |
| Performance benchmarking | Standard workloads benchmarked across providers/models (latency, cost, quality) on a schedule; results feed cost/quality-aware routing (§7.1). |

### 3.14 Observability (12 features) — **(P) core**

**Purpose.** The system sees itself: every agent, tool call, provider call, error, and token is traced, and the system can replay its own history.

**Architecture notes.** All telemetry keyed by `trace_id`; stored in Postgres tables with retention tiers and exported to a dashboard API consumed by the frontend diagnostics panel and the owner's dashboard.

| Feature | Implementation Notes |
|---------|---------------------|
| Agent traces **(P)** | Structured trace spans per agent step (input, output, duration, tokens, decisions) forming a queryable timeline per task. |
| Task history **(P)** | Every task's full lifecycle: plan versions, checkpoints, status events, final result, artefacts. Queryable by project, agent, date, status. |
| Tool-call history | Per-tool invocation log (inputs sanitized, outputs truncated, latency, status); feeds usage analytics and debugging. |
| Provider-call history | Per-provider request log with model, tokens in/out, latency, status, cost estimate; the basis of cost monitoring. |
| Error tracking | Error taxonomy with dedupe, grouping, and alerting; errors link back to trace IDs and affected tasks. |
| Latency tracking | P50/p95/p99 per subsystem, per provider, per tool; SLO thresholds trigger diagnostics automatically. |
| Token / usage tracking **(P)** | Token counts per request/stage/provider with daily/weekly aggregation; budgets and alerts per provider and overall. |
| Provider health dashboard **(P)** | Live dashboard: availability, error rates, latency, cost trends, circuit-breaker states per provider (§7.1). |
| Task success rates | Success/failure/partial-success rates per task type, agent, and time window; inputs to agent evaluation. |
| Agent performance metrics | Per-agent SLAs: success rate, avg retries, avg cost, avg duration; published in the diagnostics panel. |
| Cost monitoring **(P)** | Aggregated cost per provider, per agent, per task type, with budget alerts and forecast; cost anomalies trigger investigation tasks automatically. |
| Execution replay **(P)** | Any completed task can be replayed: re-emit the trace events, re-run verification steps, or re-execute the whole plan in a sandbox for debugging. Replay is read-only by default; re-execution is gated. |

### 3.15 Data & Project Management (12 features) — **(P) core**

**Purpose.** Persistent workspaces: the places where David's projects, files, tasks, decisions, and artefacts live between conversations.

**Architecture notes.** Workspaces are database-backed with object storage for files; every workspace has memory scoping, an activity log, and an API surface.

| Feature | Implementation Notes |
|---------|---------------------|
| Persistent project workspaces **(P)** | First-class `Workspace` objects: projects, sub-projects, and a personal inbox workspace. Creation is conversational ("start a project for the Lagos launch"). |
| Project files **(P)** | Files stored in workspace object storage with versions; the Coding/Creative agents read and write files through versioned operations. |
| Project memory **(P)** | Per-workspace memory scope (§3.2); workspace context automatically lenses retrieval and tool defaults. |
| Project tasks **(P)** | Tasks/subtasks scoped to workspaces with status, assignee (agent or David), priority, and deadlines; conversational task management ("move this to next week"). |
| Project decisions **(P)** | Decision ledger per workspace (§3.2); decisions surface in project summaries and review sessions. |
| Artifact management | Generated artefacts (documents, videos, code snapshots, reports) linked to their producing task and versioned; artefact shelf browseable in the UI. |
| Version history | File and artefact versions with diffs and provenance; rollback to any prior version through the standard approval flow. |
| Activity history | Append-only workspace activity log (who/which-agent did what, when); the basis of project summaries and audit. |
| Database-backed state **(P)** | All project state lives in Postgres/Supabase; no state-only-in-memory paths; state schema migrations are versioned and tested. |
| File storage | Tiered storage: hot (recent project files) on fast storage, warm (historical) on object storage; lifecycle policies configurable. |
| Searchable artifacts | Full-text + vector search across artefacts within workspaces; "find the report where we discussed pricing" resolves via semantic search. |
| Automatic project summaries **(P)** | Scheduled and on-demand summaries: status, blockers, decisions, next actions; delivered via notification channels and the UI. |

### 3.16 Notifications & Communication (9 features)

**Purpose.** The system keeps David informed without being noisy: the right alert, on the right channel, at the right time.

**Architecture notes.** A `Notification Service` consumes the event bus, applies user routing preferences (voice-first, then UI, then email), dedupes, and rate-limits.

| Feature | Implementation Notes |
|---------|---------------------|
| Task-completion notifications | Delivered on the user's primary channel with a concise summary and artefact links; batched for low-priority completions. |
| Failure notifications | Immediate, high-priority, on all active channels, with diagnosis and suggested next action. |
| Deployment notifications | Pre-deploy notice, deployment result, and post-deploy health verdict; anomalies escalate automatically. |
| Approval requests **(P)** | Approval cards on UI + voice prompt + email fallback; expiry policy with auto-escalation ("still waiting on your approval for X"). |
| Scheduled reminders | Deadline and schedule reminders from the scheduler; snooze and reschedule are conversational. |
| Email integration | Gmail connector (§7.2) for sending digests, approvals, and reports; sending email is a sensitive action requiring appropriate permissions. |
| Social-media integration | Status updates to connected accounts under the social workflow (§3.18); governed by the approval engine. |
| Webhook notifications | Outbound webhooks for external integrations (Slack, Discord, custom endpoints); webhook secrets vault-stored, payloads signed. |
| Real-time activity updates **(P)** | The live UI feed and voice channel receive streaming task events; WebSocket/SSE with reconnection and replay of missed events. |

### 3.17 Financial / Transaction Intelligence (7 features) — high-governance

**Purpose.** Money operations exist but behind the strictest governance: payments via Paystack are proposals until approved, tracked after execution, and reconciled against limits.

**Architecture notes.** The **Finance Agent** (§6) executes within hard constraints: spending limits, dual confirmation thresholds, and the sensitive-action matrix. Facebook-related or unapproved payment flows are excluded by policy.

| Feature | Implementation Notes |
|---------|---------------------|
| Payment integration | Paystack connector: create payment links, verify payments, handle webhooks; payment creation is a sensitive action. |
| Payment verification **(P)** | Every payment event verified server-side against Paystack signatures and reconciled to internal records; unverified events are quarantined. |
| Transaction tracking | Transaction ledger (status, amount, reference, associated task/project); queryable conversationally and in dashboards. |
| Payment approval workflows **(P)** | Payment creation requires approval above a configured threshold; thresholds are per-category and time-boxed. |
| Spending limits **(P)** | Hard limits per period and per category; the permission engine rejects any operation that would breach a limit; limit changes require owner approval. |
| Financial-action confirmations | Voice or UI confirmation for every financial action, with summary of amount, recipient, and category read back before execution. |
| Transaction history **(P)** | Full history with export; periodic financial digests (with reconciliation anomalies highlighted) delivered via the notification service. |

### 3.18 Social & Automation (8 features)

**Purpose.** Content operations across connected social accounts with calendar discipline and analytics feedback.

**Architecture notes.** **Social Media Agent** (§6); connector set is YouTube + TikTok (and others David authorizes); **Facebook is explicitly excluded from all social integrations by policy**, and this exclusion is enforced at the connector registry level, not merely by convention.

| Feature | Implementation Notes |
|---------|---------------------|
| Social account connections | OAuth per platform through the External Service Manager; connection health monitored; token refresh automatic and silent. |
| Content creation **(P)** | Creative pipeline outputs (posts, captions, thumbnails, short clips) feed a social content queue with platform-specific formatting. |
| Content scheduling **(P)** | Queue entries carry publish times; the scheduler releases them; rescheduling is conversational. |
| Post publishing **(P)** | Publishing is a sensitive action: draft-by-default with approval, or auto-publish under per-platform policy David sets. |
| Cross-platform publishing **(P)** | One content item adapts to multiple platforms (aspect ratios, caption lengths, hashtags) with a publish matrix; each platform's result tracked separately. |
| Social analytics **(P)** | Periodic analytics pulls per platform (engagement, growth, top content); stored in workspace data; informs content planning. |
| Content calendar **(P)** | Unified calendar across platforms and YouTube; conflicts (same content, same slot) are detected; drag-and-drop in the UI plus conversational control. |
| Automated workflows **(P)** | Workflow recipes ("when a video publishes → create TikTok clip → schedule both") defined conversationally, versioned, and monitored; loop guards prevent infinite triggers. |

### 3.19 Learning System (8 features) — **(P)**

**Purpose.** The system improves with use — learning from corrections, successes, and failures — while remaining fully reviewable and reversible. **Learning adapts configuration and knowledge; it never performs unrestricted self-modification.** Self-modification belongs to the governed evolution engine (§8.7).

**Architecture notes.** All learning outputs are typed artefacts (preference updates, workflow edits, routing weights, correction records) stored in memory/repositories with provenance and a revocation path.

| Feature | Implementation Notes |
|---------|---------------------|
| Learn from corrections **(P)** | Every user correction ("not like that, do X instead") becomes a structured correction record; the affected workflow/tool preference is updated and the correction is replayed against similar past outputs where safe. |
| Learn from successful tasks | Successful task traces are mined for reusable patterns (which provider, which tools, which order worked); patterns become procedural-memory candidates after review. |
| Learn from failures | Failure analyses feed a negative-pattern store ("approach X fails on provider Y for this task class"); the planner consults it before repeating approaches. |
| Preference adaptation | Observed behaviour updates preference memory (format, tone, channel, scheduling); significant preference changes are surfaced in a periodic "what I learned" review. |
| Workflow optimization | Measured workflow timings and costs drive optimization proposals ("reorder steps A→B saves 2 min and ₦X"); proposals execute only under approval or low-risk envelope. |
| Tool-selection learning | Routing weights adjusted from per-tool success/latency/cost history; adjustments bounded within confidence intervals and reversible. |
| Provider-selection learning | Benchmark and live-performance history tunes cost/quality/latency weights per stage; weight changes are versioned and test-gated. |
| Personalized behavior | The aggregate learning layer yields progressively personalized behaviour; a full "learned profile" is viewable and editable by David at any time. |

### 3.20 Self-Diagnostics (10 features) — **(P)**

**Purpose.** The system can examine its own health on demand and on schedule, producing honest, structured diagnostic reports.

**Architecture notes.** The `DiagnosticsRunner` executes a registered checklist of health probes, each returning `{status: ok | warn | fail | n/a, detail, metric}`, and assembles a report in the documented format. Any probe can degrade gracefully — partial diagnostics are reported, never faked.

| Feature | Implementation Notes |
|---------|---------------------|
| System health check | Core service probes: gateway, conversation engine, agents, workers, event bus, queue depth; synthetic end-to-end ping through the full pipeline. |
| Provider health check **(P)** | Canary calls per provider with latency/error summary; circuit-breaker states reported; unavailable providers flagged in routing dashboards. |
| Database health check | Connection pool, replication lag (if any), migration state, disk growth trends; slow-query watch. |
| Memory health check | Retrieval probe accuracy, index freshness, conflict backlog, store sizes, privacy-filter test pass. |
| Tool health check | Per-tool contract-test pass, recent failure rates, timeout frequency. |
| Storage health check | Object storage availability, quota usage, lifecycle policy compliance. |
| Deployment health check | Render service state, last deploy status, post-deploy health probes, recent error-rate trend. |
| API-key configuration check | Vault consistency: expected keys present, not expired, scopes correct; missing/invalid keys listed with remediation steps (never the keys themselves). |
| Security health check | Last penetration-style self-check results, audit-log integrity, approval backlog, credential-exposure scan status. |
| Automatic diagnostic reports **(P)** | On-demand ("David, run a full system diagnostic") and scheduled; output in the standard report format below, delivered via voice and UI: |

```
DAVID AI SYSTEM HEALTH
  Core Intelligence      ✓
  Memory                 ✓
  Planning               ✓
  Tools                  ✓
  AI Providers           ✓
  Voice                  ✓
  Video                  ⚠  (provider X degraded, fallback active)
  Database               ✓
  Storage                ✓
  GitHub                 ✓
  Render                 ✓
  Security               ✓
  Automation             ✓
  Overall: 96%
```

The overall score is a weighted composite of probe statuses and is always accompanied by the itemized detail — a single number is never presented without the evidence behind it.

---

## 4. Frontend Specification

### 4.1 Design Vision: JARVIS-Style Holographic Interface

The frontend embodies the **David Ademola AI** brand as a JARVIS-style holographic command interface: a dark environment (deep navy-to-black gradient) with a cyan/teal glow language, animated particles, a rotating central orb with concentric rings, and voice-first interaction. The aesthetic is cinematic, but every visual element must map to a real system state — the interface is a dashboard of a working operating system, not a screensaver.

### 4.2 Visual Language

| Element | Specification |
|---------|---------------|
| Background | Radial dark gradient (`#050a14` → `#0a1628`), subtle vignette; faint hexagonal grid overlay at 3–5 % opacity. |
| Primary glow | Cyan `#00e5ff` with teal `#2dd4bf` secondary; glow via layered CSS/SVG drop-shadows and bloom passes (WebGL or canvas). |
| Central orb | Rotating 3D orb (WebGL/Three.js) at the centre of idle state; represents the AI core. State-mapped colour shifts: idle cyan, thinking teal pulse, executing amber trace, error red pulse, listening (voice) white-cyan ring. |
| Concentric rings | 3–5 rotating rings at different speeds/axes around the orb; ring speed and count reflect active task count; rings pulse on task events. |
| Particles | 100–300 floating particles (canvas/WebGL) drifting upward; particle density and drift speed scale with system activity; particles converge toward the orb on event spikes. |
| HUD chrome | Thin 1px cyan lines, corner brackets, monospace status text (`DAVID AI — ONLINE`, timestamps, task counters); scan-line and vignette overlays at low opacity. |
| Typography | Headings: a geometric sans (e.g., Orbitron/Rajdhani); body and status: monospace (JetBrains Mono/IBM Plex Mono). |
| Motion | 60 fps target; easing on all state transitions (200–400 ms); no layout jumps — state changes interpolate. |

### 4.3 State-Driven Animation Contract

The interface is a reactive consumer of the event bus. Every animation element binds to system state, so the UI is always truthful:

| System State | Visual Behaviour |
|--------------|------------------|
| Idle / standby | Slow orb rotation, gentle ring drift, ambient particles. |
| Listening (voice) | Rings brighten and pulse to voice-activity amplitude; orb glows white-cyan. |
| Thinking / planning | Rings accelerate; orb emits a radial scan pulse; "PLANNING…" HUD text with step counter. |
| Executing | Rings split per parallel branch; particle streams flow from orb to a task cluster; per-step progress arcs. |
| Tool call / external action | A brief glyph (mail, git, play, card) flashes with the action name ("GMAIL → SEND"). |
| Approval pending | Orb pulses amber; the approval card slides in with voice confirmation prompt. |
| Error | Localized red pulse on the affected element; rings stutter; diagnostic banner with "VIEW DIAGNOSTICS" action. |
| Task complete | Success sweep animation; result card delivered; optional voice confirmation. |

### 4.4 Key Interface Surfaces

1. **Home / Command surface.** Central orb, voice mic control, text input, live task feed on the right rail, memory/context indicators. The default landing after authentication.
2. **Task console.** Live view of any running task: plan graph, step statuses, checkpoints, live log stream, agent attributions, execution replay controls.
3. **Memory browser.** Searchable view of the nine memory stores with confidence/importance visualization, edit/correct/revoke controls, and privacy-scope indicators.
4. **Project workspaces.** One panel per workspace: tasks, files, decisions, artefacts, activity log, summaries.
5. **Creative studios.** Three studios — **Image Studio**, **Video Studio**, **Audio/Voice Studio** — each with templates, asset shelves, version history, and publish queues (see §4.6).
6. **Provider & diagnostics dashboard.** Live provider health, cost and token usage, agent scorecards, and the one-click full-system diagnostic (§3.20).
7. **Approvals inbox.** Pending approval requests with context, risk level, and approve/deny/modify actions; accessible from UI, voice, and email.
8. **Settings & governance.** Permissions matrix, spending limits, notification routing, connected accounts, and the learned-profile review.

### 4.5 Technical Stack & Performance

The frontend is a single-page application (React or Vue) communicating with the FastAPI backend via REST, WebSocket (voice and live events), and SSE (task streams). WebGL/canvas handles orb, rings, and particles; CSS handles HUD chrome. Performance contracts: first paint under 2 s on the deployed Render instance, animation at 60 fps on mid-range hardware with a reduced-motion fallback, and an offline-degraded mode that shows the last-known state when the backend is unreachable. Accessibility: reduced-motion preference, keyboard navigation, screen-reader text equivalents for all state-driven visuals, and full text-mode parity with every voice capability.

### 4.6 Creative Studios with Templates

Each studio is a template-driven workflow surface:

- **Image Studio.** Templates: social post, YouTube thumbnail, brand asset, logo concept, portrait, product. Each template defines provider routing, aspect presets, style presets from the brand kit, and output formats.
- **Video Studio.** Templates: script-to-video, promotional video, short clip, compilation. The full pipeline (§3.10) runs here with per-stage progress and approval gates.
- **Audio/Voice Studio.** Templates: voice-over, music bed, sound effect, podcast segment. Uses ElevenLabs voice settings and music providers; every generated asset carries licensing metadata.

Templates are versioned, user-extensible (David describes a new template; the Coding Agent scaffolds it under the usual approval flow), and consume the brand kit automatically.

---

## 5. Voice System Specification

### 5.1 Interaction Model: Voice-First

The default interaction posture is **voice-first**: David speaks, David AI listens, thinks, and speaks back. Every voice capability has an equivalent text/WebSocket path, and every text capability is reachable by voice. The voice channel is a peer of the text channel, not a wrapper around it.

### 5.2 Pipeline Architecture

```
[User mic] ──audio──► Voice Adapter (WebSocket, full-duplex)
                          │
                          ├─► VAD (voice-activity detection)
                          ├─► STT (streaming, language auto-detect) ──transcript──► Conversation Engine
                          │                    (identical pipeline as text, §2.2)
                          │                                    │
                          ▼                                    ▼
                   Wake-word gate ◄────────────── response (text) ──► TTS Engine
                                                                        │
                                                                        ▼
                                                               [User speaker] ◄─streaming audio
```

**Components and their roles:**

- **Voice Adapter.** A persistent WebSocket connection carrying PCM/WebM audio both directions with sequence numbering, reconnection with event replay, and echo handling.
- **VAD.** Filters silence and non-speech; drives turn-taking and interruption detection (§5.4).
- **STT.** Streaming speech-to-text with automatic language detection (English primary, Yoruba support per §5.8); transcripts persist as memory entries with voice provenance.
- **TTS Engine.** ElevenLabs as primary with Voice ID `5hZv9mAOcmcMt1TxA5Iz`; the fallback chain (§5.5) ensures voice never silently dies. Audio is streamed chunk-by-chunk to minimize time-to-first-audio.
- **Turn Manager.** Prevents the model from talking over the user: barge-in halts playback and re-resolves the interrupted utterance.

### 5.3 The Voice Persona

The voice is a **British, JARVIS-style deep male voice** — calm, courteous, concise. Voice output follows a spoken-register style guide: short sentences, no markdown, spoken-friendly citations ("according to the report from Tuesday…"), and length budgeting (default spoken answers capped by a configurable duration; long reports offered as "I'll send the full report to your dashboard"). The voice persona settings (rate, warmth, formality) are preference-memory backed and adjustable conversationally.

### 5.4 Interruption & Real-Time Conversation

Full-duplex means the user can interrupt at any moment. On barge-in: TTS playback stops within a frame, the in-flight turn is abandoned, the new utterance is resolved against the partially-built response state, and the conversation continues naturally ("Sorry — you said…?"). Interruption events are audit-logged. Wake-word detection activates attentive mode; always-on listening is strictly opt-in with a persistent on-screen/listening indicator.

### 5.5 Provider Resilience for Voice

| Layer | Primary | Fallback |
|-------|---------|----------|
| TTS | ElevenLabs (`5hZv9mAOcmcMt1TxA5Iz`) | Secondary ElevenLabs voice; then other configured TTS provider; finally cached/stock voice with disclosure |
| STT | Provider streaming STT (model-native or dedicated) | Alternate STT provider; local/batched fallback with honest latency disclosure |
| Provider failure | Automatic provider switch via Model/Provider Router | Failure reported in voice ("Voice service is degraded; I'll answer in text") with self-diagnostic note |

### 5.6 Voice Commands & Confirmation

Voice commands traverse the identical intent-detection path as text. Sensitive actions requested by voice are confirmed by voice: the system reads back a short summary ("You asked me to publish the Lagos video as unlisted. Shall I proceed?"), awaits an audible approval within a timeout, and falls back to an UI approval card if the user is silent. Confirmations are audit-logged with references to the audio recordings.

### 5.7 Voice Memory

Spoken instructions, corrections, and preferences are captured into the same memory stores as text (§3.2), tagged with `provenance: voice` and language. Voice corrections update the same records a text correction would — there is one memory, reached by two channels.

### 5.8 Multilingual & Yoruba Support

Language is detected per utterance and can switch mid-conversation. The system supports English natively today and works toward full Yoruba support per the stated goals: Yoruba-capable STT/TTS providers are evaluated at each release cycle, and coverage gaps are reported honestly in self-diagnostics rather than masked. Mixed English–Yoruba speech is handled natively where the provider supports it, with graceful per-provider degradation documented in §3.11.

---

## 6. Multi-Agent Orchestration System

### 6.1 Concept: Coordinator Delegation

David Ademola AI operates as a **coordinator that delegates to specialized sub-agents**. The Master/Orchestrator Agent never does specialist work itself: it understands the goal, builds the plan, assigns each subtask to the right agent, mediates agent-to-agent communication, aggregates results, verifies outcomes, and reports to David. Sub-agents are stateless workers that receive scoped context, tool permissions, and a completion contract.

```
                  ┌───────────────────────┐
                  │   DAVID (user)        │
                  └──────────┬────────────┘
                             │
                  ┌──────────▼────────────┐
                  │  Master Orchestrator  │  plan, delegate, verify, aggregate
                  └──────────┬────────────┘
     ┌───────────────────────┼────────────────────────┐
     │         ┌─────────────▼──────────────┐          │
     │         │  Sub-Agent Fleet (23)      │          │
     │         │  Research · Coding · Web · │          │
     │         │  Browser · Creative · …    │          │
     │         └─────────────┬──────────────┘          │
     │                       │                          │
     └───── shared: Memory · Tool boundary · Queue ─────┘
```

### 6.2 Agent Registry & Lifecycle

Every agent is registered in an **Agent Registry** with: name, capability description (model-readable), permission profile, max concurrency, stage affinity (§2.3), health status, and current scorecard (§3.13). Agents are spawned per task (or pooled for high-throughput classes), receive least-privilege context, and terminate with a structured result and resource release. The orchestrator monitors all live agents, detects stalls (no progress events within the class SLA), and can terminate and re-delegate.

### 6.3 The Sub-Agent Fleet (23 agents)

| # | Agent | Primary Domain | Key Responsibilities |
|---|-------|----------------|----------------------|
| 1 | **Master/Orchestrator** | Coordination | Goal intake, planning, delegation, verification oversight, aggregation, user reporting |
| 2 | **Planning** | Strategy | Plan construction, replanning, risk assessment of plans, deadline/dependency analysis |
| 3 | **Research** **(P)** | Knowledge | Deep research, multi-source synthesis, fact verification, citation building |
| 4 | **Web** | Public web | Search orchestration, page extraction, source comparison |
| 5 | **Browser** | Interactive web | Headless automation, form interaction, JS-rendered content, monitoring |
| 6 | **Coding** **(P)** | Software | Code generation/editing, debugging, refactoring, dependency work |
| 7 | **Testing** **(P)** | Quality | Unit/integration/API/security test generation and execution, quality gates |
| 8 | **Review** | Assurance | Cross-model code/content review, PR review, learning-artefact review |
| 9 | **Deployment** | Release | Deploys across Render and other targets, canary monitoring, rollback execution |
| 10 | **Security** | Protection | Security scanning, intrusion/adversarial-input analysis, audit review |
| 11 | **Creative** | Studio lead | Creative project coordination, template management, brand compliance |
| 12 | **Image** | Image | Generation, editing, variations, upscaling across creative providers |
| 13 | **Video** **(P)** | Video/YouTube | Full production pipeline orchestration (§3.10) |
| 14 | **Voice** | Speech | STT/TTS orchestration, voice UX, transcription memory writes |
| 15 | **Data** | Data work | Extraction, transformation, analysis, visualization, reporting |
| 16 | **Database** | State | Schema work, migrations, query optimisation, data health (gated, read-mostly by default) |
| 17 | **Finance/Payment** | Money | Paystack flows, verification, reconciliation, limit enforcement |
| 18 | **Social Media** | Social | Content queue, publishing, cross-platform adaptation, analytics |
| 19 | **Automation** | Workflows | Scheduled/recurring/event-triggered workflow management, loop-guard monitoring |
| 20 | **Monitoring** | Health | Health probes, alerting, diagnostic runs, incident records |
| 21 | **Learning** | Adaptation | Correction/success/failure mining, preference updates under review |
| 22 | **Evolution** | Self-improvement | Runs the governed evolution loop (§8.7) in sandbox |
| 23 | **Notifications** | Comms | Notification routing, delivery verification, channel management |

### 6.4 Agent Communication Protocol

Agents communicate only through **typed, structured messages** over the internal event bus — never by sharing memory objects or credentials:

- **Delegation message:** `{task_id, goal_ref, context (scoped, budgeted), contract {success_criteria, artefacts, deadline}, permissions granted}`.
- **Status message:** `{step, progress, artefacts, blockers}` — drives the live UI/voice feed.
- **Result message:** `{status, artefacts, verification_evidence, cost/tokens}` — the orchestrator verifies against the contract before accepting.
- **Escalation message:** `{type: blocked | needs_approval | failed | loop_detected, detail}` — escalates to the orchestrator (and onward to David) with full context.

**Agent-to-agent handoffs** are explicit: an agent can request delegation to a specialist ("I need image generation — handing off to the Image Agent"), and the orchestrator mediates the transfer, preserving the shared `trace_id` so the whole sequence remains one replayable trace.

**Result aggregation** follows the plan graph: parallel branches are joined only when all branches satisfy their contracts; partial-success branches contribute their verified results with explicit residual gaps listed in the final report.

### 6.5 Orchestration Safeguards

| Safeguard | Mechanism |
|-----------|-----------|
| Loop protection **(P)** | Maximum agent-step budgets per task; repetition detection (same tool call pattern N times); automatic halt with report when a loop is detected. |
| Permission isolation | Each agent runs with its registered permission profile; an agent can never elevate its own permissions. |
| Failure containment | Agent failure terminates that branch only; the orchestrator re-delegates or re-plans. Dead agents are quarantined and health-checked before reuse. |
| Context least privilege | Agents receive scoped context slices, not the full session. |
| Cross-model validation | Verification stages use a different model family than generation to reduce correlated failure. |
| Emergency stop **(P)** | A global stop the owner can invoke from any channel at any time; terminates all agents, preserves checkpoints, and produces a stop report. |

### 6.6 Orchestration Metrics

The orchestrator publishes a live scorecard consumed by the diagnostics panel and the Learning System: active/delegated/completed/failed tasks, per-agent success rate and retry rate, average cost per agent per task type, loop/halt events, and handoff latency. These metrics tune delegation decisions over time through the Learning System's bounded, reviewable weight adjustments (§3.19).

---

## 7. Integration & Provider Architecture

### 7.1 AI Provider Intelligence (13 features) — **(P)**

**Purpose.** Make every AI provider an interchangeable, monitored, routable capability. No business logic may depend on a provider by name.

**Provider abstraction layers:**

| Layer | Contract |
|-------|----------|
| Provider registry | `{id, base_url, auth_method, health_endpoint, config}` — one row per provider; credentials vault-only. |
| Model capability registry | `{model_id, provider, capabilities[], context_window, pricing{input,output}, latency_p50/p95, quality_scores, availability}` — the routing substrate. |
| Normalized adapter | Every provider implements a common interface: `chat / stream / embeddings / image / audio / status`. Provider-specific quirks are encapsulated behind the adapter; errors are normalized into the shared taxonomy (401/402/403/404/408/409/429/5xx). |
| Router | `capabilities required → eligible models → rank by {health, capability fit, cost, latency, quality, user override} → primary + ordered fallbacks`. Routing decisions logged with rationale. |

**Resilience behaviours:**

- **Automatic fallback:** on provider failure (auth, 5xx, timeout), the router switches to the next provider/model with the required capability, transparently to the task (failure + switch event logged).
- **Circuit breakers:** per-provider open/close states with error-rate thresholds and gradual re-probing (canary calls) before closing.
- **Rate-limit handling:** 429 responses trigger backoff respecting `Retry-After`, local token-bucket accounting, and load-shedding to alternate providers before waiting.
- **Billing-error detection:** 401/402 patterns (credential invalid, payment failed) are distinguished from transient failures, alert the owner immediately, and exclude the provider from routing until resolved.
- **Health checks:** periodic synthetic calls per provider; health feeds the routing weights and the provider dashboard.
- **Usage analytics:** per-provider token/cost/latency aggregates; feed cost monitoring (§3.14) and provider-selection learning (§3.19).
- **User override:** David can pin a model/provider per task or globally ("use Claude for this review"); overrides are preference-memory backed and auditable.

**Current provider roster** (each treated as an interchangeable capability, never a hardcoded dependency):

| Provider | Primary Role in Routing |
|----------|------------------------|
| Gemini | Multimodal generation, long-context research, Veo creative access |
| OpenAI | Reasoning, code, image (DALL-E), GPT-based voice pipelines |
| Claude | Deep analysis, document work, coding review, long-horizon planning |
| Groq | Ultra-low-latency serving for interactive/voice stages |
| OpenRouter | Aggregated access and cross-family fallback breadth |
| Voyage AI | Embeddings for memory retrieval and search |
| Hugging Face | Open-model coverage, niche image/audio tasks |
| Cloudflare | Edge-adjacent inference, Workers AI workloads |
| Cerebras | High-speed inference for latency-sensitive stages |
| SambaNova | High-throughput inference alternative |

### 7.2 External Service Connectors

**Architecture.** `External Service Manager → connector → secure credentials/OAuth → tool operation → normalized result → verification`. Every external service is integrated as a connector package containing: OAuth/API-key flow (tokens vault-stored, scoped, auto-refreshed), tool definitions in the shared registry, result normalization to internal schemas, and verification rules.

| Service | Connection Method | Key Capabilities | Governance Notes |
|---------|------------------|------------------|------------------|
| YouTube | OAuth 2.0 | Uploads, playlists, metadata, analytics, channel info | Uploads default to draft/approval; analytics read-only |
| TikTok | Login Kit / OAuth | Content posting, account integration, analytics | Publishing approval-gated per policy |
| Gmail | OAuth | Read/search, draft, send, reply, attachments | Sending is a sensitive action; drafts default for new flows |
| GitHub | OAuth / fine-grained tokens | Repos, branches, commits, PRs, issues, CI, releases | Production deploys via PR + approval |
| Supabase | Service-role (vault) | PostgreSQL, Storage, auth helpers | Direct writes gated by the Data Agent |
| Google Maps | API key (vault) | Places, geocoding, location queries | Read-only |
| OpenWeather | API key (vault) | Current, forecast | Read-only |
| Paystack | Secret key (vault) | Payment creation, verification, webhooks | Sensitive action class; spending limits enforced |
| Runway | API key (vault) | Video/image generation | Async jobs; creative approval flows |
| ElevenLabs | API key (vault) | TTS (JARVIS voice), voice workflows | Designated voice ID §5; cloning gated |
| Gemini/Veo | Service auth | Creative generation, video | Async jobs, queue-backed |

**Facebook is explicitly excluded.** The connector registry enforces this: no Facebook connector may be registered, and the permission engine denies any tool tagged with a prohibited platform. This is a policy-level exclusion, verifiable in self-diagnostics and audit.

**Adding a new service** is a bounded operation: connector package + tool specs + registration tests → review → approval → enabled. MCP servers (§3.5) follow the same path through the adaptor.

### 7.3 Creative Provider Routing

Creative jobs (image, video, music) route through the same router with creative-specific criteria: output quality tier, generation duration limits, per-clip cost ceilings, provider asset-return formats, and per-use-case templates. Jobs always run asynchronously with checkpointed stages, and creative outputs carry provenance metadata (provider, model, parameters, seed, licensing notes) stored with the asset.

---

## 8. Security & Governance Framework

### 8.1 Security Model: Defence in Depth

Security is a layered, cross-cutting framework rather than a module: perimeter (auth, rate limiting, TLS), boundary (the tool security wall §2.4), runtime (sandboxing, input validation), data (encryption, privacy filtering), and oversight (audit, monitoring, self-checks). The owner is the root of trust; no agent, model, or subsystem can alter the trust model.

### 8.2 Authentication & Authorization

Single-owner system by default: owner authentication (OAuth provider or email+passkey) protects the gateway; session tokens are short-lived and bound to device/channel. Authorization is role-scoped for any future shared-access mode (owner / reviewer / read-only viewer), with **owner permissions immutable from within the system**. Rate limiting is per-endpoint and per-identity with burst allowances for voice streams.

### 8.3 Permission Engine & Approval Gates — **(P)**

Permissions are declarative policy-as-data:

```
PermissionRule {
  tool | agent | action,
  sensitivity: low | medium | high | critical,
  effect: allow | deny | require_approval,
  conditions: {channel, amount, time_window, category, ...},
  overrides: owner_only, expires_at
}
```

| Element | Behaviour |
|---------|-----------|
| Tool-level permissions | Every tool declares its sensitivity class; invocation is checked before execution. Denials are structured and actionable ("request approval" path exists). |
| Sensitive-action confirmation | High/critical actions (sending email, publishing, payments, deploys to production, memory deletions) require confirmation on the user's active channel, with a readable summary and timeout fallback to the UI card. |
| Approval workflows | Multi-channel approval cards (UI, voice, email) with expiry, delegation notes, and immutable audit records of who approved what and when. |
| Financial controls | Spending limits and payment-approval thresholds are permission rules with hard enforcement in the Finance Agent. |

### 8.4 Secret & Credential Protection

Secrets live in an encrypted vault (Render environment variables for platform-level, an encrypted database vault for OAuth tokens) with: at-rest encryption, scoped and least-privilege tokens, automatic refresh, never serialized into logs, prompts, memory entries, or model contexts. The **Secret Guard** scans every outbound payload — model outputs, notifications, webhooks, memory writes — for credential patterns before transmission; a detection quarantines the payload and logs a security event. API-key configuration checks (§3.20) continuously verify expected keys are present and valid.

### 8.5 Input & Content Safety

- **Prompt-injection detection:** scanning on user input, tool results, memory writes, and file contents; injected instructions addressed at the system are quarantined and flagged rather than executed.
- **Malicious-file detection:** file-type validation against claimed type, content inspection, and strictly sandboxed opening; execution of untrusted code only inside the sandbox with no network egress by default.
- **Command safety:** no raw shell passthrough to models; command patterns are allowlisted and parameterized; the sandbox enforces resource limits and egress controls.
- **Data-access controls:** memory and file access scoped by sensitivity and project; private-scope data (relationship memory, preference details) is never used outside owner contexts.

### 8.6 Audit & Monitoring

**Audit logs** are append-only with integrity chaining (hash-linked rows): every sensitive action, approval, permission change, memory correction, deploy, and financial operation is recorded with trace ID, actor, timestamp, inputs (sanitized), and outcome. **Security monitoring** watches for anomalous patterns (unusual approval bursts, credential-access spikes, injection attempts) and files findings as owner-visible alerts. **Credential exposure detection** runs continuously on all outbound surfaces.

### 8.7 Self-Evolution Engine — Governed Autonomy

The evolution engine is the system's controlled mechanism for improving itself, and it is governed separately from ordinary conversation and API integration. Its loop:

```
Observe → Detect → Analyze → Plan → Risk Assess → Authorize → Isolate →
Modify → Build → Test → Security Gate → Regression → Review →
Git branch → Commit → PR → Approval → Merge → Deploy → Monitor →
Verify → Rollback (if needed) → Learn
```

**Components:** Self-Observation, Failure Detection, Health/Performance Analyzers, Root Cause Analysis, Improvement Planner, Risk Analyzer, Codebase Analyzer/Repository Mapper, Change/Patch Generator, Sandbox Manager, Test Runner, Regression Engine, Compatibility Checker, Security Gate, Secret Guard, Git Manager, GitHub Manager, Pull Request Manager, Deployment Manager, Health/Monitoring, Rollback Manager, Evolution Memory/Audit, Capability Discovery, Research Engine, and a Third-party Component Evaluator.

**Allowed building blocks** (as engineering components and references, not replacements for David AI; licenses and attribution preserved): [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk), [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent), [Aider](https://github.com/Aider-AI/aider).

**Constitutional prohibitions — the engine must never:**

> Remove owner permissions · expose secrets · disable audit logs · disable rollback · bypass authorization · grant itself unlimited permissions · directly overwrite production without the required workflow · create infinite self-modification loops.

**Risk tiers and approval defaults:** low-risk changes (docs, tests, non-production config) may proceed autonomously within the conservative default envelope; medium-risk changes auto-PR with required owner approval before merge; high/critical changes require owner approval before any deploy. The **emergency stop** halts the engine instantly and preserves full state. Every evolution cycle writes to **evolution memory**: what changed, why, evidence of testing, and outcome monitoring — the basis of continuous learning.

### 8.8 Governance Summary Matrix

| Concern | Mechanism | Owner Visibility |
|---------|-----------|------------------|
| Who can do what | Permission engine, tool-level rules | Full matrix in Settings |
| What got approved | Approval records, immutable audit | Approvals inbox + audit log |
| Where the secrets are | Vault + Secret Guard scanning | Config checks in diagnostics |
| What the AI changed about itself | Evolution engine PR workflow + evolution memory | PRs, reports, review sessions |
| What the AI learned about David | Learning artefacts in memory | Learned-profile review |
| Kill switch | Emergency stop on every channel | Always available |

---

## 9. Deployment Architecture

### 9.1 Platform & Topology

The system deploys on **Render** with `david-ademola.onrender.com` as the production endpoint, backed by **Supabase (PostgreSQL + Storage)** for the persistence layer and object storage for generated assets:

```
                    ┌────────────────────────────────────────────┐
                    │                RENDER                       │
                    │                                             │
  HTTPS ◄── TLS ──►│  Web Service: FastAPI app (gateway,         │
                    │    API, conversation, orchestration)        │
                    │                                             │
                    │  Workers: async task queue consumers        │
                    │   (long-running jobs, creative renders,     │
                    │    scheduled tasks, event-triggered work)   │
                    │                                             │
                    │  Cron triggers: health probes,              │
                    │    scheduled digests, memory maintenance    │
                    │                                             │
                    │  Static site: JARVIS frontend               │
                    └───────────────┬────────────────────────────┘
                                    │
                    ┌───────────────▼────────────────────────────┐
                    │              SUPABASE                       │
                    │  PostgreSQL: state, memory stores, audit,   │
                    │  projects, tasks, jobs, config              │
                    │  Vector index: pgvector (embeddings)        │
                    │  Storage: files, creative assets, traces    │
                    └────────────────────────────────────────────┘
```

### 9.2 Service Decomposition

| Render Service | Role | Scaling Notes |
|----------------|------|---------------|
| API (FastAPI) | Request handling, orchestration API, conversation | Scale vertically first; stateless apart from Postgres |
| Worker pool | Queue consumers for long-running jobs | Horizontal: workers are stateless, checkpoint-driven |
| Scheduler | Cron-style triggers (jobs, digests, maintenance) | Database-backed schedules, not platform-cron-only |
| Frontend | Static SPA | CDN-backed static site |

### 9.3 Environments & Release Flow

Three environments: **development → staging → production**. All code changes (human or evolution-engine-generated) flow through the Git/GitHub workflow: branch → CI (tests, security scan, build verification) → PR → review/approval → merge → staging deploy → staging smoke suite → canary production deploy → post-deploy monitoring (§3.7) → full rollout or automatic rollback. Environment parity is enforced: provider configs, feature flags, and permission policies are versioned alongside code.

### 9.4 Data Protection & Resilience

Database backups on a schedule with periodic restore-verification tests; point-in-time recovery where supported. Object storage with lifecycle tiers. Secrets in the vault only; environment variables for platform-level configuration. Cross-region considerations for availability are documented as a Phase-4 objective if David's usage demands it.

### 9.5 Reliability Budgets

| SLO | Target | Breach Response |
|-----|--------|-----------------|
| API availability | 99.5 % (free-tier Render constraints acknowledged) | Health alerts, graceful degradation (read-only memory mode, queued writes) |
| Task durability | 100 % (no lost jobs) | Checkpoint pipeline + dead-letter review |
| Voice pipeline latency (first audio) | < 2.5 s p95 | Provider fallback; reduced-motion/latency disclosure |
| Audit integrity | 100 % | Hash-chain verification in security health checks |

---

## 10. Implementation Priority & Phases

The 270 features are sequenced into five phases. The sequencing rule: **build the autonomous OS core first** (the fifteen priority capabilities), then capability breadth, then intelligence and autonomy refinements, then scale. Each phase ships a demonstrable milestone David can actually use.

### Phase 1 — Autonomous Core (Weeks 1–6)

**Theme: from chatbot to agent.** The foundation everything else depends on.

| Workstream | Scope |
|------------|-------|
| Goal/intent/planning | Goal Manager, intent detection, decomposition, versioned plans (§3.1) |
| Execution loop | Plan → Execute → Verify, checkpoints, retry policies, cancellation/resumption (§3.1, §3.6) |
| Memory v1 | Long-term + short-term stores, retrieval/ranking, privacy filter, write-back validation (§3.2) |
| Provider intelligence v1 | Provider registry, capability registry, health checks, fallback, circuit breakers (§7.1) |
| Permissions v1 | Permission engine, approval gates, audit log v1 (§8.3, §8.6) |
| Diagnostics v1 | Core/system/provider/database health checks + report format (§3.20) |

**Milestone:** David can give a multi-step goal; the system plans, executes with checkpoints, recovers from failures, remembers across sessions, and reports its own health.

### Phase 2 — Capability Width (Weeks 7–14)

**Theme: the working toolbox.** The agents and integrations that make autonomy useful.

| Workstream | Scope |
|------------|-------|
| Multi-agent skeleton | Orchestrator + agent registry, delegation/handoff protocol, loop protection (§6) |
| Coding agent | Repository understanding, generation, testing, Git/PR workflows, deployment monitoring (§3.7) |
| Research agent | Web search, deep research, verification, citations, reports (§3.8) |
| Tool intelligence | Full registry, dynamic selection, chaining, timeouts, performance monitoring (§3.5) |
| Persistent workspaces | Projects, files, tasks, decisions, artefacts, summaries (§3.15) |
| Background/scheduled work | Queue/worker hardening, scheduled and recurring tasks, event triggers (§3.6) |
| Connectors | YouTube, Gmail, GitHub, Supabase, Maps, OpenWeather, Paystack (read-mostly first) (§7.2) |
| Observability v1 | Traces, task/tool/provider history, dashboards, cost tracking (§3.14) |

**Milestone:** David can say "research X, build Y, deploy it, and schedule a weekly report" and watch it happen across agents with full traces and cost visibility.

### Phase 3 — Voice, Creative & Content (Weeks 15–22)

**Theme: the JARVIS experience.** Voice-first interaction and the content production engine.

| Workstream | Scope |
|------------|-------|
| Voice system | Full-duplex voice pipeline, ElevenLabs JARVIS voice, interruption, wake-word, confirmations (§5) |
| JARVIS frontend | Holographic UI, state-driven animations, task console, approvals inbox (§4) |
| Video/YouTube pipeline | Script → storyboard → scenes → VO → assembly → upload → metadata → analytics (§3.10) |
| Creative studios | Image/Video/Audio studios with templates and brand kit (§4.6, §3.9) |
| Social & automation | TikTok connector, content calendar, cross-platform publishing, workflow recipes (§3.18) |
| Notifications | Multi-channel notifications, reminders, webhooks (§3.16) |

**Milestone:** David speaks to a holographic interface; produces and publishes YouTube content end-to-end; content flows to social channels on a calendar.

### Phase 4 — Intelligence & Learning (Weeks 23–30)

**Theme: the system that improves.** Learning, quality, and self-awareness.

| Workstream | Scope |
|------------|-------|
| Learning system | Corrections, success/failure mining, preference adaptation, routing learning (§3.19) |
| Testing & quality gates | Agent scorecards, provider/memory/security test suites, output quality evaluation (§3.13) |
| Full memory suite | Episodic/procedural/relationship/decision stores, memory graph, consolidation (§3.2) |
| Advanced web intelligence | Monitoring, price/news subscriptions, browser automation hardening (§3.8) |
| Financial flows | Payment approvals, spending limits, reconciliation, digests (§3.17) |

**Milestone:** David visibly sees the system get better at his workflows; quality is measured and reported, not assumed.

### Phase 5 — Governed Self-Evolution (Weeks 31–40)

**Theme: controlled autonomy over itself.** The most sensitive capability, built last, on the firmest foundation.

| Workstream | Scope |
|------------|-------|
| Evolution engine v1 | Observe → detect → analyze → plan → sandboxed modify → build/test → PR → approval → deploy → monitor → rollback → learn (§8.7) |
| Security hardening | Full injection defence, malicious-file pipeline, penetration-style self-checks, Secret Guard sweep of all surfaces (§8.5) |
| Execution replay & advanced diagnostics | Full replay, agent evaluation dashboards, benchmarking-driven routing (§3.13, §3.14) |
| Yoruba voice GA | Yoruba STT/TTS coverage completion and honest capability reporting (§5.8) |
| Scale | Worker scaling, caching layers, availability improvements per §9.5 |

**Milestone:** The system proposes, proves, and (with approval) ships improvements to itself — with rollback always one step away.

### 10.1 Phase Dependencies & Risk Notes

Phase 2 depends on Phase 1's memory and permission foundations; Phase 3 depends on Phase 2's connectors and queue hardening; Phases 4 and 5 deliberately come last because learning and self-evolution are only safe on top of strong audit, permissions, and quality gates. Two standing risks are called out: **Render free-tier constraints** (cold starts, memory limits) may require worker-tier upgrades before Phase 3's creative workloads; and **provider API changes** (especially creative providers) are mitigated by the adapter layer but require periodic adapter maintenance scheduled into each phase.

### 10.2 Definition of Done (All Phases)

No phase is complete until: all tests green in CI, regression suite passing, security scan clean, audit trail verified for sensitive paths, diagnostics reporting green for every built subsystem, and David has personally exercised the milestone workflow end-to-end in voice and text.

---

## Appendix A — Feature-to-Priority Cross-Reference

The fifteen priority capabilities map to specification sections as follows, for fast navigation:

| Priority Capability | Primary Sections |
|---------------------|------------------|
| Autonomous Agent Core | §3.1, §6 |
| Goal → Plan → Execute → Verify | §3.1, §3.6 |
| Advanced Long-Term Memory | §3.2 |
| Multi-Agent Orchestrator | §6 |
| Dynamic Tool Selection | §3.5 |
| Self-Correction & Failure Recovery | §3.1, §3.6, §3.13 |
| Coding Agent | §3.7, §6.3 |
| Research Agent | §3.8, §6.3 |
| Permission & Human Approval Engine | §3.12, §8.3 |
| Provider Intelligence / Fallback | §7.1 |
| Persistent Project Workspaces | §3.15 |
| Background & Scheduled Tasks | §3.6, §2.6 |
| Self-Diagnostics | §3.20, §9.5 |
| Agent Observability & Tracing | §3.14, §6.6 |
| Learning From Corrections | §3.19 |

## Appendix B — Exclusions & Out-of-Scope

The following are explicitly out of scope and must remain so unless David revises this specification: **any Facebook integration** (policy-enforced at the connector registry), unrestricted model access to credentials or infrastructure, autonomous production overwrites without workflow, unlimited self-modification loops, unreviewed self-modification, and learning that mutates behaviour without a reviewable, reversible artefact trail.

## Appendix C — Glossary

| Term | Definition |
|------|------------|
| Agent | A stateless, permission-scoped specialist worker that executes contracted subtasks |
| Capability | A unit of function (e.g., "text-to-image") addressed through the router, independent of provider |
| Checkpoint | A persisted snapshot of job/plan state enabling resumption |
| Connector | A versioned package integrating one external service (auth, tools, normalization) |
| Correlation/trace ID | A single identifier linking all events of one request across subsystems |
| Governance | The permission/approval/audit framework that keeps the owner sovereign |
| Tool Security Boundary | The enforcement line where model proposals become validated, authorized, executed actions |
| Workspace | A persistent, scoped project environment with its own memory view |

---

*End of specification — David Ademola AI Master Specification v2.0.*
