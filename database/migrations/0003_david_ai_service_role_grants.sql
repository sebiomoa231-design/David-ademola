-- David AI service-role privileges
-- The backend sends the Supabase server secret and never exposes these tables
-- to browser clients. Direct anon/authenticated access remains denied by the
-- server-only RLS policies in 0002_david_ai_server_only_rls.sql.

grant usage on schema public to service_role;
grant select, insert, update, delete on table
  public.david_projects,
  public.david_tasks,
  public.david_memories,
  public.david_conversations,
  public.david_messages,
  public.david_assets,
  public.david_generations,
  public.david_favorites,
  public.david_github_repositories,
  public.david_github_audit_log
to service_role;
