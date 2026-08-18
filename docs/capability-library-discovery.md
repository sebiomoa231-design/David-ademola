# David-Ademola Capability Library Discovery

**Repository inspected:** `sebiomoa231-design/David-ademola`  
**Branch:** `main`  
**Baseline commit:** `ec356474` — *Upgrade Intelligence Fabric without removing supplied sources*

## Existing internal architecture

The repository already contains a Python FastAPI application under `app/` and a separate `david_fabric/` Intelligence Fabric package. The Fabric package exposes the following capability-system primitives:

| Area | Existing implementation |
|---|---|
| Capability registry | `david_fabric/services/registry.py` loads `config/capabilities.yaml`, enriches entries with adapter readiness, and deterministically matches request keywords. |
| Capability API | `david_fabric/api/router.py` exposes capability lists, details, adapters, agents, tools, providers, routing, goals, plans, runs, artifacts, and verification. |
| Planning and execution | `david_fabric/services/planner.py`, `execution.py`, `policy.py`, and `verification.py` provide the internal planning, authorization, execution, and verification layers. |
| Stored run evidence | `david_fabric/storage/db.py` persists goals, plans, runs, events, attempts, artifacts, and verification. |
| Provider handling | `app/providers/ai_router.py` and provider adapters support backend-only provider routing and fallback. |
| Voice | `app/services/voice_engine.py` and `app/providers/piper_tts.py` provide the Ryan Piper path; the README records that the voice model is retrieved during build rather than committed. |

## Registered coverage found

`config/capabilities.yaml` already registers native and adapter-bound entries for core intelligence, research, website development, image, video, audio, TTS, STT, marketing, web automation, controlled tools, background jobs, artifacts, evaluation, QA, coding, deployment, and observability.

## Integration constraints

1. The registry must remain manifest-driven; repository files cannot become executable capabilities merely by existing.
2. Provider routing and capability routing must remain separate.
3. Unavailable adapters must remain unavailable in responses; no preview, render, deployment, or artifact success can be fabricated.
4. Secrets must remain in server-side environment variables and never be copied into manifests, generated artifacts, browser responses, or Git history.
5. The Node-based Agent Nexus preview must be bridged to this repository through explicit, tested contracts; it must not be copied into an arbitrary unvalidated execution path.
