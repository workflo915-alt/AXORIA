-- Applied to the AXORIA Supabase project during Phase 5 launch hardening.
-- Keep the public storefront read surface minimal and avoid duplicate permissive SELECT policies.

drop policy if exists storefront_read_public on public.axoria_store;
drop policy if exists storefront_read_tracking on public.axoria_store;

create policy storefront_read_public
on public.axoria_store
for select
to anon
using (
  key = any (
    array[
      'axoria_products'::text,
      'axoria_categories'::text,
      'axoria_tracking'::text
    ]
  )
);
