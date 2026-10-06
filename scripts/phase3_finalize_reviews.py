from pathlib import Path

path = Path('admin.html')
text = path.read_text(encoding='utf-8')

if 'data-review-delete=' in text and "sb.rpc('delete_review'" in text:
    print('Phase 3 final review actions already applied.')
    raise SystemExit(0)

buttons_old = '''      <button class="btn primary" data-review-approve="${esc(r.id)}" ${r.status==='approved'?'disabled':''}>Approuver</button>\n      <button class="btn danger" data-review-reject="${esc(r.id)}" ${r.status==='rejected'?'disabled':''}>Refuser</button>'''
buttons_new = '''      <button class="btn primary" data-review-approve="${esc(r.id)}" ${r.status==='approved'?'disabled':''}>Approuver</button>\n      <button class="btn danger" data-review-reject="${esc(r.id)}" ${r.status==='rejected'?'disabled':''}>Refuser</button>\n      <button class="btn ghost" style="color:var(--danger)" data-review-delete="${esc(r.id)}">Supprimer</button>'''
if buttons_old not in text:
    raise SystemExit('review action buttons marker not found')
text = text.replace(buttons_old, buttons_new, 1)

handlers_old = '''  body.querySelectorAll('[data-review-approve]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewApprove,'approve',b));\n  body.querySelectorAll('[data-review-reject]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewReject,'reject',b));\n}\nasync function moderateReview(id,action,btn){'''
handlers_new = '''  body.querySelectorAll('[data-review-approve]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewApprove,'approve',b));\n  body.querySelectorAll('[data-review-reject]').forEach(b=>b.onclick=()=>moderateReview(b.dataset.reviewReject,'reject',b));\n  body.querySelectorAll('[data-review-delete]').forEach(b=>b.onclick=()=>deleteReview(b.dataset.reviewDelete,b));\n}\nasync function deleteReview(id,btn){\n  if(!confirm('Supprimer définitivement cet avis ?'))return;\n  btn.disabled=true;\n  try{\n    const {error}=await sb.rpc('delete_review',{p_review_id:id});\n    if(error)throw error;\n    await loadReviewSubmissions();\n    toast('Avis supprimé du tableau et du site');\n  }catch(e){\n    console.error(e);\n    toast('Échec de suppression de l’avis');\n    await loadReviewSubmissions();\n  }\n}\nasync function moderateReview(id,action,btn){'''
if handlers_old not in text:
    raise SystemExit('review handlers marker not found')
text = text.replace(handlers_old, handlers_new, 1)

checks = [
    'data-review-delete=',
    "sb.rpc('delete_review'",
    "toast('Avis supprimé du tableau et du site')",
]
for marker in checks:
    if marker not in text:
        raise SystemExit(f'missing generated marker: {marker}')

path.write_text(text, encoding='utf-8')
print('Phase 3 final review actions patch applied.')
