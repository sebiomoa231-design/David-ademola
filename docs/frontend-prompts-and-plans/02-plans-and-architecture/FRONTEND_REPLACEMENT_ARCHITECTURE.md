# David AI Elite Agent Operating System — Frontend Replacement Architecture

**Status:** Preview implementation in progress. This document governs the replacement UI only; it does not introduce a new provider router, credential store, execution engine, or database.

## Product model

David AI is implemented as **one governed personal AI operating system** with two views of the same system: the immersive Agent Nexus interface and the Command Center surface. Both views use the existing authenticated server procedures and canonical Intelligence Fabric boundary. The interface creates objectives, shows plans and approvals, invokes only enabled capabilities, retains artifacts with provenance, and leaves unavailable work visibly unavailable rather than simulating success. [1] [2] [3]

| Layer | Replacement responsibility | Canonical source of truth | UI rule |
|---|---|---|---|
| David Core | Mission state, wake feedback, listening, transcription, thinking, execution, Ryan playback, errors | Mission workspace + voice activity state | State changes follow actual recorder, transcription, response, and audio-element events. |
| Mission workspace | Chat, voice, attachments, governed planning, latest context | `chat`, `voice`, and `agentRuns` server procedures | Never claim a reply, transcript, or audio playback before the backend or audio element confirms it. |
| Agent Runs | Goal creation, policy review, approval, execution, pause, resume, cancellation, artifacts | Local Agent Run runtime plus canonical governed run bridge | Show planning and approval boundaries before execution. |
| Creation studios | Website, content, image, video, marketing, research | Existing provider-backed studio contracts and Library persistence | Render actual outputs when produced; otherwise render a precise unavailable or configuration state. |
| Context OS | Projects, tasks, memory, artifacts, connectors, provider settings, automations | Existing protected backend procedures and persistence tables | Never create frontend-only records that pretend to be durable. |

## Replacement navigation and workspace architecture

The replacement is a fixed desktop operating-system rail and a sheet-based mobile navigation model, with a stable command header and route-rendered workspace body. The navigation is intentionally grouped by operator intent rather than by unrelated feature pages: **Core OS**, **Intelligence & Create**, **Growth & Automation**, and **System**. Each route uses an existing workspace component or a truthful status surface connected to the same backend contracts. [1] [4]

| Navigation area | Routes | Connected workspace |
|---|---|---|
| Core OS | `/dashboard`, `/chat`, `/agent-runs`, `/activity`, `/skills` | Command dashboard, David Core mission control, governed run board |
| Intelligence & Create | `/website-development`, `/video`, `/image-generation`, `/voice-speech`, `/content` | Creation Hub or Mission Workspace with Ryan/Whisper lifecycle |
| Growth & Automation | `/marketing`, `/automations`, `/connectors-page`, `/templates` | Marketing Studio, Automation Desk, Connector Context Desk |
| System | `/projects`, `/memory`, `/connectors-page`, `/settings` | Project Vault, Memory Vault, integrations, provider settings |

## Design system

The visual system uses a dark ink base, cyan operational signals, restrained violet focus accents, thin data-grid texture, rounded technical panels, and a large stateful David Core. Motion is reserved for real state transitions and is disabled by user reduced-motion preferences. Typography uses high-contrast headlines, small uppercase system labels, and compact metrics rather than decorative dense text.

> **Truthfulness rule:** A visual card is not evidence that an action completed. Completion, artifacts, provider availability, voice playback, and approvals must be driven by an authenticated backend response or browser media event.

## Acceptance boundaries

The replacement is accepted only when the desktop and mobile shell navigate to real workspaces, voice state tracks true media lifecycle, Agent Runs require explicit approval where policy requires it, and creation work links to the existing server contracts. Live provider-dependent functions remain subject to configured credentials, quota, worker availability, and CORS or deployment configuration. [2] [3] [4]

## References

[1]: file:///home/ubuntu/david-ai/client/src/pages/Home.tsx "Live Agent Nexus route composition"
[2]: file:///home/ubuntu/david-ai/client/src/components/AgentMissionWorkspace.tsx "Voice, transcript, planning, and Ryan playback lifecycle"
[3]: file:///home/ubuntu/david-ai/client/src/components/AgentRunBoard.tsx "Governed Agent Run controls"
[4]: file:///home/ubuntu/david-ai/client/src/components/EliteCommandCenterShell.tsx "Elite operating-system navigation shell"
