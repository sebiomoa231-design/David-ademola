# David AI Command Center

This directory contains the replacement David AI frontend requested by the pasted frontend architecture directives. It is a Next.js App Router application with React, TypeScript, Tailwind CSS, and Lucide React. It is a new frontend shell; the FastAPI backend, API router, provider wrappers, voice infrastructure, persistence, configuration, and preserved vendor source sets remain outside this directory and are not replaced.

## Run locally

From this directory:

```bash
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev
```

The UI is preview/development-only. It does not publish or deploy automatically. It uses `NEXT_PUBLIC_API_URL` as the primary backend base URL and optionally `NEXT_PUBLIC_API_FALLBACK_URL` for failover.

## Routes

The App Router serves the following workspace paths through one reusable command-center shell:

`/`, `/auth`, `/dashboard`, `/chat`, `/agents`, `/memory`, `/tasks`, `/projects`, `/devices`, `/activity`, `/settings`, `/website-builder`, `/video-studio`, `/image-studio`, `/providers`, `/connectors`, and `/owner`.

The frontend centralizes all backend communication in `lib/api.ts`. It uses the live legacy routes for chat, auth, voice, memory, projects, tasks, conversations, and website generation. It uses the live Intelligence Fabric routes for readiness, capabilities, adapters, providers, routing, goals, plans, runs, artifacts, and verification.

Voice behavior is intentionally truthful. Browser microphone capture can request permission and show listening/processing states. Text-to-speech plays only when `/api/voice/synthesize` returns an audio payload. If STT or TTS is not configured by the backend, the UI reports that state instead of pretending that voice is available.

Imported services and mixed-runtime workers are represented through Fabric readiness and adapter metadata. The frontend does not expose credentials, claim unsupported phone control, invent asset outputs, or trigger deployment from the preview interface.
