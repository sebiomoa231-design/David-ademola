# GitHub Deployment Handoff

## Current state

This directory is prepared as a GitHub-ready repository for David AI. The master specification now includes the cinematic multimodal command center, David HUD/Core, Visual Explanation Canvas, Agent Execution Theater, and voice/text/visual synchronization requirements.

The source was preserved from the user-supplied build and repaired in a separate working copy. The existing frontend, visual styling, voice modules, orchestrator, route surfaces, and documentation were retained. The current changes are ready to be committed locally.

## Before publishing

Choose the exact target repository before pushing. Several David AI repositories are already visible to the GitHub account, so do not assume that the newest or similarly named repository is the intended destination. The safest choices are either an existing repository explicitly selected by David or a new private repository.

The following commands are intentionally not run automatically:

```bash
gh repo create david-ai-cinematic-command-center --private --source . --remote origin --push
```

For an existing repository, the destination must first be confirmed and then the remote can be configured explicitly:

```bash
git remote add origin https://github.com/OWNER/REPOSITORY.git
git branch -M main
git push -u origin main
```

Publishing requires review of the target owner/repository and confirmation that the files should be pushed. No secrets should be added; deployment credentials belong in GitHub/Render secret configuration, not in the repository.

## Recommended first commit

Use a descriptive commit such as:

```bash
git add .
git commit -m "Preserve David AI build and add cinematic multimodal command center spec"
```

The commit should include the updated `DAVID_ADEMOLA_AI_MASTER_SPEC.md`, the repaired frontend route/client boundary, backend runtime scaffold, verification tests, handoff documentation, and `.gitignore`. Generated dependency and build directories should remain excluded.

## Post-publish checks

After the target repository is confirmed and the first push is approved, configure CI to run:

```bash
./scripts/verify-handoff.sh
```

Then configure deployment secrets and service variables through the selected deployment platform. The repository is a buildable foundation, not a claim that every external connector, persistent-memory feature, governance workflow, or provider integration has already been completed.
