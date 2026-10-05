-- AXORIA — Security Phase 1
-- Run this in Supabase SQL Editor after the AXORIA admin Auth user exists.
-- This version is safe even if `axoria_store` was previously deleted.

begin;

-- -----------------------------------------------------------------------------
-- 1) Store/catalog table
-- Re-create the current AXORIA shared store only if it does not exist.
-- This is NOT the old site's data: it is a clean store for the current AXORIA site.
-- -----------------------------------------------------------------------------

create table if not exists public.axoria_store (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.axoria_store enable row level security;

-- Remove any broad legacy policies if they exist.
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

-- Seed only the current AXORIA storefront defaults when rows do not exist.
-- Existing rows are preserved.
insert into public.axoria_store (key, value)
values
(
  'axoria_categories',
  '[
    {"id":"c1","name":"Support & Récupération","img":4506106},
    {"id":"c2","name":"Ceinture Amincissante","img":5629203},
    {"id":"c3","name":"Fitness & Mobilité","img":4397831},
    {"id":"c4","name":"Massage & Détente","img":6207527},
    {"id":"c5","name":"Confort & Sommeil","img":6541176}
  ]'::jsonb
),
(
  'axoria_products',
  '[
    {
      "id":"1965",
      "cat":"Support & Récupération",
      "name":"Posture Corrector",
      "price":149,
      "oldPrice":null,
      "discount":0,
      "badge":"bestseller",
      "stock":50,
      "status":"active",
      "visible":true,
      "desc":"Redresse les épaules et soutient le dos pour une meilleure posture au quotidien, dès les premières minutes de port.",
      "longDesc":"Redresse les épaules et soutient le dos pour une meilleure posture au quotidien, dès les premières minutes de port. Fabriqué avec des matériaux résistants et respirants, ce produit AXORIA est conçu pour un usage quotidien prolongé, que ce soit au bureau, à la maison ou pendant le sport. Réglable et ajustable pour s''adapter à toutes les morphologies.",
      "img":"https://images.pexels.com/photos/4506106/pexels-photo-4506106.jpeg?auto=compress&cs=tinysrgb&w=900"
    },
    {
      "id":"1966",
      "cat":"Ceinture Amincissante",
      "name":"Slimming Waist Belt",
      "price":179,
      "oldPrice":null,
      "discount":0,
      "badge":"new",
      "stock":50,
      "status":"active",
      "visible":true,
      "desc":"Ceinture amincissante ajustable qui affine la taille, soutient le dos et accompagne vos séances de sport ou votre routine quotidienne.",
      "longDesc":"Ceinture amincissante ajustable qui affine la taille, soutient le dos et accompagne vos séances de sport ou votre routine quotidienne. Fabriqué avec des matériaux résistants et respirants, ce produit AXORIA est conçu pour un usage quotidien prolongé, que ce soit au bureau, à la maison ou pendant le sport. Réglable et ajustable pour s''adapter à toutes les morphologies.",
      "img":"https://images.pexels.com/photos/5629203/pexels-photo-5629203.jpeg?auto=compress&cs=tinysrgb&w=900"
    }
  ]'::jsonb
),
(
  'axoria_reviews',
  '[
    {"name":"Yassine B.","loc":"Casablanca, Maroc","rating":5,"comment":"Le correcteur de posture a changé ma façon de m''asseoir au bureau. Moins de douleurs au dos après une semaine."},
    {"name":"Sara M.","loc":"Rabat, Maroc","rating":5,"comment":"La ceinture amincissante est confortable et le service a été rapide."}
  ]'::jsonb
)
on conflict (key) do nothing;

-- Remove obsolete client-side admin secrets if they somehow exist.
delete from public.axoria_store
where key in ('axoria_admin_pin', 'axoria_admin_recovery');

-- -----------------------------------------------------------------------------
-- 2) Orders
-- Visitors can create an order, but cannot read/list/update/delete orders.
-- Authenticated admin users can manage orders.
-- -----------------------------------------------------------------------------

alter table if exists public.orders enable row level security;

drop policy if exists "public insert" on public.orders;
drop policy if exists "public read" on public.orders;
drop policy if exists "public update" on public.orders;
drop policy if exists "public delete" on public.orders;
drop policy if exists "storefront_create_order" on public.orders;
drop policy if exists "admin_read_orders" on public.orders;
drop policy if exists "admin_insert_orders" on public.orders;
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

-- Optional verification after COMMIT:
-- select key from public.axoria_store order by key;
-- select policyname, roles, cmd from pg_policies
-- where schemaname='public' and tablename in ('axoria_store','orders')
-- order by tablename, policyname;
