# David AI Agent Operating System — Replacement Architecture

## Experience Model

The replacement is a **personal AI operating system**, not a page collection or chat skin. Its primary surface is Mission Control: a request enters as an outcome, David produces a governed plan where applicable, work appears as a run with tools and approvals, and durable outputs return as artifacts linked to the project, task, or evidence that created them.

The operating system has six persistent domains: **Mission**, **Runs**, **Create**, **Knowledge**, **Automation**, and **System**. A compact mobile rail and responsive sheet provide the same route map as desktop navigation.

## Module Map

| Module | Responsibility | Primary contracts |
|---|---|---|
| `os/AgentOsShell` | Authentication gate, responsive navigation, global status, route transition frame | `auth.me`, `overview`, `providers.status` |
| `os/MissionControl` | Conversational outcome intake, Ryan lifecycle, live transcript, secure evidence tray, plan-or-answer dispatch | chat, voice, attachments, agent runs |
| `os/RunConsole` | Governed runs, canonical Fabric controls, approvals, execution history, artifacts and plan versions | agent runs, canonical agent |
| `os/CreateStudio` | Separate Website, Image, Video, Audio, Content, Campaign, and Research sub-workspaces | generation, content, media projects, research |
| `os/KnowledgeWorkspace` | Projects, tasks, memory, retention controls, evidence/artifact context | projects, tasks, memory, artifacts |
| `os/AutomationWorkspace` | Manual and scheduled automations with approval-safe status | automations |
| `os/SystemWorkspace` | Provider observatory, connection status, encrypted key entry, connector registry and availability detail | providers, provider settings, connectors |

## Routing

`/mission` is the default primary route. `/dashboard` remains an at-a-glance command surface. `/runs`, `/create/*`, `/knowledge/*`, `/automation`, and `/system/*` render dedicated modules. Legacy paths remain as compatibility aliases during the preview period but resolve to new replacement components, not legacy visual components.

## Interface Semantics

The shell uses a dark spatial field, luminous cyan for ready system state, violet for planning and governed work, amber for review, green for confirmed completion, and red only for errors requiring action. The visual language emphasizes information density, readable hierarchy, keyboard and touch reachability, and controlled motion that respects `prefers-reduced-motion`.

The David Core orb is not an interaction substitute. It shows one of `resting`, `ready`, `listening`, `thinking`, `speaking`, or `attention` based on actual state returned by the UI operation, browser audio events, or permission failures.

## Delivery Rule

No new release is published from this replacement effort until the user explicitly approves publishing after preview validation.
