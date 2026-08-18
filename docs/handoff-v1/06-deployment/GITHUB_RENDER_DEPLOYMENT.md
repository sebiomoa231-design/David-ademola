# GITHUB + RENDER DEPLOYMENT WORKFLOW

## Current reported backend
- GitHub repo: `David-ademola` (existing project repository)
- reported main branch commit: `2ea43f91b1d7e6e1cd242232ffee104df2dfcf86`
- reported Render backend: `https://david-ademola.onrender.com`
- reported Render deployment: `dep-da1p6qgu01pc73d88nsg`
- reported Render service ID: `srv-d9qg4bp42hec73e98dq0`

These are historical status notes from the handoff, not guarantees that they are still current. Verify them before making changes.

## Required workflow
1. Inspect repository.
2. Run tests.
3. Review git diff.
4. Ensure no secrets are present.
5. Commit.
6. Push.
7. Deploy to the existing Render service.
8. Check build logs.
9. Check runtime logs.
10. Check health endpoint.
11. Run production smoke tests.
12. Fix genuine errors and redeploy.

## Secrets
- Render environment variables/secrets must hold runtime credentials.
- GitHub Actions secrets/variables may hold CI credentials where appropriate.
- Never commit real secret values.
- Never paste secret values into documentation.
