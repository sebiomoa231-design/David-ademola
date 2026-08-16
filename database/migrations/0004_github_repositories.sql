-- 0004 GitHub multi-repository integration
-- Tracks every website repository David AI creates and auditors important
-- GitHub actions. Apply through the Supabase SQL editor or the deployment
-- migration runner. The backend always uses the server-only
-- SUPABASE_SECRET_KEY, so these tables stay private and no GitHub secrets
-- are stored here.

create table if not exists public.david_github_repositories (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  project_id text,
  repository_id bigint,
  repository_name text not null,
  repository_full_name text not null unique,
  repository_owner text not null,
  repository_url text not null,
  clone_url text,
  default_branch text not null default 'main',
  visibility text not null default 'private' check (visibility in ('private', 'public')),
  deployment_provider text,
  deployment_url text,
  deployment_status text not null default 'none' check (deployment_status in ('none', 'pending', 'building', 'live', 'error')),
  last_commit_sha text,
  last_deployment_status text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_github_audit_log (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  event text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_github_repos_project on public.david_github_repositories (project_id);
create index if not exists idx_github_audit_event on public.david_github_audit_log (event);

alter table public.david_github_repositories enable row level security;
alter table public.david_github_audit_log enable row level security;

-- Direct client roles must not read or mutate GitHub records. The backend
-- performs application-level authorization (see 0003 service-role grants).
drop policy if exists david_github_repositories_server_only on public.david_github_repositories;
create policy david_github_repositories_server_only on public.david_github_repositories
  for all to anon, authenticated
  using (false)
  with check (false);

drop policy if exists david_github_audit_server_only on public.david_github_audit_log;
create policy david_github_audit_server_only on public.david_github_audit_log
  for all to anon, authenticated
  using (false)
  with check (false);
