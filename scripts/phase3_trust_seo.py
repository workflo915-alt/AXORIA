from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "admin.html"
INDEX = ROOT / "index.html"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            print(f"[skip] {label} already applied")
            return text
        raise RuntimeError(f"Anchor not found for {label}")
    return text.replace(old, new, 1)


admin = ADMIN.read_text(encoding="utf-8")
index = INDEX.read_text(encoding="utf-8")

# -------------------------
# Admin: Reviews moderation
# -------------------------
admin = replace_once(
    admin,
    '      <button class="btn tab ghost" data-tab="categories">Catégories</button>',
    '      <button class="btn tab ghost" data-tab="categories">Catégories</button>\n'
    '      <button class="btn tab ghost" data-tab="reviews">Avis</button>',
    "reviews admin tab",
)

admin = replace_once(
    admin,
    '    <section id="categoriesPanel" class="card panel hidden">\n'
    '      <div class="bar"><h2>Catégories</h2><div class="actions"><input id="newCategory" placeholder="Nouvelle catégorie"><button id="addCategory" class="btn primary">Ajouter</button></div></div>\n'
    '      <div id="categoriesList"></div>\n'
    '    </section>\n'
    '  </div>\n'
    '</div>',
    '    <section id="categoriesPanel" class="card panel hidden">\n'
    '      <div class="bar"><h2>Catégories</h2><div class="actions"><input id="newCategory" placeholder="Nouvelle catégorie"><button id="addCategory" class="btn primary">Ajouter</button></div></div>\n'
    '      <div id="categoriesList"></div>\n'
    '    </section>\n\n'
    '    <section id="reviewsPanel" class="card panel hidden">\n'
    '      <div class="bar">\n'
    '        <div><h2>Avis clients</h2><div class="sub">Seuls les avis approuvés sont visibles sur la boutique.</div></div>\n'
    '        <div class="actions">\n'
    '          <select id="reviewStatusFilter"><option value="">Tous les statuts</option><option value="pending">En attente</option><option value="approved">Approuvés</option><option value="rejected">Rejetés</option></select>\n'
    '          <button id="reloadReviews" class="btn ghost">Actualiser</button>\n'
    '        </div>\n'
    '      </div>\n'
    '      <div id="reviewsSummary" class="sub" style="margin:0 0 12px"></div>\n'
    '      <div class="table-wrap"><table style="min-width:1080px"><thead><tr><th>Date</th><th>Client</th><th>Note</th><th>Commentaire</th><th>Statut</th><th>Modération</th></tr></thead><tbody id="reviewsBody"></tbody></table></div>\n'
    '    </section>\n'
    '  </div>\n'
    '</div>',
    "reviews admin panel",
)

admin = replace_once(
    admin,
    '.status.Cancelled{background:#EEE;color:#666}',
    '.status.Cancelled{background:#EEE;color:#666}.status.pending{background:#FFF5D6;color:#775B00}.status.approved{background:#E7F6EC;color:#157347}.status.rejected{background:#FDE8E7;color:#9C2D28}',
    "review status styles",
)

admin = replace_once(
    admin,
    "async function requireSession(){const {data:{session}}=await sb.auth.getSession();if(recoveryMode){showPasswordEditor('recovery');return !!session;}if(!session){showLogin();return false;}hideAuthViews();$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();return true;}",
    "async function requireSession(){const {data:{session}}=await sb.auth.getSession();if(recoveryMode){showPasswordEditor('recovery');return !!session;}if(!session){showLogin();return false;}hideAuthViews();$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();await loadReviews();return true;}",
    "load reviews with admin session",
)

admin = replace_once(
    admin,
    "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));['products','orders','categories'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='categories')renderCategories();});",
    "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));['products','orders','categories','reviews'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='categories')renderCategories();if(b.dataset.tab==='reviews')loadReviews();});",
    "reviews tab switching",
)

