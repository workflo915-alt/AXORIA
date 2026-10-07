from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'missing pattern: {label}')
    s = s.replace(old, new, 1)

# Brand/SEO positioning: wellness-first, no exaggerated body-shape claims.
replace_once(
    '<meta name="description" content="AXORIA — correcteur de posture et ceinture amincissante premium. Marque marocaine de bien-être. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta name="description" content="AXORIA — essentiels bien-être et confort au quotidien. Marque marocaine avec livraison partout au Maroc et paiement à la livraison.">',
    'meta description'
)
replace_once(
    '<meta property="og:description" content="Correcteur de posture et ceinture amincissante premium. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta property="og:description" content="Essentiels bien-être et confort au quotidien. Livraison partout au Maroc et paiement à la livraison.">',
    'og description'
)

# Honest proof: replace hard-coded volume/rating claims with service facts.
replace_once('statsLbl:["Clients satisfaits","Commandes livrées","Note moyenne clients","Villes livrées au Maroc"],',
             'statsLbl:["Paiement à la livraison","Délai indicatif","Support WhatsApp","Livraison nationale"],',
             'fr stats')
replace_once("statsLbl:['Happy customers','Orders delivered','Average customer rating','Cities delivered in Morocco'],",
             "statsLbl:['Cash on delivery','Typical delivery time','WhatsApp support','Nationwide delivery'],",
             'en stats')
replace_once("statsLbl:['عملاء راضون','طلبات تم توصيلها','متوسط تقييم العملاء','مدن مغربية تم التوصيل إليها'],",
             "statsLbl:['الدفع عند الاستلام','مدة التوصيل التقريبية','دعم واتساب','توصيل داخل المغرب'],",
             'ar stats')
replace_once("const statVals = ['5K+','12K+','4.8/5','20+'];",
             "const statVals = ['COD','24–72h','7j/7','Maroc'];",
             'stat values')

# Remove fabricated default testimonials: only approved real reviews should display.
s2, n = re.subn(r"const DEFAULT_REVIEWS = \[.*?\n\];", "const DEFAULT_REVIEWS = [];", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('missing pattern: default reviews')
s = s2

# Neutralize slimming claim in fallback/generated copy.
replace_once("'slimming waist belt':'Ceinture amincissante ajustable qui affine la taille, soutient le dos et accompagne vos séances de sport ou votre routine quotidienne.',",
             "'slimming waist belt':'Ceinture ajustable pensée pour offrir maintien et confort pendant vos activités ou votre routine quotidienne.',",
             'slimming generated description')
replace_once("'Ceinture Amincissante':'Pensée pour affiner la silhouette tout en soutenant le dos.',",
             "'Ceinture Amincissante':'Pensée pour apporter maintien, confort et ajustement au quotidien.',",
             'slimming category description')

# Product modal conversion reassurance without changing overall page structure.
replace_once(
    '.modal .mprice{font-family:var(--font-mono);font-weight:800;font-size:24px;margin-top:auto;}',
    '.modal .mprice{font-family:var(--font-mono);font-weight:800;font-size:24px;margin-top:auto;}\n.modal-trust{display:grid;gap:8px;padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:var(--bg-alt);font-size:12.5px;color:var(--text-soft);}\n.modal-trust span{display:flex;align-items:center;gap:8px;line-height:1.35;}\n.modal-trust span::before{content:\'✓\';color:var(--teal);font-weight:800;}',
    'modal trust css'
)
replace_once(
    '      <div class="mprice" id="modalPrice"></div>\n      <button class="btn btn-primary" id="modalAddBtn" style="width:100%;justify-content:center;"></button>',
    '      <div class="mprice" id="modalPrice"></div>\n      <div class="modal-trust" id="modalTrust"></div>\n      <button class="btn btn-primary" id="modalAddBtn" style="width:100%;justify-content:center;"></button>',
    'modal trust html'
)
replace_once(
    "  document.getElementById('modalAddBtn').textContent = t.modalAdd;",
    "  document.getElementById('modalAddBtn').textContent = t.modalAdd;\n  const modalTrust = document.getElementById('modalTrust');\n  if(modalTrust) modalTrust.innerHTML = t.trustBadges.map(x=>`<span>${x}</span>`).join('');",
    'modal trust text'
)

# Real-review empty state instead of fake testimonials.
replace_once(
    '.review-slider::-webkit-scrollbar-thumb{background:var(--line);border-radius:10px;}',
    '.review-slider::-webkit-scrollbar-thumb{background:var(--line);border-radius:10px;}\n.review-empty{width:100%;padding:26px;border:1px dashed var(--line);border-radius:18px;background:var(--surface);color:var(--text-soft);font-size:14px;line-height:1.6;}',
    'review empty css'
)
replace_once(
    "function renderReviews(){\n  const slider = document.getElementById('reviewSlider');\n  slider.innerHTML = REVIEWS.map(r=>`",
    "function renderReviews(){\n  const slider = document.getElementById('reviewSlider');\n  if(!REVIEWS.length){\n    const emptyMsg = currentLang==='ar' ? 'ستظهر هنا آراء العملاء بعد مراجعتها والموافقة عليها.' : currentLang==='en' ? 'Approved customer reviews will appear here.' : 'Les avis clients approuvés apparaîtront ici.';\n    slider.innerHTML = `<div class=\"review-empty\">${emptyMsg}</div>`;\n    return;\n  }\n  slider.innerHTML = REVIEWS.map(r=>`",
    'review empty state'
)

p.write_text(s, encoding='utf-8')
print('sales trust/conversion patch applied')
