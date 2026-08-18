# 02 — BACKEND ARCHITECTURE AND HISTORICAL STRUCTURE

## Referenced stack

- Python
- FastAPI
- Docker
- Render-ready deployment
- python-dotenv/environment configuration
- Supabase/PostgreSQL
- persistent storage
- modular providers
- test suite

## Referenced project structure

```text
david/
  providers/
  core/
  memory/
  api/
  models/
  utils/
data/
tests/
```

Provider integrations discussed for:
- Gemini
- Groq
- Hugging Face
- OpenRouter
- Cloudflare
- Cerebras
- SambaNova
- other providers as later configured

Referenced data concepts:
- memories.json
- projects.json
- tasks.json
- learning.json
- conversations.json
- decisions.json
- settings.json

## DavidMind / core concepts discussed

DavidMind was described as containing/connecting:
- memory
- projects
- tasks
- learning
- conversations
- decisions
- permissions
- planner
- content
- websites
- security
- voice

Example settings previously discussed:
- name: David
- voice disabled by default in an earlier code example

## Memory model details previously discussed

- confidence default: 0.8
- importance default: 0.6
- memory conflict threshold >= 0.30 was discussed
- these values should be treated as historical implementation guidance and verified against current code before changing.

## Provider router responsibilities

- read keys from environment
- select provider/model
- provider health
- fallback
- retry
- error classification
- model availability
- usage tracking
- logging
- no frontend secrets

## Current rule

Do not assume old file layout is still exact. The currently deployed backend/repository is the source of truth. Extend actual code.
