from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)

# Meta Purchase deduplication: browser Pixel event + one DB-triggered CAPI server event.
replace_once(
"function trackCommerceEvent(eventName,customData={},userData={}){\n  if(!META_TRACKING.enabled||!validMetaPixelId(META_TRACKING.pixelId))return null;\n  const eventID=metaEventId(eventName.toLowerCase());",
"function trackCommerceEvent(eventName,customData={},userData={},options={}){\n  if(!META_TRACKING.enabled||!validMetaPixelId(META_TRACKING.pixelId))return null;\n  const eventID=String(options?.eventID||'').trim() || metaEventId(eventName.toLowerCase());",
'Meta tracking signature'
)
replace_once(
"  if(META_TRACKING.capiEnabled&&sb){\n    const body={pixel_id:META_TRACKING.pixelId,event_name:eventName,event_id:eventID,event_time:Math.floor(Date.now()/1000),event_source_url:location.href,user_data:{...userData,fbp:getCookieValue('_fbp'),fbc:getCookieValue('_fbc')},custom_data:customData};",
"  if(!options?.browserOnly && META_TRACKING.capiEnabled&&sb){\n    const body={pixel_id:META_TRACKING.pixelId,event_name:eventName,event_id:eventID,event_time:Math.floor(Date.now()/1000),event_source_url:location.href,user_data:{...userData,fbp:getCookieValue('_fbp'),fbc:getCookieValue('_fbc')},custom_data:customData};",
'Meta CAPI guard'
)
old_purchase = "    trackCommerceEvent('Purchase',{value:purchaseValue,currency:'MAD',content_type:'product',content_ids:CART.map(c=>String(c.id)),contents:CART.map(c=>({id:String(c.id),quantity:Number(c.qty||0),item_price:Number(c.price||0)})),order_id:String(placed?.order_code||placed?.order_id||'')},{ph:phone,fn:name,ct:city,country:'ma',external_id:String(placed?.order_code||placed?.order_id||'')});"
new_purchase = "    const orderUuid=String(placed?.order_id||'').trim();\n    const purchaseEventID=orderUuid ? `purchase-${orderUuid}` : metaEventId('purchase');\n    trackCommerceEvent('Purchase',{value:purchaseValue,currency:'MAD',content_type:'product',content_ids:CART.map(c=>String(c.id)),contents:CART.map(c=>({id:String(c.id),quantity:Number(c.qty||0),item_price:Number(c.price||0)})),order_id:String(placed?.order_code||placed?.order_id||'')},{ph:phone,fn:name,ct:city,country:'ma',external_id:orderUuid||String(placed?.order_code||'')},{eventID:purchaseEventID,browserOnly:true});"
replace_once(old_purchase, new_purchase, 'Purchase event')

# Missing local asset guards. Preserve local images when present, avoid broken production UI.
replace_once(
'<img src="asest/batal1.png" alt="AXORIA — bien-être et posture" loading="lazy">',
'<img src="asest/batal1.png" alt="AXORIA — bien-être et confort" loading="lazy" onerror="this.onerror=null;this.src=\'https://images.pexels.com/photos/7222429/pexels-photo-7222429.jpeg?auto=compress&amp;cs=tinysrgb&amp;w=1000\';">',
'About asset fallback'
)
replace_once(
'<img src="asest/b12.png" alt="Avant — mauvaise posture" loading="lazy">',
'<img src="asest/b12.png" alt="Avant" loading="lazy" onerror="const section=document.getElementById(\'beforeafter\');if(section)section.hidden=true;">',
'Before asset guard'
)
replace_once(
'<img src="asest/b21.png" alt="Après — posture corrigée" loading="lazy">',
'<img src="asest/b21.png" alt="Après" loading="lazy" onerror="const section=document.getElementById(\'beforeafter\');if(section)section.hidden=true;">',
'After asset guard'
)

p.write_text(s, encoding='utf-8')
print('Applied sales readiness core fixes')
