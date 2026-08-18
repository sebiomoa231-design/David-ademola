# 17 — DETAILED EXAMPLE WORKFLOWS

## Example A — “Create a website”

1. Conversation engine receives request.
2. Context engine retrieves active project and preferences.
3. Intent = website generation.
4. Capability router identifies:
   - requirements
   - planning
   - design
   - coding
   - testing
   - deployment if asked.
5. Model router selects appropriate models.
6. Planner builds task graph.
7. Coding agent/provider generates code.
8. Reviewer checks code.
9. Build runs.
10. Failures routed to debugging/coding model.
11. Tests rerun.
12. GitHub commit/push if requested.
13. Deployment tool if requested.
14. Render/Vercel health verification if configured.
15. Final response states actual state.

## Example B — “Remember this”

User:
“Remember that David AI uses Supabase.”

1. Intent = memory write.
2. Memory write gate.
3. Sensitive data filter.
4. Type = project/decision/fact as appropriate.
5. Project association = David AI.
6. Source = user explicit.
7. Confidence/importance assigned.
8. Duplicate search.
9. Conflict search.
10. Persist.
11. Embedding if configured.
12. Audit.
13. Confirm truthfully.

## Example C — “Upload to YouTube”

1. Intent = YouTube publish/upload.
2. Resolve connected account.
3. Check authorization/scopes.
4. Validate media.
5. Validate metadata.
6. Execute upload.
7. Poll/monitor if async.
8. Verify resource exists.
9. Apply visibility/publish policy.
10. Return actual result.
11. Store safe event metadata.
12. Never expose OAuth tokens.

## Example D — “Fix the repository”

1. Resolve GitHub repository.
2. Retrieve relevant files/history.
3. Analyze with coding/reasoning model.
4. Create sandbox/branch if authorized.
5. Modify code.
6. Run tests.
7. Review.
8. Commit.
9. PR if required.
10. Deploy only with authorization.
11. Verify.
12. Record result.

## Example E — “Create a promotional video”

1. Understand target.
2. Retrieve project/brand context.
3. Plan script/scenes.
4. Generate script.
5. Review.
6. Generate media with configured provider.
7. Voice with ElevenLabs if configured.
8. Validate output.
9. Store asset.
10. Prepare YouTube/TikTok workflow if requested.
11. Publish only if authorized.
