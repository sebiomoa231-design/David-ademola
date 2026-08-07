# David AI — Clean Unified Build

David AI is a personal AI backend/frontend project assembled from the supplied development specification, backend-with-voice package, and full frontend package.

## Repository layout

```text
.
├── app/                    # FastAPI backend package
├── main.py                 # FastAPI entry point
├── frontend/               # Next.js frontend
├── data/                   # JSON runtime storage
├── voices/                 # Piper voice configuration
├── scripts/                # deployment/build helpers
├── tests/                  # backend tests
├── docs/specification/     # supplied project specifications
├── build.sh                # Render/Linux build script
├── render.yaml             # Render Blueprint configuration
├── runtime.txt             # Python 3.11.11
└── requirements.txt
```

## Important deployment fix

The FastAPI entry point imports `app.api.router`. The `app/` package is therefore kept at the repository root. Do not flatten its files into the repository root.

Do not create a root-level `logging.py`. The application logger is `app/core/logging.py`.

## Render

Use:

- Build command: `bash build.sh`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Set the environment variables from `.env.example` in Render.

The build script downloads the Piper Ryan high-quality English voice model because the model is larger than GitHub's normal single-file upload limit and should not be committed directly to the repository.

## Local backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_piper_voice.py
uvicorn main:app --reload
```

Health endpoint:

```text
GET /api/health
```

Root:

```text
GET /
```

## Local frontend

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## AI providers

Provider API keys are backend-only environment variables. The router tries providers in the configured priority order and falls back when a configured provider fails.

No real API keys are included in this repository.

## Voice

The current bundled voice configuration targets Piper's `en_US-ryan-high` voice. The large ONNX model is downloaded during deployment instead of being stored in GitHub.

Yoruba text support is retained. The Ryan Piper model is an English voice, so the backend does not falsely claim that it can synthesize Yoruba speech.

## Testing

Run:

```bash
pytest -q
```

The backend test suite covers health, chat, memory, planning, agents, voice status, and knowledge endpoints.
