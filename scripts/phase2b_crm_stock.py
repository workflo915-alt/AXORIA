from pathlib import Path

index_path = Path('index.html')
admin_path = Path('admin.html')
index = index_path.read_text(encoding='utf-8')
admin = admin_path.read_text(encoding='utf-8')


def replace_between(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'{label}: start marker not found')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'{label}: end marker not found')
    return text[:start] + replacement + text[end:]


# Safe to rerun after the generated files have already been committed.
if "sb.rpc('place_order'" in index and "sb.rpc('set_order_status'" in admin:
    print('Phase 2B patch already applied.')
    raise SystemExit(0)

checkout_start = "  // Automatically pulled from the cart -- never re-entered by the customer."
checkout_end = "    CART = [];"
checkout_replacement = """  // Only product IDs and quantities leave the browser. Prices, availability and
  // stock are resolved atomically on the server by the place_order RPC.
  const rpcItems = CART.map(c=>({ product_id:c.id, qty:c.qty }));

  const btn = document.getElementById('orderFormSubmitBtn');
  btn.disabled = true;
  try{
    const { data, error } = await sb.rpc('place_order', {
      p_customer_name:name,
      p_phone:phone,
      p_city:city,
      p_address:address,
      p_notes:notes || null,
      p_items:rpcItems
    });
    if(error) throw error;
    const placed = Array.isArray(data) ? data[0] : data;

    // Stock changed server-side: refresh the visible catalog immediately.
    const fresh = await fetchProductsSafe();
    if(fresh.status==='ok' && Array.isArray(fresh.data)){
      PRODUCTS = fresh.data;
      syncNextProductId();
      renderCatFilters();
      renderMenuGrid();
    }
"""
index = replace_between(index, checkout_start, checkout_end, checkout_replacement, 'storefront checkout')

old_success = """    toast(t.orderSuccess);
  }catch(e){
    console.error('submitOrder failed', e);
    errEl.textContent = t.orderFailed;"""
new_success = """    const ref = placed?.order_code ? ` #${placed.order_code}` : '';
    toast(t.orderSuccess + ref);
  }catch(e){
    console.error('submitOrder failed', e);
    const msg = String(e?.message || '');
    if(msg.includes('Insufficient stock') || msg.includes('Product unavailable') || msg.includes('Product not found')){
      errEl.textContent = currentLang==='ar'
        ? 'الكمية المطلوبة غير متوفرة حالياً. حدّث الصفحة وحاول من جديد.'
        : currentLang==='en'
          ? 'The requested quantity is no longer available. Refresh and try again.'
          : 'La quantité demandée n’est plus disponible. Actualisez puis réessayez.';
      const fresh = await fetchProductsSafe();
      if(fresh.status==='ok' && Array.isArray(fresh.data)){
        PRODUCTS=fresh.data; syncNextProductId(); renderCatFilters(); renderMenuGrid(); renderCart();
      }
    }else{
      errEl.textContent = t.orderFailed;
    }"""
if old_success not in index:
    raise SystemExit('storefront success/error block not found')
index = index.replace(old_success, new_success, 1)

old_panel = """    <section id=\"ordersPanel\" class=\"card panel hidden\">
      <div class=\"bar\"><h2>Commandes</h2><button id=\"reloadOrders\" class=\"btn ghost\">Actualiser</button></div>
      <div class=\"table-wrap\"><table><thead><tr><th>Date</th><th>Client</th><th>Téléphone</th><th>Ville</th><th>Adresse</th><th>Produits</th><th>Total</th><th>Notes</th><th>Statut</th></tr></thead><tbody id=\"ordersBody\"></tbody></table></div>
    </section>"""
new_panel = """    <section id=\"ordersPanel\" class=\"card panel hidden\">
      <div class=\"bar\">
        <h2>Commandes</h2>
        <div class=\"actions\">
          <input id=\"orderSearch\" placeholder=\"Rechercher client, téléphone, ville ou référence\" style=\"min-width:300px\">
          <select id=\"orderStatusFilter\"><option value=\"\">Tous les statuts</option><option>New</option><option>Contacted</option><option>Confirmed</option><option>Shipped</option><option>Delivered</option><option>Cancelled</option></select>
          <button id=\"reloadOrders\" class=\"btn ghost\">Actualiser</button>
        </div>
      </div>
      <div id=\"ordersSummary\" class=\"sub\" style=\"margin:0 0 12px\"></div>
      <div class=\"table-wrap\"><table style=\"min-width:1380px\"><thead><tr><th>Référence</th><th>Date</th><th>Client</th><th>Téléphone</th><th>Ville</th><th>Adresse</th><th>Produits</th><th>Total</th><th>Notes</th><th>Statut</th><th>Contact</th></tr></thead><tbody id=\"ordersBody\"></tbody></table></div>
    </section>"""
if old_panel not in admin:
    raise SystemExit('admin orders panel not found')
admin = admin.replace(old_panel, new_panel, 1)

