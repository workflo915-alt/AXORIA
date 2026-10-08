-- Applied to the AXORIA Supabase project during Phase 5 launch hardening.
-- Normalize Moroccan phone numbers before they are stored and reject invalid values.

create or replace function public.axoria_normalize_order_phone()
returns trigger
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_phone text;
begin
  v_phone := trim(coalesce(new.phone, ''));
  v_phone := regexp_replace(v_phone, '[\s().-]', '', 'g');

  if v_phone like '00212%' then
    v_phone := '0' || substring(v_phone from 6);
  elsif v_phone like '+212%' then
    v_phone := '0' || substring(v_phone from 5);
  elsif v_phone like '212%' then
    v_phone := '0' || substring(v_phone from 4);
  end if;

  v_phone := regexp_replace(v_phone, '[^0-9]', '', 'g');

  if v_phone !~ '^0[5-7][0-9]{8}$' then
    raise exception 'Invalid phone';
  end if;

  new.phone := v_phone;
  return new;
end;
$$;

drop trigger if exists trg_axoria_normalize_order_phone on public.orders;
create trigger trg_axoria_normalize_order_phone
before insert or update of phone on public.orders
for each row
execute function public.axoria_normalize_order_phone();
