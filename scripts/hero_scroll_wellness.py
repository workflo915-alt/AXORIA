from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'hero-scroll-wellness-v1'
if marker in s:
    print('Hero wellness scroll patch already applied')
    raise SystemExit(0)

old_css = ".hero video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;transform:scale(1.05);animation:heroZoom 22s ease-in-out infinite alternate;}\n@keyframes heroZoom{from{transform:scale(1.0);}to{transform:scale(1.14);}}"
new_css = """.hero-scene{position:absolute;inset:-4%;z-index:0;pointer-events:none;will-change:transform;transform:translate3d(0,0,0) scale(1.04);transform-origin:center center;overflow:hidden;}\n.hero-scene img{width:100%;height:100%;object-fit:cover;object-position:center 45%;filter:saturate(.92) contrast(.98) brightness(.86);transform:scale(1.02);}\n.hero-atmosphere{position:absolute;inset:-14%;z-index:.4;pointer-events:none;will-change:transform;background:radial-gradient(circle at 18% 24%,rgba(63,143,196,.28),transparent 34%),radial-gradient(circle at 82% 70%,rgba(201,162,39,.16),transparent 28%),radial-gradient(circle at 56% 48%,rgba(10,77,155,.20),transparent 42%);filter:blur(28px);opacity:.95;}\n.hero::before,.hero::after{content:'';position:absolute;left:0;right:0;z-index:1;pointer-events:none;}\n.hero::before{top:0;height:120px;background:linear-gradient(to bottom,var(--bg) 0%,color-mix(in srgb,var(--bg) 76%,transparent) 42%,transparent 100%);}\n.hero::after{bottom:0;height:150px;background:linear-gradient(to top,var(--bg-alt) 0%,color-mix(in srgb,var(--bg-alt) 78%,transparent) 44%,transparent 100%);}\n[data-theme=\"dark\"] .hero-scene img{filter:saturate(.88) contrast(1.02) brightness(.68);}\n@media (max-width:760px){.hero-scene{inset:-2% -16%;}.hero-scene img{object-position:center 44%;}.hero::before{height:88px}.hero::after{height:120px}.hero-atmosphere{filter:blur(20px);}}"""
if old_css not in s:
    raise SystemExit('Hero video CSS marker not found')
s = s.replace(old_css, new_css, 1)

old_overlay = ".hero-overlay{position:absolute;inset:0;background:linear-gradient(180deg, rgba(8,16,28,.35) 0%, rgba(7,14,24,.58) 55%, rgba(4,8,14,.9) 100%);transition:background 1s ease;}\n[data-theme=\"light\"] .hero-overlay{background:linear-gradient(175deg, rgba(10,77,155,.30) 0%, rgba(9,35,60,.55) 45%, rgba(4,8,14,.92) 100%);}"
new_overlay = ".hero-overlay{position:absolute;inset:0;z-index:.8;background:linear-gradient(180deg,rgba(6,13,24,.16) 0%,rgba(7,18,31,.34) 48%,rgba(6,12,22,.62) 100%);transition:background .6s ease;}\n[data-theme=\"light\"] .hero-overlay{background:linear-gradient(175deg,rgba(255,255,255,.05) 0%,rgba(10,77,155,.18) 46%,rgba(6,12,22,.56) 100%);}"
if old_overlay not in s:
    raise SystemExit('Hero overlay CSS marker not found')
s = s.replace(old_overlay, new_overlay, 1)

old_html = '''  <video autoplay muted loop playsinline poster="https://images.pexels.com/videos/5793440/pexels-photo-5793440.jpeg?auto=compress&cs=tinysrgb&w=1600">\n    <source src="https://videos.pexels.com/video-files/5793440/5793440-uhd_2560_1440_25fps.mp4" type="video/mp4">\n  </video>'''
new_html = '''  <div class="hero-scene" id="heroScene" aria-hidden="true">\n    <img src="https://images.pexels.com/photos/7222429/pexels-photo-7222429.jpeg?auto=compress&cs=tinysrgb&w=1800" alt="" fetchpriority="high" decoding="async">\n  </div>\n  <div class="hero-atmosphere" id="heroAtmosphere" aria-hidden="true"></div>'''
if old_html not in s:
    raise SystemExit('Hero video HTML marker not found')
s = s.replace(old_html, new_html, 1)

motion = r'''
<script id="hero-scroll-wellness-v1">
(()=>{
  const hero=document.getElementById('home');
  const scene=document.getElementById('heroScene');
  const atmosphere=document.getElementById('heroAtmosphere');
  if(!hero||!scene||!atmosphere)return;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduced)return;
  let ticking=false;
  const update=()=>{
    const rect=hero.getBoundingClientRect();
    const h=Math.max(hero.offsetHeight,1);
    const y=Math.min(Math.max(-rect.top,0),h);
    const p=y/h;
    scene.style.transform=`translate3d(0,${(p*46).toFixed(1)}px,0) scale(${(1.04+p*.045).toFixed(3)})`;
    atmosphere.style.transform=`translate3d(${(-p*18).toFixed(1)}px,${(-p*30).toFixed(1)}px,0) scale(${(1+p*.07).toFixed(3)})`;
    ticking=false;
  };
  const request=()=>{if(!ticking){requestAnimationFrame(update);ticking=true;}};
  update();
  window.addEventListener('scroll',request,{passive:true});
  window.addEventListener('resize',request,{passive:true});
})();
</script>
'''
if '</body>' not in s:
    raise SystemExit('Body close marker not found')
s = s.replace('</body>', motion + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Applied AXORIA wellness hero scroll patch')
