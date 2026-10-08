from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    if old not in s:
        if new in s:
            print(f'[skip] {label} already applied')
            return
        raise SystemExit(f'missing anchor: {label}')
    s = s.replace(old, new, 1)

# Faster font connection without touching hero/SEO/tracking structure.
replace_once(
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    'fonts preconnect'
)

# Accessible, bounded checkout fields. Limits mirror the server RPC constraints.
replace_once(
    '<div class="form-row"><label id="lblOrderName"></label><input type="text" id="ofName" autocomplete="name"></div>\n        <div class="form-row"><label id="lblOrderPhone"></label><input type="tel" id="ofPhone" autocomplete="tel"></div>',
    '<div class="form-row"><label id="lblOrderName" for="ofName"></label><input type="text" id="ofName" autocomplete="name" maxlength="120" required></div>\n        <div class="form-row"><label id="lblOrderPhone" for="ofPhone"></label><input type="tel" id="ofPhone" autocomplete="tel" inputmode="tel" maxlength="30" required aria-describedby="orderFormError"></div>',
    'checkout identity fields'
)
replace_once(
    '<div class="form-row"><label id="lblOrderCity"></label><input type="text" id="ofCity" autocomplete="address-level2"></div>\n        <div class="form-row"><label id="lblOrderAddress"></label><input type="text" id="ofAddress" autocomplete="street-address"></div>',
    '<div class="form-row"><label id="lblOrderCity" for="ofCity"></label><input type="text" id="ofCity" autocomplete="address-level2" maxlength="120" required></div>\n        <div class="form-row"><label id="lblOrderAddress" for="ofAddress"></label><input type="text" id="ofAddress" autocomplete="street-address" maxlength="300" required></div>',
    'checkout address fields'
)
replace_once(
    '<div class="form-row"><label id="lblOrderNotes"></label><textarea id="ofNotes" rows="3"></textarea></div>\n      <div class="form-error" id="orderFormError"></div>',
    '<div class="form-row"><label id="lblOrderNotes" for="ofNotes"></label><textarea id="ofNotes" rows="3" maxlength="1000"></textarea></div>\n      <div class="form-error" id="orderFormError" role="alert" aria-live="polite"></div>',
    'checkout notes and error'
)

# Trilingual invalid-phone feedback.
replace_once(
    "    orderNoConnection:'Connexion indisponible. Merci de réessayer ou de nous contacter sur WhatsApp.'",
    "    orderNoConnection:'Connexion indisponible. Merci de réessayer ou de nous contacter sur WhatsApp.',\n    orderInvalidPhone:'Veuillez saisir un numéro marocain valide (ex. 06 12 34 56 78 ou +212 6 12 34 56 78).'",
    'fr phone message'
)
replace_once(
    "    orderNoConnection:'Connection unavailable. Please try again or contact us on WhatsApp.'",
    "    orderNoConnection:'Connection unavailable. Please try again or contact us on WhatsApp.',\n    orderInvalidPhone:'Please enter a valid Moroccan phone number (e.g. 06 12 34 56 78 or +212 6 12 34 56 78).'",
    'en phone message'
)
replace_once(
    "    orderNoConnection:'الاتصال غير متوفر. يرجى المحاولة مجدداً أو التواصل معنا عبر واتساب.'",
    "    orderNoConnection:'الاتصال غير متوفر. يرجى المحاولة مجدداً أو التواصل معنا عبر واتساب.',\n    orderInvalidPhone:'يرجى إدخال رقم هاتف مغربي صحيح، مثل 06 12 34 56 78 أو +212 6 12 34 56 78.'",
    'ar phone message'
)

# Normalize Moroccan phone formats before placing an order.
replace_once(
    'async function submitOrder(){',
    "function normalizeMoroccanPhone(value){\n  let v=String(value||'').trim().replace(/[\\s().-]/g,'');\n  if(v.startsWith('00212')) v='0'+v.slice(5);\n  else if(v.startsWith('+212')) v='0'+v.slice(4);\n  else if(v.startsWith('212')) v='0'+v.slice(3);\n  v=v.replace(/\\D/g,'');\n  return /^0[5-7]\\d{8}$/.test(v) ? v : '';\n}\n\nasync function submitOrder(){",
    'phone normalizer'
)
replace_once(
    "  const phone = document.getElementById('ofPhone').value.trim();",
    "  let phone = document.getElementById('ofPhone').value.trim();",
    'mutable order phone'
)
replace_once(
    "  if(!name || !phone || !city || !address){ errEl.textContent = t.orderFillFields; return; }\n  if(!sb){ errEl.textContent = t.orderNoConnection; return; }",
    "  const phoneInput=document.getElementById('ofPhone');\n  phoneInput.removeAttribute('aria-invalid');\n  if(!name || !phone || !city || !address){ errEl.textContent = t.orderFillFields; return; }\n  const normalizedPhone=normalizeMoroccanPhone(phone);\n  if(!normalizedPhone){ phoneInput.setAttribute('aria-invalid','true'); errEl.textContent=t.orderInvalidPhone; phoneInput.focus(); return; }\n  phone=normalizedPhone;\n  phoneInput.value=phone;\n  if(!sb){ errEl.textContent = t.orderNoConnection; return; }",
    'phone validation'
)

