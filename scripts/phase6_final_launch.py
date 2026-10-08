from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
PRIVACY = ROOT / 'privacy.html'
TERMS = ROOT / 'terms.html'
SHIPPING = ROOT / 'shipping-returns.html'
SITEMAP = ROOT / 'sitemap.xml'


def rep(text, old, new, label):
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        print('[skip]', label)
        return text
    raise RuntimeError('anchor not found: ' + label)

index = INDEX.read_text(encoding='utf-8')

# Category analytics: one anonymous id per browser session, not persistent storage.
index = rep(index,
    "try{id=localStorage.getItem(CATEGORY_SESSION_KEY)||'';}catch(_){ }",
    "try{id=sessionStorage.getItem(CATEGORY_SESSION_KEY)||'';}catch(_){ }",
    'category analytics session read')
index = rep(index,
    "try{localStorage.setItem(CATEGORY_SESSION_KEY,id);}catch(_){ }",
    "try{sessionStorage.setItem(CATEGORY_SESSION_KEY,id);}catch(_){ }",
    'category analytics session write')

# Success-state styling.
form_error = ".form-error{color:#D34747;font-size:12.5px;font-weight:600;min-height:16px;margin-bottom:6px;}"
success_css = form_error + "\n" + r'''
.order-success-card{text-align:center;padding:34px 28px 30px;}
.order-success-icon{width:66px;height:66px;border-radius:50%;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#E9F8EE,#DDF2E3);color:#157347;border:1px solid #CBE8D4;box-shadow:0 12px 30px rgba(21,115,71,.12);}
.order-success-icon svg{width:32px;height:32px;}
.order-success-card h3{font-size:clamp(22px,4vw,30px);margin-bottom:10px;}
.order-success-card>p{color:var(--text-soft);line-height:1.6;font-size:14.5px;}
.order-success-ref{margin:20px auto;padding:13px 16px;max-width:360px;border:1px solid var(--line);background:var(--bg-alt);border-radius:15px;display:flex;align-items:center;justify-content:space-between;gap:16px;font-size:12px;color:var(--text-soft);}
.order-success-ref strong{font-family:var(--font-mono);font-size:14px;color:var(--text);letter-spacing:.03em;}
.order-success-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px;}
.order-success-actions .btn{justify-content:center;padding:13px 16px;font-size:13px;}
@media(max-width:560px){.order-success-card{padding:28px 18px 22px}.order-success-actions{grid-template-columns:1fr}.order-success-ref{align-items:flex-start;flex-direction:column;gap:4px;text-align:left}}
'''.strip()
index = rep(index, form_error, success_css, 'order success styles')

# Add success overlay before mobile sticky cart bar.
sticky_anchor = '<div class="sticky-buybar" id="stickyBuybar">'
success_html = r'''
<div class="modal-overlay" id="orderSuccessOverlay" aria-hidden="true">
  <div class="modal-box" style="width:min(520px,96vw);" role="dialog" aria-modal="true" aria-labelledby="orderSuccessTitle">
    <div class="order-success-card">
      <div class="order-success-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 6L9 17l-5-5"/></svg></div>
      <h3 id="orderSuccessTitle"></h3>
      <p id="orderSuccessText"></p>
      <div class="order-success-ref"><span id="orderSuccessRefLabel"></span><strong id="orderSuccessRef">—</strong></div>
      <p id="orderSuccessNext"></p>
      <div class="order-success-actions">
        <button class="btn btn-dark" id="orderSuccessBack"></button>
        <button class="btn btn-green" id="orderSuccessWa"></button>
      </div>
    </div>
  </div>
</div>

'''+sticky_anchor
index = rep(index, sticky_anchor, success_html, 'order success overlay')

# Localized success messaging + loading label.
index = rep(index,
    "orderSuccess:'Commande envoyée ! Nous vous contacterons bientôt.', orderFailed:",
    "orderSuccess:'Votre commande a bien été enregistrée.', orderSuccessTitle:'Commande confirmée', orderSuccessRefLabel:'Référence', orderSuccessNext:'Notre équipe vous contactera prochainement pour confirmer votre commande avant expédition.', orderSuccessBack:'Continuer mes achats', orderSuccessWa:'Contacter sur WhatsApp', orderSubmitting:'Envoi en cours…', orderFailed:",
    'fr order success translations')
