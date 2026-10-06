-- AXORIA Phase 3 Reviews System

create table if not exists review_submissions (
  id uuid default gen_random_uuid() primary key,
  customer_name text not null,
  rating integer not null check (rating >= 1 and rating <= 5),
  comment text not null,
  product_id uuid,
  status text default 'pending',
  created_at timestamp with time zone default now()
);

-- Enable security
alter table review_submissions enable row level security;


-- Customers can send reviews
create policy "Allow public review submission"
on review_submissions
for insert
with check (true);


-- Website shows only approved reviews
create policy "Allow approved reviews reading"
on review_submissions
for select
using (status = 'approved');