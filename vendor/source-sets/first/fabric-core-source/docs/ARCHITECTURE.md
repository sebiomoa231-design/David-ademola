# David AI Intelligence Fabric

## Control-plane principle

David is the single orchestration/control plane. The supplied projects are capability
providers, not competing brains.

A task is represented as:

Goal -> Plan -> Step -> Agent -> Skill -> Tool -> Provider/Service -> Artifact -> Verification

The router selects a capability by task requirements, health and policy.

## Why the source trees stay isolated

The supplied repositories span Python, TypeScript/Node, Go, GPU/CUDA and platform infrastructure.
Flattening them into one runtime would create dependency collisions and would make upgrades unsafe.

The Fabric therefore owns the contracts and routing while each heavy project can run in its native
runtime when needed.

## Failure strategy

1. Never claim success from a missing service.
2. If a selected service is unavailable, mark the step failed/unavailable.
3. If multiple compatible providers exist, the orchestrator may choose a healthy alternative.
4. External side effects remain approval-gated.
5. Every run should be traceable through the run/event store.

## Integration priority

1. David core
2. Provider routing
3. Agent orchestration
4. Browser/coding
5. Creative/voice
6. Durable execution/automation
7. Observability
8. Deployment

This order is a recommendation, not a claim that all external repositories are already wired.
