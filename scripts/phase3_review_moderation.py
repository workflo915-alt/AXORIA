from pathlib import Path

path = Path('admin.html')
text = path.read_text(encoding='utf-8')

if 'data-tab="reviews"' in text and "sb.rpc('moderate_review'" in text:
    print('Phase 3 review moderation already applied.')
    raise SystemExit(0)

# Add moderation status styling.
style_marker = '.password-hint{font-size:11.5px;color:var(--muted);line-height:1.45;margin-top:-4px}\n</style>'
style_replacement = ".password-hint{font-size:11.5px;color:var(--muted);line-height:1.45;margin-top:-4px}\n.status.pending{background:#FFF5D6;color:#775B00}.status.approved{background:#E7F6EC;color:#157347}.status.rejected{background:#FDE8E7;color:#B42318}\n.review-stars{color:#C9A227;letter-spacing:1px;font-size:14px;white-space:nowrap}\n</style>"
if style_marker not in text:
    raise SystemExit('style marker not found')
text = text.replace(style_marker, style_replacement, 1)

# Add the Avis tab.
tabs_old = '''      <button class="btn tab active" data-tab="products">Produits</button>\n      <button class="btn tab ghost" data-tab="orders">Commandes</button>\n      <button class="btn tab ghost" data-tab="categories">Catégories</button>'''
tabs_new = '''      <button class="btn tab active" data-tab="products">Produits</button>\n      <button class="btn tab ghost" data-tab="orders">Commandes</button>\n      <button class="btn tab ghost" data-tab="reviews">Avis</button>\n      <button class="btn tab ghost" data-tab="categories">Catégories</button>'''
if tabs_old not in text:
    raise SystemExit('tabs marker not found')
text = text.replace(tabs_old, tabs_new, 1)

# Insert the review moderation panel before categories.
categories_marker = '''    <section id="categoriesPanel" class="card panel hidden">'''
reviews_panel = '''    <section id="reviewsPanel" class="card panel hidden">\n      <div class="bar">\n        <h2>Avis clients</h2>\n        <div class="actions">\n          <input id="reviewSearch" placeholder="Rechercher un nom ou un commentaire" style="min-width:280px">\n          <select id="reviewStatusFilter">\n            <option value="">Tous les statuts</option>\n            <option value="pending">En attente</option>\n            <option value="approved">Approuvés</option>\n            <option value="rejected">Refusés</option>\n          </select>\n          <button id="reloadReviews" class="btn ghost">Actualiser</button>\n        </div>\n      </div>\n      <div id="reviewsSummary" class="sub" style="margin:0 0 12px"></div>\n      <div class="table-wrap"><table style="min-width:1050px"><thead><tr><th>Date</th><th>Client</th><th>Note</th><th>Commentaire</th><th>Statut</th><th>Actions</th></tr></thead><tbody id="reviewsBody"></tbody></table></div>\n    </section>\n\n'''
if categories_marker not in text:
    raise SystemExit('categories panel marker not found')
text = text.replace(categories_marker, reviews_panel + categories_marker, 1)

# Add review state.
state_old = 'let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];'
state_new = 'let PRODUCTS=[];let CATEGORIES=[];let ORDERS=[];let REVIEW_SUBMISSIONS=[];'
if state_old not in text:
    raise SystemExit('state marker not found')
text = text.replace(state_old, state_new, 1)

# Load reviews when authenticated.
session_old = "async function requireSession(){const {data:{session}}=await sb.auth.getSession();if(recoveryMode){showPasswordEditor('recovery');return !!session;}if(!session){showLogin();return false;}hideAuthViews();$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();return true;}"
session_new = "async function requireSession(){const {data:{session}}=await sb.auth.getSession();if(recoveryMode){showPasswordEditor('recovery');return !!session;}if(!session){showLogin();return false;}hideAuthViews();$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();await loadReviewSubmissions();return true;}"
if session_old not in text:
    raise SystemExit('session marker not found')
text = text.replace(session_old, session_new, 1)

# Teach tab navigation about the new panel.
tab_old = "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));['products','orders','categories'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='categories')renderCategories();});"
tab_new = "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));['products','orders','reviews','categories'].forEach(t=>$(t+'Panel').classList.toggle('hidden',t!==b.dataset.tab));if(b.dataset.tab==='orders')loadOrders();if(b.dataset.tab==='reviews')loadReviewSubmissions();if(b.dataset.tab==='categories')renderCategories();});"
if tab_old not in text:
    raise SystemExit('tab navigation marker not found')
