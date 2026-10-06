alter table public.review_submissions
  add column if not exists moderated_at timestamptz,
  add column if not exists moderated_by uuid;

create index if not exists review_submissions_status_created_idx
  on public.review_submissions(status, created_at desc);

create or replace function public.moderate_review(p_review_id uuid, p_action text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_review public.review_submissions%rowtype;
  v_reviews jsonb := '[]'::jsonb;
  v_action text := lower(trim(coalesce(p_action,'')));
  v_published jsonb;
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  if v_action not in ('approve','reject') then
    raise exception 'Invalid moderation action';
  end if;

  select * into v_review
  from public.review_submissions
  where id = p_review_id
  for update;

  if not found then
    raise exception 'Review not found';
  end if;

  select coalesce(value, '[]'::jsonb)
    into v_reviews
  from public.axoria_store
  where key = 'axoria_reviews'
  for update;

  if v_reviews is null or jsonb_typeof(v_reviews) <> 'array' then
    v_reviews := '[]'::jsonb;
  end if;

  select coalesce(jsonb_agg(item), '[]'::jsonb)
    into v_reviews
  from jsonb_array_elements(v_reviews) as item
  where coalesce(item->>'submission_id','') <> p_review_id::text;

  if v_action = 'approve' then
    v_published := jsonb_build_object(
      'submission_id', p_review_id::text,
      'name', v_review.name,
      'loc', 'Maroc',
      'rating', v_review.rating,
      'comment', v_review.comment,
      'created_at', v_review.created_at
    );
    v_reviews := v_reviews || jsonb_build_array(v_published);

    insert into public.axoria_store(key, value, updated_at)
    values ('axoria_reviews', v_reviews, now())
    on conflict (key) do update
      set value = excluded.value,
          updated_at = excluded.updated_at;

    update public.review_submissions
      set status = 'approved', moderated_at = now(), moderated_by = auth.uid()
    where id = p_review_id;
  else
    insert into public.axoria_store(key, value, updated_at)
    values ('axoria_reviews', v_reviews, now())
    on conflict (key) do update
      set value = excluded.value,
          updated_at = excluded.updated_at;

    update public.review_submissions
      set status = 'rejected', moderated_at = now(), moderated_by = auth.uid()
    where id = p_review_id;
  end if;

  return jsonb_build_object(
    'id', p_review_id,
    'status', case when v_action='approve' then 'approved' else 'rejected' end
  );
end;
$$;

revoke all on function public.moderate_review(uuid,text) from public;
revoke all on function public.moderate_review(uuid,text) from anon;
grant execute on function public.moderate_review(uuid,text) to authenticated;