review_admin_js = r'''
let REVIEW_SUBMISSIONS=[];
function reviewDate(v){try{return new Intl.DateTimeFormat('fr-MA',{dateStyle:'medium',timeStyle:'short'}).format(new Date(v));}catch(_){return String(v||'');}}
function reviewStatusLabel(v){return v==='approved'?'Approuvé':v==='rejected'?'Rejeté':'En attente';}
async function loadReviews(){
  if(!$('reviewsBody'))return;
  $('reviewsBody').innerHTML='<tr><td colspan="6" class="muted">Chargement…</td></tr>';
  try{
    const {data,error}=await sb.from('review_submissions').select('id,created_at,name,rating,comment,status,moderated_at').order('created_at',{ascending:false});
    if(error)throw error;
    REVIEW_SUBMISSIONS=Array.isArray(data)?data:[];
    renderAdminReviews();
  }catch(e){console.error(e);$('reviewsBody').innerHTML='<tr><td colspan="6" class="muted">Impossible de charger les avis.</td></tr>';toast('Échec chargement des avis');}
}
function renderAdminReviews(){
  const filter=$('reviewStatusFilter')?.value||'';
  const rows=REVIEW_SUBMISSIONS.filter(r=>!filter||r.status===filter);
  const counts=REVIEW_SUBMISSIONS.reduce((a,r)=>(a[r.status]=(a[r.status]||0)+1,a),{});
  $('reviewsSummary').textContent=`${REVIEW_SUBMISSIONS.length} avis · ${counts.pending||0} en attente · ${counts.approved||0} approuvé(s) · ${counts.rejected||0} rejeté(s)`;
  if(!rows.length){$('reviewsBody').innerHTML='<tr><td colspan="6" class="muted">Aucun avis pour ce filtre.</td></tr>';return;}
  $('reviewsBody').innerHTML=rows.map(r=>`<tr>
    <td>${esc(reviewDate(r.created_at))}</td>
    <td><strong>${esc(r.name)}</strong></td>
    <td>${'★'.repeat(Math.max(0,Math.min(5,Number(r.rating)||0)))}${'☆'.repeat(Math.max(0,5-(Number(r.rating)||0)))}</td>
    <td style="max-width:430px;white-space:normal;line-height:1.5">${esc(r.comment)}</td>
    <td><span class="status ${esc(r.status)}">${esc(reviewStatusLabel(r.status))}</span></td>
    <td><div class="row-actions">
      <button class="btn primary" data-review-approve="${esc(r.id)}" ${r.status==='approved'?'disabled':''}>Approuver</button>
      <button class="btn ghost" data-review-reject="${esc(r.id)}" ${r.status==='rejected'?'disabled':''}>Rejeter</button>
      <button class="btn danger" data-review-delete="${esc(r.id)}">Supprimer</button>
    </div></td>
  </tr>`).join('');
  $('reviewsBody').querySelectorAll('[data-review-approve]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewApprove,'approve'));
  $('reviewsBody').querySelectorAll('[data-review-reject]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewReject,'reject'));
  $('reviewsBody').querySelectorAll('[data-review-delete]').forEach(b=>b.onclick=()=>removeReview(b.dataset.reviewDelete));
}
async function moderateReview(id,action){
  try{
    const {error}=await sb.rpc('moderate_review',{p_review_id:id,p_action:action});
    if(error)throw error;
    toast(action==='approve'?'Avis approuvé':'Avis rejeté');
    await loadReviews();
  }catch(e){console.error(e);toast('Échec de la modération');}
}
async function removeReview(id){
  if(!confirm('Supprimer définitivement cet avis ?'))return;
  try{
    const {error}=await sb.rpc('delete_review',{p_review_id:id});
    if(error)throw error;
    toast('Avis supprimé');
    await loadReviews();
  }catch(e){console.error(e);toast('Échec suppression avis');}
}
$('reloadReviews').onclick=loadReviews;
$('reviewStatusFilter').addEventListener('change',renderAdminReviews);
'''.strip()

admin = replace_once(
    admin,
    "$('orderStatusFilter').addEventListener('change',renderOrders);\n\nrequireSession();",
    "$('orderStatusFilter').addEventListener('change',renderOrders);\n\n" + review_admin_js + "\n\nrequireSession();",
    "reviews admin javascript",
)

# -------------------------
# Storefront: approved reviews only + XSS protection
# -------------------------
index = replace_once(
    index,
    '<meta name="description" content="AXORIA — correcteur de posture et ceinture amincissante premium. Marque marocaine de bien-être. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta name="description" content="AXORIA — correcteur de posture et accessoires de bien-être premium au Maroc. Confort au quotidien, livraison partout au Maroc et paiement à la livraison.">\n'
    '<link rel="canonical" href="https://axoria.ma/">\n'
    '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">\n'
    '<meta name="author" content="AXORIA">',
    "SEO canonical and robots meta",
)

