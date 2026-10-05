insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'product-images',
  'product-images',
  true,
  5242880,
  array['image/jpeg','image/png','image/webp']
)
on conflict (id) do update
set public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "admin_select_product_images" on storage.objects;
drop policy if exists "admin_insert_product_images" on storage.objects;
drop policy if exists "admin_update_product_images" on storage.objects;
drop policy if exists "admin_delete_product_images" on storage.objects;

create policy "admin_select_product_images"
on storage.objects
for select
to authenticated
using (bucket_id = 'product-images');

create policy "admin_insert_product_images"
on storage.objects
for insert
to authenticated
with check (bucket_id = 'product-images');

create policy "admin_update_product_images"
on storage.objects
for update
to authenticated
using (bucket_id = 'product-images')
with check (bucket_id = 'product-images');

create policy "admin_delete_product_images"
on storage.objects
for delete
to authenticated
using (bucket_id = 'product-images');
