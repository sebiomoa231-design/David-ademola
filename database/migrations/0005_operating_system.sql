-- David AI Phase 6–8 governed operating-system state.
-- All records are owner-scoped and payloads contain no provider secrets.

create table if not exists public.david_operating_records (
  id text primary key,
  owner_id text not null default 'default-owner',
  entity_type text not null,
  status text,
  project_id text,
  parent_id text,
  name text,
  payload jsonb not null default '{}'::jsonb,
  due_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists david_operating_records_entity_idx on public.david_operating_records (owner_id, entity_type, updated_at desc);
create index if not exists david_operating_records_status_idx on public.david_operating_records (owner_id, status, updated_at desc);
create index if not exists david_operating_records_project_idx on public.david_operating_records (owner_id, project_id, updated_at desc);

create table if not exists public.david_operating_events (
  id uuid primary key,
  owner_id text not null default 'default-owner',
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  actor text not null default 'david',
  correlation jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists david_operating_events_type_idx on public.david_operating_events (owner_id, event_type, created_at desc);
create index if not exists david_operating_events_created_idx on public.david_operating_events (owner_id, created_at desc);

create table if not exists public.david_operating_audit (
  id uuid primary key,
  owner_id text not null default 'default-owner',
  action text not null,
  actor text not null,
  policy_decision jsonb not null default '{}'::jsonb,
  result text not null,
  payload jsonb not null default '{}'::jsonb,
  correlation jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists david_operating_audit_action_idx on public.david_operating_audit (owner_id, action, created_at desc);

alter table public.david_operating_records enable row level security;
alter table public.david_operating_events enable row level security;
alter table public.david_operating_audit enable row level security;

drop policy if exists david_operating_records_owner_policy on public.david_operating_records;
create policy david_operating_records_owner_policy on public.david_operating_records for all using (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner')) with check (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner'));

drop policy if exists david_operating_events_owner_policy on public.david_operating_events;
create policy david_operating_events_owner_policy on public.david_operating_events for all using (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner')) with check (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner'));

drop policy if exists david_operating_audit_owner_policy on public.david_operating_audit;
create policy david_operating_audit_owner_policy on public.david_operating_audit for all using (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner')) with check (owner_id = coalesce(auth.jwt() ->> 'sub', 'default-owner'));

-- The existing backend uses the server-side Supabase secret only. Grants remain
-- explicit so a newly created table cannot cause production 500s.
grant select, insert, update, delete on public.david_operating_records to service_role;
grant select, insert, update, delete on public.david_operating_events to service_role;
grant select, insert, update, delete on public.david_operating_audit to service_role;