admin_start = "async function loadOrders(){"
admin_end = "$('reloadOrders').onclick=loadOrders;"
admin_replacement = r"""function waPhone(v){let n=String(v||'').replace(/\D/g,'');if(n.startsWith('0'))n='212'+n.slice(1);return n;}
function telPhone(v){return String(v||'').replace(/[^\d+]/g,'');}
async function loadOrders(){
  const body=$('ordersBody');
  body.innerHTML='<tr><td colspan="11" class="muted">Chargement…</td></tr>';
  try{
    const {data,error}=await sb.from('orders').select('*').order('created_at',{ascending:false});
    if(error)throw error;
    ORDERS=data||[];
    renderOrders();
  }catch(e){
    console.error(e);
    body.innerHTML='<tr><td colspan="11" class="muted">Accès refusé ou erreur de chargement.</td></tr>';
  }
}
function renderOrders(){
  const body=$('ordersBody');
  const q=($('orderSearch')?.value||'').trim().toLowerCase();
  const status=$('orderStatusFilter')?.value||'';
  const rows=ORDERS.filter(o=>{
    if(status && o.status!==status)return false;
    if(!q)return true;
    return [o.order_code,o.customer_name,o.phone,o.city,o.address].some(v=>String(v||'').toLowerCase().includes(q));
  });
  const counts=ORDER_STATUSES.map(s=>`${s}: ${ORDERS.filter(o=>o.status===s).length}`).join(' · ');
  if($('ordersSummary'))$('ordersSummary').textContent=`${ORDERS.length} commande(s) · ${counts}`;
  if(!rows.length){body.innerHTML='<tr><td colspan="11" class="muted">Aucune commande pour ce filtre.</td></tr>';return;}
  body.innerHTML=rows.map(o=>{
    const wa=waPhone(o.phone),tel=telPhone(o.phone);
    const ref=o.order_code||`AX-${String(o.id||'').slice(0,8).toUpperCase()}`;
    return `<tr>
      <td><strong>${esc(ref)}</strong></td>
      <td>${esc(new Date(o.created_at).toLocaleString('fr-FR'))}</td>
      <td>${esc(o.customer_name)}</td>
      <td>${esc(o.phone)}</td>
      <td>${esc(o.city)}</td>
      <td>${esc(o.address)}</td>
      <td>${Array.isArray(o.items)?o.items.map(i=>`${esc(i.name)} ×${Number(i.qty||0)}`).join('<br>'):''}</td>
      <td><strong>${money(o.total)}</strong></td>
      <td>${esc(o.notes||'—')}</td>
      <td><span class="status ${esc(o.status)}">${esc(o.status)}</span><select data-order="${esc(o.id)}" style="margin-top:7px">${ORDER_STATUSES.map(s=>`<option value="${s}" ${s===o.status?'selected':''}>${s}</option>`).join('')}</select></td>
      <td><div class="row-actions"><a class="btn ghost" href="https://wa.me/${wa}" target="_blank" rel="noopener">WhatsApp</a><a class="btn ghost" href="tel:${tel}">Appeler</a></div></td>
    </tr>`;
  }).join('');
  body.querySelectorAll('[data-order]').forEach(s=>s.onchange=()=>updateOrder(s.dataset.order,s.value,s));
}
async function updateOrder(id,status,sel){
  sel.disabled=true;
  try{
    const {error}=await sb.rpc('set_order_status',{p_order_id:id,p_status:status});
    if(error)throw error;
    await Promise.all([loadOrders(),loadProducts()]);
    toast(status==='Cancelled'?'Commande annulée · stock restauré':'Statut mis à jour');
  }catch(e){
    console.error(e);
    toast(String(e?.message||'').includes('Insufficient stock')?'Stock insuffisant pour réactiver cette commande':'Échec mise à jour');
    await loadOrders();
  }
}
$('reloadOrders').onclick=loadOrders;
$('orderSearch').addEventListener('input',renderOrders);
$('orderStatusFilter').addEventListener('change',renderOrders);"""
admin = replace_between(admin, admin_start, admin_end, admin_replacement, 'admin orders')
# replace_between keeps end marker; remove the duplicated old marker left after replacement.
admin = admin.replace("$('orderStatusFilter').addEventListener('change',renderOrders);$('reloadOrders').onclick=loadOrders;", "$('orderStatusFilter').addEventListener('change',renderOrders);", 1)

for marker, text, label in [
    ("sb.rpc('place_order'", index, 'storefront RPC'),
    ("sb.rpc('set_order_status'", admin, 'admin status RPC'),
    ('orderSearch', admin, 'CRM search'),
    ('order_code', admin, 'order reference'),
]:
    if marker not in text:
        raise SystemExit(f'missing {label}: {marker}')
if "sb.from('orders').insert" in index:
    raise SystemExit('direct storefront insert remains')
if "sb.from('orders').update({status})" in admin:
    raise SystemExit('direct admin status update remains')

index_path.write_text(index, encoding='utf-8')
admin_path.write_text(admin, encoding='utf-8')
print('Phase 2B CRM + stock patch applied.')
