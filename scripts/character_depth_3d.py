from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_css=".character-stage{position:absolute;inset:0;z-index:2;pointer-events:none;transform:translateZ(0);}"
new_css=".character-stage{position:absolute;inset:0;z-index:2;pointer-events:none;perspective:900px;perspective-origin:50% 58%;transform-style:preserve-3d;}"
if old_css not in s:
    raise RuntimeError('character-stage css anchor not found')
s=s.replace(old_css,new_css,1)

old="""      const y=isAthlete ? 0 : (1-local)*(mobile?5:14)+local*(mobile?1:2);\n      const scale=(finalScale[i] ?? .84)*fit;\n      const opacity=isAthlete ? 1 : (finalAlpha[i] ?? .88)*local;\n\n      el.style.left=`${xPct.toFixed(2)}%`;\n      el.style.opacity=opacity.toFixed(3);\n      el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;"""
new="""      const y=isAthlete ? 0 : (1-local)*(mobile?5:14)+local*(mobile?1:2);\n      const targetScale=(finalScale[i] ?? .84)*fit;\n      const depthStart=mobile?.80:.74;\n      const scale=isAthlete ? targetScale : targetScale*(depthStart+(1-depthStart)*local);\n      const z=isAthlete ? 0 : -(mobile?82:118)*(1-local);\n      const opacity=isAthlete ? 1 : (finalAlpha[i] ?? .88)*(.20+.80*local);\n\n      el.style.left=`${xPct.toFixed(2)}%`;\n      el.style.opacity=opacity.toFixed(3);\n      el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,${z.toFixed(1)}px) scale(${scale.toFixed(3)})`;"""
if old not in s:
    raise RuntimeError('character transform anchor not found')
s=s.replace(old,new,1)

old2="const ease=t=>1-Math.pow(1-t,3);"
new2="const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;"
if old2 not in s:
    raise RuntimeError('ease anchor not found')
s=s.replace(old2,new2,1)

p.write_text(s,encoding='utf-8')
print('3D character depth polish applied')
