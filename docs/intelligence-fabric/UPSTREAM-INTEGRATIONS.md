# David AI Intelligence Fabric: Upstream Integration Record

David AI remains the single application and control plane. The uploaded repositories are not mounted as competing applications; they are classified as native capabilities, service adapters, runtime references, or incomplete source records. All capability discovery, goal planning, approval policy, run tracking, and adapter health are exposed through `/api/intelligence`.

| Upstream | Useful capability | Integration boundary | Runtime | Upload/license status |
|---|---|---|---|---|
| David AI existing backend | Chat, memory, projects, tasks, legacy planning, voice, knowledge, website, agent routes | Native in-process routes | Python/FastAPI | Existing functionality preserved |
| David AI Intelligence Fabric Core | Capability registry, goal planning, run/event tracking, approval policy, service health | Native `david_fabric` package | Python | Integrated; persistence adapted to David JSON storage |
| David Creative Backend | Image/video/artwork/music/voice/enhancer/editor model catalog and generation-job shape | External Node service adapter | Node/Express/Mongo | Recovered from Pack 1; no upstream license file was present, so executable source is not vendored |
| Microsoft Agent Framework | Multi-agent orchestration, middleware, workflows, checkpointing, human-in-the-loop, observability, declarative YAML agents | Adapter/reference boundary | Python/.NET | Recovered from Pack 1; MIT license preserved |
| OpenHands Agent Canvas | Coding-agent sessions, remote/local agent backends, coding automations, GitHub/webhook workflows | External coding-worker adapter | Node/React/agent-server | Recovered from Pack 1; MIT license and package metadata preserved |
| Browser Use | Browser-agent navigation, form filling, extraction, custom tools, web research | External Python browser-agent adapter | Python 3.11+ | Recovered from Pack 1; MIT license, Dockerfile, and dependency metadata preserved |
| Playwright | Browser automation, test runner, CLI, MCP-oriented agent automation | External Node service adapter | Node | Recovered as a partial nested archive across Pack 2 uploads; Apache-2.0 license and NOTICE preserved |
| ComfyUI | Image generation and diffusion workflow execution | External GPU image-worker adapter | Python/CUDA | Recovered from Pack 2-1/2-2; GPL-3.0 license and runtime metadata preserved; source is not vendored |
| WanGP/Wan2GP | GPU video/image/audio/TTS generation, queues, headless/API workflows | External GPU service adapter | Python/CUDA | Recovered as partial nested archives across Pack 3 uploads; custom WanGP license and Dockerfile preserved. Paid API/SaaS/hosted/OEM use requires separate permission under the supplied license |
| Chatterbox | English and multilingual TTS, voice cloning, expressive/paralinguistic speech | External GPU voice-worker adapter | Python/PyTorch | Recovered from Pack 2-1/2-2; upstream license and Torch/Transformers dependency metadata preserved; not added to David’s base requirements |
| faster-whisper | CPU/GPU Whisper transcription, quantization, VAD, word timestamps | External STT worker adapter | Python/CTranslate2 | Recovered from Pack 2-1/2-2; MIT license and Docker/runtime metadata preserved. One recovered test WAV entry has a CRC/overlap defect, so only source metadata is trusted |
| n8n | Visual workflow automation, AI-agent workflows, webhooks, approvals, integrations | External Node service adapter | Node | Recovered as a partial nested archive from Pack 4; Sustainable Use and Enterprise license records preserved. `.ee` source is not vendored |
| Voice backend split archives | Potential FastAPI/Piper voice backend and Ryan voice model reference | Not activated; adapter reports incomplete upload | Python/FastAPI | Both `part-aa` names and `part-ab` fragments were supplied, but the exposed central directory is offset by 83,886,080 bytes and required middle chunks are absent. No license entry was recoverable; no executable integration is claimed |

## Archive coverage and deduplication

Every supplied ZIP and split fragment was validated or boundedly salvaged. Packs 2-1 and 2-2 contain byte-identical Playwright, ComfyUI, and Chatterbox nested archives; their faster-whisper entries differ but both have a damaged test fixture. Packs 2-3, 2-4, and 2-5 are continuation fragments exposing only Playwright data. Packs 3, 3-1, and 3-2 expose partial Wan2GP nested data, while Pack 4 exposes the partial n8n nested archive. Duplicate uploads were not copied into David, and no ZIP or split fragment was committed.

## Adapter behavior

The adapter registry is deliberately conservative. An adapter with no configured URL reports `unconfigured`; an adapter with a URL receives a bounded health probe and reports `healthy`, `unhealthy`, or `unreachable`. David does not silently execute browser automation, GPU generation, workflow runs, coding agents, deployments, purchases, or external writes merely because an adapter is configured. Fabric approval policy remains the gate for side effects.

The native `/api/plan` endpoint remains the lightweight legacy planner used by existing clients. Fabric planning is additive at `POST /api/intelligence/goals/{goal_id}/plan`, and run state is tracked under `/api/intelligence/runs`.

## Preserved upstream files

The attribution bundle under `docs/intelligence-fabric/upstreams/` contains the recovered upstream README, license, NOTICE, package metadata, Dockerfile, selected operational configuration files, and the recoverable voice-backend metadata. The full multi-runtime source trees remain in the quarantined workspace used for inspection; they are not copied wholesale into the Python application, which avoids dependency conflicts and avoids presenting GPL, n8n, WanGP, or incomplete voice code as code that David can redistribute or sell without observing the applicable upstream terms.
