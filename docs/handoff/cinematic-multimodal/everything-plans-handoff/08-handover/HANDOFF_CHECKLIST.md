# DAVID AI — HANDOFF CHECKLIST

## Understand
- Read every file in this handoff package.
- Inspect the actual David AI repository.
- Treat repository state as authoritative for implemented features.
- Treat this package as the product/specification history.

## Verify
- Current Git branch/commit.
- Current Render service/deployment.
- Current database/migrations.
- Actual provider environment variables.
- Current OAuth apps/scopes/redirect URLs.
- Current tests and their results.

## Build
- Implement only real functionality.
- Reuse existing components.
- Do not duplicate systems.
- Preserve backward compatibility.

## Secure
- Regenerate any credentials that were exposed in chat.
- Configure secrets via secure secret-entry systems.
- Never commit secrets.
- Never store credentials as memory.

## Deploy
- Test.
- Commit.
- Push.
- Deploy.
- Verify.
- Fix failures.
- Report honestly.

## Next suggested order
1. Stabilize AI Core provider integrations.
2. Configure and live-test the confirmed providers.
3. Complete memory/personal knowledge implementation.
4. Connect Creative Suite and external services.
5. Complete task/workflow orchestration.
6. Harden production/security.
7. Then resume Self-Evolution work.
