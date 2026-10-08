from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

repls=[
(".hero-logo-orbit{position:absolute;right:7%;top:50%;width:clamp(190px,24vw,330px);aspect-ratio:1;transform:translateY(-50%);display:grid;place-items:center;opacity:.94;filter:drop-shadow(0 24px 42px rgba(0,0,0,.22));}",
 ".hero-logo-orbit{position:absolute;right:8.5%;top:48%;width:clamp(170px,20vw,285px);aspect-ratio:1;transform:translateY(-50%);display:grid;place-items:center;opacity:.86;border-radius:50%;background:radial-gradient(circle at 38% 32%,rgba(255,255,255,.10),transparent 42%),color-mix(in srgb,var(--surface) 10%,transparent);filter:drop-shadow(0 22px 38px rgba(0,0,0,.18));}"),
(".hero-logo-inner{width:62%;height:62%;display:grid;place-items:center;animation:heroLogoFloat 5.8s ease-in-out infinite;will-change:transform;}",
 ".hero-logo-inner{width:58%;height:58%;display:grid;place-items:center;animation:heroLogoFloat 7s ease-in-out infinite;will-change:transform;}"),
(".hero-logo-ring{position:absolute;inset:7%;border-radius:50%;border:1px solid color-mix(in srgb,var(--teal) 38%,transparent);box-shadow:0 0 0 18px color-mix(in srgb,var(--teal) 5%,transparent),inset 0 0 50px color-mix(in srgb,var(--teal) 8%,transparent);animation:heroRingSpin 18s linear infinite;}",
 ".hero-logo-ring{position:absolute;inset:9%;border-radius:50%;border:1px solid color-mix(in srgb,var(--teal) 32%,transparent);box-shadow:0 0 0 12px color-mix(in srgb,var(--teal) 4%,transparent),inset 0 0 42px color-mix(in srgb,var(--teal) 7%,transparent);animation:heroRingSpin 24s linear infinite;}"),
(".character-bridge .hero-character{bottom:0!important;width:clamp(130px,13.4vw,190px)!important;filter:drop-shadow(0 15px 18px rgba(0,0,0,.18));}",
 ".character-bridge .hero-character{bottom:7%!important;width:clamp(130px,13.4vw,190px)!important;filter:drop-shadow(0 15px 18px rgba(0,0,0,.18));}"),
(".character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(148px,15.3vw,216px)!important;bottom:-.5%!important;}",
 ".character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:clamp(148px,15.3vw,216px)!important;bottom:5%!important;}"),
]
for old,new in repls:
    if old not in text:
        raise RuntimeError('anchor not found: '+old[:90])
    text=text.replace(old,new,1)

