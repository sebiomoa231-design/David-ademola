# 16 — MASTER COMMAND TO THE NEXT AI

You are inheriting an existing David AI Personal AI Operating System.

Read every file in this handoff before modifying code.

Do not interpret this as a new project.

Do not restart the architecture.

Do not replace existing working systems.

Treat the handoff as the product/specification history and the current repository as the implementation source of truth.

Your first responsibility is to:
1. inventory the current repository;
2. compare it to this handoff;
3. identify what is actually implemented;
4. identify what is deployed;
5. identify what is configured;
6. identify what is missing;
7. identify what is contradictory or stale;
8. produce a precise gap map;
9. then implement the next requested capability.

Security:
- never reveal or print secrets;
- never commit secrets;
- regenerate any credential that was exposed;
- use secure environment/secret management;
- never put server secrets in frontend code.

Truthfulness:
- do not fabricate tests;
- do not fabricate deployments;
- do not fabricate provider success;
- do not claim an integration works unless verified.

Compatibility:
- preserve current APIs;
- preserve database data;
- preserve existing providers/tools;
- preserve existing project/task/conversation behavior.

Deployment:
- when explicitly asked to deploy, use the existing GitHub/Render setup;
- test after deployment;
- fix genuine errors;
- redeploy;
- verify live behavior.

The desired final system is:
A real Personal AI Operating System with persistent memory, multi-model orchestration, tool execution, external-service integrations, creative capabilities, task/project management, secure automation, and a future controlled self-evolution engine.
