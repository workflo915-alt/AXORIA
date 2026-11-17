-- Product reviews: each customer review names the product it is about (product_id),
-- so the site can show stars per product and Google can show them in search results.
-- Run once in the Supabase SQL Editor (production). Safe to run again.

alter table public.review_submissions
  add column if not exists product_id text;

-- Product ids are short ("1965"): refuse anything long sent from the public form.
do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'review_submissions_product_id_len'
      and conrelid = 'public.review_submissions'::regclass
  ) then
    alter table public.review_submissions
      add constraint review_submissions_product_id_len
      check (product_id is null or char_length(product_id) <= 40);
  end if;
end $$;

create index if not exists review_submissions_product_status_idx
  on public.review_submissions(product_id, status, created_at desc);

-- The storefront sends product_id with new reviews and reads it back with approved ones.
-- Harmless when the roles already have rights on the whole table.
grant select (product_id), insert (product_id) on public.review_submissions to anon, authenticated;
