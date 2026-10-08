from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="document.getElementById('footQuick').innerHTML = t.nav.map((label,i)=>`<li><a href=\"${ids[i]}\">${label}</a></li>`).join('');"
new="const guidesLabel=currentLang==='ar'?'دليل AXORIA':currentLang==='en'?'Guides':'Guides';\n  document.getElementById('footQuick').innerHTML = t.nav.map((label,i)=>`<li><a href=\"${ids[i]}\">${label}</a></li>`).join('') + `<li><a href=\"guides.html\">${guidesLabel}</a></li>`;"
if old not in s: raise RuntimeError('footQuick anchor not found')
s=s.replace(old,new,1)
old2="document.getElementById('footBottomLinks').innerHTML = `<li><a href=\"#faq\">FAQ</a></li><li><a href=\"privacy.html\">${t.footInfo[1]}</a></li><li><a href=\"terms.html\">${t.footInfo[2]}</a></li>`;"
new2="document.getElementById('footBottomLinks').innerHTML = `<li><a href=\"guides.html\">${guidesLabel}</a></li><li><a href=\"#faq\">FAQ</a></li><li><a href=\"privacy.html\">${t.footInfo[1]}</a></li><li><a href=\"terms.html\">${t.footInfo[2]}</a></li>`;"
if old2 not in s: raise RuntimeError('footBottomLinks anchor not found')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
print('home guide links added')
