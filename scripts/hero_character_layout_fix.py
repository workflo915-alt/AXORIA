from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep the premium hero, but make the character fan fit the viewport cleanly.
old_css = ".hero-character.is-main{opacity:1;width:clamp(238px,28vw,430px);z-index:22;}"
new_css = old_css + "\n.hero-character.is-featured{width:clamp(226px,25.5vw,390px);z-index:21;}"
if old_css in s and '.hero-character.is-featured{' not in s:
    s = s.replace(old_css, new_css, 1)

s = s.replace(
    "@media (max-width:900px){.hero-character{left:60%;width:clamp(150px,29vw,250px);bottom:-1%;}.hero-character.is-main{width:clamp(210px,42vw,340px);}",
    "@media (max-width:900px){.hero-character{left:60%;width:clamp(150px,29vw,250px);bottom:-1%;}.hero-character.is-main{width:clamp(210px,42vw,340px);}.hero-character.is-featured{width:clamp(195px,37vw,305px);}",
    1,
)
s = s.replace(
    "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(138px,38vw,205px);bottom:4%;}.hero-character.is-main{width:clamp(210px,58vw,300px);bottom:2.5%;}.hero::after{height:40px;}}",
    "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(138px,38vw,205px);bottom:4%;}.hero-character.is-main{width:clamp(210px,58vw,300px);bottom:2.5%;}.hero-character.is-featured{width:clamp(190px,52vw,270px);bottom:3%;}.hero::after{height:40px;}}",
    1,
)

start = s.index('<script id="hero-character-fan-v2">')
end = s.index('</script>', start) + len('</script>')
script = r'''<script id="hero-character-fan-v3">
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

  // The first two cells are the athlete man + athlete woman.
  if(chars[1]) chars[1].classList.add('is-featured');

  const desktopTargets=[66,80,52,88,44,90,58,84,37,89,48,82,31,74];
  const finalScale=[1.04,.98,.82,.80,.73,.72,.71,.70,.67,.66,.65,.64,.62,.62];
  const finalAlpha=[1,1,.94,.92,.90,.88,.86,.84,.82,.80,.78,.76,.74,.72];

  chars.forEach((el,i)=>{
    if(!el.dataset.main) el.style.zIndex=el.dataset.z||String(20-i);
  });

  const update=()=>{
    const rect=hero.getBoundingClientRect();
    const h=Math.max(hero.offsetHeight,1);
    const mobile=window.innerWidth<700;

    // Reveal the fan early, before the hero has scrolled too far away.
    const scrollP=clamp(-rect.top/(h*.42));
    const p=Math.max(scrollP,interaction);

    // Shrink the whole group only as the visible hero height gets shorter,
    // so heads/feet stay inside the viewport instead of getting chopped.
    const fit=clamp((rect.bottom-8)/(h*.92),.26,1);
    const basePct=mobile?50:66;

    chars.forEach((el,i)=>{
      const delay=Number(el.dataset.delay||0);
      const local=i===0?1:ease(clamp((p-delay)/Math.max(.44-delay,.10)));
      const rawTarget=desktopTargets[i] ?? basePct;
      const targetPct=mobile ? 50+(rawTarget-66)*.55 : rawTarget;
      const xPct=basePct+(targetPct-basePct)*local;
      const y=(1-local)*(mobile?20:28) - local*(mobile?0:4);
      const scale=(finalScale[i] ?? .66)*fit;
      const opacity=i===0 ? 1 : (finalAlpha[i] ?? .78)*local;

      el.style.left=`${xPct.toFixed(2)}%`;
      el.style.opacity=opacity.toFixed(3);
      el.style.transform=`translate3d(-50%,${y.toFixed(1)}px,0) scale(${scale.toFixed(3)})`;
    });

    atmosphere.style.transform=`translate3d(${(-p*8).toFixed(1)}px,${(-p*12).toFixed(1)}px,0) scale(${(1+p*.03).toFixed(3)})`;
    ticking=false;
  };

  const request=()=>{if(!ticking){requestAnimationFrame(update);ticking=true;}};
  const boost=()=>{
    if(reduced)return;
    interaction=Math.max(interaction,.30);
    clearTimeout(resetTimer);
    resetTimer=setTimeout(()=>{interaction=0;request();},850);
    request();
  };

  if(reduced){interaction=.30;update();return;}
  update();
  window.addEventListener('scroll',request,{passive:true});
  window.addEventListener('resize',request,{passive:true});
  hero.addEventListener('pointerdown',boost,{passive:true});
})();
</script>'''

s = s[:start] + script + s[end:]
p.write_text(s, encoding='utf-8')
print('hero character layout fix applied')
