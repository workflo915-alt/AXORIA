-- Aggregated category analytics for the authenticated AXORIA admin.

create or replace view public.category_interest_stats
with (security_invoker = true)
as
select
  category,
  count(*)::bigint as clicks_total,
  count(distinct session_id)::bigint as visitors_unique,
  count(*) filter (where created_at >= now() - interval '7 days')::bigint as clicks_7d,
  count(distinct session_id) filter (where created_at >= now() - interval '7 days')::bigint as visitors_7d,
  max(created_at) as last_view_at
from public.category_views
group by category;

revoke all on public.category_interest_stats from anon;
grant select on public.category_interest_stats to authenticated;
