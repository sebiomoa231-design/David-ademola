# David AI Elite Frontend Replacement Capability Matrix

## Purpose

This matrix is the implementation boundary for the complete David AI frontend replacement. It records what the existing backend actually supports, what requires review or approval, and what must remain visibly unavailable until an external integration is connected. The new interface must not manufacture success states, rendered media, deployments, or connector access.

| Domain | New workspace | Real frontend contract | Operational state | Evidence |
|---|---|---|---|---|
| Core agent | Mission Control | `chat.history`, `chat.send`, `chat.sendWithAttachments`, `agentRuns.plan` | Connected; text responses and governed planning are real | `server/routers.ts:459-496`, `173-202` |
| Voice | Voice bridge in Mission Control | `voice.upload`, `voice.transcribe`, `voice.speak`; Ryan Piper playback | Connected subject to browser microphone permission and runtime voice assets | `server/routers.ts:517-537`, `server/voiceSynthesis.ts` |
| Attachments | Evidence tray | `attachments.upload`, `chat.sendWithAttachments` | Connected; 19 MB maximum, supported MIME types, user-scoped storage | `server/routers.ts:499-515`, `472-495` |
| Governance | Run Console | plan, execute, pause, resume, cancel, replan, approvals, plan versions, events, artifacts | Connected; approval must remain prominent before external action | `server/routers.ts:173-202` |
| Intelligence Fabric | Canonical Run bridge | `canonicalAgent.createRun`, `approveAndExecute`, `getRun` | Connected only when `DAVID_CANONICAL_API_URL` is configured | `server/routers.ts:120-171` |
| Providers | Provider Observatory | provider status, encrypted per-user key save, test, override and probe | Connected; only configuration state and health outcomes may be shown | `server/routers.ts:264-272`, `671-735`, `795-808` |
| Website creation | Website Studio | `generation.website`, `websiteBuilder.create`, `websiteBuilder.modify` | Connected for blueprint/workspace generation; no preview or deployment claim | `server/routers.ts:296-315`, `770-781` |
| Image generation | Image Studio | `generation.image`, `generation.imageModels` | Connected when the configured image service returns a URL | `server/routers.ts:317-337` |
| Video | Video Studio | `generation.videoPlan`, `mediaProjects` | Connected for production planning only; rendering and image-to-video are unavailable | `server/routers.ts:339-369`, `383-391` |
| Audio creation | Audio Studio | Ryan TTS is real; music and generic audio generation are not connected | TTS connected; generative audio unavailable | `server/routers.ts:517-537`, `368-369` |
| Content | Content Studio | `content.generateArtifact`, content list/create | Connected; external distribution creates a review/approval record rather than sending | `server/routers.ts:539-610` |
| Marketing | Campaign Studio | `content.generateMarketingArtifact` | Connected for reviewable campaigns; delivery remains approval-gated | `server/routers.ts:611-668` |
| Research | Evidence Desk | `agentRuns.research` with user-supplied HTTPS URLs | Connected; provenance is stored and source claims remain review-required | `server/routers.ts:203-261` |
| Projects | Project Command | `projects.list`, `projects.create`, `projects.delete` | Connected | `server/routers.ts:427-437` |
| Tasks | Task Command | `tasks.list`, `tasks.create`, `tasks.update`, `tasks.delete` | Connected | `server/routers.ts:439-457` |
| Memory | Memory Vault | list/create/remove plus retention settings | Connected; context and retention controls are user-scoped | `server/routers.ts:393-425` |
| Automation | Automation Control | list/create/toggle plus Heartbeat scheduling | Connected for saved automation; the UI must state that schedules do not bypass approval safeguards | `server/routers.ts:737-763` |
| Connectors | Connector Registry | connector status and explicit precondition errors | GitHub, Gmail, and browser session access are unavailable in production without connectors | `server/routers.ts:274-294` |
| Authentication | Secure entry | Manus OAuth and protected procedures | Connected; all operational pages require an authenticated user | `server/_core/oauth.ts`, `server/_core/trpc.ts` |
| Storage | Evidence and audio storage | storage proxy helpers plus signed URLs | Connected; no direct client credential exposure | `server/storage.ts`, `server/routers.ts:476-513` |

## Required Availability Language

The UI must distinguish the following states in copy, labels, controls, and activity timelines.

| State | Meaning | Interface treatment |
|---|---|---|
| **Ready** | A real server-side operation is configured and may be started | Show the real action button and progress tied to mutation state |
| **Needs configuration** | The contract exists but a provider or environment requirement is missing | Show the dependency and a route to Provider Settings; do not show success |
| **Awaiting approval** | A potentially external action has been prepared but not authorized | Show the approval record, action scope, and no dispatch success |
| **Plan only** | A real plan, blueprint, or storyboard is available but no final output is connected | Show the reviewable plan and an explicit boundary badge |
| **Unavailable** | The deployment cannot perform the requested operation | Disable execution and describe the required external integration |
| **Failed** | The backend reported an error | Show a retry action only when it repeats the same real request and preserve the error context |

## Replacement Acceptance Criteria

The replacement is acceptable only when it provides a single coherent operating-system shell; modular route-driven workspaces; visible system and run state; a primary Mission Control surface; governed execution; provider and connector truthfulness; workspace-specific creation flows; responsive navigation; and no imported visual layouts from the current `EliteCommandCenterShell`, `AgentMissionWorkspace`, or `AgentCreationHub` implementations.

## Non-Negotiable Boundaries

The frontend must preserve encrypted provider-key handling, protected procedure access, user-scoped attachment paths, immutable provenance-bearing artifacts, current Ryan-only output voice rules, and pending-approval requirements. The replacement must not display fabricated generated images, completed video renders, published content, deployed sites, live Gmail data, GitHub data, browser-session data, or autonomous external actions when the backend does not return them.
