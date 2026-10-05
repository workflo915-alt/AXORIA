-- AXORIA Phase 2B — authoritative checkout + stock synchronization
-- This migration has also been applied to the connected Supabase project.

alter table public.orders add column if not exists order_code text;
alter table public.orders add column if not exists updated_at timestamptz;
alter table public.orders add column if not exists inventory_reserved boolean not null default false;
alter table public.orders add column if not exists source text not null default 'legacy';

update public.orders
set order_code = 'AX-' || to_char(coalesce(created_at, now()), 'YYMMDD') || '-' || upper(substr(replace(id::text, '-', ''), 1, 6))
where order_code is null;

update public.orders
set updated_at = coalesce(updated_at, created_at, now())
where updated_at is null;

alter table public.orders alter column order_code set not null;
alter table public.orders alter column updated_at set not null;
alter table public.orders alter column updated_at set default now();
create unique index if not exists orders_order_code_uidx on public.orders(order_code);

create or replace function public.place_order(
  p_customer_name text,
  p_phone text,
  p_city text,
  p_address text,
  p_notes text,
  p_items jsonb
)
returns table(order_id uuid, order_code text, order_total numeric)
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_products jsonb;
  v_item jsonb;
  v_product jsonb;
  v_product_id text;
  v_qty integer;
  v_stock integer;
  v_price numeric;
  v_total numeric := 0;
  v_clean_items jsonb := '[]'::jsonb;
  v_index integer;
  v_order_id uuid;
  v_code text;
begin
  if coalesce(auth.role(), '') not in ('anon', 'authenticated') then
    raise exception 'Unauthorized';
  end if;

  p_customer_name := trim(coalesce(p_customer_name, ''));
  p_phone := trim(coalesce(p_phone, ''));
  p_city := trim(coalesce(p_city, ''));
  p_address := trim(coalesce(p_address, ''));
  p_notes := nullif(trim(coalesce(p_notes, '')), '');

  if char_length(p_customer_name) not between 2 and 120 then raise exception 'Invalid customer name'; end if;
  if char_length(p_phone) not between 8 and 30 then raise exception 'Invalid phone'; end if;
  if char_length(p_city) not between 2 and 120 then raise exception 'Invalid city'; end if;
  if char_length(p_address) not between 3 and 300 then raise exception 'Invalid address'; end if;
  if p_notes is not null and char_length(p_notes) > 1000 then raise exception 'Notes too long'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) < 1 or jsonb_array_length(p_items) > 20 then
    raise exception 'Invalid cart';
  end if;

  select value into v_products
  from public.axoria_store
  where key = 'axoria_products'
  for update;

  if v_products is null or jsonb_typeof(v_products) <> 'array' then
    raise exception 'Catalog unavailable';
  end if;

  for v_item in select value from jsonb_array_elements(p_items)
  loop
    v_product_id := nullif(trim(v_item->>'product_id'), '');
    begin
      v_qty := (v_item->>'qty')::integer;
    exception when others then
      raise exception 'Invalid quantity';
    end;

    if v_product_id is null or v_qty < 1 or v_qty > 20 then
      raise exception 'Invalid cart item';
    end if;

    select x.elem, (x.ord - 1)::integer
      into v_product, v_index
    from jsonb_array_elements(v_products) with ordinality as x(elem, ord)
    where x.elem->>'id' = v_product_id
    limit 1;

    if not found then raise exception 'Product not found'; end if;
    if coalesce((v_product->>'visible')::boolean, false) is not true or coalesce(v_product->>'status','') <> 'active' then
      raise exception 'Product unavailable';
    end if;

    begin
      v_stock := coalesce((v_product->>'stock')::integer, 0);
      v_price := round(coalesce((v_product->>'price')::numeric, 0), 2);
    exception when others then
      raise exception 'Invalid catalog data';
    end;

    if v_price < 0 then raise exception 'Invalid product price'; end if;
    if v_stock < v_qty then raise exception 'Insufficient stock for %', coalesce(v_product->>'name', v_product_id); end if;

    v_total := v_total + (v_price * v_qty);
    v_clean_items := v_clean_items || jsonb_build_array(jsonb_build_object(
      'product_id', v_product_id,
      'name', coalesce(v_product->>'name', 'Produit'),
      'qty', v_qty,
      'price', v_price,
      'subtotal', v_price * v_qty
    ));

    v_products := jsonb_set(v_products, array[v_index::text, 'stock'], to_jsonb(v_stock - v_qty), true);
  end loop;

  update public.axoria_store
  set value = v_products, updated_at = now()
  where key = 'axoria_products';

  v_code := 'AX-' || to_char(now(), 'YYMMDD') || '-' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 6));

  insert into public.orders(customer_name, phone, city, address, items, total, notes, status, order_code, updated_at, inventory_reserved, source)
  values (p_customer_name, p_phone, p_city, p_address, v_clean_items, v_total, p_notes, 'New', v_code, now(), true, 'storefront')
  returning id into v_order_id;

  order_id := v_order_id;
  order_code := v_code;
  order_total := v_total;
  return next;
