from pathlib import Path


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'{label} marker not found')
    return text.replace(old, new, 1)

admin_path = Path('admin.html')
admin = admin_path.read_text(encoding='utf-8')

admin = replace_once(admin,
'''      <button class="btn tab ghost" data-tab="reviews">Avis</button>\n      <button class="btn tab ghost" data-tab="categories">Catégories</button>''',
'''      <button class="btn tab ghost" data-tab="reviews">Avis</button>\n      <button class="btn tab ghost" data-tab="tracking">Tracking</button>\n      <button class="btn tab ghost" data-tab="categories">Catégories</button>''',
'admin tracking tab')

tracking_panel = '''
    <section id="trackingPanel" class="card panel hidden">
      <div class="bar">
        <div><h2>Meta Pixel & Conversions API</h2><div class="sub">Le Pixel ID peut être public. Le token CAPI reste secret côté Supabase.</div></div>
        <div class="actions"><button id="saveTracking" class="btn primary">Enregistrer</button></div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;max-width:820px">
        <div class="card" style="padding:14px">
          <label style="display:flex;gap:10px;align-items:center;font-weight:700"><input id="trackingEnabled" type="checkbox" style="width:auto"> Activer Meta Pixel</label>
          <div class="field"><label>Pixel ID</label><input id="trackingPixelId" inputmode="numeric" placeholder="Ex: 123456789012345"></div>
        </div>
        <div class="card" style="padding:14px">
          <label style="display:flex;gap:10px;align-items:center;font-weight:700"><input id="trackingCapiEnabled" type="checkbox" style="width:auto"> Activer Conversions API</label>
          <p class="sub" style="line-height:1.55">À activer seulement après configuration du secret Meta dans Supabase. Le token ne doit jamais être enregistré dans le navigateur.</p>
        </div>
      </div>
      <div id="trackingStatus" class="notice" style="margin-top:14px;margin-bottom:0"></div>
    </section>
'''
if 'id="trackingPanel"' not in admin:
    marker = '    <section id="categoriesPanel" class="card panel hidden">'
    if marker not in admin: raise SystemExit('admin categories panel marker not found')
    admin = admin.replace(marker, tracking_panel + '\n' + marker, 1)

admin = replace_once(admin,
'let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];let REVIEW_SUBMISSIONS=[];',
"let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];let REVIEW_SUBMISSIONS=[];let TRACKING_CONFIG={enabled:false,pixelId:'',capiEnabled:false};",
'admin state')

admin = replace_once(admin,
"await loadProducts();await loadOrders();await loadReviewSubmissions();return true;}",
"await loadProducts();await loadOrders();await loadReviewSubmissions();await loadTrackingConfig();return true;}",
'admin session loader')

admin = replace_once(admin,
"['products','orders','reviews','categories'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='reviews')loadReviewSubmissions();if(b.dataset.tab==='categories')renderCategories();",
"['products','orders','reviews','tracking','categories'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='reviews')loadReviewSubmissions();if(b.dataset.tab==='tracking')loadTrackingConfig();if(b.dataset.tab==='categories')renderCategories();",
'admin tabs handler')

