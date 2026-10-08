from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

# Remove animated hero emblem markup.
old_markup='''    <div class="hero-logo-orbit" id="heroLogoOrbit">\n      <div class="hero-logo-ring"></div>\n      <div class="hero-logo-inner" id="heroLogoInner"></div>\n      <span class="hero-logo-dot d1"></span><span class="hero-logo-dot d2"></span><span class="hero-logo-dot d3"></span>\n    </div>\n'''
if old_markup in text:
    text=text.replace(old_markup,'',1)

# Remove hero emblem initialization.
old_init="\n  const heroLogoInner=document.getElementById('heroLogoInner'); if(heroLogoInner) heroLogoInner.innerHTML=badgeLogoSVG(220);"
text=text.replace(old_init,'',1)

# Remove all emblem-specific CSS blocks.
start=text.find('.hero-logo-orbit{')
end=text.find('[data-theme=\"light\"] .hero-logo-orbit{')
if start!=-1 and end!=-1:
    end2=text.find('}\n',end)
    if end2!=-1:
        text=text[:start]+text[end2+2:]

# Remove phone/tablet overrides referring to the emblem.
lines=[]
for line in text.splitlines():
    if any(tok in line for tok in ['.hero-logo-orbit{','.hero-logo-inner{','.hero-logo-ring{','.hero-logo-dot{']):
        continue
    lines.append(line)
text='\n'.join(lines)+'\n'

INDEX.write_text(text,encoding='utf-8')
print('Hero emblem removed.')
