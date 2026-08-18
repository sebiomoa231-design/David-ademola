# 08 — EXTERNAL SERVICES AND CONNECTED ACCOUNT FABRIC

## Connector architecture

```text
David Core
 ↓
Capability Router
 ↓
Tool Registry
 ↓
External Service Manager
 ├─ YouTube
 ├─ TikTok
 ├─ Google/Gmail
 ├─ GitHub
 ├─ Supabase
 ├─ Render
 ├─ Google Maps
 ├─ OpenWeather
 ├─ Paystack
 ├─ AI providers
 └─ Manus
```

## Requirements

Every connector must expose:
- service identity
- supported operations
- auth type
- required scopes
- permissions
- health
- retry policy
- rate-limit handling
- normalized result/error format
- verification strategy

## OAuth
Support:
- state protection
- callback validation
- code exchange
- secure token storage
- token refresh
- disconnect
- scope tracking
- reauthorization state

Never expose refresh tokens to AI models or frontend unnecessarily.

## Webhooks
Where a service supports webhooks:
- authenticate/signature verify
- validate payload
- deduplicate
- associate event with workflow/task/project
- update state
- audit

## Cross-service workflows
Examples:
1. GitHub commit → Render deploy → health check
2. Video generation → YouTube/TikTok publishing
3. Website build → GitHub → Render/Vercel
4. Research → content → image/video → social publishing

One service failure must not incorrectly erase already-successful steps.
