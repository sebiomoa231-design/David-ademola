# David AI ElevenLabs Speech Engine

David AI now includes a server-side ElevenLabs Speech Engine bridge at:

```text
wss://<render-host>/api/voice/speech-engine/ws
```

The bridge verifies the `X-Elevenlabs-Speech-Engine-Authorization` JWT supplied by ElevenLabs, sends user transcripts through David’s existing governed orchestrator, and streams the resulting response text back through the Speech Engine session. The ElevenLabs API key is never sent to the browser.

## Configuration

Set these values in the Render service environment:

```text
ELEVENLABS_API_KEY=<server-only ElevenLabs API key>
ELEVENLABS_SPEECH_ENGINE_ID=<created Speech Engine ID>
ELEVENLABS_SPEECH_ENGINE_PUBLIC_WS_URL=wss://<render-host>/api/voice/speech-engine/ws
ELEVENLABS_SPEECH_ENGINE_NAME=David AI Speech Engine
```

The public WebSocket URL must use `wss://` in production and must end with `/api/voice/speech-engine/ws`.

## Create the Speech Engine resource

After the backend is deployed at its public HTTPS hostname, run the administrative script from the repository root with the API key and public WebSocket URL available in the environment:

```bash
python scripts/create_speech_engine.py
```

The script prints the newly created Speech Engine ID. Store that ID as `ELEVENLABS_SPEECH_ENGINE_ID` in Render. Do not commit the ID together with an API key, and do not put either value in frontend environment variables.

## Runtime checks

The readiness endpoint is:

```text
GET /api/voice/speech-engine/status
```

It reports whether the server has both the API key and Speech Engine ID configured, the public WebSocket URL, and the authenticated WebSocket path. It does not return credentials.

## Local development

For local development, the Speech Engine resource must point to a publicly reachable secure WebSocket URL, such as a temporary `wss://` tunnel that forwards to the local `/api/voice/speech-engine/ws` route. Use the Render hostname directly in production; do not leave an example ngrok URL in committed configuration.

The bridge intentionally uses David’s existing orchestrator rather than a separate hard-coded OpenAI loop. This keeps voice conversations aligned with David’s provider routing, agent policies, and response contracts while avoiding an unnecessary direct OpenAI dependency.
