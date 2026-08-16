# David AI Unified Capability Matrix

## Canonical Architecture Decision

**David AI** is the single intelligence. The FastAPI service in this repository is the canonical shared service boundary for the Command Center, including chat, provider routing, voice status and synthesis, memory, conversations, projects, tasks, Library, generations, and the Intelligence Fabric. Agent Nexus is retained as the advanced workspace, but it must call verified canonical contracts through an explicit server-side bridge rather than introduce another public provider, storage, or approval system.

| Capability | Command Center evidence | Agent Nexus evidence | Canonical service/data boundary | Verified state | Implementation next step |
|---|---|---|---|---|---|
| Chat | `frontend/lib/api.ts` calls `/api/chat` | Existing mission workspace preserves its own UI | FastAPI chat and conversation services | Command Center contract implemented; cross-interface bridge pending | Add server-side bridge and consume shared conversation records in Agent Nexus |
| Memory | `/api/memory` client methods and Memory workspace | Existing scoped-memory workspace | `david_memories` through `SupabasePersistence` | Command Center implemented; shared-store bridge pending | Route Agent Nexus memory reads and writes through canonical API |
| Projects | `/api/projects` client methods and Projects workspace | Existing project workspace | `david_projects` through `SupabasePersistence` | Command Center implemented; shared-store bridge pending | Route Agent Nexus project context through canonical API |
| Tasks | `/api/projects/tasks` client methods and Tasks workspace | Existing task-aware run planning | `david_tasks` through `SupabasePersistence` | Command Center implemented; shared-store bridge pending | Associate canonical tasks with governed agent runs |
| Conversations | `/api/conversations` client methods | Agent mission interface has local conversation model | `david_conversations` and `david_messages` | Command Center implemented; shared-store bridge pending | Add canonical conversation retrieval contract to Agent Nexus |
| Agent runs | `/api/intelligence/*` methods and Agent runs workspace | Agent Run Board, plans, controls, diagnostics | Intelligence Fabric store, currently JsonStorage | Functional but not yet Supabase-durable | Add Supabase-backed Fabric record persistence with safe local fallback |
| Provider router | Readiness/providers endpoints | Existing multi-provider router | Backend provider configuration and canonical service contracts | Two routers currently exist | Define bridge use and avoid exposing a second public provider configuration |
| Failover | Fabric candidate fallbacks and provider registry | Existing bounded failover router | Provider adapter/registry boundaries | Contract tests present; live provider success varies by credential | Record normalized fallback diagnostics in canonical run events |
| Website | `/api/website/generate`, persisted generation metadata | Website Studio blueprints | `david_generations` | Blueprint generation is implemented | Store outputs and expose canonical history to both interfaces |
| Image | Capability registry and Library contract | Image Studio project persistence | Creative adapter plus `david_generations` | Unavailable unless configured adapter reports READY | Keep capability unavailable until adapter succeeds and persists output |
| Video | Capability registry and studio shell | Video Studio project persistence | Creative adapter plus `david_generations` | Plan persistence implemented; rendering adapter may be unavailable | Preserve truthful capability state and unified history |
| Music/artwork/enhance/edit/reshoot | Truthful unavailable studio shells | Advanced creative workspaces are retained | Capability registry and Library | Explicitly unavailable unless an adapter is connected | Do not fabricate output; expose provider/credential dependency |
| Voice | `/api/voice/status` and `/api/voice/synthesize` | Ryan-only Piper voice pipeline | Ryan Piper backend service | Backend contract implemented; device validation remains separate | Bridge canonical status and playback response to Agent Nexus where appropriate |
| Library | `/api/library/*` and Library workspace | Artifact surfaces | Private `Davidai` bucket and `david_assets` | Canonical contract implemented when Supabase is enabled | Add canonical Library bridge and signed URL consumption |
| Approvals | Fabric authorization/run lifecycle | Agent Run Board approval gates | Fabric policy and approval records | Implemented in both surfaces but not yet one record store | Make canonical Fabric approval events available to Agent Nexus |
| Diagnostics | Health, readiness, provider, Library status | Agent run diagnostics | Health/readiness and run events | Implemented with safe redaction | Normalize shared diagnostics read model |
| Automation | Capability registry and truthful shell | Existing automation workspace | Fabric policy/adapter registry | Unavailable unless a real adapter is configured | Retain approval requirement and explicit unavailable state |

## Non-Negotiable Boundaries

The application will not create a second GitHub repository, Render service, Supabase project, storage bucket, public key path, provider-key store, or public agent API. Server-only Supabase and provider credentials remain outside frontend bundles. Unsupported capabilities must return an explicit unavailable state rather than a simulated completion.

## Immediate Implementation Sequence

The next implementation slice is to make Intelligence Fabric run records durable in the existing Supabase project while retaining safe local fallback only when Supabase persistence is deliberately disabled. The following slice will add the server-side Agent Nexus bridge to the canonical FastAPI contracts for memory, projects, tasks, conversations, Library, governed runs, approvals, and diagnostics. Creative capability work will follow only for adapters that successfully pass real readiness and persistence checks.