tracking_admin_js = r'''
async function loadTrackingConfig(){
  try{
    const raw=await getStore('axoria_tracking');
    TRACKING_CONFIG={enabled:!!raw?.enabled,pixelId:String(raw?.pixelId||'').trim(),capiEnabled:!!raw?.capiEnabled};
    if($('trackingEnabled'))$('trackingEnabled').checked=TRACKING_CONFIG.enabled;
    if($('trackingPixelId'))$('trackingPixelId').value=TRACKING_CONFIG.pixelId;
    if($('trackingCapiEnabled'))$('trackingCapiEnabled').checked=TRACKING_CONFIG.capiEnabled;
    if($('trackingStatus')){
      const pixelReady=/^\d{5,30}$/.test(TRACKING_CONFIG.pixelId);
      $('trackingStatus').textContent=TRACKING_CONFIG.enabled
        ? (pixelReady?'Meta Pixel prêt côté site.':'Tracking activé mais Pixel ID invalide ou manquant.')
        : 'Tracking Meta désactivé. Aucun événement Meta ne sera envoyé.';
    }
  }catch(e){console.error(e);if($('trackingStatus'))$('trackingStatus').textContent='Impossible de charger la configuration tracking.';}
}
async function saveTrackingConfig(){
  const pixelId=String($('trackingPixelId')?.value||'').trim();
  const enabled=!!$('trackingEnabled')?.checked;
  const capiEnabled=!!$('trackingCapiEnabled')?.checked;
  if(enabled && !/^\d{5,30}$/.test(pixelId)){toast('Pixel ID invalide');return;}
  TRACKING_CONFIG={enabled,pixelId,capiEnabled};
  try{await setStore('axoria_tracking',TRACKING_CONFIG);await loadTrackingConfig();toast('Configuration tracking enregistrée');}
  catch(e){console.error(e);toast('Échec sauvegarde tracking');}
}
if($('saveTracking'))$('saveTracking').onclick=saveTrackingConfig;
'''
if 'async function loadTrackingConfig()' not in admin:
    marker = "$('reviewStatusFilter').addEventListener('change',renderReviewSubmissions);\n\nrequireSession();"
    if marker not in admin: raise SystemExit('admin tracking js insertion marker not found')
    admin = admin.replace(marker, "$('reviewStatusFilter').addEventListener('change',renderReviewSubmissions);\n" + tracking_admin_js + "\nrequireSession();", 1)

admin_path.write_text(admin, encoding='utf-8')

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

tracking_js = r'''

/* ---------- Phase 4: Meta Pixel + CAPI instrumentation ---------- */
let META_TRACKING={enabled:false,pixelId:'',capiEnabled:false};
let META_PIXEL_INITIALIZED=false;
let META_PAGEVIEW_SENT=false;
function validMetaPixelId(v){return /^\d{5,30}$/.test(String(v||'').trim());}
function metaEventId(prefix='ax'){return `${prefix}-${Date.now()}-${(crypto.randomUUID?crypto.randomUUID():Math.random().toString(36).slice(2))}`;}
function getCookieValue(name){const prefix=name+'=';return document.cookie.split(';').map(v=>v.trim()).find(v=>v.startsWith(prefix))?.slice(prefix.length)||'';}
function ensureMetaPixel(){
  if(!META_TRACKING.enabled||!validMetaPixelId(META_TRACKING.pixelId))return false;
  if(!window.fbq){
    const n=window.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!window._fbq)window._fbq=n;
    n.push=n;n.loaded=true;n.version='2.0';n.queue=[];
    const s=document.createElement('script');s.async=true;s.src='https://connect.facebook.net/en_US/fbevents.js';
    const first=document.getElementsByTagName('script')[0];first.parentNode.insertBefore(s,first);
  }
  if(!META_PIXEL_INITIALIZED){window.fbq('init',META_TRACKING.pixelId);META_PIXEL_INITIALIZED=true;}
  return true;
}
async function loadTrackingConfig(){
  try{
    const raw=await storeGet('axoria_tracking',true);
    META_TRACKING={enabled:!!raw?.enabled,pixelId:String(raw?.pixelId||'').trim(),capiEnabled:!!raw?.capiEnabled};
    if(ensureMetaPixel()&&!META_PAGEVIEW_SENT){META_PAGEVIEW_SENT=true;trackCommerceEvent('PageView');}
  }catch(e){console.warn('Meta tracking config unavailable',e);}
}
function trackCommerceEvent(eventName,customData={},userData={}){
  if(!META_TRACKING.enabled||!validMetaPixelId(META_TRACKING.pixelId))return null;
  const eventID=metaEventId(eventName.toLowerCase());
  try{if(ensureMetaPixel()&&window.fbq)window.fbq('track',eventName,customData,{eventID});}catch(e){console.warn('Meta Pixel event failed',e);}
  if(META_TRACKING.capiEnabled&&sb){
    const body={pixel_id:META_TRACKING.pixelId,event_name:eventName,event_id:eventID,event_time:Math.floor(Date.now()/1000),event_source_url:location.href,user_data:{...userData,fbp:getCookieValue('_fbp'),fbc:getCookieValue('_fbc')},custom_data:customData};
    sb.functions.invoke('meta-capi',{body}).then(({error})=>{if(error)console.warn('Meta CAPI event failed',error);}).catch(e=>console.warn('Meta CAPI unavailable',e));
  }
  return eventID;
}
'''
if 'Phase 4: Meta Pixel + CAPI instrumentation' not in index:
    marker = "const sb = (SUPABASE_URL.startsWith('http') && window.supabase)\n  ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)\n  : null;"
    if marker not in index: raise SystemExit('storefront supabase client marker not found')
    index = index.replace(marker, marker + tracking_js, 1)

