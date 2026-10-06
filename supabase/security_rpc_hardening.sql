revoke all on function public.set_order_status(uuid,text) from public;
revoke all on function public.set_order_status(uuid,text) from anon;
grant execute on function public.set_order_status(uuid,text) to authenticated;

revoke all on function public.rls_auto_enable() from public;
revoke all on function public.rls_auto_enable() from anon;
revoke all on function public.rls_auto_enable() from authenticated;
