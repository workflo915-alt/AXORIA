-- AXORIA Phase 4/5 tracking production state
-- Keeps the public storefront tracking config readable and sends one server-side
-- Purchase event after each successful order insert. The browser uses the same
-- deterministic event_id (purchase-<order uuid>) so Meta can deduplicate.

DROP POLICY IF EXISTS storefront_read_tracking ON public.axoria_store;
CREATE POLICY storefront_read_tracking
ON public.axoria_store
FOR SELECT
TO anon, authenticated
USING (key = 'axoria_tracking');

CREATE OR REPLACE FUNCTION public.axoria_meta_purchase_on_order_insert()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public', 'net', 'pg_temp'
AS $function$
DECLARE
  v_content_ids jsonb := '[]'::jsonb;
  v_num_items integer := 0;
  v_payload jsonb;
BEGIN
  SELECT
    coalesce(jsonb_agg(item->>'product_id'), '[]'::jsonb),
    coalesce(sum((item->>'qty')::integer), 0)
  INTO v_content_ids, v_num_items
  FROM jsonb_array_elements(coalesce(new.items, '[]'::jsonb)) AS item;

  v_payload := jsonb_build_object(
    'event_name', 'Purchase',
    'event_time', extract(epoch from coalesce(new.created_at, now()))::bigint,
    'event_id', 'purchase-' || new.id::text,
    'event_source_url', 'https://axoria.ma',
    'user_data', jsonb_build_object(
      'ph', coalesce(new.phone, ''),
      'fn', coalesce(new.customer_name, ''),
      'ct', coalesce(new.city, ''),
      'country', 'ma',
      'external_id', new.id::text
    ),
    'custom_data', jsonb_build_object(
      'currency', 'MAD',
      'value', new.total,
      'content_ids', v_content_ids,
      'content_type', 'product',
      'num_items', v_num_items,
      'order_id', new.order_code
    )
  );

  PERFORM net.http_post(
    url := 'https://gdemgpkkrmpridqgjmtx.supabase.co/functions/v1/meta-capi',
    body := v_payload,
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'apikey', 'sb_publishable_LcXsTIdML2gITtM8UDqtWw_toCYU4qD'
    ),
    timeout_milliseconds := 5000
  );

  RETURN new;
EXCEPTION
  WHEN others THEN
    RAISE WARNING 'AXORIA Meta Purchase tracking failed for order %: %', new.id, sqlerrm;
    RETURN new;
END;
$function$;

DROP TRIGGER IF EXISTS trg_axoria_meta_purchase ON public.orders;
CREATE TRIGGER trg_axoria_meta_purchase
AFTER INSERT ON public.orders
FOR EACH ROW
EXECUTE FUNCTION public.axoria_meta_purchase_on_order_insert();
