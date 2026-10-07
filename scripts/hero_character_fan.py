from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Dark is the premium default for new visitors; stored user preference can still override it.
s = s.replace('<html lang="fr" data-theme="light">', '<html lang="fr" data-theme="dark">', 1)

preload = '<link rel="preload" as="image" href="assets/hero/axoria-hero-characters.webp" type="image/webp">'
if preload not in s:
    anchor = '<link rel="canonical" href="https://axoria.ma/">'
    if anchor not in s:
        raise SystemExit('canonical anchor missing')
    s = s.replace(anchor, anchor + '\n' + preload, 1)

# Replace only the visual layer of the hero. Keep existing content, CTAs, particles and trust copy intact.
start = s.index('/* ---------- Hero ---------- */')
end = s.index('.hero-particles{', start)
hero_css = r'''/* ---------- Hero ---------- */
.hero{position:relative;height:100vh;min-height:650px;display:flex;align-items:flex-end;overflow:hidden;color:#fff;isolation:isolate;background:radial-gradient(ellipse at 72% 58%,rgba(35,133,191,.18) 0%,rgba(35,133,191,0) 38%),radial-gradient(ellipse at 82% 22%,rgba(13,83,151,.24) 0%,rgba(13,83,151,0) 34%),linear-gradient(135deg,#07101C 0%,#0A1626 50%,#07111D 100%);}
[data-theme="light"] .hero{color:#0B1524;background:radial-gradient(ellipse at 70% 52%,rgba(63,143,196,.16) 0%,rgba(63,143,196,0) 38%),radial-gradient(ellipse at 86% 18%,rgba(32,191,169,.10) 0%,rgba(32,191,169,0) 30%),linear-gradient(135deg,#F8FAFC 0%,#EEF3F8 52%,#E8EEF5 100%);}
.hero-visual{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden;}
.hero-stage{position:absolute;inset:0;z-index:1;pointer-events:none;transform:translateZ(0);}
.hero-stage::after{content:'';position:absolute;left:52%;bottom:4.5%;width:min(720px,58vw);height:70px;transform:translateX(-20%);border-radius:50%;background:radial-gradient(ellipse,rgba(3,10,18,.28) 0%,rgba(3,10,18,.08) 42%,transparent 72%);opacity:.7;}
[data-theme="light"] .hero-stage::after{background:radial-gradient(ellipse,rgba(58,80,104,.18) 0%,rgba(58,80,104,.06) 44%,transparent 72%);opacity:.72;}
.hero-character{position:absolute;left:66%;bottom:-1.8%;width:clamp(176px,21vw,318px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 22px 24px rgba(0,0,0,.26));}
[data-theme="light"] .hero-character{filter:drop-shadow(0 19px 22px rgba(35,54,76,.18));}
.hero-character.is-main{opacity:1;width:clamp(238px,28vw,430px);z-index:22;}
.hero-atmosphere{position:absolute;inset:-8%;z-index:0;pointer-events:none;will-change:transform;background:radial-gradient(circle at 76% 34%,rgba(32,191,169,.12),transparent 27%),radial-gradient(circle at 58% 72%,rgba(47,128,237,.14),transparent 34%);filter:blur(24px);opacity:.72;}
[data-theme="light"] .hero-atmosphere{background:radial-gradient(circle at 78% 36%,rgba(32,191,169,.08),transparent 27%),radial-gradient(circle at 58% 72%,rgba(47,128,237,.09),transparent 34%);filter:blur(20px);opacity:.62;}
.hero::before,.hero::after{content:'';position:absolute;left:0;right:0;z-index:1;pointer-events:none;}
.hero::before{top:0;height:42px;background:linear-gradient(to bottom,color-mix(in srgb,var(--bg) 36%,transparent),transparent);}
.hero::after{bottom:0;height:58px;background:linear-gradient(to top,var(--bg-alt) 0%,color-mix(in srgb,var(--bg-alt) 48%,transparent) 46%,transparent 100%);}
.hero-overlay{position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(4,12,22,.78) 0%,rgba(4,12,22,.54) 30%,rgba(4,12,22,.14) 55%,transparent 77%);transition:background .45s ease;pointer-events:none;}
[data-theme="light"] .hero-overlay{background:linear-gradient(90deg,rgba(248,250,252,.97) 0%,rgba(248,250,252,.76) 32%,rgba(248,250,252,.20) 58%,transparent 78%);}
[data-theme="light"] .hero .tagline{color:#344256;text-shadow:none;}
[data-theme="light"] .hero .subtitle{color:#0A4D9B;}
[data-theme="light"] .hero-content .eyebrow{color:#073869;}
[data-theme="light"] .hero-content .eyebrow::before{background:#073869;}
[data-theme="light"] .hero .btn-outline{color:#0B1524;border-color:rgba(11,21,36,.28);background:rgba(255,255,255,.44);}
[data-theme="light"] .hero .btn-outline:hover{background:#0B1524;color:#fff;border-color:#0B1524;}
[data-theme="light"] .scrolldown{color:#314156;}
@media (max-width:900px){.hero-character{left:60%;width:clamp(150px,29vw,250px);bottom:-1%;}.hero-character.is-main{width:clamp(210px,42vw,340px);}.hero-overlay{background:linear-gradient(180deg,rgba(4,12,22,.05) 0%,rgba(4,12,22,.18) 42%,rgba(4,12,22,.76) 78%,rgba(4,12,22,.90) 100%);}[data-theme="light"] .hero-overlay{background:linear-gradient(180deg,rgba(248,250,252,.02) 0%,rgba(248,250,252,.16) 40%,rgba(248,250,252,.80) 76%,rgba(248,250,252,.96) 100%);}.hero-stage::after{left:50%;bottom:4%;width:78vw;transform:translateX(-50%);}.hero-atmosphere{filter:blur(18px);}}
@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(138px,38vw,205px);bottom:4%;}.hero-character.is-main{width:clamp(210px,58vw,300px);bottom:2.5%;}.hero::after{height:40px;}}
'''
s = s[:start] + hero_css + s[end:]

