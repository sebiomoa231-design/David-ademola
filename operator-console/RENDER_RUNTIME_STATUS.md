# Render Runtime Status

**Checked:** 18 August 2026

The public Render deployment at `https://david-ademola.onrender.com` identifies itself as **David Ademola AI**, reports `status: online`, and reports `version: handoff-scaffold` at its root route.

The public API documentation exposes the following deployed route groups:

| Route group | Observed status | David AI Operator treatment |
| --- | --- | --- |
| `/api/health`, `/health`, `/api/readiness` | Documented as read-only health routes | May be surfaced as external service health only. |
| `/api/voice/status`, `/api/voice/transcribe`, `/api/voice/synthesize`, `/api/voice/synthesize/stream` | Documented and previously verified for voice use | May power the secured server-side voice adapter. |
| `/api/orchestrator/*` | Documented, but `GET /api/orchestrator/status` returned `{"detail":"Orchestrator not initialized"}` | Must remain unavailable/degraded in the interface; do not report execution readiness. |
| Memory, project, task, file, and persistent operating-system record routes | Not exposed in the live public API documentation | The full GitHub backend must be deployed and initialized before these can become backend-authoritative. |

The current React/Express project keeps its private workspace records in its managed database. That remains a temporary operator foundation rather than a replacement for the supplied backend persistence model.

## Cinematic Interface Boundary

The David AI Operator presentation layer now provides an abstract reactive core, real microphone-amplitude and voice-output analysis, interruption feedback, pause/resume controls, transcript clearing, responsive layouts, local accessibility preferences, and a telemetry strip based on live browser time, voice state, active persisted run context, and service health.

The following requested experiences remain deliberately unavailable until the authoritative backend persistence and control-plane deployment is initialized: notifications backed by a service, external application/device execution, confirmation and evidence for sensitive external actions, and any labelled demonstration mode. David AI Operator does not substitute simulated external completion for these missing capabilities.

## Authoritative Repository Deployment Contract

The repository README documents a Render build command of `bash build.sh` and a FastAPI start command of `uvicorn main:app --host 0.0.0.0 --port $PORT`. The available production `Procfile` and `Dockerfile` instead run the compatible Gunicorn/Uvicorn-worker command `gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}`. The cloned source does not currently contain the `render.yaml` referenced by its README, so the active Render service configuration should be reviewed in Render before changing the start command. Its deployment environment must be populated from `.env.example`; provider keys and database credentials remain server-side and must not be copied into David AI Operator’s browser bundle.

Once this complete repository build is deployed and initialized on Render, the operating-system integration should be extended against the exposed backend routes and persistence contract. Until then, the current live Render deployment must continue to be treated as a **voice-and-health service**, not as the authoritative persistence/control-plane runtime.

## Connected Render Service Inventory

The connected Render workspace exposes the authoritative service **David-ademola** at `https://david-ademola.onrender.com` (`srv-d9qg4bp42hec73e98dq0`). It is configured for automatic deployment from the repository `sebiomoa231-design/David-ademola` on branch `feat/david-ai-cinematic-complete`.

The deployed service configuration still uses an older Piper-model download build command and `uvicorn main:app --host 0.0.0.0 --port $PORT` start command. This differs from the current authoritative source, which provides a Gunicorn/Uvicorn-worker production entrypoint and server-side ElevenLabs voice routing. The service must be reconciled to the intended authoritative branch and current deployment configuration, then redeployed and verified before the operator treats its persistence/control-plane routes as live.
