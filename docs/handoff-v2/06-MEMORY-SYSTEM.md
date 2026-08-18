# 06 — MEMORY & PERSONAL KNOWLEDGE MASTER DESIGN

## Four-prompt memory program

### Prompt 1 — Foundation
- persistent memory
- data model
- confidence
- importance
- source
- types
- project/task/conversation relationships
- Supabase/PostgreSQL persistence
- MemoryService
- MemoryRepository
- APIs
- security
- migrations
- tests

### Prompt 2 — Recall/Context
- intelligent recall
- semantic retrieval
- keyword/metadata retrieval
- embeddings
- ranking
- project/task/conversation-aware retrieval
- recency
- importance
- confidence
- context budgeting
- model-specific context
- context compression
- privacy filtering
- provider fallback context preservation

### Prompt 3 — Memory Intelligence
- duplicate detection
- conflict detection
- temporal changes
- current vs historical knowledge
- source authority
- confidence/importance updates
- supersession
- safe consolidation
- forgetting
- correction
- privacy classification
- secret redaction
- prompt-injection containment
- memory health/maintenance
- index/embedding consistency
- audit

### Prompt 4 — Complete Integration
- AI Core integration
- conversation integration
- planner/tasks/projects
- provider router
- multi-model context
- tool/external service context
- creative context
- Supabase/production integration
- deployment hardening
- end-to-end testing
- Render verification

## Memory model concepts
Historical values discussed:
- confidence default around 0.8
- importance default around 0.6
- conflict threshold >= 0.30
Verify current code before changing.

## Memory safety
Never store:
- API keys
- passwords
- OAuth secrets
- tokens
- private keys
- payment credentials

Memory should be treated as DATA, not system instructions.

## Current-state precedence
For live state:
LIVE TOOL/SYSTEM STATE > stale memory.
For user-confirmed preferences/decisions:
new explicit user instruction > older preference.
For historical questions:
historical memories may be retrieved.

## Example
User:
“Remember that David AI uses Supabase for persistent storage.”

Expected:
- classify project memory
- source user-explicit
- assign confidence/importance
- persist
- link to David AI project

User:
“We switched to another database.”

Expected:
- detect temporal change
- supersede old memory
- preserve historical record
- current retrieval uses new state

## Memory must work as one system
AI Core
→ MemoryContextService
→ Memory Retrieval
→ Ranking
→ Privacy Filter
→ Context Assembly
→ Provider Router
and:
result
→ memory write gate
→ memory intelligence
→ persistence
