-- Keep category analytics attached to a stable category ID even if its label is renamed.

drop view if exists public.category_interest_stats;

alter table public.category_views add column if not exists category_id text;

update public.category_views
set category_id = category
where category_id is null;

alter table public.category_views alter column category_id set not null;

alter table public.category_views
  drop constraint if exists category_views_category_id_length;
alter table public.category_views
  add constraint category_views_category_id_length check (char_length(category_id) between 1 and 100);

create index if not exists category_views_category_id_created_idx
  on public.category_views (category_id, created_at desc);

drop policy if exists category_views_insert_public on public.category_views;
create policy category_views_insert_public
  on public.category_views
  for insert
  to anon, authenticated
  with check (
    char_length(category_id) between 1 and 100
    and char_length(category) between 1 and 100
    and session_id is not null
  );

create view public.category_interest_stats
with (security_invoker = true)
as
select
  category_id,
  count(*)::bigint as clicks_total,
  count(distinct session_id)::bigint as visitors_unique,
  count(*) filter (where created_at >= now() - interval '7 days')::bigint as clicks_7d,
  count(distinct session_id) filter (where created_at >= now() - interval '7 days')::bigint as visitors_7d,
  max(created_at) as last_view_at
from public.category_views
group by category_id;

revoke all on public.category_interest_stats from anon;
grant select on public.category_interest_stats to authenticated;
