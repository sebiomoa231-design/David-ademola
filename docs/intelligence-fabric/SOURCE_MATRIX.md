# Source matrix

| Source | Primary role | Native runtime | David integration boundary |
|---|---|---|---|
| David-ademola-main | Main David application | Python/FastAPI + frontend | Native |
| DavidAI-backend-with-voice | Voice/backend reference | Python/FastAPI | Adapter/merge after audit |
| david-ai-backend | Creative backend | Node/Express/Mongo | Service/adapter |
| agent-framework-main | Agent orchestration | .NET/Python/other | Adapter/reference |
| OpenHands-main | Coding agent | Python | Service/adapter |
| browser-use-main | Browser agent | Python | Service/adapter |
| playwright-main | Browser automation | Node | Service/adapter |
| ComfyUI-master | Image workflows | Python | Service/adapter |
| Wan2GP-main | Video generation | Python/CUDA | GPU service |
| chatterbox-master | TTS | Python/PyTorch | Voice service |
| faster-whisper-master | STT | Python/CTranslate2 | Speech service |
| langfuse-main | Observability | Node/ClickHouse stack | Service |
| langgraph-main | Stateful orchestration | Python | Library/adapter |
| n8n-master | Automation | Node | Service |
| temporal-main | Durable execution | Go/server | Service |
| coolify-main | Deployment | PHP/TS/platform | Deployment service |
| dokploy-canary | Deployment | Node/TypeScript | Deployment service |

No source should be treated as "the brain" by itself.
