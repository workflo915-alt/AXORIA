from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

def rep(old,new,label):
    global text
    if old in text:
        text=text.replace(old,new,1); return
    if new in text:
        print('[skip]',label); return
    raise RuntimeError('anchor not found: '+label)

# Late CSS overrides keep existing theme intact while changing composition.
css=r'''
/* ---------- Final polish: scroll replay + character bridge ---------- */
.character-bridge{position:relative;min-height:420px;background:linear-gradient(180deg,var(--bg-alt) 0%,var(--bg) 100%);overflow:hidden;border-top:1px solid color-mix(in srgb,var(--line) 70%,transparent);border-bottom:1px solid color-mix(in srgb,var(--line) 70%,transparent);isolation:isolate;}
.character-bridge::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 65%,color-mix(in srgb,var(--teal) 11%,transparent),transparent 46%);pointer-events:none;}
.character-bridge .bridge-label{position:absolute;left:50%;top:26px;transform:translateX(-50%);font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--text-soft);opacity:.72;white-space:nowrap;z-index:3;}
.character-bridge .hero-stage{position:absolute;inset:48px 0 0;z-index:2;overflow:visible;pointer-events:none;}
.character-bridge .hero-stage::after{left:50%;bottom:6%;width:min(980px,84vw);height:64px;transform:translateX(-50%);opacity:.5;}
.character-bridge .hero-character{bottom:0;width:clamp(122px,12vw,178px);opacity:0;filter:drop-shadow(0 16px 18px rgba(0,0,0,.18));}
.character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(138px,13.5vw,194px);bottom:0;}
[data-theme="light"] .character-bridge .hero-character{filter:drop-shadow(0 15px 18px rgba(35,54,76,.13));}
.hero-orbit-mark{position:absolute;right:clamp(18px,4vw,64px);top:18%;z-index:2;width:clamp(92px,11vw,160px);height:clamp(92px,11vw,160px);display:flex;align-items:center;justify-content:center;opacity:.18;pointer-events:none;will-change:transform,opacity;filter:drop-shadow(0 18px 30px rgba(0,0,0,.12));}
.hero-orbit-mark svg{width:100%;height:100%;}
[data-theme="light"] .hero-orbit-mark{opacity:.12;}
.reveal{will-change:transform,opacity;}
@media(max-width:700px){
  .character-bridge{min-height:360px;}
  .character-bridge .bridge-label{top:18px;font-size:9px;}
  .character-bridge .hero-stage{inset:38px 0 0;}
  .character-bridge .hero-character{width:clamp(88px,24vw,118px);}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(96px,26vw,126px);}
  .hero-orbit-mark{right:-18px;top:12%;width:112px;height:112px;opacity:.12;}
}
@media(max-width:420px){
  .character-bridge{min-height:330px;}
  .character-bridge .hero-stage{inset:42px 0 0;}
  .hero-orbit-mark{width:92px;height:92px;right:-16px;top:14%;}
}
@media(prefers-reduced-motion:reduce){.hero-orbit-mark{transform:none!important}.character-bridge .hero-character{transition:none!important}}
'''
rep('</style>',css+'\n</style>','append polish css')

# Add subtle moving AXORIA mark inside hero.
rep('  <div class="hero-overlay"></div>','  <div class="hero-orbit-mark" id="heroOrbitMark" aria-hidden="true"></div>\n  <div class="hero-overlay"></div>','hero orbit mark')

# Add a dedicated character zone between hero and product selection.
bridge='''</section>\n\n<section class="character-bridge" id="characterBridge" aria-label="Univers AXORIA">\n  <div class="bridge-label">AXORIA · MOVE · RECOVER · FEEL BETTER</div>\n</section>\n\n<section class="section menu-section" id="menu">'''
rep('</section>\n\n<section class="section menu-section" id="menu">',bridge,'character bridge section')

# Build the orbit logo with the existing AXORIA badge generator.
rep("document.getElementById('loaderLogo').innerHTML = badgeLogoSVG(120);","document.getElementById('loaderLogo').innerHTML = badgeLogoSVG(120);\n  const orbitMark=document.getElementById('heroOrbitMark'); if(orbitMark) orbitMark.innerHTML=badgeLogoSVG(160);",'orbit logo render')

# Replay reveal animation whenever a section re-enters the viewport.
old="const io = new IntersectionObserver((entries)=>{ entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); } }); }, {threshold:.12});\n  document.querySelectorAll('.reveal').forEach(el=>io.observe(el));"
new="const io = new IntersectionObserver((entries)=>{ entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); } else { e.target.classList.remove('in'); } }); }, {threshold:.16,rootMargin:'-6% 0px -8% 0px'});\n  document.querySelectorAll('.reveal').forEach(el=>io.observe(el));"
rep(old,new,'repeat reveal observer')

