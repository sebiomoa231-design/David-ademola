# David AI Frontend Capability Matrix

This matrix is the source-of-truth boundary for the replacement frontend. It is derived from the two pasted directives and the actual FastAPI routes in this repository. The frontend must show unavailable or unconfigured states rather than fabricate completion.

| Capability | Backend exists | Frontend exists before rebuild | New UI required | Integration required | Tested after rebuild | Truthful boundary |
|---|---:|---:|---:|---:|---:|---|
| Backend health | Yes: `GET /api/health` | Minimal helper only | Yes | Yes | Yes | Live health response |
| Chat | Yes: `POST /api/chat` | Minimal helper/hook | Yes | Yes | Yes | Non-streaming response; streaming is not claimed |
| Conversations | Yes: `/api/conversations*` | Helper only | Yes | Yes | Yes | Persistent JSON-backed conversations |
| Voice status | Yes: `GET /api/voice/status` | No command center | Yes | Yes | Yes | STT/TTS configuration comes from backend |
| Voice synthesis | Yes: `POST /api/voice/synthesize` | No lifecycle UI | Yes | Yes | Yes | Audio plays only when `audio_available` is true |
| Browser microphone | Browser capability | No | Yes | Browser permission only | Manual/browser check | Capture is real; backend STT is not claimed when no STT endpoint is exposed |
| Memory | Yes: `/api/memory*` | Helper only | Yes | Yes | Yes | Read/add/search/delete use live endpoints |
| Projects and tasks | Yes: `/api/projects*` | Helper only | Yes | Yes | Yes | JSON-backed records; advanced editing remains bounded by route contracts |
| Website generation | Yes: `POST /api/website/generate` | Helper only | Yes | Yes | Yes | Displays backend response or error; no fake preview is created |
| Planning | Yes: `POST /api/plan` | Helper only | Yes | Yes | Yes | Native lightweight plan remains distinct from Fabric plan |
| Intelligence Fabric discovery | Yes: `/api/intelligence/{capabilities,agents,tools,providers,adapters,readiness}` | No | Yes | Yes | Yes | Live registry and readiness data |
| Fabric routing | Yes: `POST /api/intelligence/route` | No | Yes | Yes | Yes | Selected capability and fallback chain are shown from response |
| Fabric agent runs | Yes: `/goals`, `/plan`, `/runs`, `/execute` | No | Yes | Yes | Yes | Run events, attempts, artifacts, verification are read from backend |
| Artifacts and verification | Yes: `/runs/{id}/artifacts`, `/verification` | No | Yes | Yes | Yes | Render only returned records |
| Provider control | Yes: `/api/intelligence/providers` | No | Yes | Yes | Yes | No credentials exposed; readiness/status only |
| Agents and tools | Yes: `/api/intelligence/agents`, `/tools` | No | Yes | Yes | Yes | Configured directory only |
| Connectors | Metadata/readiness only | No | Yes | Partial | Yes | Authorization/unavailable states are explicit; no invented connector action |
| Video studio | Registry/readiness only | No | Yes | Partial | Yes | Shows not configured/provider unavailable when no generation endpoint exists |
| Image studio | Registry/readiness only | No | Yes | Partial | Yes | No fake image result; capability readiness is visible |
| Content studio | Chat/backend primitives | No | Yes | Partial | Yes | Uses chat/planning primitives; dedicated export is not claimed |
| Automation workspace | Workflow metadata only | No | Yes | Partial | Yes | Shows workflow definitions/readiness; no fake scheduler execution |
| Authentication | Yes: `/api/auth/*` | No usable frontend | Yes | Yes | Yes | Login/register submit to real endpoints |
| Devices and permissions | Browser APIs only | No | Yes | Browser permission only | Manual/browser check | Only legitimate browser/device permissions are shown |
| Projects, tasks, memory, activity | Backend primitives | No | Yes | Yes | Yes | Activity is assembled from returned run/conversation data where available |

## Key constraints

The repository contains a FastAPI backend and client helper files but no actual `frontend/` package or `package.json`. The new frontend therefore creates a new Next.js App Router application under `frontend/` rather than mutating backend Python modules. Existing backend secrets remain server-side and are never copied into client code. The frontend is preview/development-only and does not publish or deploy automatically.
