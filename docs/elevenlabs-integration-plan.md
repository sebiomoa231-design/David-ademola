# David AI ElevenLabs Integration Plan

## Scope

Adapt the provided ElevenLabs repositories into David AI as server-side capabilities, not as a wholesale copy of unrelated repositories. The active David AI FastAPI routes and frontend contracts remain authoritative.

## Sources and intended use

| Source | Intended adaptation |
| --- | --- |
| `elevenlabs-python` | Official server-side Python SDK patterns for TTS, STT, voice search, sound effects, voice conversion, and streaming. |
| `elevenlabs-mcp` | Capability inventory and safe request/response ideas; do not embed a standalone MCP process into the FastAPI request path. |
| `skills` | Official usage guidance for models, voice settings, realtime transcription, Speech Engine, and security boundaries. |
| `examples` | Reference implementations for TTS, STT, realtime transcription, and Speech Engine browser flows. |
| `cli`, `elevenlabs-swift-sdk`, `packages` | Reference-only; CLI, Swift, and monorepo-specific code are not copied into the Python backend. |

## David AI changes

1. Preserve `POST /api/voice/synthesize`, `POST /api/voice/transcribe`, and the current frontend base64/fallback contract.
2. Extend the provider layer with official SDK-backed optional operations and lazy imports so deployments without the SDK or API key retain truthful fallback behavior.
3. Add bounded voice capabilities behind explicit endpoints: voice listing, sound-effect generation, speech-to-speech voice conversion, and richer transcription metadata where supported.
4. Add a secure realtime Speech Engine WebSocket route only if the SDK dependency and Render runtime support it; retain JWT verification and never disable authentication by default.
5. Keep all ElevenLabs credentials server-side and add environment settings without committing secrets.
6. Add mocked tests for request validation, provider-disabled behavior, base64/audio responses, and new capability contracts. No live ElevenLabs calls will be made during tests.

## Non-goals

Do not copy the standalone MCP server, desktop file-output behavior, local audio-device dependencies, Swift SDK, CLI tooling, or unrelated music/video workflows into David AI’s runtime. Do not expose the ElevenLabs API key to the browser.

## Deployment constraint

The current GitHub default branch is `main` at commit `9035e9898e4fd55378666125daf88ccfcd4d37e7`, while the connected Render service previously tracked `feat/david-ai-cinematic-complete`. Implementation and validation will be performed against `main`; deployment branch selection must be confirmed before pushing or deploying.
