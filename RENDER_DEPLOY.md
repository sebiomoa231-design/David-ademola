# David AI — Render Deployment

## Backend entrypoint

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

The FastAPI package lives in `app/`, so `main.py` imports modules as `app.*`.

## Critical logging rule

Keep `app/core/logging.py` — this is the application's correctly namespaced logger.

Do **not** create a root-level `logging.py`. A root-level file named `logging.py` shadows Python's standard-library `logging` module and can break Render before the application starts.

## Render settings

- Runtime: Python 3
- Build command: `bash build.sh`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`
- Python: 3.11.11 via `runtime.txt` / `PYTHON_VERSION`

Keep API keys, owner credentials, and other secrets in Render Environment Variables. Do not commit `.env`.
