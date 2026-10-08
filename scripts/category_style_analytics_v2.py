from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
ADMIN=ROOT/'admin.html'

def rep(text,old,new,label):
    if old in text:
        return text.replace(old,new,1)
    if new in text:
        print('[skip]',label); return text
    raise RuntimeError('anchor not found: '+label)

index=INDEX.read_text(encoding='utf-8')
admin=ADMIN.read_text(encoding='utf-8')

old_css=""".cat-filters{display:flex;gap:10px;overflow-x:auto;padding-bottom:14px;margin-bottom:44px;scrollbar-width:thin;}
.cat-filters::-webkit-scrollbar{height:5px;}
.cat-filters::-webkit-scrollbar-thumb{background:var(--line);border-radius:10px;}
.cat-chip{flex:0 0 auto;font-family:var(--font-mono);font-size:13px;font-weight:600;letter-spacing:.02em;padding:11px 20px;border-radius:999px;border:1.5px solid var(--line);background:var(--surface);color:var(--text-soft);transition:all .25s ease;white-space:nowrap;}
.cat-chip:hover{border-color:var(--teal-deep);color:var(--text);}
.cat-chip.active{background:var(--charcoal);color:var(--teal);border-color:var(--charcoal);}"""
new_css=""".cat-filters{display:flex;gap:12px;overflow-x:auto;padding:4px 2px 16px;margin-bottom:44px;scrollbar-width:thin;scroll-snap-type:x proximity;}
.cat-filters::-webkit-scrollbar{height:5px;}
.cat-filters::-webkit-scrollbar-thumb{background:var(--line);border-radius:10px;}
.cat-chip{flex:0 0 auto;scroll-snap-align:start;font-family:var(--font-mono);font-size:13px;font-weight:700;letter-spacing:.02em;padding:12px 22px;border-radius:999px;border:1px solid #D4DCE8;background:linear-gradient(180deg,#FFFFFF 0%,#F5F7FA 100%);color:#34445B;box-shadow:0 7px 18px rgba(10,36,60,.06),inset 0 1px 0 rgba(255,255,255,.9);transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease,background .22s ease,color .22s ease;white-space:nowrap;}
.cat-chip:hover{transform:translateY(-2px);border-color:#9BAEC6;color:#0B1524;box-shadow:0 10px 24px rgba(10,36,60,.10);}
.cat-chip.active{background:linear-gradient(135deg,#0B1524 0%,#162A45 100%);color:#FFFFFF;border-color:#0B1524;box-shadow:0 10px 24px rgba(11,21,36,.18),inset 0 1px 0 rgba(255,255,255,.08);}
[data-theme=\"dark\"] .cat-chip{background:linear-gradient(180deg,rgba(255,255,255,.065) 0%,rgba(255,255,255,.025) 100%);color:#C7D3E4;border-color:rgba(255,255,255,.12);box-shadow:0 8px 20px rgba(0,0,0,.18),inset 0 1px 0 rgba(255,255,255,.04);}
[data-theme=\"dark\"] .cat-chip:hover{color:#FFFFFF;border-color:rgba(255,255,255,.25);background:rgba(255,255,255,.08);}
[data-theme=\"dark\"] .cat-chip.active{background:linear-gradient(135deg,#FFFFFF 0%,#DCE6F2 100%);color:#0B1524;border-color:#FFFFFF;box-shadow:0 10px 28px rgba(0,0,0,.30);}"""
index=rep(index,old_css,new_css,'premium category pills')

old_render="""function renderCatFilters(){
  const t = I18N[currentLang];"""
new_render="""const CATEGORY_SESSION_KEY='axoria_category_analytics_session';
function categoryAnalyticsSessionId(){
  let id='';
  try{id=localStorage.getItem(CATEGORY_SESSION_KEY)||'';}catch(_){ }
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)){
    if(globalThis.crypto?.randomUUID)id=globalThis.crypto.randomUUID();
    else id='xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0,v=c==='x'?r:(r&3|8);return v.toString(16);});
    try{localStorage.setItem(CATEGORY_SESSION_KEY,id);}catch(_){ }
  }
  return id;
}
async function trackCategoryInterest(catName){
  if(!sb||!catName||catName==='all')return;
  const cat=CATEGORIES.find(c=>c.name===catName);
  if(!cat)return;
  try{const {error}=await sb.from('category_views').insert({category_id:String(cat.id),category:String(cat.name),session_id:categoryAnalyticsSessionId()});if(error)throw error;}
  catch(e){console.warn('Category analytics unavailable',e);}
}

function renderCatFilters(){
  const t = I18N[currentLang];"""
index=rep(index,old_render,new_render,'storefront analytics helper')
index=rep(index,"    b.onclick = ()=>{ currentCategory = b.dataset.cat; renderCatFilters(); renderMenuGrid(); };","    b.onclick = ()=>{ currentCategory = b.dataset.cat; if(currentCategory!=='all')void trackCategoryInterest(currentCategory); renderCatFilters(); renderMenuGrid(); };",'storefront category click')

style_anchor=".review-stars{color:#C9A227;letter-spacing:1px;font-size:14px;white-space:nowrap}"
style_extra=style_anchor+"\n"+""".cat-admin-row{padding:12px 13px;margin:9px 0;display:grid;grid-template-columns:minmax(220px,1fr) auto auto;gap:12px;align-items:center}.cat-metrics{display:flex;gap:7px;flex-wrap:wrap}.cat-metric{min-width:82px;padding:8px 10px;border-radius:12px;background:#F6F8FC;border:1px solid var(--line);text-align:center}.cat-metric strong{display:block;font-family:'JetBrains Mono',monospace;font-size:15px;color:var(--ink)}.cat-metric span{display:block;margin-top:2px;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700}.cat-metric.recent{background:#EEF5FF;border-color:#D4E3F8}.cat-analytics-note{padding:10px 12px;border-radius:12px;background:#F8FAFD;border:1px solid var(--line);font-size:11.5px;color:var(--muted);line-height:1.5;margin-bottom:12px}@media(max-width:760px){.cat-admin-row{grid-template-columns:1fr}.cat-admin-row .btn.danger{justify-self:start}.cat-metrics{order:2}}"""
admin=rep(admin,style_anchor,style_extra,'admin analytics styles')

