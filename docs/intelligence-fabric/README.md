# David AI — Intelligence Fabric

David AI remains the **single user-facing application and control plane**. The Intelligence Fabric is the internal orchestration layer that discovers capabilities, selects agents and skills, chooses tools and providers, executes through native handlers or approved service boundaries, verifies outcomes, records artifacts, and returns one David result.

> User → David AI → Intelligence Fabric → Capability Discovery → Agent / Skill / Tool Selection → Provider / Service Selection → Execution → Verification → Artifact → Result

## Non-destructive integration rule

Existing David functionality remains mounted and available: chat, memory, projects, tasks, knowledge, voice, website, agents, authentication, file handling, legacy planning, provider routing, automation, and existing APIs. The Fabric is additive under `/api/intelligence`; it does not create a second David product or replace the existing control paths.

Both supplied upload sets are preserved separately under `vendor/source-sets/first` and `vendor/source-sets/second`. Recoverable upstream source trees, Dockerfiles, YAML/configuration, package manifests, notices, licenses, and recovery indexes remain within those boundaries. The upload checksum and source-preservation record is at `docs/intelligence-fabric/UPLOAD-PRESERVATION-MANIFEST.md`. The governing user directive is preserved at `docs/intelligence-fabric/FULL-CAPABILITY-DIRECTIVE.txt`.

## Capability model

Every registry record declares the capability’s purpose, agent, skill, tool, provider, runtime, accepted inputs, produced outputs, permissions, approval requirement, fallback candidates, source provenance, and implementation mode. The registry exposes truthful readiness states rather than treating an adapter record as proof of execution:

| State | Meaning |
|---|---|
| `IMPLEMENTED` | David has a handler or controlled boundary for the capability. |
| `CONNECTED` | A service boundary or provider URL is configured. |
| `CONFIGURED` | Required settings exist but readiness still needs verification. |
| `HEALTHY` | The configured service responded successfully to its probe. |
| `READY` | The capability can be selected for execution under current policy. |
| `UNAVAILABLE` | The capability is preserved but cannot execute in the current environment. |
| `REQUIRES_EXTERNAL_SERVICE` | A separate service or worker must be deployed. |
| `REQUIRES_CREDENTIAL` | Credentials or an API key must be configured. |
| `REQUIRES_GPU` | A suitable GPU worker/runtime is required. |
| `REQUIRES_APPROVAL` | The operation is blocked until explicit approval is recorded. |

David never converts an unavailable external capability into a fake success. Native capabilities return a recorded delegation envelope to the existing David surface. External workers are invoked only when a configured service URL exists, and failures move through the declared fallback chain. Side-effecting operations remain fail-closed.

## Control-plane endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/intelligence/capabilities` | Discover enriched capability records and readiness. |
| `POST /api/intelligence/route` | Select candidates, agents, tools, providers, and fallbacks for an objective. |
| `GET /api/intelligence/agents` | List registered agent roles and capabilities. |
| `GET /api/intelligence/tools` | List controlled tools and associated capabilities. |
| `GET /api/intelligence/providers` | List provider/service roles and readiness. |
| `GET /api/intelligence/readiness` | Inspect adapter probes and capability-level readiness. |
| `POST /api/intelligence/goals` | Create a persistent goal. |
| `POST /api/intelligence/goals/{goal_id}/plan` | Build a multi-step plan with fallback metadata. |
| `POST /api/intelligence/runs` | Create a run under the existing David control plane. |
| `POST /api/intelligence/runs/{run_id}/authorize` | Record explicit approval for an eligible capability. |
| `POST /api/intelligence/runs/{run_id}/execute` | Execute natively or through a configured adapter with bounded fallback. |
| `GET /api/intelligence/runs/{run_id}` | Inspect run, attempts, events, artifacts, and verification. |
| `GET /api/intelligence/runs/{run_id}/artifacts` | Retrieve artifact references. |
| `GET /api/intelligence/runs/{run_id}/verification` | Retrieve verification results. |

## Imported capabilities and boundaries

The source matrix at `docs/intelligence-fabric/UPSTREAM-INTEGRATIONS.md` records the exact repository roles and licenses. In brief, Microsoft Agent Framework and OpenHands provide orchestration/coding-worker boundaries; Browser Use and Playwright provide browser boundaries; ComfyUI and Wan2GP provide GPU image/video workers; Chatterbox and faster-whisper provide GPU/CPU voice workers; n8n provides workflow automation; and the creative backend provides a Node/Mongo media boundary. These runtimes are not merged into David’s base FastAPI dependency graph, avoiding Python/Node/CUDA conflicts while keeping each capability activatable through the Fabric.

The incomplete voice fragments and partial outer archives remain preserved as recovery artifacts and are explicitly unavailable until their missing bytes, license records, or required runtime pieces are supplied. This is a readiness limitation, not a deletion or downgrade.

## Local verification

```bash
pytest -q
python -m compileall -q david_fabric
python -c "import yaml; yaml.safe_load(open('config/capabilities.yaml'))"
```

The current test suite covers legacy coexistence, capability discovery, routing, agent/tool/provider metadata, native delegation, unavailable-service handling, fallback after a worker failure, approval enforcement, readiness truthfulness, artifact tracking, and verification.

## Configuration

Configure external services only when they are deployed and approved. Relevant environment variables include `BROWSER_USE_URL`, `PLAYWRIGHT_URL`, `OPENHANDS_URL`, `COMFYUI_URL`, `WAN2GP_URL`, `CHATTERBOX_URL`, `FASTER_WHISPER_URL`, `N8N_URL`, `LANGFUSE_URL`, `LANGGRAPH_URL`, `TEMPORAL_URL`, `COOLIFY_URL`, and `DOKPLOY_URL`. External side effects remain disabled by default; enabling them is an operational decision that should be paired with explicit approvals and monitoring.

## Repository

<https://github.com/sebiomoa231-design/David-ademola>
