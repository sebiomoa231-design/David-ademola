-- David AI core persistence schema
-- Apply this migration in the Supabase SQL editor or through the deployment migration runner.
-- The backend uses the server-only SUPABASE_SECRET_KEY and the tables remain private.

create extension if not exists pgcrypto;
create extension if not exists vector;

create table if not exists public.david_projects (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  name text not null,
  description text not null default '',
  goals jsonb not null default '[]'::jsonb,
  decisions jsonb not null default '[]'::jsonb,
  milestones jsonb not null default '[]'::jsonb,
  blockers jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_tasks (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  project_id text not null default '',
  title text not null,
  notes text not null default '',
  status text not null default 'todo' check (status in ('todo', 'doing', 'done')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_memories (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  type text not null default 'general',
  content text not null,
  confidence double precision not null default 0.8,
  importance double precision not null default 0.6,
  source text not null default 'user',
  tags jsonb not null default '[]'::jsonb,
  status text not null default 'active' check (status in ('active', 'archived')),
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_conversations (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  title text not null default 'New conversation',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_messages (
  id text primary key default gen_random_uuid()::text,
  conversation_id text not null references public.david_conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.david_assets (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  project_id text,
  filename text not null,
  storage_path text not null unique,
  content_type text not null default 'application/octet-stream',
  size_bytes bigint not null default 0,
  kind text not null default 'other' check (kind in ('image', 'video', 'audio', 'document', 'website', 'other')),
  metadata jsonb not null default '{}'::jsonb,
  favorite boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.david_generations (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null default 'default-owner',
  project_id text,
  asset_id text references public.david_assets(id) on delete set null,
  kind text not null default 'other',
  prompt text not null default '',
  provider text not null default 'unknown',
  status text not null default 'completed',
  output text not null default '',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.david_favorites (
  owner_id text not null default 'default-owner',
  asset_id text not null references public.david_assets(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (owner_id, asset_id)
);

create index if not exists david_memories_active_created_idx on public.david_memories (status, created_at desc);
create index if not exists david_tasks_project_status_idx on public.david_tasks (project_id, status);
create index if not exists david_messages_conversation_created_idx on public.david_messages (conversation_id, created_at asc);
create index if not exists david_assets_project_kind_created_idx on public.david_assets (project_id, kind, created_at desc);
create index if not exists david_generations_project_created_idx on public.david_generations (project_id, created_at desc);

-- Keep the bucket private. The backend returns only time-limited signed URLs.
insert into storage.buckets (id, name, public)
values ('Davidai', 'Davidai', false)
on conflict (id) do update set public = false;

-- All David tables are intentionally protected. The backend uses the Supabase
-- secret key and performs application-level authorization before data access.
alter table public.david_projects enable row level security;
alter table public.david_tasks enable row level security;
alter table public.david_memories enable row level security;
alter table public.david_conversations enable row level security;
alter table public.david_messages enable row level security;
alter table public.david_assets enable row level security;
alter table public.david_generations enable row level security;
alter table public.david_favorites enable row level security;

comment on table public.david_projects is 'David AI project memory and workspaces';
comment on table public.david_tasks is 'David AI task records';
comment on table public.david_memories is 'David AI long-term memory records with optional pgvector embeddings';
comment on table public.david_assets is 'Metadata for private objects stored in the Davidai bucket';
comment on table public.david_generations is 'Creative Suite and generation history records';
