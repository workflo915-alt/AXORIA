create table if not exists public.newsletter_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  locale text not null default 'fr' check (locale in ('fr','en','ar')),
  source text not null default 'storefront',
  created_at timestamptz not null default now(),
  constraint newsletter_email_length check (char_length(email) between 5 and 254),
  constraint newsletter_email_format check (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

create unique index if not exists newsletter_subscribers_email_lower_idx
  on public.newsletter_subscribers (lower(email));

alter table public.newsletter_subscribers enable row level security;

drop policy if exists storefront_insert_newsletter on public.newsletter_subscribers;
create policy storefront_insert_newsletter
on public.newsletter_subscribers
for insert
to anon, authenticated
with check (
  locale in ('fr','en','ar')
  and source = 'storefront'
  and char_length(email) between 5 and 254
);

grant insert on public.newsletter_subscribers to anon, authenticated;
revoke select, update, delete on public.newsletter_subscribers from anon, authenticated;