# WhatsApp: build plain text then URL-encode it, so &, #, accents and Arabic cannot break the link.
old_wa = '''function buildWhatsAppMessage(fromContactForm){
  let msg = `Bonjour AXORIA! Je souhaite commander:%0A%0A`;
  if(CART.length){
    CART.forEach(c=>{ msg += `• ${c.name} x${c.qty} — ${fmtPrice(c.price*c.qty)}%0A`; });
    const total = CART.reduce((s,c)=>s+c.price*c.qty,0);
    msg += `%0ATotal: ${fmtPrice(total)}%0A`;
  }
  if(fromContactForm){
    const n = document.getElementById('cName').value, ph = document.getElementById('cPhone').value,
      em = document.getElementById('cEmail').value, sub = document.getElementById('cSubject').value, me = document.getElementById('cMessage').value;
    if(n||ph||em||sub||me){ msg += `%0A--- Infos contact ---%0ANom: ${n}%0ATél: ${ph}%0AEmail: ${em}%0ASujet: ${sub}%0AMessage: ${me}`; }
  }
  return `https://wa.me/212621575115?text=${msg}`;
}'''
new_wa = '''function buildWhatsAppMessage(fromContactForm){
  const lines=[];
  if(CART.length){
    lines.push('Bonjour AXORIA ! Je souhaite commander :','');
    CART.forEach(c=>lines.push(`• ${c.name} x${c.qty} — ${fmtPrice(c.price*c.qty)}`));
    const total=CART.reduce((sum,c)=>sum+c.price*c.qty,0);
    lines.push('',`Total : ${fmtPrice(total)}`);
  }else{
    lines.push('Bonjour AXORIA !');
  }
  if(fromContactForm){
    const n=document.getElementById('cName').value.trim(), ph=document.getElementById('cPhone').value.trim(),
      em=document.getElementById('cEmail').value.trim(), sub=document.getElementById('cSubject').value.trim(), me=document.getElementById('cMessage').value.trim();
    if(n||ph||em||sub||me){
      lines.push('','--- Infos contact ---');
      if(n) lines.push(`Nom : ${n}`);
      if(ph) lines.push(`Tél : ${ph}`);
      if(em) lines.push(`Email : ${em}`);
      if(sub) lines.push(`Sujet : ${sub}`);
      if(me) lines.push(`Message : ${me}`);
    }
  }
  return `https://wa.me/212621575115?text=${encodeURIComponent(lines.join('\\n'))}`;
}'''
replace_once(old_wa, new_wa, 'WhatsApp URL encoding')

# Safer new-tab opening for generated WhatsApp links.
replace_once(
    "  document.getElementById('waOrderBtn').onclick = ()=>{ window.open(buildWhatsAppMessage(true), '_blank'); };",
    "  document.getElementById('waOrderBtn').onclick = ()=>{ const w=window.open(buildWhatsAppMessage(true),'_blank','noopener,noreferrer'); if(w)w.opener=null; };",
    'contact WhatsApp open'
)
replace_once(
    "  document.getElementById('orderFormWaBtn').onclick = ()=>{ window.open(buildWhatsAppMessage(false), '_blank'); };",
    "  document.getElementById('orderFormWaBtn').onclick = ()=>{ const w=window.open(buildWhatsAppMessage(false),'_blank','noopener,noreferrer'); if(w)w.opener=null; };",
    'checkout WhatsApp open'
)

# Small invalid-field visual cue, added to the existing main style block.
replace_once(
    '</style>\n</head>',
    "input[aria-invalid='true']{border-color:#B42318!important;box-shadow:0 0 0 3px rgba(180,35,24,.12)!important;}\n</style>\n</head>",
    'invalid input style'
)

p.write_text(s, encoding='utf-8')
print('Phase 5 launch hardening patch applied.')
