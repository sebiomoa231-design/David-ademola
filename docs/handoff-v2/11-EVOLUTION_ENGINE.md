# 11 — SELF-INTEGRATION / SELF-UPGRADE / EVOLUTION ENGINE

This is a separate advanced subsystem. The user explicitly asked at one point to leave it aside while the ordinary AI integration work proceeds, but wants it preserved in the full handoff.

## Objective

David should eventually be able to:
- monitor itself
- detect failures and weaknesses
- diagnose root cause
- identify capability gaps
- research solutions
- plan improvements
- modify its own code in isolation
- test changes
- perform security checks
- perform regression tests
- create Git branches/commits/PRs
- deploy approved changes
- monitor post-deployment
- rollback failures
- remember lessons

## Safety lifecycle

OBSERVE
→ DETECT
→ ANALYZE
→ PLAN
→ RISK ASSESS
→ AUTHORIZE
→ ISOLATE
→ MODIFY
→ BUILD
→ TEST
→ SECURITY
→ REGRESSION
→ REVIEW
→ APPROVE
→ MERGE
→ DEPLOY
→ MONITOR
→ VERIFY
→ LEARN

Failure:
STOP → ROLLBACK → VERIFY → INCIDENT → LESSON

## Risk tiers

LOW:
- documentation
- non-functional tests
- safe internal refactors

MEDIUM:
- dependency updates
- performance/internal logic changes

HIGH:
- authentication
- provider routing
- memory architecture
- deployment configuration

CRITICAL:
- security architecture
- secrets
- owner permissions
- evolution engine itself
- destructive DB operations

High/Critical require owner approval.

## Safety prohibitions

David must not autonomously:
- overwrite production directly
- remove owner controls
- expose secrets
- disable audit
- disable rollback
- grant itself privileges
- bypass authorization
- disable security

## Sandbox
- isolated filesystem
- restricted network
- restricted credentials
- resource limits
- timeouts
- cleanup

## Git-first evolution
main/production protected.
Use evolution branch.
Test and validate before PR.
Trace every change to commit.

## Rollback
Keep last-known-good version.
Monitor deployment.
Auto-rollback on configured critical conditions.

## Evolution memory
Record:
- problem
- plan
- attempts
- changed files
- tests
- security checks
- commit
- PR
- deployment
- rollback
- outcome
- lessons

## Open-source components investigated
- OpenHands Software Agent SDK
- mini-SWE-agent
- Aider

Use as building blocks/reference, not as blind full-repository replacement.
Check licenses and preserve required attribution.
