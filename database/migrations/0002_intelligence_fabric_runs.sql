-- Durable canonical Intelligence Fabric records for David AI.
-- This extends the existing David AI Supabase project; it creates no parallel store.

create table if not exists public.david_agent_goals (
  id text primary key,
  owner_id text not null default 'default-owner',
  title text not null,
  objective text not null,
  project_id text,
  context jsonb not null default '{}'::jsonb,
  status text not null default 'created',
  created_at timestamptz not null default now()
);

create table if not exists public.david_agent_plans (
  goal_id text primary key references public.david_agent_goals(id) on delete cascade,
  plan jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.david_agent_runs (
  id text primary key,
  owner_id text not null default 'default-owner',
  goal_id text not null references public.david_agent_goals(id) on delete cascade,
  status text not null default 'queued',
  approved boolean not null default false,
  objective text,
  requested_capability text,
  selected_capability text,
  selected_agent text,
  selected_tool text,
  selected_provider text,
  failure_reason text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists public.david_agent_attempts (
  id text primary key,
  run_id text not null references public.david_agent_runs(id) on delete cascade,
  capability_id text not null,
  status text not null default 'queued',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  finished_at timestamptz
);

create table if not exists public.david_agent_artifacts (
  id text primary key,
  run_id text not null references public.david_agent_runs(id) on delete cascade,
  attempt_id text,
  name text not null,
  kind text not null,
  uri text,
  content_type text,
  checksum text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.david_agent_verifications (
  id text primary key,
  run_id text not null references public.david_agent_runs(id) on delete cascade,
  attempt_id text,
  status text not null default 'pending',
  checks jsonb not null default '[]'::jsonb,
  message text,
  created_at timestamptz not null default now()
);

create table if not exists public.david_agent_events (
  id text primary key default gen_random_uuid()::text,
  run_id text not null references public.david_agent_runs(id) on delete cascade,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists david_agent_runs_goal_created_idx on public.david_agent_runs (goal_id, created_at desc);
create index if not exists david_agent_runs_status_created_idx on public.david_agent_runs (status, created_at desc);
create index if not exists david_agent_attempts_run_created_idx on public.david_agent_attempts (run_id, created_at asc);
create index if not exists david_agent_artifacts_run_created_idx on public.david_agent_artifacts (run_id, created_at asc);
create index if not exists david_agent_verifications_run_created_idx on public.david_agent_verifications (run_id, created_at asc);
create index if not exists david_agent_events_run_created_idx on public.david_agent_events (run_id, created_at asc);

alter table public.david_agent_goals enable row level security;
alter table public.david_agent_plans enable row level security;
alter table public.david_agent_runs enable row level security;
alter table public.david_agent_attempts enable row level security;
alter table public.david_agent_artifacts enable row level security;
alter table public.david_agent_verifications enable row level security;
alter table public.david_agent_events enable row level security;

comment on table public.david_agent_runs is 'Canonical durable governed David AI agent runs shared by Command Center and Agent Nexus';
comment on table public.david_agent_events is 'Redacted lifecycle events for canonical David AI agent runs';
