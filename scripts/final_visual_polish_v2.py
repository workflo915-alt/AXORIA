from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

repls=[
(".character-bridge{position:relative;height:clamp(300px,35vw,430px);overflow:hidden;", ".character-bridge{position:relative;height:clamp(235px,27vw,320px);overflow:hidden;"),
(".character-bridge .hero-character{bottom:2%!important;width:clamp(104px,11vw,158px)!important;", ".character-bridge .hero-character{bottom:0!important;width:clamp(130px,13.4vw,190px)!important;"),
(".character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(118px,12.5vw,178px)!important;bottom:1.2%!important;}", ".character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(148px,15.3vw,216px)!important;bottom:-.5%!important;}"),
(".character-bridge + .menu-section{padding-top:76px;}", ".character-bridge + .menu-section{padding-top:48px;}"),
("  .character-bridge{height:340px;}", "  .character-bridge{height:270px;}"),
("  .character-bridge .hero-character{width:clamp(92px,18vw,128px)!important;}", "  .character-bridge .hero-character{width:clamp(112px,21vw,148px)!important;}"),
("  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(104px,20vw,144px)!important;}", "  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(128px,24vw,168px)!important;}"),
("  .character-bridge + .menu-section{padding-top:64px;}", "  .character-bridge + .menu-section{padding-top:42px;}"),
("  .character-bridge{height:286px;}", "  .character-bridge{height:235px;}"),
("  .character-bridge .hero-character{width:88px!important;}", "  .character-bridge .hero-character{width:96px!important;}"),
("  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:102px!important;}", "  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:112px!important;}"),
("  .character-bridge + .menu-section{padding-top:54px;}", "  .character-bridge + .menu-section{padding-top:36px;}"),
("  const hero=document.getElementById('home');\n  const stage=document.getElementById('heroStage');\n  const atmosphere=document.getElementById('heroAtmosphere');\n  if(!hero||!stage||!atmosphere)return;", "  const hero=document.getElementById('home');\n  const bridge=document.getElementById('characterBridge');\n  const stage=document.getElementById('heroStage');\n  const atmosphere=document.getElementById('heroAtmosphere');\n  if(!hero||!bridge||!stage||!atmosphere)return;"),
("    const rect=hero.getBoundingClientRect();\n    const h=Math.max(hero.offsetHeight,1);", "    const rect=bridge.getBoundingClientRect();\n    const h=Math.max(bridge.offsetHeight,1);"),
("    // Reveal the fan early, before the hero has scrolled too far away.\n    const scrollP=clamp(-rect.top/(h*.34));", "    // Fan opens while the bridge enters the viewport and reverses on scroll-up.\n    const vh=Math.max(window.innerHeight,1);\n    const enterStart=vh*.92;\n    const enterEnd=vh*.46;\n    const scrollP=clamp((enterStart-rect.top)/Math.max(enterStart-enterEnd,1));"),
("    const fit=clamp((rect.bottom+20)/(h*.88),.88,1);", "    const fit=1;"),
]

for old,new in repls:
    if old not in text:
        raise RuntimeError('anchor not found: '+old[:80])
    text=text.replace(old,new,1)

INDEX.write_text(text,encoding='utf-8')
print('Final visual polish v2 applied.')
