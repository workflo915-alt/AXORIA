from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old=".sticky-buybar{position:fixed;left:0;right:0;bottom:0;z-index:390;background:var(--surface);border-top:1px solid var(--line);box-shadow:0 -8px 26px rgba(10,36,60,.14);padding:12px 16px;display:none;align-items:center;gap:14px;transform:translateY(100%);transition:transform .35s ease;}\n.sticky-buybar.show{display:flex;transform:translateY(0);}"
new=".sticky-buybar{position:fixed;left:0;right:0;bottom:0;z-index:390;background:var(--surface);border-top:1px solid var(--line);box-shadow:0 -8px 26px rgba(10,36,60,.14);padding:12px 16px;display:flex;align-items:center;gap:14px;opacity:0;visibility:hidden;pointer-events:none;transform:translateY(calc(100% + 18px)) scale(.985);transition:opacity .72s cubic-bezier(.2,.7,.2,1),transform .78s cubic-bezier(.2,.7,.2,1),visibility 0s linear .78s;will-change:opacity,transform;}\n.sticky-buybar.show{opacity:1;visibility:visible;pointer-events:auto;transform:translateY(0) scale(1);transition:opacity .72s cubic-bezier(.2,.7,.2,1),transform .78s cubic-bezier(.2,.7,.2,1),visibility 0s linear 0s;}"
if old not in s:
    raise RuntimeError('sticky buybar anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('sticky cart motion fixed')
