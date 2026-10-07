from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """  const storedReviews = await storeGet('axoria_reviews', true);\n  if(storedReviews){ REVIEWS = storedReviews; } else { REVIEWS = DEFAULT_REVIEWS; }"""
new = """  let approvedReviews=[];\n  if(sb){\n    try{\n      const {data,error}=await sb.from('review_submissions').select('id,name,rating,comment,created_at').eq('status','approved').order('created_at',{ascending:false});\n      if(error) throw error;\n      approvedReviews=(Array.isArray(data)?data:[]).map(r=>({\n        submission_id:r.id,\n        name:r.name,\n        rating:Number(r.rating)||0,\n        comment:r.comment,\n        loc:'Maroc',\n        created_at:r.created_at\n      }));\n    }catch(e){\n      console.error('Approved reviews load failed',e);\n    }\n  }\n  REVIEWS = approvedReviews;"""

if old not in s:
    if new in s:
        print('reviews source patch already applied')
    else:
        raise SystemExit('Expected reviews source anchor not found')
else:
    s = s.replace(old, new, 1)

old_render = """      <p class=\"quote\">\"${r.comment}\"</p>\n      <div class=\"who\"><div class=\"avatar\">${r.name.charAt(0)}</div><div><div class=\"nm\">${r.name}</div><div class=\"loc\">${r.loc}</div></div></div>"""
new_render = """      <p class=\"quote\">\"${escapeReviewHtml(r.comment)}\"</p>\n      <div class=\"who\"><div class=\"avatar\">${escapeReviewHtml((r.name||'?').charAt(0))}</div><div><div class=\"nm\">${escapeReviewHtml(r.name)}</div><div class=\"loc\">${escapeReviewHtml(r.loc||'Maroc')}</div></div></div>"""

helper_anchor = "function renderReviews(){"
helper = "function escapeReviewHtml(v){return String(v??'').replace(/[&<>\\\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}[c]));}\n\n"
if 'function escapeReviewHtml' not in s:
    if helper_anchor not in s:
        raise SystemExit('renderReviews anchor not found')
    s = s.replace(helper_anchor, helper + helper_anchor, 1)

if old_render in s:
    s = s.replace(old_render, new_render, 1)
elif new_render not in s:
    raise SystemExit('Review render anchor not found')

p.write_text(s, encoding='utf-8')
print('Storefront review source reconciled with review_submissions.')