old_scene = '''  <div class="hero-scene" id="heroScene" aria-hidden="true">\n    <img src="https://images.pexels.com/photos/7222429/pexels-photo-7222429.jpeg?auto=compress&cs=tinysrgb&w=1800" alt="" fetchpriority="high" decoding="async">\n  </div>\n  <div class="hero-atmosphere" id="heroAtmosphere" aria-hidden="true"></div>'''
new_scene = '''  <div class="hero-visual" id="heroVisual" aria-hidden="true">\n    <div class="hero-atmosphere" id="heroAtmosphere"></div>\n    <div class="hero-stage" id="heroStage">\n      <div class="hero-character is-main" data-main="1" data-spread="0" data-delay="0" data-scale="1.04" data-opacity="1" style="--bp-x:0%;--bp-y:0%;"></div>\n      <div class="hero-character" data-spread="0.18" data-delay="0.03" data-scale=".88" data-opacity=".94" data-z="20" style="--bp-x:33.333%;--bp-y:0%;"></div>\n      <div class="hero-character" data-spread="-0.18" data-delay="0.06" data-scale=".82" data-opacity=".88" data-z="18" style="--bp-x:66.667%;--bp-y:0%;"></div>\n      <div class="hero-character" data-spread="0.30" data-delay="0.10" data-scale=".80" data-opacity=".86" data-z="17" style="--bp-x:100%;--bp-y:0%;"></div>\n      <div class="hero-character" data-spread="-0.31" data-delay="0.14" data-scale=".78" data-opacity=".83" data-z="16" style="--bp-x:0%;--bp-y:33.333%;"></div>\n      <div class="hero-character" data-spread="0.40" data-delay="0.18" data-scale=".76" data-opacity=".80" data-z="15" style="--bp-x:33.333%;--bp-y:33.333%;"></div>\n      <div class="hero-character" data-spread="-0.41" data-delay="0.22" data-scale=".75" data-opacity=".80" data-z="14" style="--bp-x:66.667%;--bp-y:33.333%;"></div>\n      <div class="hero-character" data-spread="0.50" data-delay="0.26" data-scale=".72" data-opacity=".76" data-z="13" style="--bp-x:100%;--bp-y:33.333%;"></div>\n      <div class="hero-character" data-spread="-0.51" data-delay="0.30" data-scale=".71" data-opacity=".74" data-z="12" style="--bp-x:0%;--bp-y:66.667%;"></div>\n      <div class="hero-character" data-spread="0.59" data-delay="0.34" data-scale=".70" data-opacity=".72" data-z="11" style="--bp-x:33.333%;--bp-y:66.667%;"></div>\n      <div class="hero-character" data-spread="-0.60" data-delay="0.38" data-scale=".69" data-opacity=".70" data-z="10" style="--bp-x:66.667%;--bp-y:66.667%;"></div>\n      <div class="hero-character" data-spread="0.68" data-delay="0.42" data-scale=".67" data-opacity=".68" data-z="9" style="--bp-x:100%;--bp-y:66.667%;"></div>\n      <div class="hero-character" data-spread="-0.69" data-delay="0.46" data-scale=".66" data-opacity=".66" data-z="8" style="--bp-x:0%;--bp-y:100%;"></div>\n      <div class="hero-character" data-spread="0.76" data-delay="0.50" data-scale=".64" data-opacity=".64" data-z="7" style="--bp-x:33.333%;--bp-y:100%;"></div>\n    </div>\n  </div>'''
if old_scene not in s:
    raise SystemExit('old hero scene missing')