old_section="""    <section id=\"categoriesPanel\" class=\"card panel hidden\">
      <div class=\"bar\"><h2>Catégories</h2><div class=\"actions\"><input id=\"newCategory\" placeholder=\"Nouvelle catégorie\"><button id=\"addCategory\" class=\"btn primary\">Ajouter</button></div></div>
      <div id=\"categoriesList\"></div>
    </section>"""
new_section="""    <section id=\"categoriesPanel\" class=\"card panel hidden\">
      <div class=\"bar\">
        <div><h2>Catégories & intérêt</h2><div class=\"sub\">Comprenez les catégories qui attirent le plus les visiteurs.</div></div>
        <div class=\"actions\"><input id=\"newCategory\" placeholder=\"Nouvelle catégorie\"><button id=\"addCategory\" class=\"btn primary\">Ajouter</button><button id=\"reloadCategoryAnalytics\" class=\"btn ghost\">Actualiser stats</button></div>
      </div>
      <div class=\"cat-analytics-note\">Données anonymes : <strong>Visiteurs</strong> = sessions uniques ayant ouvert la catégorie · <strong>Clics</strong> = nombre total d'ouvertures · <strong>7 jours</strong> = visiteurs uniques récents. Les statistiques commencent à partir de l'activation de ce suivi.</div>
      <div id=\"categoriesList\"></div>
    </section>"""
admin=rep(admin,old_section,new_section,'admin category panel')
admin=rep(admin,"let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];let REVIEW_SUBMISSIONS=[];let TRACKING_CONFIG={enabled:false,pixelId:'',capiEnabled:false};","let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];let REVIEW_SUBMISSIONS=[];let TRACKING_CONFIG={enabled:false,pixelId:'',capiEnabled:false};let CATEGORY_STATS={};",'admin stats state')
admin=rep(admin,"if(b.dataset.tab==='tracking')loadTrackingConfig();if(b.dataset.tab==='categories')renderCategories();","if(b.dataset.tab==='tracking')loadTrackingConfig();if(b.dataset.tab==='categories')loadCategoryAnalytics();",'admin category tab')
old_cat="""function renderCategories(){const host=$('categoriesList');if(!CATEGORIES.length){host.innerHTML='<p class=\"muted\">Aucune catégorie.</p>';return;}host.innerHTML=CATEGORIES.map(c=>`<div class=\"card\" style=\"padding:10px 12px;margin:8px 0;display:flex;gap:8px;align-items:center\"><input data-catname=\"${esc(c.id)}\" value=\"${esc(c.name)}\" style=\"flex:1\"><button class=\"btn danger\" data-catdel=\"${esc(c.id)}\">Supprimer</button></div>`).join('');host.querySelectorAll('[data-catname]').forEach(i=>i.onchange=()=>renameCategory(i.dataset.catname,i.value));host.querySelectorAll('[data-catdel]').forEach(b=>b.onclick=()=>deleteCategory(b.dataset.catdel));}"""
new_cat="""async function loadCategoryAnalytics(){try{const {data,error}=await sb.from('category_interest_stats').select('category_id,clicks_total,visitors_unique,clicks_7d,visitors_7d,last_view_at');if(error)throw error;CATEGORY_STATS={};(Array.isArray(data)?data:[]).forEach(r=>{CATEGORY_STATS[String(r.category_id)]={clicks_total:Number(r.clicks_total||0),visitors_unique:Number(r.visitors_unique||0),clicks_7d:Number(r.clicks_7d||0),visitors_7d:Number(r.visitors_7d||0),last_view_at:r.last_view_at};});renderCategories();}catch(e){console.error(e);toast('Impossible de charger les statistiques catégories');renderCategories();}}
function renderCategories(){const host=$('categoriesList');if(!CATEGORIES.length){host.innerHTML='<p class=\"muted\">Aucune catégorie.</p>';return;}host.innerHTML=CATEGORIES.map(c=>{const s=CATEGORY_STATS[String(c.id)]||{clicks_total:0,visitors_unique:0,visitors_7d:0};return `<div class=\"card cat-admin-row\"><input data-catname=\"${esc(c.id)}\" value=\"${esc(c.name)}\"><div class=\"cat-metrics\"><div class=\"cat-metric\"><strong>${s.visitors_unique}</strong><span>Visiteurs</span></div><div class=\"cat-metric\"><strong>${s.clicks_total}</strong><span>Clics</span></div><div class=\"cat-metric recent\"><strong>${s.visitors_7d}</strong><span>7 jours</span></div></div><button class=\"btn danger\" data-catdel=\"${esc(c.id)}\">Supprimer</button></div>`;}).join('');host.querySelectorAll('[data-catname]').forEach(i=>i.onchange=()=>renameCategory(i.dataset.catname,i.value));host.querySelectorAll('[data-catdel]').forEach(b=>b.onclick=()=>deleteCategory(b.dataset.catdel));}
$('reloadCategoryAnalytics').onclick=loadCategoryAnalytics;"""
admin=rep(admin,old_cat,new_cat,'admin category stats renderer')

INDEX.write_text(index,encoding='utf-8')
ADMIN.write_text(admin,encoding='utf-8')
print('category styling + analytics applied')
