# Frontend preview check

The replacement Next.js command center was previewed locally at `http://localhost:3000/dashboard` and `http://localhost:3000/chat` on 2026-08-16.

The dashboard rendered the new red-futuristic David AI shell with the left navigation, command-center hero, animated core, system pulse metrics, voice lifecycle panel, agent orchestration form, and memory workspace. The chat route rendered the conversation channel, David intro response, composer, microphone control, text-to-speech control, voice-aware status card, and response-envelope notes.

Because the FastAPI backend was not started during this frontend-only smoke test, the UI truthfully displayed `CONNECTING`, `Checking backend`, empty live metrics, `TTS not configured`, and the fact that backend STT is not exposed. No simulated backend success was displayed, and no publishing or deployment action was triggered.
