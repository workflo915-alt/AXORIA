from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

repls=[
(".hero-character{position:absolute;left:66%;bottom:-1.8%;width:clamp(176px,21vw,318px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 22px 24px rgba(0,0,0,.26));}",
 ".hero-character{position:absolute;left:64%;bottom:0;width:clamp(142px,16vw,240px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}"),
(".hero-character.is-main{opacity:1;width:clamp(238px,28vw,430px);z-index:22;}",
 ".hero-character.is-main{opacity:1;left:64%;bottom:0;width:clamp(210px,23vw,342px);z-index:22;}"),
(".hero-character.is-featured{width:clamp(226px,25.5vw,390px);z-index:21;}",
 ".hero-character.is-featured{left:64%;bottom:0;width:clamp(198px,21.5vw,318px);z-index:21;}"),
("@media (max-width:900px){.hero-character{left:60%;width:clamp(150px,29vw,250px);bottom:-1%;}.hero-character.is-main{width:clamp(210px,42vw,340px);}.hero-character.is-featured{width:clamp(195px,37vw,305px);}",
 "@media (max-width:900px){.hero-character{left:58%;width:clamp(118px,22vw,178px);bottom:1%;}.hero-character.is-main{left:57%;width:clamp(178px,32vw,260px);}.hero-character.is-featured{left:57%;width:clamp(166px,29vw,238px);}"),
("@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(138px,38vw,205px);bottom:4%;}.hero-character.is-main{width:clamp(210px,58vw,300px);bottom:2.5%;}.hero-character.is-featured{width:clamp(190px,52vw,270px);bottom:3%;}.hero::after{height:40px;}}",
 "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(96px,23vw,138px);bottom:4%;}.hero-character.is-main{left:50%;width:clamp(158px,38vw,214px);bottom:3%;}.hero-character.is-featured{left:50%;width:clamp(148px,35vw,200px);bottom:3.2%;}.hero::after{height:40px;}}"),
("const desktopTargets=[66,80,52,88,44,90,58,84,37,89,48,82,31,74];",
 "const desktopTargets=[64,73,55,80,49,83,58,79,44,81,51,76,39,71];"),
("const finalScale=[1.04,.98,.82,.80,.73,.72,.71,.70,.67,.66,.65,.64,.62,.62];",
 "const finalScale=[1.00,.98,.82,.80,.76,.75,.74,.73,.71,.70,.69,.68,.67,.66];"),
("const finalAlpha=[1,1,.94,.92,.90,.88,.86,.84,.82,.80,.78,.76,.74,.72];",
 "const finalAlpha=[1,1,.96,.94,.92,.90,.88,.86,.84,.82,.80,.78,.76,.74];"),
("const scrollP=clamp(-rect.top/(h*.42));",
 "const scrollP=clamp(-rect.top/(h*.18));"),
("const fit=clamp((rect.bottom-8)/(h*.92),.26,1);",
 "const fit=clamp((rect.bottom-8)/(h*.92),.72,1);"),
("const basePct=mobile?50:66;",
 "const basePct=mobile?50:64;"),
("const targetPct=mobile ? 50+(rawTarget-66)*.55 : rawTarget;",
 "const targetPct=mobile ? 50+(rawTarget-64)*.48 : rawTarget;"),
("const y=(1-local)*(mobile?20:28) - local*(mobile?0:4);",
 "const y=(1-local)*(mobile?12:16) + local*(mobile?1:2);")
]

changed=0
for old,new in repls:
    if old not in s:
        raise SystemExit('Expected current hero fragment missing: '+old[:100])
    s=s.replace(old,new,1)
    changed+=1

p.write_text(s,encoding='utf-8')
print(f'hero balance patch applied ({changed} replacements)')