index = replace_once(index,
"  document.getElementById('productModal').classList.add('open');\n  document.body.classList.add('no-scroll');",
"  trackCommerceEvent('ViewContent',{content_ids:[String(p.id)],content_type:'product',content_name:p.name,value:Number(p.price||0),currency:'MAD'});\n  document.getElementById('productModal').classList.add('open');\n  document.body.classList.add('no-scroll');",
'view content event')

index = replace_once(index,
"  else CART.push({key:id, id, name:p.name, price:p.price, img:p.img, qty});\n  persistCart();",
"  else CART.push({key:id, id, name:p.name, price:p.price, img:p.img, qty});\n  trackCommerceEvent('AddToCart',{content_ids:[String(p.id)],content_type:'product',content_name:p.name,value:Number(p.price||0)*Number(qty||1),currency:'MAD',contents:[{id:String(p.id),quantity:Number(qty||1),item_price:Number(p.price||0)}]});\n  persistCart();",
'add to cart event')

index = replace_once(index,
"  document.getElementById('orderFormError').textContent = '';\n  renderOrderSummary();\n  document.getElementById('orderFormOverlay').classList.add('open');",
"  document.getElementById('orderFormError').textContent = '';\n  renderOrderSummary();\n  const checkoutTotal=CART.reduce((s,c)=>s+Number(c.price||0)*Number(c.qty||0),0);\n  trackCommerceEvent('InitiateCheckout',{value:checkoutTotal,currency:'MAD',num_items:CART.reduce((s,c)=>s+Number(c.qty||0),0),content_ids:CART.map(c=>String(c.id)),contents:CART.map(c=>({id:String(c.id),quantity:Number(c.qty||0),item_price:Number(c.price||0)}))});\n  document.getElementById('orderFormOverlay').classList.add('open');",
'checkout event')

index = replace_once(index,
"    if(error) throw error;\n    const placed = Array.isArray(data) ? data[0] : data;\n\n    // Stock changed server-side: refresh the visible catalog immediately.",
"    if(error) throw error;\n    const placed = Array.isArray(data) ? data[0] : data;\n    const purchaseValue=Number(placed?.order_total||CART.reduce((s,c)=>s+Number(c.price||0)*Number(c.qty||0),0));\n    trackCommerceEvent('Purchase',{value:purchaseValue,currency:'MAD',content_type:'product',content_ids:CART.map(c=>String(c.id)),contents:CART.map(c=>({id:String(c.id),quantity:Number(c.qty||0),item_price:Number(c.price||0)})),order_id:String(placed?.order_code||placed?.order_id||'')},{ph:phone,fn:name,ct:city,country:'ma',external_id:String(placed?.order_code||placed?.order_id||'')});\n\n    // Stock changed server-side: refresh the visible catalog immediately.",
'purchase event')

index = replace_once(index,
"async function init(){\n  document.getElementById('loaderLogo').innerHTML = badgeLogoSVG(120);\n  spawnHeroParticles();",
"async function init(){\n  document.getElementById('loaderLogo').innerHTML = badgeLogoSVG(120);\n  spawnHeroParticles();\n  await loadTrackingConfig();",
'tracking init')

required=["trackCommerceEvent('PageView')","trackCommerceEvent('ViewContent'","trackCommerceEvent('AddToCart'","trackCommerceEvent('InitiateCheckout'","trackCommerceEvent('Purchase'"]
for marker in required:
    if marker not in index: raise SystemExit(f'missing storefront tracking marker: {marker}')
index_path.write_text(index, encoding='utf-8')
print('Phase 4 Meta tracking patch applied to admin.html and index.html')
