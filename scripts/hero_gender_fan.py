from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css_repls = [
    (".hero-character{position:absolute;left:64%;bottom:0;width:clamp(168px,19vw,286px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}",
     ".hero-character{position:absolute;left:64%;bottom:0;width:clamp(182px,20.5vw,312px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}"),
    (".hero-character.is-main{opacity:1;left:63%;bottom:0;width:clamp(248px,29vw,412px);z-index:24;}",
     ".hero-character.is-main{opacity:1;left:62.5%;bottom:0;width:clamp(252px,29.5vw,420px);z-index:24;}"),
    (".hero-character.is-featured{opacity:1;left:72%;bottom:0;width:clamp(232px,27vw,392px);z-index:23;}",
     ".hero-character.is-featured{opacity:1;left:71%;bottom:0;width:clamp(244px,28.2vw,404px);z-index:23;}"),
    ("@media (max-width:900px){.hero-character{left:58%;width:clamp(132px,25vw,196px);bottom:1%;}.hero-character.is-main{left:47%;width:clamp(196px,38vw,286px);}.hero-character.is-featured{left:59%;width:clamp(184px,35vw,270px);}",
     "@media (max-width:900px){.hero-character{left:58%;width:clamp(144px,27vw,214px);bottom:1%;}.hero-character.is-main{left:47%;width:clamp(204px,39vw,294px);}.hero-character.is-featured{left:59%;width:clamp(196px,37vw,282px);}"),
    ("@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(108px,27vw,152px);bottom:4%;}.hero-character.is-main{left:45%;width:clamp(176px,44vw,236px);bottom:3%;}.hero-character.is-featured{left:58%;width:clamp(166px,41vw,224px);bottom:3%;}.hero::after{height:40px;}}",
     "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(118px,29vw,164px);bottom:4%;}.hero-character.is-main{left:45%;width:clamp(184px,46vw,246px);bottom:3%;}.hero-character.is-featured{left:58%;width:clamp(176px,43vw,236px);bottom:3%;}.hero::after{height:40px;}}")
]
for old, new in css_repls:
    if old not in s:
        raise SystemExit('Expected current hero CSS fragment missing: ' + old[:120])
    s = s.replace(old, new, 1)

old_core = """  // Sprite order alternates man / woman by lifestyle role.
  // Keep the athlete duo visible from the start, then fan men left and women right.
  const desktopTargets=[63,72,57,78,52,81,47,84,42,86,37,88,32,90];
  const mobileTargets=[45,58,40,64,36,68,32,72,28,76,24,80,20,82];
  const finalScale=[1.08,1.04,.92,.92,.90,.90,.88,.88,.86,.86,.84,.84,.82,.82];
  const finalAlpha=[1,1,.97,.97,.95,.95,.93,.93,.91,.91,.89,.89,.87,.87];
"""
new_core = """  // Sprite order alternates man / woman by lifestyle role.
  // Keep the athlete duo visible from the start, then fan men left and women right.
  const desktopTargets=[62.5,71,55,78,49,82,43,86,37,89,32,92,27,95];
  const mobileTargets=[45,58,39,64,34,69,30,74,26,78,22,82,18,86];
  const finalScale=[1.06,1.03,.98,.98,.96,.96,.94,.94,.92,.92,.90,.90,.88,.88];
  const finalAlpha=[1,1,.98,.98,.97,.97,.96,.96,.95,.95,.94,.94,.92,.92];
"""
if old_core not in s:
    raise SystemExit('Expected current hero arrays missing')
s = s.replace(old_core, new_core, 1)

repls = [
    ("const scrollP=clamp(-rect.top/(h*.30));", "const scrollP=clamp(-rect.top/(h*.34));"),
    ("const fit=clamp((rect.bottom-8)/(h*.92),.80,1);", "const fit=clamp((rect.bottom+20)/(h*.88),.88,1);"),
    ("const manAnchor=mobile?45:63;", "const manAnchor=mobile?45:62.5;"),
    ("const womanAnchor=mobile?58:72;", "const womanAnchor=mobile?58:71;"),
    ("interaction=Math.max(interaction,.42);", "interaction=Math.max(interaction,.55);")
]
for old, new in repls:
    if old not in s:
        raise SystemExit('Expected current hero script fragment missing: ' + old)
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('hero stronger gender fan patch applied')
