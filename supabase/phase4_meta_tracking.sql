-- Phase 4 — public tracking configuration only.
-- Never store the Meta CAPI access token in axoria_store or frontend code.
insert into public.axoria_store(key,value,updated_at)
values (
  'axoria_tracking',
  jsonb_build_object('enabled', false, 'pixelId', '', 'capiEnabled', false),
  now()
)
on conflict (key) do nothing;