anchor="input[aria-invalid='true']{border-color:#B42318!important;box-shadow:0 0 0 3px rgba(180,35,24,.12)!important;}"
mobile_css=r'''/* ---------- Phone-first polish ---------- */
@media(max-width:700px){
  .wrap{padding-left:18px;padding-right:18px;}
  .section{padding:72px 0;}
  .section-head{margin-bottom:32px;}
  .section-head h2{font-size:clamp(28px,8vw,38px);line-height:1.08;}
  .section-head p{font-size:14.5px;line-height:1.55;}

  .hero{height:100svh;min-height:620px;}
  .hero-content{padding:0 18px 46px;}
  .hero h1{font-size:clamp(40px,13vw,62px);line-height:.98;letter-spacing:-.03em;}
  .hero .subtitle{font-size:12px;letter-spacing:.055em;gap:7px;margin-top:11px;}
  .hero .tagline{font-size:14px;line-height:1.55;max-width:94%;margin-top:14px;}
  .hero-ctas{display:grid;grid-template-columns:1fr;gap:10px;margin-top:24px;max-width:360px;}
  .hero-ctas .btn{width:100%;justify-content:center;padding:13px 16px;}
  .trust-badges{gap:9px 14px;margin-top:18px;}
  .trust-badges span{font-size:11.5px;gap:6px;}
  .trust-badges span svg{width:14px;height:14px;}
  .scrolldown{display:none;}

  .hero-logo-orbit{right:16px;top:25%;width:132px;transform:none;opacity:.42;background:none;filter:none;}
  .hero-logo-inner{width:60%;height:60%;}
  .hero-logo-ring{inset:11%;box-shadow:0 0 0 7px color-mix(in srgb,var(--teal) 4%,transparent);}
  .hero-logo-dot{display:none;}

  .character-bridge{height:228px;}
  .character-bridge .hero-character{bottom:8%!important;width:96px!important;}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{bottom:6%!important;width:112px!important;}
  .character-bridge + .menu-section{padding-top:34px;}

  .cat-filters{display:flex;flex-wrap:nowrap;overflow-x:auto;overscroll-behavior-inline:contain;scroll-snap-type:x proximity;gap:10px;padding:2px 18px 10px 2px;margin-right:-18px;scrollbar-width:none;}
  .cat-filters::-webkit-scrollbar{display:none;}
  .cat-chip{flex:0 0 auto;scroll-snap-align:start;white-space:nowrap;padding:11px 16px;font-size:12px;}

  .menu-grid{grid-template-columns:1fr;gap:18px;}
  .pcard{border-radius:18px;}
  .pcard:hover{transform:none;box-shadow:var(--shadow-sm);}
  .pcard:hover .imgwrap img{transform:none;}

  .modal-overlay{padding:10px;}
  .modal-box{width:calc(100vw - 20px)!important;max-height:92svh;border-radius:20px;}
  .modal-body{padding:18px;}
  .modal-head{padding:16px 18px;}
  .formgrid{grid-template-columns:1fr!important;gap:0!important;}
  .order-success-card{padding:26px 18px 22px;}

  .sticky-buybar{left:8px!important;right:8px!important;bottom:8px!important;width:auto!important;max-width:none!important;}
  .floatbtns{right:14px;bottom:16px;}
  body.cart-bar-visible .floatbtns{bottom:100px;}
}

@media(max-width:430px){
  .nav-inner{padding:9px 12px;}
  .brand{font-size:14px;}
  .brand img{width:36px!important;height:36px!important;}
  .nav-tools{gap:5px;}
  .iconbtn{width:31px;height:31px;}
  .langsel{max-width:58px;padding:6px 20px 6px 8px;font-size:11px;}
  .mobile-menu{top:66px;left:10px;right:10px;}
  .hero-content{padding-left:16px;padding-right:16px;}
  .hero h1{font-size:clamp(38px,12.5vw,54px);}
  .hero .tagline{max-width:100%;}
  .hero-logo-orbit{width:116px;right:8px;top:23%;opacity:.34;}
  .character-bridge{height:214px;}
  .character-bridge .hero-character{width:91px!important;}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:106px!important;}
  .fab{width:50px;height:50px;}
}

@media(max-width:360px){
  .hero{min-height:600px;}
  .hero h1{font-size:37px;}
  .hero .subtitle{font-size:10.5px;}
  .hero .tagline{font-size:13px;}
  .hero-ctas{margin-top:20px;}
  .trust-badges{gap:7px 10px;}
  .trust-badges span{font-size:10.5px;}
  .hero-logo-orbit{width:96px;opacity:.28;}
  .section{padding:62px 0;}
  .character-bridge{height:198px;}
  .character-bridge .hero-character{width:84px!important;}
  .character-bridge .hero-character.is-main,.character-bridge .hero-character.is-featured{width:98px!important;}
}
'''
if anchor not in text:
    raise RuntimeError('css insertion anchor not found')
text=text.replace(anchor,mobile_css+'\n'+anchor,1)

INDEX.write_text(text,encoding='utf-8')
print('Final visual polish v4 applied.')
