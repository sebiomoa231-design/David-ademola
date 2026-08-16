-- David AI server-only RLS posture
-- The backend uses the Supabase server secret and performs application-level
-- authorization. Direct client roles must not read or mutate David tables.

alter table public.david_projects enable row level security;
alter table public.david_tasks enable row level security;
alter table public.david_memories enable row level security;
alter table public.david_conversations enable row level security;
alter table public.david_messages enable row level security;
alter table public.david_assets enable row level security;
alter table public.david_generations enable row level security;
alter table public.david_favorites enable row level security;

drop policy if exists david_projects_server_only on public.david_projects;
create policy david_projects_server_only on public.david_projects
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_tasks_server_only on public.david_tasks;
create policy david_tasks_server_only on public.david_tasks
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_memories_server_only on public.david_memories;
create policy david_memories_server_only on public.david_memories
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_conversations_server_only on public.david_conversations;
create policy david_conversations_server_only on public.david_conversations
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_messages_server_only on public.david_messages;
create policy david_messages_server_only on public.david_messages
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_assets_server_only on public.david_assets;
create policy david_assets_server_only on public.david_assets
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_generations_server_only on public.david_generations;
create policy david_generations_server_only on public.david_generations
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_favorites_server_only on public.david_favorites;
create policy david_favorites_server_only on public.david_favorites
  for all to anon, authenticated
  using (false)
  with check (false);
