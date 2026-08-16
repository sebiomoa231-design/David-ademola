# David AI production backend deployment

This repository contains the existing David AI FastAPI application. The supported production entrypoint is `main:app`; no second API or replacement backend is required.

## Runtime

The repository provides both a portable `Dockerfile` and a `Procfile`. The container starts the existing application with Gunicorn and the Uvicorn worker class, binding to `0.0.0.0:${PORT:-8000}`. Hosts that use a Procfile can use the same command. The existing `/api/health` endpoint is the container health check.

The image installs `requirements.txt` and `requirements-prod.txt`, copies the existing application, and creates the runtime directories used by the legacy local fallback. It does not copy `.env`, local data, uploads, logs, frontend build output, or secrets into the image.

## Required server environment

Set these values in the hosting provider's encrypted server-side environment. Do not commit them and do not expose the secret key to the frontend.

```text
APP_ENV=production
APP_HOST=0.0.0.0
PORT=8000
APP_PORT=8000
CORS_ORIGINS=https://<deployed-frontend-domain>
SUPABASE_URL=https://yvkylmxvikffkyhxqesh.supabase.co
SUPABASE_SECRET_KEY=<server-side-secret-key>
SUPABASE_STORAGE_BUCKET=Davidai
SUPABASE_PERSISTENCE_ENABLED=true
SUPABASE_SIGNED_URL_TTL=3600
SUPABASE_REQUEST_TIMEOUT_SECONDS=20
```

`DATABASE_URL` is optional for the current REST-based Supabase adapter. If a deployment platform provides a PostgreSQL connection string, it may be stored server-side for future direct-driver use, but it is not required by the current integration.

Keep provider keys and existing owner configuration in the same encrypted server environment. Never put `SUPABASE_SECRET_KEY` or any other server secret in `NEXT_PUBLIC_*` variables.

## Frontend connection

Build the existing Next.js frontend with:

```text
NEXT_PUBLIC_API_URL=https://<deployed-backend-domain>
NEXT_PUBLIC_API_FALLBACK_URL=
```

The frontend calls David AI through the backend. It does not call Supabase directly with the server secret.

## CORS

Set `CORS_ORIGINS` to the exact deployed frontend origin(s), comma-separated when more than one is required. Do not use `*` together with credentials in production. The backend already enables credentialed CORS using this allowlist.

## Verification

After deployment, check:

```text
GET https://<deployed-backend-domain>/api/health
GET https://<deployed-backend-domain>/api/library/status
```

The Library status response should report that Supabase is configured, database persistence is enabled, the database is reachable, and a migration is not required. Then perform real project, memory, and asset tests through the deployed API. Confirm the asset metadata is in `david_assets`, the object is in the private `Davidai` bucket, the signed URL works, and the public object URL does not work.

After restarting or redeploying the backend, retrieve the same test records again. This verifies persistence across process restarts rather than relying on local JSON state.

## Current deployment limitation

The repository previously had no configured Render, Railway, Fly.io, Cloud Run, AWS, or other conventional hosting target. The session has an enabled Cloudflare API connector, but the credential currently available to the sandbox was rejected by Cloudflare as an invalid Authorization header. Therefore no production URL may be claimed until a valid hosting credential or a connected deployment target is available.
