from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

anchor = '<meta property="og:description" content="Essentiels bien-être et confort au quotidien. Livraison partout au Maroc et paiement à la livraison.">'
if anchor not in s:
    raise SystemExit('SEO head anchor not found')

extras = []
if 'name="robots"' not in s:
    extras.append('<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">')
if 'property="og:site_name"' not in s:
    extras.append('<meta property="og:site_name" content="AXORIA">')
if 'property="og:locale"' not in s:
    extras.append('<meta property="og:locale" content="fr_MA">')
if 'name="twitter:card"' not in s:
    extras.append('<meta name="twitter:card" content="summary">')
if 'name="twitter:title"' not in s:
    extras.append('<meta name="twitter:title" content="AXORIA — Feel Better, Every Day">')
if 'name="twitter:description"' not in s:
    extras.append('<meta name="twitter:description" content="Essentiels bien-être et confort au quotidien. Livraison partout au Maroc et paiement à la livraison.">')
if 'name="theme-color"' not in s:
    extras.append('<meta name="theme-color" content="#0A1220">')

if extras:
    s = s.replace(anchor, anchor + '\n' + '\n'.join(extras), 1)

p.write_text(s, encoding='utf-8')
print('AXORIA pre-launch SEO head polished')
