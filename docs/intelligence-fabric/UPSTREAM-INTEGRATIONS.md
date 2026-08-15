# David AI Intelligence Fabric: Upstream Integration Record

David AI remains the single application and control plane. The uploaded repositories are not mounted as competing applications; they are classified as native capabilities, service adapters, runtime references, or incomplete source records. All capability discovery, goal planning, approval policy, run tracking, and adapter health are exposed through `/api/intelligence`.

| Upstream | Useful capability | Integration boundary | Runtime | Upload/license status |
|---|---|---|---|---|
| David AI existing backend | Chat, memory, projects, tasks, legacy planning, voice, knowledge, website, agent routes | Native in-process routes | Python/FastAPI | Existing functionality preserved |
| David AI Intelligence Fabric Core | Capability registry, goal planning, run/event tracking, approval policy, service health | Native `david_fabric` package | Python | Integrated; persistence adapted to David JSON storage |
| David Creative Backend | Image/video/artwork/music/voice/enhancer/editor model catalog and generation-job shape | External Node service adapter | Node/Express/Mongo | Recovered; no upstream license file was present in the supplied tree, so it is not vendored as executable source |
| Microsoft Agent Framework | Multi-agent orchestration, middleware, workflows, checkpointing, human-in-the-loop, observability, declarative YAML agents | Adapter/reference boundary | Python/.NET | Recovered and inspected; MIT license preserved |
| Playwright | Browser automation, test runner, CLI, MCP-oriented agent automation | External Node service adapter | Node | Nested upload partial; Apache-2.0 license and NOTICE preserved |
| WanGP/Wan2GP | GPU video/image/audio/TTS generation, queues, headless/API workflows | External GPU service adapter | Python/CUDA | Nested upload partial; custom WanGP license and Dockerfile preserved. Paid API/SaaS/hosted/OEM use requires separate permission under the supplied license |
| n8n | Visual workflow automation, AI-agent workflows, webhooks, approvals, integrations | External Node service adapter | Node | Nested upload partial; Sustainable Use and Enterprise license records preserved. `.ee` source is not vendored |
| Voice backend split archives | Potential voice backend reference | Not activated; adapter reports incomplete upload | Python/FastAPI | Only `part-ab` supplied; corresponding `part-aa` is missing, so no executable integration is claimed |

## Adapter behavior

The adapter registry is deliberately conservative. An adapter with no configured URL reports `unconfigured`; an adapter with a URL receives a bounded health probe and reports `healthy`, `unhealthy`, or `unreachable`. David does not silently execute browser automation, GPU generation, workflow runs, deployments, purchases, or external writes merely because an adapter is configured. Fabric approval policy remains the gate for side effects.

The native `/api/plan` endpoint remains the lightweight legacy planner used by existing clients. Fabric planning is additive at `POST /api/intelligence/goals/{goal_id}/plan`, and run state is tracked under `/api/intelligence/runs`.

## Preserved upstream files

The attribution bundle under `docs/intelligence-fabric/upstreams/` contains the recovered upstream README, license, NOTICE, package metadata, Dockerfile, and selected operational configuration files. The full multi-runtime source trees remain in the quarantined workspace used for inspection; they are not copied wholesale into the Python application, which avoids dependency conflicts and avoids presenting n8n or WanGP as code that David can redistribute or sell without their separate terms.
