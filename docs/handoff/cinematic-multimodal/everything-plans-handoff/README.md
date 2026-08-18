# DAVID AI — COMPLETE PROJECT HANDOFF PACKAGE

Purpose: hand this package to another AI/developer as the consolidated product, architecture, capability, integration, prompt, evolution, deployment, and upgrade specification for David AI.

## Important status
- David AI is a Personal AI Operating System, not a SaaS product.
- Existing production backend is Python/FastAPI and has been deployed to Render.
- AI Core was reported implemented, committed to GitHub, and deployed to Render.
- AI Core commit reported: `2ea43f91b1d7e6e1cd242232ffee104df2dfcf86`.
- Reported live backend: `https://david-ademola.onrender.com`.
- The latest report said AI Core routes/health checks were live and 87 tests passed.
- Provider verification was still degraded: Gemini/Groq/OpenRouter were configured but live reasoning requests were not all succeeding.
- Never treat credentials mentioned in chat as safe credentials. Regenerate compromised secrets and configure them via secure secret-entry systems.
- Self-Evolution/Self-Upgrade is a major planned capability, but it was explicitly set aside temporarily while core/provider work continues.

## Non-negotiables
1. Do not build a demo or fake capability.
2. Do not claim an action succeeded unless it actually succeeded.
3. Preserve existing David AI functionality.
4. Do not put API keys/secrets in source code, GitHub commits, frontend code, logs, prompts, or public files.
5. Use secure backend environment variables/secrets for credentials.
6. Inspect the existing repository before changing architecture.
7. Reuse working components instead of creating duplicates.
8. Test real behavior, not just file existence.
9. Automatically diagnose/fix genuine implementation and deployment errors when possible.
10. Do not invent missing credentials, OAuth redirect URLs, provider access, or unsupported API capabilities.
11. Owner/security controls must not be bypassed.
12. External APIs and OAuth are capability integrations, not the AI core itself.
