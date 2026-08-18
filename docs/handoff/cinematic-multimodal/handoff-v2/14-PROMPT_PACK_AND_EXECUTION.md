# 14 — PROMPT PACK AND HOW THE SYSTEM SHOULD BE BUILT

## AI/Core prompts developed

1. Conversation architecture + provider router
2. Context/memory/intent
3. Multi-model intelligence, capability routing, orchestration, fallback, review
4. Tool/capability/action execution fabric
5. External services, OAuth, connected accounts, webhooks
6. Provider execution/fallback/capability routing
7. Creative Suite: website, image, video, voice
8. Memory foundation/recall/intelligence/integration prompts

## Memory-specific four-prompt sequence
1. Foundation
2. Intelligent recall/context
3. Memory intelligence/conflicts/dedup/consolidation/privacy
4. Full integration/AI Core/providers/workflows/production

## How Manus should execute

Read the entire relevant prompt pack before coding.
Inspect existing source before changing it.
Map requirements to existing modules.
Reuse existing systems.
Implement real code.
Run tests.
Fix failures.
Review secrets.
Commit.
Push.
Deploy.
Verify.
Report truthfully.

## Generic implementation workflow

UNDERSTAND
→ INSPECT
→ PLAN
→ IMPLEMENT
→ TEST
→ DEBUG
→ SECURITY CHECK
→ COMMIT
→ PUSH
→ DEPLOY
→ LIVE TEST
→ FIX
→ REDEPLOY
→ VERIFY

## No-fabrication policy

Do not claim:
- test passed unless run
- commit exists unless pushed
- PR exists unless created
- deployment succeeded unless verified
- provider configured unless credential and API work
- memory exists unless persisted
- upload published unless verified

## Short execution command

Use the existing David AI architecture and implement the supplied David AI specifications directly into the current backend. Preserve all existing functionality, never hard-code secrets, test all changes, automatically fix real errors, commit and push verified changes to GitHub, deploy to the existing Render service when requested, and verify the live system before reporting success.
