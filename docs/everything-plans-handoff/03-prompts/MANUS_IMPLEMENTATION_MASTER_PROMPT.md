# MANUS — MASTER DAVID AI IMPLEMENTATION COMMAND

Inspect the existing David AI backend and all provided specification files in this handoff. Continue the existing project; do not rebuild it as a demo or replace working architecture.

Implement the complete feature set into the current backend. Reuse existing systems and avoid duplicates. Build real code, real integrations, real persistence, real tests, and real error handling.

For every capability:
1. inspect the existing implementation;
2. map the requirement;
3. implement the actual backend behavior;
4. integrate with AI Core, memory, tasks, tools, providers, database, and security as appropriate;
5. test;
6. diagnose and fix failures;
7. review the diff;
8. commit and push to the existing David AI GitHub repository;
9. deploy to the existing Render backend when deployment access is configured;
10. run live health/smoke tests;
11. fix build/runtime/deployment issues and redeploy when possible.

Never invent credentials, redirect URLs, provider access, model names, API responses, deployment results, commits, or test results.

Secrets must be configured through secure environment variables/secrets. Never place actual secret values in source code, GitHub commits, frontend bundles, logs, docs, prompts, or public files.

The system must be truthful about degraded states and partial failures.
