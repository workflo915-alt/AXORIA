create or replace function public.delete_review(p_review_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_reviews jsonb := '[]'::jsonb;
  v_exists boolean := false;
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  select exists(
    select 1 from public.review_submissions where id = p_review_id
  ) into v_exists;

  if not v_exists then
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

  insert into public.axoria_store(key, value, updated_at)
  values ('axoria_reviews', v_reviews, now())
  on conflict (key) do update
    set value = excluded.value,
        updated_at = excluded.updated_at;

  delete from public.review_submissions where id = p_review_id;

  return jsonb_build_object('id', p_review_id, 'deleted', true);
end;
$$;

revoke all on function public.delete_review(uuid) from public;
revoke all on function public.delete_review(uuid) from anon;
grant execute on function public.delete_review(uuid) to authenticated;