index = replace_once(
    index,
    '<meta property="og:description" content="Correcteur de posture et ceinture amincissante premium. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta property="og:description" content="Correcteur de posture et accessoires de bien-être premium. Livraison partout au Maroc, paiement à la livraison.">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:url" content="https://axoria.ma/">\n'
    '<meta property="og:site_name" content="AXORIA">\n'
    '<meta property="og:locale" content="fr_MA">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="twitter:title" content="AXORIA — Feel Better, Every Day">\n'
    '<meta name="twitter:description" content="Correcteur de posture et accessoires de bien-être premium au Maroc.">',
    "SEO social metadata",
)

index = replace_once(
    index,
    '  "name": "AXORIA",\n  "telephone": "+212621575115",',
    '  "name": "AXORIA",\n  "url": "https://axoria.ma/",\n  "telephone": "+212621575115",',
    "store schema URL",
)

index = replace_once(
    index,
    '</script>\n<style>',
    '</script>\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "WebSite",\n  "name": "AXORIA",\n  "url": "https://axoria.ma/",\n  "inLanguage": ["fr-MA", "ar-MA", "en"]\n}\n</script>\n<style>',
    "website schema",
)

index = replace_once(
    index,
    'function renderReviews(){\n  const slider = document.getElementById(\'reviewSlider\');',
    "function escapeReviewHtml(v){return String(v??'').replace(/[&<>\\\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}[c]));}\n\nfunction renderReviews(){\n  const slider = document.getElementById('reviewSlider');",
    "review HTML escaping helper",
)

index = replace_once(
    index,
    '      <p class="quote">"${r.comment}"</p>\n      <div class="who"><div class="avatar">${r.name.charAt(0)}</div><div><div class="nm">${r.name}</div><div class="loc">${r.loc}</div></div></div>',
    '      <p class="quote">"${escapeReviewHtml(r.comment)}"</p>\n      <div class="who"><div class="avatar">${escapeReviewHtml((r.name||\'?\').charAt(0))}</div><div><div class="nm">${escapeReviewHtml(r.name)}</div><div class="loc">${escapeReviewHtml(r.loc||\'Maroc\')}</div></div></div>',
    "escape displayed reviews",
)

index = replace_once(
    index,
    "  const storedReviews = await storeGet('axoria_reviews', true);\n  if(storedReviews){ REVIEWS = storedReviews; } else { REVIEWS = DEFAULT_REVIEWS; }",
    "  let approvedReviews=[];\n  if(sb){\n    try{\n      const {data,error}=await sb.from('review_submissions').select('id,name,rating,comment,created_at').eq('status','approved').order('created_at',{ascending:false});\n      if(error)throw error;\n      approvedReviews=(Array.isArray(data)?data:[]).map(r=>({submission_id:r.id,name:r.name,rating:r.rating,comment:r.comment,loc:'Maroc',created_at:r.created_at}));\n    }catch(e){console.error('approved reviews load failed',e);}\n  }\n  REVIEWS=approvedReviews;",
    "approved reviews as storefront source",
)

# Ensure honest empty state instead of fabricated testimonials.
index = replace_once(
    index,
    "  slider.innerHTML = REVIEWS.map(r=>`",
    "  if(!REVIEWS.length){slider.innerHTML='<div class=\"rcard\"><p class=\"quote\">Les avis clients vérifiés apparaîtront ici après validation.</p></div>';return;}\n  slider.innerHTML = REVIEWS.map(r=>`",
    "reviews empty state",
)

ADMIN.write_text(admin, encoding="utf-8")
INDEX.write_text(index, encoding="utf-8")

ROBOTS.write_text(
    "User-agent: *\nAllow: /\nDisallow: /admin.html\nSitemap: https://axoria.ma/sitemap.xml\n",
    encoding="utf-8",
)

SITEMAP.write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    '  <url>\n'
    '    <loc>https://axoria.ma/</loc>\n'
    '    <changefreq>weekly</changefreq>\n'
    '    <priority>1.0</priority>\n'
    '  </url>\n'
    '</urlset>\n',
    encoding="utf-8",
)

print("Phase 3 Reviews/Trust + SEO foundation patch applied.")
