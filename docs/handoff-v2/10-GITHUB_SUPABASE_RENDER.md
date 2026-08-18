# 10 — GITHUB, SUPABASE, RENDER: HISTORY AND CURRENT STATE

## GitHub

Referenced David repositories in prior work included:
- `David-ademola`
- `DavidAI-backend3.0.4`
- other related backend/frontend repositories

Current AI Core verified repository:
`David-ademola`

Current verified AI Core commit:
`2ea43f91b1d7e6e1cd242232ffee104df2dfcf86`

GitHub use:
- code storage
- branches
- commits
- pull requests
- issues
- workflow status
- source persistence

## Supabase

Supabase was integrated into the David AI backend.

Verified migration history discussed:
- `20260816103122` — `david_ai_core`
- `20260816103246` — `david_ai_server_only_rls`
- `20260816103624` — `david_ai_service_role_grants`

A service-role privilege issue was discovered:
- server key could reach Supabase
- service role lacked CRUD grants on new David tables
- migration `0003_david_ai_service_role_grants.sql` fixed this

Post-fix:
- backend successfully wrote/read records
- remote verification succeeded
- David tables included examples such as:
  - `david_projects`
  - `david_tasks`
  - `david_memories`
  - `david_conversations`

## Render

Historical URLs included:
- `https://david-ademola.onrender.com`
- other older test URLs

Current verified AI Core service:
`srv-d9qg4bp42hec73e98dq0`

Current verified deployment:
`dep-da1p6qgu01pc73d88nsg`

Current verified public backend:
`https://david-ademola.onrender.com`

Latest verified AI Core deployment:
LIVE

## Render operational rule

When deploying:
- use existing service
- inspect build logs
- inspect runtime logs
- run health checks
- fix errors
- redeploy
- verify live endpoints

Do not claim deployed until the online service is actually checked.
