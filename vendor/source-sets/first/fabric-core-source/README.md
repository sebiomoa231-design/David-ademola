# David AI — Intelligence Fabric Backend

This package is a **unified David AI control plane** built around the David Ademola backend.

It brings the supplied repositories into one repository as source/integration material and
provides one capability registry, routing layer, goal/run API, policy layer, health model,
artifact/run persistence, and service integration boundary.

## Important architecture rule

The external repositories are **not blindly merged into one Python process**. They remain under
`vendor/` so their original runtimes, licenses, Dockerfiles and dependency trees are preserved.
David's Intelligence Fabric is the single control plane that decides which capability to use.

This avoids Python/Node/Go dependency collisions while still making the entire collection available
to David.

### Supplied source groups

- `vendor/David-ademola-main` — primary David application/backend source
- `vendor/DavidAI-backend-with-voice` — alternate David FastAPI/voice backend
- `vendor/david-ai-backend` — creative Node/Mongo backend
- `vendor/agent-framework-main` — multi-agent/orchestration reference
- `vendor/OpenHands-main` — coding/agent execution capability
- `vendor/browser-use-main` — browser-agent capability
- `vendor/playwright-main` — browser automation
- `vendor/ComfyUI-master` — image/creative workflow engine
- `vendor/Wan2GP-main` — video/media generation
- `vendor/chatterbox-master` — TTS/voice generation
- `vendor/faster-whisper-master` — speech-to-text
- `vendor/langfuse-main` — observability/evaluation
- `vendor/langgraph-main` — stateful agent orchestration
- `vendor/n8n-master` — workflow/integration automation
- `vendor/temporal-main` — durable execution
- `vendor/coolify-main` — deployment platform
- `vendor/dokploy-canary` — deployment platform

## What this repository is

David AI remains the product and user-facing API.

The Intelligence Fabric supplies:

1. capability discovery
2. capability routing
3. agent/skill/tool registration
4. goal/run persistence
5. policy checks
6. health/fallback selection
7. external service adapters
8. event recording
9. artifact references
10. a single API boundary for the frontend

## What is intentionally NOT claimed

This bundle does not claim that every upstream project is automatically executable on every
machine merely because its source is present. Heavy components such as video generation,
browser engines, Temporal, Coolify and Dokploy require their own runtime/infrastructure.

Configure their service URLs in `.env` when they are deployed.

## Run the fabric locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn david_fabric.main:app --reload --port 8000
```

Health:

`GET /api/health`

Capabilities:

`GET /api/intelligence/capabilities`

Create a goal:

`POST /api/goals`

Plan a goal:

`POST /api/goals/{goal_id}/plan`

Inspect a run:

`GET /api/runs/{run_id}`

## GitHub

This is designed to be uploaded into the existing David Ademola repository:

https://github.com/sebioma231-design/David-ademola

Do not create a second David product unless you intentionally want a separate deployment.
