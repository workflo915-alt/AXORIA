from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

# 1) Move the existing character stage out of the hero and into a bridge section.
pat=re.compile(r'    <div class="hero-stage" id="heroStage">(?P<body>.*?)    </div>\n  </div>\n  <div class="hero-overlay">',re.S)
m=pat.search(text)
if not m:
    raise RuntimeError('hero stage anchor not found')
body=m.group('body')
hero_logo='''    <div class="hero-logo-orbit" id="heroLogoOrbit">\n      <div class="hero-logo-ring"></div>\n      <div class="hero-logo-inner" id="heroLogoInner"></div>\n      <span class="hero-logo-dot d1"></span><span class="hero-logo-dot d2"></span><span class="hero-logo-dot d3"></span>\n    </div>\n  </div>\n  <div class="hero-overlay">'''
text=pat.sub(hero_logo,text,count=1)

menu_anchor='''</section>\n\n<section class="section menu-section" id="menu">'''
bridge=f'''</section>\n\n<section class="character-bridge" id="characterBridge" aria-hidden="true">\n  <div class="bridge-glow"></div>\n  <div class="hero-stage character-stage" id="heroStage">{body}    </div>\n</section>\n\n<section class="section menu-section" id="menu">'''
if menu_anchor not in text:
    raise RuntimeError('menu anchor not found')
text=text.replace(menu_anchor,bridge,1)

# 2) Final visual CSS overrides.
css_anchor="input[aria-invalid='true']{border-color:#B42318!important;box-shadow:0 0 0 3px rgba(180,35,24,.12)!important;}"
css='''/* ---------- Final visual polish ---------- */
.hero-logo-orbit{position:absolute;right:7%;top:50%;width:clamp(190px,24vw,330px);aspect-ratio:1;transform:translateY(-50%);display:grid;place-items:center;opacity:.94;filter:drop-shadow(0 24px 42px rgba(0,0,0,.22));}
.hero-logo-inner{width:62%;height:62%;display:grid;place-items:center;animation:heroLogoFloat 5.8s ease-in-out infinite;will-change:transform;}
.hero-logo-inner svg{width:100%;height:100%;filter:drop-shadow(0 12px 28px rgba(10,77,155,.22));}
.hero-logo-ring{position:absolute;inset:7%;border-radius:50%;border:1px solid color-mix(in srgb,var(--teal) 38%,transparent);box-shadow:0 0 0 18px color-mix(in srgb,var(--teal) 5%,transparent),inset 0 0 50px color-mix(in srgb,var(--teal) 8%,transparent);animation:heroRingSpin 18s linear infinite;}
.hero-logo-ring::before,.hero-logo-ring::after{content:'';position:absolute;border-radius:50%;inset:14%;border:1px dashed color-mix(in srgb,var(--coral) 38%,transparent);}
.hero-logo-ring::after{inset:28%;border-style:solid;border-color:color-mix(in srgb,var(--sky) 26%,transparent);}
.hero-logo-dot{position:absolute;width:8px;height:8px;border-radius:50%;background:var(--coral);box-shadow:0 0 16px color-mix(in srgb,var(--coral) 75%,transparent);}
.hero-logo-dot.d1{top:10%;right:27%;}.hero-logo-dot.d2{bottom:18%;left:11%;width:6px;height:6px;background:var(--teal);}.hero-logo-dot.d3{top:37%;left:4%;width:5px;height:5px;background:var(--sky);}
@keyframes heroLogoFloat{0%,100%{transform:translate3d(0,-8px,0) rotate(-2deg)}50%{transform:translate3d(0,10px,0) rotate(2deg)}}
@keyframes heroRingSpin{to{transform:rotate(360deg)}}
[data-theme="light"] .hero-logo-orbit{filter:drop-shadow(0 24px 38px rgba(35,54,76,.14));}

.character-bridge{position:relative;height:clamp(300px,35vw,430px);overflow:hidden;background:linear-gradient(180deg,var(--bg-alt) 0%,var(--bg) 86%);isolation:isolate;border-bottom:1px solid var(--line);}
.character-bridge::before{content:'';position:absolute;left:50%;bottom:7%;width:min(1000px,88vw);height:72px;transform:translateX(-50%);border-radius:50%;background:radial-gradient(ellipse,rgba(10,36,60,.16) 0%,rgba(10,36,60,.06) 42%,transparent 73%);filter:blur(2px);}
[data-theme="dark"] .character-bridge::before{background:radial-gradient(ellipse,rgba(0,0,0,.42) 0%,rgba(0,0,0,.14) 42%,transparent 73%);}
.bridge-glow{position:absolute;inset:0;background:radial-gradient(circle at 50% 55%,color-mix(in srgb,var(--teal) 10%,transparent),transparent 43%);pointer-events:none;}
.character-stage{position:absolute;inset:0;z-index:2;pointer-events:none;transform:translateZ(0);}
.character-stage::after{display:none!important;}
.character-bridge .hero-character{bottom:2%!important;width:clamp(104px,11vw,158px)!important;filter:drop-shadow(0 15px 18px rgba(0,0,0,.18));}
.character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(118px,12.5vw,178px)!important;bottom:1.2%!important;}
.character-bridge + .menu-section{padding-top:76px;}

.reveal{will-change:opacity,transform;}
.floatbtns{transition:bottom .28s ease;}
body.cart-bar-visible .floatbtns{bottom:92px;}

@media(max-width:900px){
  .hero-logo-orbit{right:50%;top:31%;width:clamp(150px,35vw,230px);transform:translateX(50%) translateY(-50%);opacity:.72;}
  .hero-content{padding-bottom:70px;}
  .character-bridge{height:340px;}
  .character-bridge .hero-character{width:clamp(92px,18vw,128px)!important;}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(104px,20vw,144px)!important;}
  .character-bridge + .menu-section{padding-top:64px;}
}
@media(max-width:600px){
  .hero{min-height:680px;}
  .hero-logo-orbit{top:27%;width:154px;opacity:.56;}
  .hero-content{padding:0 18px 54px;}
  .character-bridge{height:286px;}
  .character-bridge .hero-character{width:88px!important;}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:102px!important;}
  .character-bridge .hero-character:nth-child(n+9){display:none;}
  .character-bridge + .menu-section{padding-top:54px;}
  body.cart-bar-visible .floatbtns{bottom:104px;right:14px;}
  .floatbtns{right:14px;bottom:16px;}
  .fab{width:52px;height:52px;}
}
'''
if css_anchor not in text:
    raise RuntimeError('css anchor not found')
