from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text


def sub_once(pattern, repl, s, label, flags=re.S):
    out, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 replacement, got {n}')
    return out

text = text.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
)

text = sub_once(
    r'/\* ====== CONNEXION BASE DE DONNÉES \(Supabase\) ======.*?=================================================== \*/',
    """/* ====== SUPABASE ======\n   The publishable key below is intentionally safe to expose in the browser.\n   Database security is enforced by Row Level Security (RLS): storefront visitors\n   can read catalog data and create orders, while administration requires an\n   authenticated Supabase session through admin.html.\n   ======================== */""",
    text,
    'supabase comment'
)

text = sub_once(
    r'/\* ---------- Admin ---------- \*/.*?(?=/\* ---- Modal shell \(Category Manager\) ---- \*/)',
    '.form-error{color:#D34747;font-size:12.5px;font-weight:600;min-height:16px;margin-bottom:6px;}\n\n',
    text,
    'legacy admin css'
)
text = sub_once(
    r'/\* ---- Category manager ---- \*/.*?(?=\.toast\{)',
    '',
    text,
    'legacy category css'
)

text = text.replace('class="pin-error" id="orderFormError"', 'class="form-error" id="orderFormError"')

text = sub_once(
    r'\n<button class="admin-tiny-btn"[\s\S]*?</div>\n\n<script src="https://cdn\.jsdelivr\.net/npm/@supabase/supabase-js@2/dist/umd/supabase\.js"></script>',
    '\n\n<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>',
    text,
    'legacy admin html'
)

text, n = re.subn(r"\n\s*addDishLabel:'[^']*', addDishSub:'[^']*',", '', text)
if n != 3:
    raise SystemExit(f'i18n admin labels: expected 3 removals, got {n}')

text = text.replace("function saveCategories(){ storeSet('axoria_categories', CATEGORIES, true); }\n", '')
text = text.replace('let adminUnlocked = false;\n', '')

text = sub_once(
    r"  if\(items\.length===0 && currentCategory!=='all'\)\{.*?    return;\n  \}",
    """  if(items.length===0 && currentCategory!=='all'){\n    grid.innerHTML = `<div class=\"cat-empty\" style=\"grid-column:1/-1;\">${t.comingSoon}</div>`;\n    return;\n  }""",
    text,
    'empty-category admin card'
)
text = sub_once(
    r"  \}\)\.join\(''\) \+ `\n    <button class=\"pcard pcard-add\" id=\"menuAddCard\"[\s\S]*?  document\.getElementById\('menuAddCard'\)\.onclick = \(\)=>openAdminGate\('quick'\);",
    "  }).join('');",
    text,
    'product-grid admin card'
)

text = sub_once(
    r'/\* ---------- Admin: Orders management ----------.*?(?=function renderReviews\(\)\{)',
    '',
    text,
    'legacy orders admin js'
)

text = sub_once(
    r"let ADMIN_PIN = 'Kaltommohamed1965';.*?(?=function spawnHeroParticles\(\)\{)",
    '',
    text,
    'legacy admin js'
)

text = text.replace("    await storeSet('axoria_products', PRODUCTS, true);\n", '')
text = text.replace(
    "  if(storedCats && storedCats.length){ CATEGORIES = storedCats; } else { await storeSet('axoria_categories', CATEGORIES, true); }",
    "  if(storedCats && storedCats.length){ CATEGORIES = storedCats; }"
)
text = text.replace(
    "  if(storedReviews){ REVIEWS = storedReviews; } else { REVIEWS = DEFAULT_REVIEWS; await storeSet('axoria_reviews', REVIEWS, true); }",
    "  if(storedReviews){ REVIEWS = storedReviews; } else { REVIEWS = DEFAULT_REVIEWS; }"
)
text = sub_once(
    r"  const storedPin = await storeGet\('axoria_admin_pin', true\);.*?  if\(storedRecovery\)\{ ADMIN_RECOVERY_ANSWER = storedRecovery; \} else \{ await storeSet\('axoria_admin_recovery', ADMIN_RECOVERY_ANSWER, true\); \}\n",
    '',
    text,
    'pin init'
)

review_handler = """  document.getElementById('submitReview').onclick = async ()=>{\n    const t = I18N[currentLang];\n    const name = document.getElementById('revName').value.trim();\n    const comment = document.getElementById('revComment').value.trim();\n    if(!name || !comment){ toast(t.fillFields); return; }\n    if(!sb){ toast(currentLang==='ar'?'تعذر إرسال الرأي الآن.':currentLang==='en'?'Unable to submit your review right now.':'Impossible d\\'envoyer votre avis pour le moment.'); return; }\n    const btn = document.getElementById('submitReview');\n    btn.disabled = true;\n    try{\n      const { error } = await sb.from('review_submissions').insert({\n        name, rating:selectedStars, comment, status:'pending'\n      });\n      if(error) throw error;\n      document.getElementById('revName').value='';\n      document.getElementById('revComment').value='';\n      selectedStars=5;\n      renderStarInput();\n      toast(currentLang==='ar'?'شكراً! سيتم نشر رأيك بعد المراجعة.':currentLang==='en'?'Thank you! Your review will be published after moderation.':'Merci ! Votre avis sera publié après vérification.');\n    }catch(e){\n      console.error('review submission failed', e);\n      toast(currentLang==='ar'?'تعذر إرسال الرأي الآن.':currentLang==='en'?'Unable to submit your review right now.':'Impossible d\\'envoyer votre avis pour le moment.');\n    }finally{\n      btn.disabled = false;\n    }\n  };"""
text = sub_once(
    r"  document\.getElementById\('submitReview'\)\.onclick = async \(\)=>\{.*?\n  \};(?=\n\n  document\.getElementById\('newsBtn'\))",
    review_handler,
    text,
    'review submit handler'
)

text = sub_once(
    r'\n  let clicks=0, clickTimer;.*?(?=\n\}\n\ntry\{ init\(\);)',
    '',
    text,
    'legacy admin event bindings'
)

for forbidden in [
    'Kaltommohamed1965',
    'ADMIN_RECOVERY_ANSWER',
    'recoverAnswer',
    'adminTinyBtn',
    'openAdminGate(',
    'adminPanel',
    'axoria_admin_pin',
    'axoria_admin_recovery',
]:
    if forbidden in text:
        raise SystemExit(f'cleanup incomplete: still found {forbidden!r}')

if text == original:
    print('No changes needed.')
else:
    path.write_text(text, encoding='utf-8')
    print(f'Cleaned {path}: {len(original)} -> {len(text)} bytes')
