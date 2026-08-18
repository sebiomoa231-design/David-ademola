# Git LFS Repair Record

## Incident

The Render checkout failed before dependency installation because Git LFS could not download two objects referenced by the preserved second upload set. The affected paths were:

- `vendor/source-sets/second/upstreams/agent-framework-main/python/packages/lab/lightning/assets/train_math_agent.png`
- `vendor/source-sets/second/upstreams/agent-framework-main/python/packages/lab/lightning/assets/train_tau2_agent.png`

The original Git LFS pointers declared object sizes of 153,014 bytes and 189,488 bytes, respectively. The deployment checkout reported that the corresponding LFS objects were unavailable, so the failure occurred during source checkout rather than during the David AI build or startup process.

## Relevance investigation

The affected directory belongs to the upstream `agent-framework-lab` Lightning package. Its README identifies the package as a GPU-heavy reinforcement-learning training integration for Microsoft Agent Framework and Agent-lightning. The two PNGs are referenced only by README training-curve image links for the `train_math_agent.py` and `train_tau2_agent.py` examples. They are not imported by David AI, the FastAPI startup path, the Intelligence Fabric adapters, the production Dockerfile, or the production Python requirements.

The repository’s Intelligence Fabric documentation defines Microsoft Agent Framework as an adapter/reference boundary and explicitly states that imported runtimes remain outside David’s base FastAPI dependency graph. The second Agent Framework tree is therefore preserved as source/reference material, but the two missing documentation images are not production dependencies.

## Repair decision

The two unresolvable documentation-only image files are removed from the preserved upstream tree. The repair does **not** remove `agent-framework-main`, the Lightning package code, its licenses, its README, its samples, or any other source-set content. The upstream `.gitattributes` file is retained; Git LFS is not disabled globally and no unrelated LFS path is changed.

This is a narrow removal of two unavailable, non-runtime assets so that the existing repository can be cloned and checked out without requiring inaccessible LFS objects. No placeholder or fabricated replacement is used.

## Verification scope

After the repair, verification must include a fresh clone and checkout, repository and backend tests, frontend type/build checks, and a deployment of the existing Render service. Deployment success must be confirmed through startup and live API checks rather than inferred from a successful Git push.