end;
$$;

create or replace function public.set_order_status(p_order_id uuid, p_status text)
returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_order public.orders%rowtype;
  v_products jsonb;
  v_item jsonb;
  v_product jsonb;
  v_product_id text;
  v_qty integer;
  v_stock integer;
  v_index integer;
  v_reserved boolean;
begin
  if coalesce(auth.role(), '') <> 'authenticated' then raise exception 'Unauthorized'; end if;
  if p_status not in ('New','Contacted','Confirmed','Shipped','Delivered','Cancelled') then raise exception 'Invalid status'; end if;

  select * into v_order from public.orders where id = p_order_id for update;
  if not found then raise exception 'Order not found'; end if;
  if v_order.status = p_status then return; end if;

  v_reserved := v_order.inventory_reserved;

  if p_status = 'Cancelled' and v_order.status <> 'Cancelled' and v_reserved then
    select value into v_products from public.axoria_store where key = 'axoria_products' for update;
    for v_item in select value from jsonb_array_elements(v_order.items)
    loop
      v_product_id := v_item->>'product_id';
      v_qty := coalesce((v_item->>'qty')::integer, 0);
      select x.elem, (x.ord - 1)::integer into v_product, v_index
      from jsonb_array_elements(v_products) with ordinality as x(elem, ord)
      where x.elem->>'id' = v_product_id limit 1;
      if found then
        v_stock := coalesce((v_product->>'stock')::integer, 0);
        v_products := jsonb_set(v_products, array[v_index::text, 'stock'], to_jsonb(v_stock + greatest(v_qty,0)), true);
      end if;
    end loop;
    update public.axoria_store set value=v_products, updated_at=now() where key='axoria_products';
    v_reserved := false;
  elsif v_order.status = 'Cancelled' and p_status <> 'Cancelled' and not v_reserved and v_order.source = 'storefront' then
    select value into v_products from public.axoria_store where key = 'axoria_products' for update;
    for v_item in select value from jsonb_array_elements(v_order.items)
    loop
      v_product_id := v_item->>'product_id';
      v_qty := coalesce((v_item->>'qty')::integer, 0);
      select x.elem, (x.ord - 1)::integer into v_product, v_index
      from jsonb_array_elements(v_products) with ordinality as x(elem, ord)
      where x.elem->>'id' = v_product_id limit 1;
      if not found then raise exception 'Product no longer exists'; end if;
      v_stock := coalesce((v_product->>'stock')::integer, 0);
      if v_stock < v_qty then raise exception 'Insufficient stock for %', coalesce(v_product->>'name', v_product_id); end if;
      v_products := jsonb_set(v_products, array[v_index::text, 'stock'], to_jsonb(v_stock - v_qty), true);
    end loop;
    update public.axoria_store set value=v_products, updated_at=now() where key='axoria_products';
    v_reserved := true;
  end if;

  update public.orders
  set status = p_status, inventory_reserved = v_reserved, updated_at = now()
  where id = p_order_id;
end;
$$;

revoke all on function public.place_order(text,text,text,text,text,jsonb) from public;
grant execute on function public.place_order(text,text,text,text,text,jsonb) to anon, authenticated;
revoke all on function public.set_order_status(uuid,text) from public;
grant execute on function public.set_order_status(uuid,text) to authenticated;
