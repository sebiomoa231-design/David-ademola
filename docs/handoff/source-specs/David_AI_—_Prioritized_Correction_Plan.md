# David AI — Prioritized Correction Plan

## Executive recommendation

Do not begin by adding more screens, provider names, or decorative animation. First make the existing application runnable, then build one secure end-to-end workflow, and only then deepen the cinematic and voice experiences. The current bundle is visually broad but technically uneven: the frontend has a substantial shell, while the backend contracts, persistence, governance, and runtime packaging are incomplete.

## Priority 0 — Make the existing project run

| Correction | Location | Acceptance criterion |
|---|---|---|
| Resolve the root-route conflict | `frontend/app/page.tsx`, `frontend/app/[[...slug]]/page.tsx` | `npm run build` completes successfully. Use either a root page plus explicit routes or only a catch-all route; do not keep both matching `/`. |
| Add frontend error and loading states | App shell and API-driven screens | A failed backend call produces a clear degraded state rather than a blank panel; loading states are visible and recoverable. |
| Add backend application entrypoint | New `app/main.py` or equivalent | A real FastAPI application starts locally, mounts all supplied routers, exposes health, and shuts down cleanly. |
| Add dependency and deployment manifests | Root `requirements.txt`/`pyproject.toml`, Dockerfile or Render manifest | A clean environment can install dependencies and start the backend using documented commands. |
| Complete or remove broken provider imports | `app/providers/intelligent_router.py` | Import smoke test succeeds; every imported adapter/base/logging module exists and has tests. |
| Add CI checks | Repository CI | Typecheck, unit tests, production build, Python compilation/import, and startup smoke test all run on every change. |

## Priority 1 — Establish the secure vertical slice

Implement one workflow before expanding the feature catalogue:

> Authenticated user request → structured intent/goal → persisted plan → policy check → owner approval when required → provider execution → verification → persisted result → trace/audit event → text and voice response.

The minimum durable data model should include users, sessions, conversations, goals, plans, plan steps, runs, approvals, provider calls, audit events, and artefacts. In-memory Python lists are not adequate for plans, task history, approvals, or audit data because restarts lose state.

## Priority 2 — Correct the cinematic and animatic interface

The current interface should be upgraded from a styled dashboard into a state-driven cinematic command centre. The goal is not merely more effects; every animation should communicate system state and remain usable when motion is disabled.

| Required correction | What to build |
|---|---|
| State-driven visual engine | Define explicit states such as idle, listening, thinking, planning, awaiting approval, executing, verifying, completed, degraded, and emergency stop. Drive the core visual, typography, sound cues, progress timeline, and activity feed from the same state machine. |
| Cinematic core scene | Replace the mostly decorative core visual with a composed scene: layered orb/core, energy rings, particles, volumetric glow, scan sweep, status typography, and controlled transitions. Use CSS/WebGL only where it improves the experience; provide a lightweight fallback. |
| Animatic/timeline layer | Add a visible execution timeline with step cards, dependencies, current frame/phase, tool/provider activity, checkpoints, retries, and approval pauses. The user should be able to understand what the system is doing without relying on animation alone. |
| Motion design system | Define durations, easing, entrance/exit transitions, interruption behaviour, and reduced-motion variants. Avoid unrelated looping animations that make the interface feel decorative rather than intelligent. |
| Voice-visual synchronization | Synchronize listening waveform, transcription text, speaking indicator, captions, and core state with actual audio lifecycle events rather than timers. |
| Creative studio reality | Replace placeholder completion states with durable generation jobs, progress, failed/retry states, artefact previews, metadata, and download/export actions. |
| Responsive and accessible presentation | Ensure keyboard access, focus visibility, contrast, screen-reader labels, reduced motion, mobile layout, and error recovery. |
| Visual QA | Add screenshot/browser tests for dashboard, chat, voice, approval, error, and reduced-motion states. |

The important correction is architectural: the cinematic layer must be a **visualization of real execution state**, not a separate animation that implies work is happening when the backend is idle or unavailable.

## Priority 3 — Complete the voice system

The existing ElevenLabs/Piper foundation should be wrapped in a single channel pipeline so voice and text use the same governed execution path.

| Voice area | Required correction | Acceptance criterion |
|---|---|---|
| Input | Implement microphone capture, audio chunking, transcription, and clear permission/error handling. | User can start/stop listening and sees a transcript or honest failure state. |
| Conversation | Add turn detection, interruption/barge-in, cancellation, and follow-up context. | David can interrupt speech and the system stops or revises the response safely. |
| Output | Integrate ElevenLabs as the primary voice and Piper/local fallback where appropriate. | Audio lifecycle is represented in the UI and failures fall back to text. |
| Full duplex | Add a WebSocket or equivalent streaming channel for audio/events. | Partial transcript, state, and audio events update in real time. |
| Wake word | Treat wake-word activation as an optional, permissioned feature. | No always-on microphone behaviour without explicit user consent. |
| Sensitive actions | Require spoken confirmation plus an equivalent visual approval action for high-risk operations. | Sending, publishing, deploying, or spending cannot be triggered by ambiguous speech alone. |
| Voice identity | Store the selected voice/provider in configuration and expose health/capability state without exposing keys. | UI distinguishes configured, unavailable, degraded, and fallback states. |
| Yoruba | Verify STT/TTS quality and report honestly if only English is supported. | No UI claim of Yoruba capability without a tested provider path. |
| Testing | Add mocked provider tests, audio-format tests, interruption tests, and browser microphone tests. | Voice regressions are caught without requiring live credentials in CI. |

## Priority 4 — Add governance before external actions

The specification’s most important safety rule is that models propose actions and backend policy services decide whether they may execute. Implement this before GitHub push, publishing, payments, deployment, or messaging.

The minimum governance components are an action registry, risk classification, user/role permissions, approval records, spending and rate limits, secret isolation, immutable audit events, emergency stop, and rollback/cancellation. Facebook should be rejected by the connector registry, not merely omitted from documentation.

## Priority 5 — Reconcile the frontend with the backend

Create a contract matrix from `frontend/lib/api.ts`. For each endpoint, mark it as implemented, deferred, or removed. The interface should not show a working-looking control for an endpoint that is absent or unconfigured. Every API response should include a capability state and an actionable error category such as unavailable, needs approval, needs credentials, degraded, or failed.

## Recommended delivery sequence

| Stage | Deliverable | Stop condition |
|---|---|---|
| A | Buildable frontend and startable backend | Clean build, import, and startup checks |
| B | Authenticated text vertical slice | Persisted result, approval gate, trace, and restart recovery |
| C | Real execution-state visualization | Timeline and cinematic core reflect actual backend events |
| D | Reliable voice channel | Transcription, synthesis, interruption, captions, fallback, and tests |
| E | First governed connector | One integration works with least privilege, approval, audit, and rollback |
| F | Broader agents, studios, schedules, and learning | Each feature has a real backend contract, durable state, and verification |

## Final answer in plain terms

Correct the **runtime and contract problems first**, then turn the existing visual shell into a state-driven cinematic interface, and finally complete voice as a real-time channel with interruption and approval handling. The current files are a useful foundation, but the missing backend and governance work must be completed before the interface can honestly be presented as a complete autonomous AI operating system.
