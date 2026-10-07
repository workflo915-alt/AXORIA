from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def r1(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing pattern: {label}')
    s=s.replace(old,new,1)

# SEO/store metadata cleanup.
r1('  "priceRange": "149-179 MAD",\n','', 'schema price range')
r1('<meta property="og:title" content="AXORIA — Feel Better, Every Day">', '<meta property="og:title" content="AXORIA — Feel Better, Every Day">\n<meta property="og:type" content="website">\n<meta property="og:url" content="https://axoria.ma/">\n<link rel="canonical" href="https://axoria.ma/">', 'og/canonical')

# Mobile navigation panel, preserving desktop structure.
r1('.burger-btn{display:none;}\n@media (max-width:960px){.nav-links{display:none;}.clockbox{display:none;}.burger-btn{display:flex;}}',
   '.burger-btn{display:none;}\n.mobile-menu{display:none;position:fixed;left:14px;right:14px;top:78px;z-index:520;background:var(--surface);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow-lg);padding:10px;}\n.mobile-menu.open{display:block;}\n.mobile-menu a{display:block;padding:13px 14px;border-radius:12px;font-weight:700;font-size:14px;}\n.mobile-menu a:hover{background:var(--bg-alt);}\n@media (max-width:960px){.nav-links{display:none;}.clockbox{display:none;}.burger-btn{display:flex;}}\n@media (min-width:961px){.mobile-menu{display:none!important;}}',
   'mobile menu css')
r1('</header>\n\n<section class="hero" id="home">', '</header>\n<div class="mobile-menu" id="mobileMenu" aria-hidden="true"></div>\n\n<section class="hero" id="home">', 'mobile menu html')
r1("  document.getElementById('footQuick').innerHTML = t.nav.map((label,i)=>`<li><a href=\"${ids[i]}\">${label}</a></li>`).join('');",
   "  document.getElementById('footQuick').innerHTML = t.nav.map((label,i)=>`<li><a href=\"${ids[i]}\">${label}</a></li>`).join('');\n  const mobileMenu=document.getElementById('mobileMenu');\n  if(mobileMenu) mobileMenu.innerHTML=t.nav.map((label,i)=>`<a href=\"${ids[i]}\">${label}</a>`).join('');",
   'mobile menu render')
r1("  document.getElementById('burgerBtn').onclick = ()=>{ document.getElementById('menu').scrollIntoView({behavior:'smooth'}); };",
   "  document.getElementById('burgerBtn').onclick = ()=>{ const m=document.getElementById('mobileMenu'); if(!m)return; const open=!m.classList.contains('open'); m.classList.toggle('open',open); m.setAttribute('aria-hidden',open?'false':'true'); };\n  document.getElementById('mobileMenu')?.querySelectorAll('a').forEach(a=>a.onclick=()=>{ const m=document.getElementById('mobileMenu'); m?.classList.remove('open'); m?.setAttribute('aria-hidden','true'); });",
   'burger behavior')

# Footer links now point to real information pages.
r1("  document.getElementById('footInfo').innerHTML = t.footInfo.map(l=>`<li><a href=\"#\">${l}</a></li>`).join('');\n  document.getElementById('footBottomLinks').innerHTML = `<li><a href=\"#faq\">FAQ</a></li><li><a href=\"#\">${t.footInfo[1]}</a></li><li><a href=\"#\">${t.footInfo[2]}</a></li>`;",
   "  const infoLinks=['shipping-returns.html','privacy.html','terms.html'];\n  document.getElementById('footInfo').innerHTML = t.footInfo.map((l,i)=>`<li><a href=\"${infoLinks[i]}\">${l}</a></li>`).join('');\n  document.getElementById('footBottomLinks').innerHTML = `<li><a href=\"#faq\">FAQ</a></li><li><a href=\"privacy.html\">${t.footInfo[1]}</a></li><li><a href=\"terms.html\">${t.footInfo[2]}</a></li>`;",
   'footer links')

# Remove artificial wait and geolocation permission request.
r1("  setTimeout(()=>{ document.getElementById('loader').classList.add('hidden'); }, 1700);",
   "  requestAnimationFrame(()=>setTimeout(()=>{ document.getElementById('loader').classList.add('hidden'); }, 120));",
   'loader delay')
pat=r"let CLIENT_TZ = 'Africa/Casablanca';\nfunction initClientTimezone\(\)\{.*?\n\}\nfunction updateClock\(\)\{"
rep="let CLIENT_TZ = 'Africa/Casablanca';\nfunction initClientTimezone(){\n  try{ CLIENT_TZ = Intl.DateTimeFormat().resolvedOptions().timeZone || 'Africa/Casablanca'; }\n  catch(e){ CLIENT_TZ='Africa/Casablanca'; }\n}\nfunction updateClock(){"
s2,n=re.subn(pat,rep,s,count=1,flags=re.S)
if n!=1: raise SystemExit('missing pattern: timezone function')
s=s2

p.write_text(s,encoding='utf-8')

base_css='''<style>body{margin:0;font-family:Arial,sans-serif;background:#f6f8fb;color:#0b1524;line-height:1.7}.wrap{max-width:850px;margin:auto;padding:40px 20px}.card{background:#fff;border:1px solid #dce6f2;border-radius:20px;padding:28px;box-shadow:0 10px 30px rgba(10,36,60,.08)}h1{margin-top:0}.muted{color:#66758a}.back{display:inline-block;margin-bottom:18px;color:#0a4d9b;font-weight:700;text-decoration:none}h2{margin-top:28px;font-size:20px}a{color:#0a4d9b}</style>'''

def page(title, body):
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — AXORIA</title><meta name="robots" content="index,follow">{base_css}</head><body><div class="wrap"><a class="back" href="index.html">← Retour à AXORIA</a><div class="card"><h1>{title}</h1><p class="muted">Informations AXORIA — Maroc</p>{body}<h2>Contact</h2><p>Pour toute question, contactez AXORIA via WhatsApp au <a href="https://wa.me/212621575115">06 21 57 51 15</a>.</p></div></div></body></html>'''

Path('shipping-returns.html').write_text(page('Livraison & Retours','''<h2>Livraison</h2><p>AXORIA livre partout au Maroc. Le délai habituel annoncé est de 24 à 72 heures selon la ville et la disponibilité du transporteur. Ce délai reste indicatif.</p><h2>Paiement</h2><p>Le paiement principal est le paiement à la livraison.</p><h2>Réception et problème</h2><p>En cas de produit endommagé, incorrect ou présentant un défaut, contactez-nous dans les 48 heures suivant la réception avec votre référence de commande et, si possible, des photos du problème.</p><h2>Échange ou remboursement</h2><p>Après vérification du dossier, AXORIA peut proposer un échange ou un remboursement selon la situation. Les modalités exactes sont confirmées avec le client avant traitement.</p>'''),encoding='utf-8')
Path('privacy.html').write_text(page('Politique de confidentialité','''<p>AXORIA collecte uniquement les informations nécessaires au traitement des commandes, au support client et au fonctionnement du site, notamment le nom, le téléphone, la ville, l’adresse et les informations saisies volontairement dans les formulaires.</p><h2>Utilisation des données</h2><p>Ces données servent à préparer et suivre les commandes, contacter le client, assurer le support et mesurer les performances du site et des campagnes publicitaires.</p><h2>Services techniques</h2><p>Le site peut utiliser des services techniques et analytiques, notamment Supabase pour les données de commande et Meta Pixel / Conversions API pour la mesure publicitaire lorsque le tracking est activé.</p><h2>Conservation et demandes</h2><p>Les données sont conservées uniquement pendant la durée utile à ces finalités et aux obligations applicables. Vous pouvez contacter AXORIA pour demander l’accès, la correction ou la suppression de vos données lorsque cela est applicable.</p>'''),encoding='utf-8')
Path('terms.html').write_text(page('Conditions générales','''<h2>Commandes</h2><p>Une commande est considérée comme enregistrée après validation du formulaire en ligne. AXORIA peut contacter le client pour confirmer les informations avant expédition.</p><h2>Prix et disponibilité</h2><p>Les prix affichés sur le site sont indiqués en dirhams marocains. La disponibilité est vérifiée au moment de la commande et peut évoluer selon le stock.</p><h2>Paiement</h2><p>Sauf indication contraire, le règlement s’effectue à la livraison.</p><h2>Livraison</h2><p>Les délais affichés sont indicatifs et peuvent varier selon la ville, le transporteur ou des circonstances indépendantes d’AXORIA.</p><h2>Utilisation des produits</h2><p>Les informations présentées sur le site sont générales. Le client doit respecter les indications d’utilisation du produit et arrêter son utilisation en cas d’inconfort important.</p><h2>Service client</h2><p>Pour toute question sur une commande, un produit, un échange ou un retour, le service client AXORIA est disponible via WhatsApp.</p>'''),encoding='utf-8')
print('stage3 sales readiness patch applied')