# Harden quick-buy popup too.
rep("window.open('https://wa.me/212621575115?text=' + encodeURIComponent(lines.join('\\n')), '_blank');","const w=window.open('https://wa.me/212621575115?text=' + encodeURIComponent(lines.join('\\n')), '_blank','noopener,noreferrer'); if(w)w.opener=null;",'quick buy noopener')

# Replace old hero fan controller: move the same sprites into the bridge and keep scroll-driven fan behavior.
pattern=r'<script id="hero-character-fan-v3">.*?</script>'
replacement=r'''<script id="hero-character-fan-v4">
(()=>{
  const hero=document.getElementById('home');
  const bridge=document.getElementById('characterBridge');
  const stage=document.getElementById('heroStage');
  const atmosphere=document.getElementById('heroAtmosphere');
  const orbit=document.getElementById('heroOrbitMark');
  if(!hero||!bridge||!stage||!atmosphere)return;

  bridge.appendChild(stage);
  const chars=[...stage.querySelectorAll('.hero-character')];
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let ticking=false,interaction=0,resetTimer=0;
  const clamp=(n,a=0,b=1)=>Math.min(Math.max(n,a),b);
  const ease=t=>1-Math.pow(1-t,3);

  if(chars[1]) chars[1].classList.add('is-featured');

  // Same scroll-fan idea, but spread across a dedicated runway instead of crowding the hero.
  const desktopTargets=[16,27,36,44,51,58,65,72,79,85,21,90,31,75];
  const mobileTargets=[14,30,46,62,78,22,54,86];
  const finalScale=[1,1,.96,.96,.94,.94,.92,.92,.90,.90,.88,.88,.86,.86];
  const finalAlpha=[1,1,.98,.98,.96,.96,.94,.94,.92,.92,.90,.90,.88,.88];

  chars.forEach((el,i)=>{ if(!el.dataset.main) el.style.zIndex=el.dataset.z||String(20-i); });

  const update=()=>{
    const b=bridge.getBoundingClientRect();
    const vh=Math.max(window.innerHeight,1);
    const mobile=window.innerWidth<700;
    const visibleCount=mobile?8:chars.length;

    // 0 before the bridge enters, ~1 while it reaches the visual center.
    const raw=clamp((vh-b.top)/(vh+b.height*.42));
    const p=Math.max(ease(raw),interaction);

    chars.forEach((el,i)=>{
      if(i>=visibleCount){ el.style.opacity='0'; return; }
      const delay=Math.min(Number(el.dataset.delay||0),.36);
      const local=i<2 ? 1 : ease(clamp((p-delay)/Math.max(.72-delay,.18)));
      const targets=mobile?mobileTargets:desktopTargets;
      const target=targets[i] ?? (10 + i*(80/Math.max(visibleCount-1,1)));
      const center=mobile?(i%2===0?42:58):(i%2===0?46:54);
      const x=center+(target-center)*local;
      const rise=(1-local)*(mobile?18:26);
      const scale=(finalScale[i]??.86)*(mobile?.92:1);
      const opacity=(finalAlpha[i]??.88)*(i<2?1:local);
      el.style.left=`${x.toFixed(2)}%`;
      el.style.opacity=opacity.toFixed(3);
      el.style.transform=`translate3d(-50%,${rise.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
    });

    atmosphere.style.transform=`translate3d(${(-p*7).toFixed(1)}px,${(-p*10).toFixed(1)}px,0) scale(${(1+p*.025).toFixed(3)})`;
    if(orbit){
      const heroRect=hero.getBoundingClientRect();
      const heroP=clamp(-heroRect.top/Math.max(hero.offsetHeight,1));
      orbit.style.transform=`translate3d(0,${(heroP*44).toFixed(1)}px,0) rotate(${(heroP*34).toFixed(1)}deg) scale(${(1+heroP*.05).toFixed(3)})`;
      orbit.style.opacity=String((window.innerWidth<700?.11:.18)*(1-heroP*.42));
    }
    ticking=false;
  };

  const request=()=>{ if(!ticking){ requestAnimationFrame(update); ticking=true; } };
  const boost=()=>{
    if(reduced)return;
    interaction=Math.max(interaction,.56);
    clearTimeout(resetTimer);
    resetTimer=setTimeout(()=>{interaction=0;request();},850);
    request();
  };

  if(reduced){ interaction=.7; update(); return; }
  update();
  window.addEventListener('scroll',request,{passive:true});
  window.addEventListener('resize',request,{passive:true});
  bridge.addEventListener('pointerdown',boost,{passive:true});
})();
</script>'''
text2,n=re.subn(pattern,replacement,text,flags=re.S)
if n!=1:
    if 'hero-character-fan-v4' not in text:
        raise RuntimeError(f'hero fan script replace count={n}')
else:
    text=text2

INDEX.write_text(text,encoding='utf-8')
print('Final polish 1 patch applied.')
