# 00 — GOVERNING STATUS

## Product identity

Project: David AI
Type: Personal AI Operating System
Primary owner: single-owner system
Core objective: a real, persistent, multi-provider AI operating system that can converse, remember, plan, use tools, manage external services, create content, develop software, run workflows, and eventually perform controlled self-evolution.

## Non-negotiable product principles

- David AI is NOT a SaaS product.
- Do not turn the system into a demo.
- Do not create fake buttons, fake agent runs, fake provider status, fake deployments, or fake success messages.
- Preserve existing working functionality.
- Extend the current architecture rather than restarting from scratch.
- Keep secrets server-side.
- Never commit secrets to GitHub.
- Never place server API keys in frontend code.
- Dangerous actions require permission/approval.
- Current verified system state must override stale memory.
- Existing code is authoritative for exact filenames, interfaces, environment variable names, and deployed behavior.

## Build philosophy

User command:
USER REQUEST
→ CONVERSATION
→ CONTEXT/MEMORY
→ INTENT
→ PLAN
→ CAPABILITY ROUTING
→ MODEL/PROVIDER ROUTING
→ TOOL/API EXECUTION
→ VALIDATION
→ RETRY/FALLBACK
→ RESULT
→ MEMORY WRITE-BACK

Complex tasks may use multiple models, agents, tools, and external services.

## Current separation

ALREADY IMPLEMENTED / DEPLOYED:
- David AI Core orchestration layer (current verified state described in 03).
- Existing backend architecture, database, persistence, provider registry and related systems.

IN PROGRESS / EXTENSION:
- Memory & Personal Knowledge improvements.
- Provider and external-service integration hardening.

FUTURE / SEPARATE:
- Self-integration / self-upgrade / evolution engine. It has a detailed design but should not be mixed into ordinary conversation/API integration work unless explicitly requested.

## Credential safety

A credential that was ever pasted into chat should be treated as exposed and regenerated. Do not use or reproduce historical raw secret values.

## Accuracy rule

When a provider was discussed but key ownership is uncertain, mark:
“Provider discussed; credential status unconfirmed.”
Do not invent confirmation.