text = text.replace(tab_old, tab_new, 1)

# Insert the moderation logic before the final requireSession call.
end_marker = "$('orderStatusFilter').addEventListener('change',renderOrders);\n\nrequireSession();"
review_logic = r'''$('orderStatusFilter').addEventListener('change',renderOrders);

async function loadReviewSubmissions(){
  const body=$('reviewsBody');
  if(!body)return;
  body.innerHTML='<tr><td colspan="6" class="muted">Chargement…</td></tr>';
  try{
    const {data,error}=await sb.from('review_submissions').select('*').order('created_at',{ascending:false});
    if(error)throw error;
    REVIEW_SUBMISSIONS=data||[];
    renderReviewSubmissions();
  }catch(e){
    console.error(e);
    body.innerHTML='<tr><td colspan="6" class="muted">Impossible de charger les avis.</td></tr>';
  }
}
function reviewStatusLabel(s){return s==='approved'?'Approuvé':s==='rejected'?'Refusé':'En attente';}
function renderReviewSubmissions(){
  const body=$('reviewsBody');
  if(!body)return;
  const q=($('reviewSearch')?.value||'').trim().toLowerCase();
  const status=$('reviewStatusFilter')?.value||'';
  const rows=REVIEW_SUBMISSIONS.filter(r=>{
    if(status && r.status!==status)return false;
    if(!q)return true;
    return [r.name,r.comment].some(v=>String(v||'').toLowerCase().includes(q));
  });
  const pending=REVIEW_SUBMISSIONS.filter(r=>r.status==='pending').length;
  const approved=REVIEW_SUBMISSIONS.filter(r=>r.status==='approved').length;
  const rejected=REVIEW_SUBMISSIONS.filter(r=>r.status==='rejected').length;
  if($('reviewsSummary'))$('reviewsSummary').textContent=`${REVIEW_SUBMISSIONS.length} avis · En attente: ${pending} · Approuvés: ${approved} · Refusés: ${rejected}`;
  if(!rows.length){body.innerHTML='<tr><td colspan="6" class="muted">Aucun avis pour ce filtre.</td></tr>';return;}
  body.innerHTML=rows.map(r=>`<tr>
    <td>${esc(new Date(r.created_at).toLocaleString('fr-FR'))}</td>
    <td><strong>${esc(r.name)}</strong></td>
    <td><span class="review-stars">${'★'.repeat(Math.max(0,Math.min(5,Number(r.rating)||0)))}${'☆'.repeat(Math.max(0,5-(Number(r.rating)||0)))}</span></td>
    <td style="max-width:430px;white-space:normal;line-height:1.45">${esc(r.comment)}</td>
    <td><span class="status ${esc(r.status)}">${reviewStatusLabel(r.status)}</span></td>
    <td><div class="row-actions">
      <button class="btn primary" data-review-approve="${esc(r.id)}" ${r.status==='approved'?'disabled':''}>Approuver</button>
      <button class="btn danger" data-review-reject="${esc(r.id)}" ${r.status==='rejected'?'disabled':''}>Refuser</button>
    </div></td>
  </tr>`).join('');
  body.querySelectorAll('[data-review-approve]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewApprove,'approve',b));
  body.querySelectorAll('[data-review-reject]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewReject,'reject',b));
}
async function moderateReview(id,action,btn){
  btn.disabled=true;
  try{
    const {error}=await sb.rpc('moderate_review',{p_review_id:id,p_action:action});
    if(error)throw error;
    await loadReviewSubmissions();
    toast(action==='approve'?'Avis approuvé et publié':'Avis refusé et retiré du site');
  }catch(e){
    console.error(e);
    toast('Échec de modération de l’avis');
    await loadReviewSubmissions();
  }
}
$('reloadReviews').onclick=loadReviewSubmissions;
$('reviewSearch').addEventListener('input',renderReviewSubmissions);
$('reviewStatusFilter').addEventListener('change',renderReviewSubmissions);

requireSession();'''
if end_marker not in text:
    raise SystemExit('end marker not found')
text = text.replace(end_marker, review_logic, 1)

checks = [
    'data-tab="reviews"',
    'id="reviewsPanel"',
    "sb.from('review_submissions').select('*')",
    "sb.rpc('moderate_review'",
    "await loadReviewSubmissions()",
]
for marker in checks:
    if marker not in text:
        raise SystemExit(f'missing generated marker: {marker}')

path.write_text(text, encoding='utf-8')
print('Phase 3 review moderation admin patch applied.')