s = s.replace(old_scene, new_scene, 1)

script_start = s.index('<script id="hero-scroll-wellness-v1">')
script_end = s.index('</script>', script_start) + len('</script>')
new_script = r'''<script id="hero-character-fan-v2">
(()=>{
  const hero=document.getElementById('home');
  const stage=document.getElementById('heroStage');
  const atmosphere=document.getElementById('heroAtmosphere');
  if(!hero||!stage||!atmosphere)return;
  const chars=[...stage.querySelectorAll('.hero-character')];
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let ticking=false,interaction=0,resetTimer=0;
  const clamp=(n,a=0,b=1)=>Math.min(Math.max(n,a),b);
  const ease=t=>1-Math.pow(1-t,3);
  chars.forEach((el,i)=>{if(!el.dataset.main)el.style.zIndex=el.dataset.z||String(18-i);});
  const update=()=>{
    const rect=hero.getBoundingClientRect();
    const h=Math.max(hero.offsetHeight,1);
    const scrollP=clamp(-rect.top/(h*.78));
    const p=Math.max(scrollP,interaction);
    const mobile=window.innerWidth<700;
    const spreadBase=mobile?Math.min(window.innerWidth*.76,330):Math.min(window.innerWidth*.70,1040);
    chars.forEach(el=>{
      if(el.dataset.main){
        const settle=ease(clamp(p/.72));
        const mainScale=1.04-settle*.035;
        const y=-settle*(mobile?5:12);
        el.style.opacity='1';
        el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,0) scale(${mainScale.toFixed(3)})`;
        return;
      }
      const delay=Number(el.dataset.delay||0);
      const local=ease(clamp((p-delay)/Math.max(.54-delay,.12)));
      const spread=Number(el.dataset.spread||0);
      const targetScale=Number(el.dataset.scale||.75)*(mobile?.88:1);
      const scale=.68+(targetScale-.68)*local;
      const x=spreadBase*spread*local;
      const y=(1-local)*(mobile?28:42)-local*(mobile?2:10);
      const opacity=Number(el.dataset.opacity||.75)*local;
      el.style.opacity=opacity.toFixed(3);
      el.style.transform=`translate3d(calc(-50% + ${x.toFixed(1)}px),${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
    });
    atmosphere.style.transform=`translate3d(${(-p*10).toFixed(1)}px,${(-p*18).toFixed(1)}px,0) scale(${(1+p*.035).toFixed(3)})`;
    ticking=false;
  };
  const request=()=>{if(!ticking){requestAnimationFrame(update);ticking=true;}};
  const boost=()=>{
    if(reduced)return;
    interaction=Math.max(interaction,.34);
    clearTimeout(resetTimer);
    resetTimer=setTimeout(()=>{interaction=0;request();},850);
    request();
  };
  if(reduced){interaction=.36;update();return;}
  update();
  window.addEventListener('scroll',request,{passive:true});
  window.addEventListener('resize',request,{passive:true});
  hero.addEventListener('pointerdown',boost,{passive:true});
})();
</script>'''
s = s[:script_start] + new_script + s[script_end:]

p.write_text(s, encoding='utf-8')
print('hero character fan patch applied')
