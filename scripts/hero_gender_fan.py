from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css_repls = [
    (".hero-character{position:absolute;left:64%;bottom:0;width:clamp(142px,16vw,240px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}",
     ".hero-character{position:absolute;left:64%;bottom:0;width:clamp(168px,19vw,286px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}"),
    (".hero-character.is-main{opacity:1;left:64%;bottom:0;width:clamp(210px,23vw,342px);z-index:22;}",
     ".hero-character.is-main{opacity:1;left:63%;bottom:0;width:clamp(248px,29vw,412px);z-index:24;}"),
    (".hero-character.is-featured{left:64%;bottom:0;width:clamp(198px,21.5vw,318px);z-index:21;}",
     ".hero-character.is-featured{opacity:1;left:72%;bottom:0;width:clamp(232px,27vw,392px);z-index:23;}"),
    ("@media (max-width:900px){.hero-character{left:58%;width:clamp(118px,22vw,178px);bottom:1%;}.hero-character.is-main{left:57%;width:clamp(178px,32vw,260px);}.hero-character.is-featured{left:57%;width:clamp(166px,29vw,238px);}",
     "@media (max-width:900px){.hero-character{left:58%;width:clamp(132px,25vw,196px);bottom:1%;}.hero-character.is-main{left:47%;width:clamp(196px,38vw,286px);}.hero-character.is-featured{left:59%;width:clamp(184px,35vw,270px);}"),
    ("@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(96px,23vw,138px);bottom:4%;}.hero-character.is-main{left:50%;width:clamp(158px,38vw,214px);bottom:3%;}.hero-character.is-featured{left:50%;width:clamp(148px,35vw,200px);bottom:3.2%;}.hero::after{height:40px;}}",
     "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(108px,27vw,152px);bottom:4%;}.hero-character.is-main{left:45%;width:clamp(176px,44vw,236px);bottom:3%;}.hero-character.is-featured{left:58%;width:clamp(166px,41vw,224px);bottom:3%;}.hero::after{height:40px;}}")
]
for old, new in css_repls:
    if old not in s:
        raise SystemExit('Expected current hero CSS fragment missing: ' + old[:110])
    s = s.replace(old, new, 1)

old_core = """  const desktopTargets=[64,73,55,80,49,83,58,79,44,81,51,76,39,71];
  const finalScale=[1.00,.98,.82,.80,.76,.75,.74,.73,.71,.70,.69,.68,.67,.66];
  const finalAlpha=[1,1,.96,.94,.92,.90,.88,.86,.84,.82,.80,.78,.76,.74];
"""
new_core = """  // Sprite order alternates man / woman by lifestyle role.
  // Keep the athlete duo visible from the start, then fan men left and women right.
  const desktopTargets=[63,72,57,78,52,81,47,84,42,86,37,88,32,90];
  const mobileTargets=[45,58,40,64,36,68,32,72,28,76,24,80,20,82];
  const finalScale=[1.08,1.04,.92,.92,.90,.90,.88,.88,.86,.86,.84,.84,.82,.82];
  const finalAlpha=[1,1,.97,.97,.95,.95,.93,.93,.91,.91,.89,.89,.87,.87];
"""
if old_core not in s:
    raise SystemExit('Expected current hero arrays missing')
s = s.replace(old_core, new_core, 1)

repls = [
    ("const scrollP=clamp(-rect.top/(h*.18));", "const scrollP=clamp(-rect.top/(h*.30));"),
    ("const fit=clamp((rect.bottom-8)/(h*.92),.72,1);", "const fit=clamp((rect.bottom-8)/(h*.92),.80,1);"),
    ("const basePct=mobile?50:64;", "const manAnchor=mobile?45:63;\n    const womanAnchor=mobile?58:72;"),
    ("interaction=Math.max(interaction,.30);", "interaction=Math.max(interaction,.42);")
]
for old, new in repls:
    if old not in s:
        raise SystemExit('Expected current hero script fragment missing: ' + old)
    s = s.replace(old, new, 1)

old_loop = """    chars.forEach((el,i)=>{
      const delay=Number(el.dataset.delay||0);
      const local=i===0?1:ease(clamp((p-delay)/Math.max(.44-delay,.10)));
      const rawTarget=desktopTargets[i] ?? basePct;
      const targetPct=mobile ? 50+(rawTarget-64)*.48 : rawTarget;
      const xPct=basePct+(targetPct-basePct)*local;
      const y=(1-local)*(mobile?12:16) + local*(mobile?1:2);
      const scale=(finalScale[i] ?? .66)*fit;
      const opacity=i===0 ? 1 : (finalAlpha[i] ?? .78)*local;

      el.style.left=`${xPct.toFixed(2)}%`;
      el.style.opacity=opacity.toFixed(3);
      el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
    });
"""
new_loop = """    chars.forEach((el,i)=>{
      const isAthlete=i<2;
      const isMale=i%2===0;
      const delay=Number(el.dataset.delay||0);
      const local=isAthlete ? 1 : ease(clamp((p-delay)/Math.max(.48-delay,.12)));
      const anchorPct=isMale ? manAnchor : womanAnchor;
      const targetPct=mobile ? (mobileTargets[i] ?? anchorPct) : (desktopTargets[i] ?? anchorPct);
      const xPct=isAthlete ? targetPct : anchorPct+(targetPct-anchorPct)*local;
      const y=isAthlete ? 0 : (1-local)*(mobile?10:14)+local*(mobile?1:2);
      const scale=(finalScale[i] ?? .84)*fit;
      const opacity=isAthlete ? 1 : (finalAlpha[i] ?? .88)*local;

      el.style.left=`${xPct.toFixed(2)}%`;
      el.style.opacity=opacity.toFixed(3);
      el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
    });
"""
if old_loop not in s:
    raise SystemExit('Expected current hero animation loop missing')
s = s.replace(old_loop, new_loop, 1)

p.write_text(s, encoding='utf-8')
print('hero gender fan patch applied')