index = rep(index,
    "orderSuccess:\"Order sent! We'll contact you soon.\", orderFailed:",
    "orderSuccess:'Your order has been registered successfully.', orderSuccessTitle:'Order confirmed', orderSuccessRefLabel:'Reference', orderSuccessNext:'Our team will contact you shortly to confirm the order before shipping.', orderSuccessBack:'Continue shopping', orderSuccessWa:'Contact on WhatsApp', orderSubmitting:'Sending…', orderFailed:",
    'en order success translations')
index = rep(index,
    "orderSuccess:'تم إرسال طلبك! سنتواصل معك قريباً.', orderFailed:",
    "orderSuccess:'تم تسجيل طلبك بنجاح.', orderSuccessTitle:'تم تأكيد الطلب', orderSuccessRefLabel:'رقم الطلب', orderSuccessNext:'سيتواصل معك فريقنا قريباً لتأكيد الطلب قبل الشحن.', orderSuccessBack:'متابعة التسوق', orderSuccessWa:'التواصل عبر واتساب', orderSubmitting:'جارٍ الإرسال…', orderFailed:",
    'ar order success translations')

# Keep success overlay language in sync.
lang_anchor = "document.getElementById('orderFormWaBtn').textContent = t.orderHelpWa;"
lang_extra = lang_anchor + "\n" + r'''  if(document.getElementById('orderSuccessTitle')){
    document.getElementById('orderSuccessTitle').textContent=t.orderSuccessTitle;
    document.getElementById('orderSuccessText').textContent=t.orderSuccess;
    document.getElementById('orderSuccessRefLabel').textContent=t.orderSuccessRefLabel;
    document.getElementById('orderSuccessNext').textContent=t.orderSuccessNext;
    document.getElementById('orderSuccessBack').textContent=t.orderSuccessBack;
    document.getElementById('orderSuccessWa').textContent=t.orderSuccessWa;
  }'''
index = rep(index, lang_anchor, lang_extra, 'success language sync')

# Success overlay behavior.
submit_anchor = 'async function submitOrder(){'
success_js = r'''let LAST_ORDER_CONFIRMATION=null;
function closeOrderSuccess(){
  const overlay=document.getElementById('orderSuccessOverlay');
  if(!overlay)return;
  overlay.classList.remove('open');
  overlay.setAttribute('aria-hidden','true');
  document.body.classList.remove('no-scroll');
}
function showOrderSuccess(placed){
  const t=I18N[currentLang];
  const code=String(placed?.order_code||placed?.order_id||'').trim();
  LAST_ORDER_CONFIRMATION={code};
  document.getElementById('orderSuccessTitle').textContent=t.orderSuccessTitle;
  document.getElementById('orderSuccessText').textContent=t.orderSuccess;
  document.getElementById('orderSuccessRefLabel').textContent=t.orderSuccessRefLabel;
  document.getElementById('orderSuccessRef').textContent=code ? `#${code}` : '—';
  document.getElementById('orderSuccessNext').textContent=t.orderSuccessNext;
  document.getElementById('orderSuccessBack').textContent=t.orderSuccessBack;
  document.getElementById('orderSuccessWa').textContent=t.orderSuccessWa;
  const overlay=document.getElementById('orderSuccessOverlay');
  overlay.classList.add('open');
  overlay.setAttribute('aria-hidden','false');
  document.body.classList.add('no-scroll');
  document.getElementById('orderSuccessBack').focus();
}
function openOrderFollowupWhatsApp(){
  const code=String(LAST_ORDER_CONFIRMATION?.code||'').trim();
  const ref=code ? ` #${code}` : '';
  const text=currentLang==='ar'
    ? `مرحباً، لقد قمت للتو بطلب${ref} من AXORIA وأرغب في متابعة الطلب.`
    : currentLang==='en'
      ? `Hello, I just placed AXORIA order${ref} and would like to follow up.`
      : `Bonjour, je viens de passer la commande AXORIA${ref} et je souhaite la suivre.`;
  const w=window.open(`https://wa.me/212621575115?text=${encodeURIComponent(text)}`,'_blank','noopener,noreferrer');
  if(w)w.opener=null;
}

'''+submit_anchor
index = rep(index, submit_anchor, success_js, 'order success behavior')

# Submit loading state.
btn_anchor = "const btn = document.getElementById('orderFormSubmitBtn');\n  btn.disabled = true;\n  try{"
btn_new = "const btn = document.getElementById('orderFormSubmitBtn');\n  btn.disabled = true;\n  btn.textContent = t.orderSubmitting || t.orderSubmitBtn;\n  try{"
index = rep(index, btn_anchor, btn_new, 'order submit loading state')

