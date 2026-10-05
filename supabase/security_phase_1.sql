-- AXORIA — Security Phase 1
-- Run this in Supabase SQL Editor ONLY after the new authenticated admin page is ready.
-- This migration removes anonymous read/write access to private/admin data.
-- IMPORTANT: in Supabase Authentication settings, disable public email sign-ups
-- and create the owner/admin account manually before applying this migration.

begin;

-- -----------------------------------------------------------------------------
-- 1) Store/catalog table
-- Public visitors may only read storefront data.
-- Only authenticated users may change shared store data.
-- -----------------------------------------------------------------------------

alter table if exists public.axoria_store enable row level security;

-- Remove the broad policies used by the original single-file prototype.
drop policy if exists "public read" on public.axoria_store;
drop policy if exists "public write" on public.axoria_store;
drop policy if exists "public update" on public.axoria_store;
drop policy if exists "public delete" on public.axoria_store;
drop policy if exists "storefront_read_public" on public.axoria_store;
drop policy if exists "admin_manage_store" on public.axoria_store;

revoke all on table public.axoria_store from anon, authenticated;
grant select on table public.axoria_store to anon, authenticated;
grant insert, update, delete on table public.axoria_store to authenticated;

create policy "storefront_read_public"
on public.axoria_store
for select
to anon, authenticated
using (
  key in ('axoria_products', 'axoria_categories', 'axoria_reviews')
);

create policy "admin_manage_store"
on public.axoria_store
for all
to authenticated
using (true)
with check (true);

-- Remove obsolete client-side admin secrets if they already exist.
delete from public.axoria_store
where key in ('axoria_admin_pin', 'axoria_admin_recovery');

-- -----------------------------------------------------------------------------
-- 2) Orders
-- Visitors can create an order, but cannot read, list, update or delete orders.
-- Authenticated admin users can manage orders.
-- NOTE: server-side price validation is Phase 2; this migration protects privacy
-- and admin mutation rights, but the browser still supplies item prices/total.
-- -----------------------------------------------------------------------------

alter table if exists public.orders enable row level security;

drop policy if exists "public insert" on public.orders;
drop policy if exists "public read" on public.orders;
drop policy if exists "public update" on public.orders;
drop policy if exists "public delete" on public.orders;
drop policy if exists "storefront_create_order" on public.orders;
drop policy if exists "admin_read_orders" on public.orders;
drop policy if exists "admin_update_orders" on public.orders;
drop policy if exists "admin_delete_orders" on public.orders;

revoke all on table public.orders from anon, authenticated;
grant insert on table public.orders to anon;
grant select, insert, update, delete on table public.orders to authenticated;

create policy "storefront_create_order"
on public.orders
for insert
to anon
with check (
  status = 'New'
  and customer_name is not null
  and length(trim(customer_name)) between 2 and 120
  and phone is not null
  and length(trim(phone)) between 8 and 30
  and city is not null
  and length(trim(city)) between 2 and 120
  and address is not null
  and length(trim(address)) between 3 and 300
  and total is not null
  and total >= 0
);

create policy "admin_read_orders"
on public.orders
for select
to authenticated
using (true);

create policy "admin_insert_orders"
on public.orders
for insert
to authenticated
with check (true);

create policy "admin_update_orders"
on public.orders
for update
to authenticated
using (true)
with check (true);

create policy "admin_delete_orders"
on public.orders
for delete
to authenticated
using (true);

commit;

-- Verification queries (run after COMMIT):
-- select policyname, roles, cmd from pg_policies
-- where schemaname='public' and tablename in ('axoria_store','orders')
-- order by tablename, policyname;