text=text.replace(css_anchor,css+'\n'+css_anchor,1)

# 3) Put the real AXORIA badge in the animated hero emblem.
loader_anchor="document.getElementById('loaderLogo').innerHTML = badgeLogoSVG(120);"
loader_new=loader_anchor+"\n  const heroLogoInner=document.getElementById('heroLogoInner'); if(heroLogoInner) heroLogoInner.innerHTML=badgeLogoSVG(220);"
if loader_anchor not in text:
    raise RuntimeError('loader anchor not found')
text=text.replace(loader_anchor,loader_new,1)

# 4) Reveal animations replay whenever a section re-enters the viewport.
old_io="const io = new IntersectionObserver((entries)=>{ entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); } }); }, {threshold:.12});"
new_io="const io = new IntersectionObserver((entries)=>{ entries.forEach(e=>{ e.target.classList.toggle('in',e.isIntersecting); }); }, {threshold:.14,rootMargin:'0px 0px -6% 0px'});"
if old_io not in text:
    raise RuntimeError('reveal observer anchor not found')
text=text.replace(old_io,new_io,1)

# 5) Softer hero fade + mobile WhatsApp safe spacing when sticky cart is visible.
old_scroll="""    const hc = document.querySelector('.hero-content');\n    if(hc){ hc.style.opacity = Math.max(1 - y/500, 0); }\n    const bar = document.getElementById('stickyBuybar');\n    if(bar && CART.reduce((s,c)=>s+c.qty,0)>0){ bar.classList.toggle('show', y>380); }"""
new_scroll="""    const hc = document.querySelector('.hero-content');\n    const heroEl=document.getElementById('home');\n    if(hc&&heroEl){ const p=Math.min(Math.max(y/Math.max(heroEl.offsetHeight*.82,1),0),1); hc.style.opacity=String(1-p*.68); }\n    const bar = document.getElementById('stickyBuybar');\n    const cartBarVisible=!!(bar && CART.reduce((s,c)=>s+c.qty,0)>0 && y>380);\n    if(bar) bar.classList.toggle('show',cartBarVisible);\n    document.body.classList.toggle('cart-bar-visible',cartBarVisible);"""
if old_scroll not in text:
    raise RuntimeError('scroll anchor not found')
text=text.replace(old_scroll,new_scroll,1)

# 6) Keep the same fan behavior but spread the characters across the new bridge.
text=text.replace("const desktopTargets=[62.5,71,55,78,49,82,43,86,37,89,32,92,27,95];","const desktopTargets=[46,54,39,61,32,68,25,75,18,82,11,89,5,95];",1)
text=text.replace("const mobileTargets=[45,58,39,64,34,69,30,74,26,78,22,82,18,86];","const mobileTargets=[44,56,32,68,20,80,8,92,18,82,26,74,34,66];",1)
text=text.replace("const manAnchor=mobile?45:62.5;\n    const womanAnchor=mobile?58:71;","const manAnchor=mobile?44:46;\n    const womanAnchor=mobile?56:54;",1)

INDEX.write_text(text,encoding='utf-8')
print('Final visual polish applied.')
