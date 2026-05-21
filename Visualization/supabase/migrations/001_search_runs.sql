-- Chạy trong Supabase SQL Editor hoặc: supabase db push

create table if not exists public.search_runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  mode text not null check (mode in ('puzzle', 'vacuum')),
  algorithm text not null,
  found boolean not null default false,
  message text,
  elapsed_ms integer,
  steps_count integer default 0,
  start_state jsonb,
  path jsonb,
  tree jsonb
);

alter table public.search_runs enable row level security;

-- Demo: cho phép đọc/ghi ẩn danh (tighten khi deploy production)
create policy "search_runs_select_anon"
  on public.search_runs for select
  to anon, authenticated
  using (true);

create policy "search_runs_insert_anon"
  on public.search_runs for insert
  to anon, authenticated
  with check (true);

create index if not exists search_runs_created_at_idx
  on public.search_runs (created_at desc);
