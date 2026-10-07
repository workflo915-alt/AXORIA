-- Applied to Supabase production on 2026-10-07.
-- review_submissions is the canonical source for storefront reviews.

create or replace function public.moderate_review(p_review_id uuid, p_action text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_action text := lower(trim(coalesce(p_action,'')));
  v_status text;
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  if v_action not in ('approve','reject') then
    raise exception 'Invalid moderation action';
  end if;

  v_status := case when v_action = 'approve' then 'approved' else 'rejected' end;

  update public.review_submissions
  set status = v_status,
      moderated_at = now(),
      moderated_by = auth.uid()
  where id = p_review_id;

  if not found then
    raise exception 'Review not found';
  end if;

  return jsonb_build_object('id', p_review_id, 'status', v_status);
end;
$$;

revoke all on function public.moderate_review(uuid,text) from public;
revoke all on function public.moderate_review(uuid,text) from anon;
grant execute on function public.moderate_review(uuid,text) to authenticated;

create or replace function public.delete_review(p_review_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  delete from public.review_submissions
  where id = p_review_id;

  if not found then
    raise exception 'Review not found';
  end if;

  return jsonb_build_object('id', p_review_id, 'deleted', true);
end;
$$;

revoke all on function public.delete_review(uuid) from public;
revoke all on function public.delete_review(uuid) from anon;
grant execute on function public.delete_review(uuid) to authenticated;
