from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker=".trust-badges span svg{width:16px;height:16px;color:var(--teal);flex-shrink:0;}"
patch='''\n/* Light theme: keep bottom hero trust copy readable over the white blend */\n[data-theme="light"] .trust-badges span{\n  color:#0B1524;\n  text-shadow:0 1px 10px rgba(255,255,255,.96),0 1px 2px rgba(255,255,255,.92);\n}\n[data-theme="light"] .trust-badges span svg{color:#073869;}\n'''
if patch.strip() not in s:
    if marker not in s:
        raise SystemExit('trust badges CSS marker not found')
    s=s.replace(marker, marker+patch, 1)
p.write_text(s,encoding='utf-8')
print('Light hero trust badges contrast fixed')
