# David AI — Intelligence Fabric Backend

This package is a **unified David AI control plane** built around the David Ademola backend. It provides one capability registry, routing layer, goal/run API, policy layer, health model, namespaced persistence layer, and service-integration boundary for the capabilities recovered from the supplied archives.

## Important architecture rule

The external repositories are **not blindly merged into one Python process**. Their original runtimes, licenses, Dockerfiles, and dependency trees are preserved as attribution and operational metadata under `docs/intelligence-fabric/upstreams/`. David’s Intelligence Fabric is the single control plane that decides which capability may be used and whether approval is required.

This avoids Python/Node/CUDA dependency collisions while still making the recoverable capabilities available through bounded adapter records. The full source trees remain in the quarantined inspection workspace rather than being copied wholesale into David or committed as an unrelated project.

### Supplied source groups and current boundaries

| Source group | David AI role | Preserved metadata |
|---|---|---|
| David-ademola-main | Native David application and legacy routes | Existing repository source |
| DavidAI-backend-with-voice fragments | Inactive voice-backend reference until a valid complete archive is supplied | Recoverable Docker, Render, requirements, voice-route, and Piper JSON metadata |
| david-ai-backend | Creative Node/Mongo service adapter | README and package metadata |
| agent-framework-main | Multi-agent orchestration reference | MIT license and README |
| OpenHands-main | Coding-worker service adapter | MIT license, README, and package metadata |
| browser-use-main | Python browser-agent service adapter | MIT license, README, Dockerfile, and package metadata |
| playwright-main | Node browser-automation service adapter | Apache-2.0 license, NOTICE, and README |
| ComfyUI-master | GPU image-generation worker adapter | GPL-3.0 license, README, and Python runtime metadata |
| Wan2GP-main | GPU video/media-generation service adapter | Custom license, README, and Dockerfile |
| chatterbox-master | GPU TTS/voice-worker service adapter | Upstream license, README, and Torch runtime metadata |
| faster-whisper-master | CPU/GPU speech-to-text worker adapter | MIT license, README, Dockerfile, and requirements |
| n8n-master | Node workflow-automation service adapter | Sustainable Use and Enterprise license records, README, Dockerfile, YAML, and package metadata |

## What David AI provides

The Intelligence Fabric supplies capability discovery, capability routing, agent/skill/tool registration, goal and run persistence, approval checks, bounded adapter health, external service references, event recording, and artifact references through the single `/api/intelligence` API boundary. Existing David endpoints remain mounted and are not replaced.

## What is intentionally not claimed

This repository does not claim that every upstream project is automatically executable on every machine merely because its metadata is preserved. Heavy components such as ComfyUI, Wan2GP, Chatterbox, browser-use, Playwright, faster-whisper, OpenHands, Temporal, Coolify, and Dokploy require their own runtime or infrastructure. Configure their service URLs in `.env` only when they are deployed and approved for use.

The supplied voice fragments are not treated as a complete executable repository: the archive central directory references missing middle bytes, and no license entry was recoverable. The Fabric therefore exposes the voice backend as an inactive reference while retaining David’s existing native voice behavior.

## Run the Fabric locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn david_fabric.main:app --reload --port 8000
```

Health: `GET /api/health`

Capabilities: `GET /api/intelligence/capabilities`

Create a goal: `POST /api/intelligence/goals`

Plan a goal: `POST /api/intelligence/goals/{goal_id}/plan`

Inspect a run: `GET /api/intelligence/runs/{run_id}`

## GitHub

This is integrated into the existing David Ademola repository:

<https://github.com/sebiomoa231-design/David-ademola>

Do not create a second David product unless a separate deployment is intentionally required.
