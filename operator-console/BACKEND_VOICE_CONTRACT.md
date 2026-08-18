# David AI OS backend voice contract

## Authoritative sources

The backend source is the user-provided `sebiomoa231-design/David-ademola` repository. The live deployment is `https://david-ademola.onrender.com`.

## Verified live capability

On 18 August 2026, the live `GET /api/voice/status` response reported the following operational configuration:

| Capability | Live value |
| --- | --- |
| Text-to-speech provider | ElevenLabs |
| Text-to-speech configured | `true` |
| Speech-to-text provider | ElevenLabs Scribe |
| Speech-to-text configured | `true` |
| Voice model | `eleven_multilingual_v2` |
| Voice style | British JARVIS-style deep male voice |

## Backend endpoints

| Method | Path | Purpose | Primary response |
| --- | --- | --- | --- |
| `GET` | `/api/voice/status` | Service readiness | Provider and configuration fields |
| `POST` | `/api/voice/transcribe` | Speech-to-text | `text`, `language`, `confidence` |
| `POST` | `/api/voice/synthesize` | Text-to-speech | Base64-encoded MP3 payload |
| `POST` | `/api/voice/synthesize/stream` | Text-to-speech playback | Raw `audio/mpeg` stream |

The operating-system frontend must show only supported voice states and must surface microphone permission, upload, backend, and playback failures truthfully.

## Operator runtime and persistence audit

The GitHub backend exposes an additive governed operating-system API under `/api`, including system health and status, policy controls, tasks, objectives, workflows, schedules, events, audits, provider capability discovery, notifications, memory context, and controlled agent dispatch. Its status endpoint reports the persistence mode and integration readiness for GitHub, Supabase, and Render.

The backend keeps provider credentials, Supabase connection details, Render credentials, GitHub credentials, and voice credentials server-side. Its documented persistence model covers memories, projects, tasks, conversations, messages, knowledge, embeddings, semantic search, assets, voice records, and durable media metadata. Supabase persistence is enabled only when the backend environment has the required Supabase settings and persistence flag.

## Operator integration boundary

David AI Operator should connect to the Render base URL through `DAVID_API_BASE_URL` only. The operator frontend must not copy the Render backend’s provider keys, database key, GitHub private key, or Render management key. Those remain in the Render environment. The correct UI contracts are the backend’s verified status, policy, task, workflow, provider, memory-context, voice, and audit endpoints.

## Live deployment availability check

The reachable Render deployment currently returns `200` for `/api/health` and reports a `handoff-scaffold` version. It returns `404` for the audited operator control-plane, providers, tasks, projects, memory, and intelligence endpoints. The voice status endpoint is live and reports both TTS and STT configured.

Therefore, the David AI Operator frontend can safely connect its speech layer now, but the repository’s fuller operator/persistence surface must be deployed to Render before the frontend can truthfully use its authoritative task, memory, audit, policy, and database APIs. The interface must continue to present those unavailable routes as unavailable rather than pretending the deployed backend provides them.

## Environment responsibility boundary

| Location | Required configuration | Rule |
| --- | --- | --- |
| David AI Operator project | `DAVID_API_BASE_URL` | Server-only URL pointing at the approved Render backend. The adapter returns a clear unavailable state if it is omitted. |
| Render backend | Supabase URL and secret key, database URL, provider API keys, ElevenLabs key and voice ID, GitHub credentials, Render management key | These secrets remain exclusively in Render. They must never be copied into browser code or this project’s client environment. |
| Browser | No provider, database, GitHub, Render, or ElevenLabs secrets | The browser calls the David AI Operator server, which proxies only the approved backend contracts. |
