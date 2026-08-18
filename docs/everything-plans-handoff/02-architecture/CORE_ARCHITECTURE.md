# DAVID AI — CORE ARCHITECTURE

## Overall request flow
USER
→ Conversation Engine
→ Context + Memory
→ Intent
→ AI Core
→ Task/Workflow Planner
→ Capability Router
→ Model/Provider Router
→ Tool Router
→ External Service / internal tool
→ Validation
→ Result synthesis
→ Memory write-back when appropriate
→ Response

## Provider routing
Capability → eligible providers/models → health/credentials/capability checks → primary → fallback(s) → result normalization.

## Multi-model orchestration
A single user command may become multiple stages:
- planning
- research
- coding
- review
- testing
- correction
- synthesis

Stages may be sequential or parallel when safe. Each receives only the context it needs.

## Tool security boundary
Model proposes structured tool request → backend validates → authorization/policy → tool executes → result → verification.
Models never receive unrestricted credentials or raw infrastructure access.

## Memory architecture
AI Core → Memory Context Service → Retrieval → Ranking → Privacy Filter → Context Assembly → Model.
Memory writes flow through validation → secret filtering → classification → duplicate/conflict decision → persistence → indexes/embeddings/audit.

## External connector architecture
External Service Manager → connector → secure credentials/OAuth → tool operation → normalized result → verification.

## Long-running work
API → queue → worker → checkpoint/job state → result/audit.

## Self-evolution architecture
Observe → detect → analyze → plan → risk → isolate → modify → build/test → security → regression → branch/commit/PR → approval → deploy → monitor → rollback → learn.