# Replace toast-only success with a real confirmation state.
success_old = "closeOrderForm();\n    const ref = placed?.order_code ? ` #${placed.order_code}` : '';\n    toast(t.orderSuccess + ref);"
success_new = "closeOrderForm();\n    showOrderSuccess(placed);"
index = rep(index, success_old, success_new, 'show order confirmation')

# Restore submit label in finally.
finally_old = "}finally{\n    btn.disabled = false;\n  }\n}"
finally_new = "}finally{\n    btn.disabled = false;\n    btn.textContent = I18N[currentLang].orderSubmitBtn;\n  }\n}"
index = rep(index, finally_old, finally_new, 'restore order submit label')

# Wire success overlay buttons.
listener_anchor = "document.getElementById('orderFormWaBtn').onclick = ()=>{ const w=window.open(buildWhatsAppMessage(false),'_blank','noopener,noreferrer'); if(w)w.opener=null; };"
listener_new = listener_anchor + "\n" + r'''  document.getElementById('orderSuccessBack').onclick=closeOrderSuccess;
  document.getElementById('orderSuccessWa').onclick=openOrderFollowupWhatsApp;
  document.getElementById('orderSuccessOverlay').addEventListener('click',e=>{if(e.target.id==='orderSuccessOverlay')closeOrderSuccess();});'''
index = rep(index, listener_anchor, listener_new, 'success overlay listeners')

INDEX.write_text(index, encoding='utf-8')

# Improve legal metadata and disclose anonymous category-interest analytics.
privacy = PRIVACY.read_text(encoding='utf-8')
privacy = rep(privacy,
    '<title>Politique de confidentialité — AXORIA</title><meta name="robots" content="index,follow">',
    '<title>Politique de confidentialité — AXORIA</title><meta name="description" content="Politique de confidentialité AXORIA Maroc : commandes, support, statistiques anonymes et mesure publicitaire."><link rel="canonical" href="https://axoria.ma/privacy.html"><meta name="robots" content="index,follow">',
    'privacy metadata')
privacy = rep(privacy,
    '<h2>Services techniques</h2><p>Le site peut utiliser des services techniques et analytiques, notamment Supabase pour les données de commande et Meta Pixel / Conversions API pour la mesure publicitaire lorsque le tracking est activé.</p>',
    '<h2>Services techniques et statistiques</h2><p>Le site utilise Supabase pour les données nécessaires au fonctionnement de la boutique. AXORIA peut également mesurer de façon anonyme l’intérêt pour les catégories au moyen d’un identifiant aléatoire limité à la session du navigateur, sans y associer le nom, le téléphone ou l’adresse du visiteur. Meta Pixel / Conversions API peuvent être utilisés pour la mesure publicitaire lorsque le tracking est activé.</p>',
    'privacy analytics disclosure')
PRIVACY.write_text(privacy, encoding='utf-8')

terms = TERMS.read_text(encoding='utf-8')
terms = rep(terms,
    '<title>Conditions générales — AXORIA</title><meta name="robots" content="index,follow">',
    '<title>Conditions générales — AXORIA</title><meta name="description" content="Conditions générales AXORIA Maroc : commandes, prix, disponibilité, paiement, livraison et service client."><link rel="canonical" href="https://axoria.ma/terms.html"><meta name="robots" content="index,follow">',
    'terms metadata')
TERMS.write_text(terms, encoding='utf-8')

shipping = SHIPPING.read_text(encoding='utf-8')
shipping = rep(shipping,
    '<title>Livraison & Retours — AXORIA</title><meta name="robots" content="index,follow">',
    '<title>Livraison & Retours — AXORIA</title><meta name="description" content="Livraison et retours AXORIA au Maroc : délais indicatifs, paiement à la livraison, échanges et assistance."><link rel="canonical" href="https://axoria.ma/shipping-returns.html"><meta name="robots" content="index,follow">',
    'shipping metadata')
SHIPPING.write_text(shipping, encoding='utf-8')

sitemap = SITEMAP.read_text(encoding='utf-8').replace('<lastmod>2026-10-07</lastmod>', '<lastmod>2026-10-08</lastmod>')
SITEMAP.write_text(sitemap, encoding='utf-8')

print('Phase 6 final launch readiness patch applied.')
