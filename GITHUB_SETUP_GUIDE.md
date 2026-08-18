# David AI — GitHub Multi-Repository Integration: Setup Guide

This guide walks the owner (Sebiomoa) through the two remaining steps on GitHub to fully activate the GitHub multi-repository integration that has been built, tested, and deployed to Render. All other work — backend service, database schema, audit logging, dashboard UI, the live deployment, and the Supabase persistence wiring — is already done.

## What Was Built

The integration gives David AI a secure, server-side connection to GitHub. Every website David AI generates can now live in its own GitHub repository. A new **GitHub** workspace has been added to the Command Center dashboard at `https://david-ademola.onrender.com/dashboard` (Operate section). From there the owner can connect their GitHub account, create a repository from a website topic, initialize it, push generated website files to it, and review a full audit trail of every operation.

| Component | Location | Purpose |
|---|---|---|
| GitHub service | `app/services/github_service.py` | Server-side GitHub API client: installation tokens, OAuth connect flow, unique repository creation, file initialization and push, rate-limit mapping |
| Persistence | `app/services/github_persistence.py` | Repository tracking and audit records in Supabase |
| Database migration | `database/migrations/0004_github_repositories.sql` | `david_github_repositories` and `david_github_audit_log` tables, applied to the production Supabase project |
| API routes | `github.py` | Endpoints under `/api/github` (health, connection, connect/callback, disconnect, repositories, push, audit) |
| Dashboard UI | `frontend/components/david-app.tsx` | GitHub workspace in the Command Center |
| Tests | `tests/test_github_integration.py` | 27 backend tests against a mocked GitHub API, all passing |

Security properties were verified against the original directive: no token, private key, or OAuth secret ever appears in API responses, error messages, or frontend code. The OAuth state parameter is stored server-side with a ten-minute TTL, and audit events are sanitized to strip anything secret-shaped before they reach the dashboard.

## What Was Verified

The integration is deployed to Render on the `main` branch (merge commit `ec916e27`, containing the fix `47067c83` that ensures the repository endpoints respond with `503` instead of crashing with `500` when the database is unavailable — the same graceful behavior as the pre-existing Supabase paths). During final production verification it was discovered that the `service_role` database role was missing privileges on the two new tables, so the grants were applied directly against the production Supabase project (`GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO service_role`). All GitHub endpoints are now live and returning `200` against `https://david-ademola.onrender.com`:

| Endpoint | Status | Result |
|---|---|---|
| `GET /api/github/health` | 200 | `{"configured":false,"connected":false}` — working, awaiting GitHub credentials |
| `GET /api/github/connection` | 200 | `{"connected":false,"configured":false}` — working |
| `GET /api/github/repositories` | 200 | `[]` — Supabase persistence is **live** and connected to production tables |
| `GET /api/github/audit` | 200 | `[]` — audit feed ready (populates as actions occur) |
| `GET /api/projects`, `/api/conversations` | 200 | Existing functionality unaffected |

The full local test suite is green (`27 passed`), and repository records plus audit events are persisted to the production database `yvkylmxvikffkyhxqesh` (tables `david_github_repositories` and `david_github_audit_log`). A real GitHub API verification was also run using the owner's GitHub account: a private repository `david-gh-integration-test` was created, a commit (`1fcebee5`, "Initialize website files (David AI verification)") was pushed to `main` with `README.md` and `site/index.html`, and the commit and file tree were confirmed through the API. The owner can review it and delete it at any time — the repository was explicitly described as safe to delete.

## Step 1 — Create the GitHub App (about 5 minutes)

1. Go to <https://github.com/settings/apps> and click **New GitHub App** (you may need to enter your GitHub password).
2. Fill in the form:
   - **GitHub App name**: `David AI` (any unique name works)
   - **Homepage URL**: `https://david-ademola.onrender.com`
   - **User authorization callback URL**: `https://david-ademola.onrender.com/api/github/connect/callback` — this is where GitHub returns after the owner approves the connection; it is the exact URL wired into the deployed backend.
   - Leave "Request user-to-server token expiration" enabled if offered, and leave webhook settings at their defaults (this integration does not use webhooks; it works through OAuth and installation tokens).
3. Under **Permissions**, set: **Repository contents — Read & write** and **Metadata — Read-only**. These are the only permissions the integration needs.
4. Under **Where can this GitHub App be installed?**, select **Only on this account**.
5. Click **Create GitHub App**.
6. On the app's page, note these two values (you will need them in Step 3):
   - **App ID** (shown near the top of the page)
   - **Client ID** (under "General")

## Step 2 — Generate the Private Key and Install the App

1. On the app's page go to **General → Private keys** and click **Generate a private key**. A `.pem` file downloads — keep it safe; it is the app's secret credential.
2. Click **Install App** on the left sidebar (or go to <https://github.com/settings/installations>) and install the app on your account, selecting **All repositories** (the integration creates a new repository per website, so it needs access to all of them).
3. After installing, note the **Installation ID** from the installation URL, which looks like `https://github.com/settings/installations/<INSTALLATION_ID>`.

## Step 3 — Set the Render Environment Variables

In the Render dashboard, open the **David-ademola** service, go to **Environment**, and add these variables. For the private key, use the "Add Secret File" / multi-line value option and paste the full `.pem` contents exactly as downloaded.

| Render Variable | Source |
|---|---|
| `GITHUB_APP_ID` | App ID from Step 1 |
| `GITHUB_APP_PRIVATE_KEY` | The full downloaded `.pem` file contents |
| `GITHUB_APP_CLIENT_ID` | Client ID from Step 1 |
| `GITHUB_APP_CLIENT_SECRET` | "Client secrets" section of the app settings |
| `GITHUB_INSTALLATION_ID` | Installation ID from Step 2 |
| `GITHUB_OAUTH_REDIRECT_URI` | `https://david-ademola.onrender.com/api/github/connect/callback` |

Saving the variables automatically redeploys the service.

## Step 4 — Connect from the Dashboard

Once the redeploy finishes (it starts automatically when you save the variables), open `https://david-ademola.onrender.com/dashboard`, select the **GitHub** workspace in the Operate section, and click **Connect GitHub**. A popup takes you to GitHub's approval screen; after approving, the popup closes and the dashboard reports you as connected (for example, `Connected as sebiomoa231-design`). From there, creating a website project and clicking **Create Repository** generates a uniquely named private repository, **Initialize** prepares it, and **Push** sends the generated website files — each action recorded in the audit feed with sanitized details.

## Notes

Supabase persistence (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `SUPABASE_PERSISTENCE_ENABLED=true`) is already configured on Render and verified live against the production database, so repository records and audit events are stored permanently — not just in memory. The verification repository `sebiomoa231-design/david-gh-integration-test` is private and safe to delete once the owner has reviewed it.
