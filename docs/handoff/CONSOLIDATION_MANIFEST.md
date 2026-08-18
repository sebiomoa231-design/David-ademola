# David AI Consolidation Manifest

This repository is the canonical merged David AI project. The current GitHub source tree is the implementation baseline because it contains the richest backend control plane, intelligence fabric, provider boundaries, deployment configuration, tests, and the upgraded Next.js command center.

The supplied handoff documents are preserved under `docs/handoff/source-specs/`. The original ZIP archives are intentionally not copied into the repository because they contain overlapping source trees and dependency/vendor payloads. Their SHA-256 checksums are recorded in `source-archive-sha256.txt` for traceability.

## Merge decisions

| Source | Decision |
| --- | --- |
| Current GitHub repository | Authoritative implementation source |
| Preserved/repaired handoff | Used as runtime, packaging, testing, and truthfulness reference; compatible documentation retained |
| Complete build and architecture archives | Used as comparison material; overlapping duplicate source trees were not blindly copied |
| Master specification and correction plan | Preserved and reflected in the frontend execution model and route coverage |

## Current upgraded surfaces

The Next.js command center includes dashboard, conversation, agents, projects, tasks, memory, files and knowledge, creative suite, website builder, video studio, providers, activity log, devices, settings, and owner governance surfaces. Dashboard objectives now flow through the existing intelligence API contract for goal creation, planning, capability routing, governed run creation, run details, approval states, verification, completion, and truthful degraded handling.

## Verification contract

The frontend must pass type checking, tests, and production build. The backend must pass Python compilation and its test suite. Sensitive actions must remain approval-gated, provider credentials must remain server-side, and the interface must not label a capability as complete when its backend is unavailable.
