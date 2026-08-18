# 07 — AGENTS, TASKS, MANUS, AND MULTI-MODEL ORCHESTRATION

## Central model

David AI is the orchestrator.

External/agentic systems are providers or tools, not replacements for David.

```text
USER
 ↓
DAVID AI CORE
 ↓
INTENT
 ↓
CAPABILITY
 ↓
TASK PLANNER
 ↓
ORCHESTRATOR
 ├─ Research Agent
 ├─ Coding Agent
 ├─ Debugging Agent
 ├─ Testing Agent
 ├─ Security Agent
 ├─ Website Agent
 ├─ Image Agent
 ├─ Video Agent
 ├─ Voice Agent
 ├─ File/Data Agent
 ├─ Deployment Agent
 └─ Monitoring Agent
 ↓
TOOLS / PROVIDERS
 ↓
VALIDATION
 ↓
DAVID
```

## Manus as a provider/agentic execution system

User stated they have a Manus API key.

Manus should be integrated as an agentic execution provider where supported:
- complex multi-step tasks
- coding/build
- research
- project/file operations
- autonomous task execution
- website/app development workflows
- other tasks allowed by its actual API

Do not make Manus the David AI core.
Do not replace David with Manus.
Do not let Manus bypass David policy/security.
Use the official Manus API contract.
Verify exact environment variable name before implementation.

## Multi-model example: website

User:
“Create a website for my business.”

Possible orchestration:
1. intent
2. requirements
3. planning model
4. design/architecture model
5. coding model/agent
6. review model
7. tests
8. debug model if needed
9. GitHub
10. deployment
11. verification
12. final response

Not every request needs every stage.

## Model specialization
Potential roles:
- strong reasoning: Anthropic/OpenAI/Gemini
- fast inference: Groq/Cerebras/SambaNova
- multi-model gateway: OpenRouter
- specialized embeddings: Voyage
- voice: ElevenLabs
- video: Runway/Luma only when configured
- website/UI: v0 only when configured; otherwise coding-capable models/agents
- agentic execution: Manus where API is available

## Agent permissions
Separate:
- read
- write sandbox
- execute tests
- create branch
- create commit
- create PR
- deploy
- rollback
- admin/security modification

High-impact actions require approval.
Do not allow infinite loops.
Apply time/action/retry/resource budgets.
