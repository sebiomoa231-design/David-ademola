# David AI

David AI is a personal AI operating system with a FastAPI backend, a Next.js command center, server-side provider routing, governed Intelligence Fabric execution, memory and project surfaces, and a bounded runtime agent lifecycle. The repository is intentionally structured so credentials stay on the server and every autonomous-looking action remains observable and controllable.

## Architecture at a glance

| Layer | Location | Responsibility |
| --- | --- | --- |
| HTTP application | `main.py`, `app/` | FastAPI entry point, routing, middleware, settings, security, and provider boundaries |
| Runtime agents | `agent_engine.py`, `agents.py` | Goal validation, bounded plans, retries, background dispatch, lifecycle events, cancellation, and run history |
| Intelligence Fabric | `david_fabric/` | Capability discovery, routing, policies, adapters, persistence, and governed execution |
| Command center | `frontend/` | Next.js interface for chat, voice, projects, memory, capabilities, and agent monitoring |
| Operational configuration | `.env.example`, `render.yaml`, `build.sh` | Environment contract and deployment entry points |
| Verification | `test_*.py`, `tests/`, `frontend/lib/*.test.ts` | Backend behavior, integration boundaries, frontend API contracts, and build checks |

## Repository layout

```text
.
├── app/                    # FastAPI backend package
├── david_fabric/           # Capability registry, routing, policies, and persistence
├── frontend/               # Next.js command center
├── data/                   # Local JSON runtime storage
├── docs/                   # Supplied specifications and handoff material
├── scripts/                # Deployment and maintenance helpers
├── agent_engine.py         # Bounded runtime agent orchestration
├── agents.py               # Agent discovery and lifecycle API
├── main.py                 # FastAPI application entry point
├── build.sh                # Render/Linux build script
├── render.yaml             # Render Blueprint configuration
├── runtime.txt             # Python runtime declaration
├── requirements.txt        # Backend dependencies
└── .env.example            # Safe environment template; no real secrets
```

The FastAPI entry point imports `app.api.router`, so the `app/` package must remain at the repository root. Do not create a root-level `logging.py`; the application logger is `app/core/logging.py`.

## Runtime agent lifecycle

The runtime agent API provides a small, explicit contract for work that needs progress visibility or background execution. Goals are validated against a configurable character limit, plans are capped by a maximum step count, failures can retry within a configured budget, and run records are bounded by a history limit. Background tasks are cancelled during application shutdown rather than being abandoned silently.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/agents` | List registered agent types and capabilities |
| `POST` | `/api/agents/dispatch` | Dispatch a goal; set `background=true` for queued execution |
| `GET` | `/api/agents/runs` | List recent run records |
| `GET` | `/api/agents/runs/{run_id}` | Inspect a run, its steps, logs, and errors |
| `POST` | `/api/agents/runs/{run_id}/cancel` | Request a safe cancellation |

A run may move through `queued`, `planning`, `executing`, `retrying`, `completed`, `failed`, or `cancelled`. The frontend Agent Runs workspace polls active records and renders step-level state rather than presenting an invented completion message.

## Configuration and secrets

Copy `.env.example` to `.env` for local development and provide real credentials only through the deployment environment or a local secret store. API keys, private keys, owner passwords, and access tokens must never be committed or sent to the browser.

The runtime guardrails are controlled by the following settings:

| Variable | Default | Meaning |
| --- | ---: | --- |
| `AGENT_MAX_GOAL_CHARS` | `12000` | Maximum accepted goal length |
| `AGENT_MAX_STEPS` | `8` | Maximum steps created for a single run |
| `AGENT_MAX_RETRIES` | `1` | Retry budget for failed steps |
| `AGENT_HISTORY_LIMIT` | `100` | Maximum in-memory run history |

ElevenLabs is the active voice integration. The configured non-secret profile is voice ID `5hZv9mAOcmcMt1TxA5Iz`, described as a British, deep male, JARVIS-style voice. Set `ELEVENLABS_API_KEY` only on the backend. The API key is intentionally absent from this repository and from frontend bundles.

## Render deployment

Use the repository’s build command and FastAPI start command:

```bash
bash build.sh
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Populate the deployment environment from `.env.example`. The build no longer depends on downloading a Piper/Ryan model; voice requests are routed through the server-side ElevenLabs provider when configured, with a truthful text fallback when it is unavailable.

## Local backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Useful endpoints include `GET /api/health`, `GET /api/agents`, and `GET /api/intelligence/readiness`.

## Local frontend

```bash
cd frontend
pnpm install
pnpm run dev
```

Create `frontend/.env.local` when the backend is not using the deployed canonical URL:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The command center includes a runtime agent panel for dispatching bounded objectives, inspecting step progress, refreshing run history, and requesting cancellation. The frontend build uses a normal catch-all route for legacy workspace paths while keeping the root dashboard and dedicated chat and creative routes build-safe.

## Testing and validation

Run the backend suite from the repository root:

```bash
pytest -q
```

Run the frontend checks:

```bash
cd frontend
pnpm run typecheck
pnpm test -- --run
pnpm run build
```

The backend coverage includes health, chat, memory, planning, agent lifecycle, voice status, knowledge, provider, GitHub, and Intelligence Fabric boundaries. The frontend suite verifies API request contracts, while the production build catches route, client-boundary, and TypeScript regressions.
