from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

repls={
".hero-character{position:absolute;left:66%;bottom:-1.8%;width:clamp(176px,21vw,318px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 22px 24px rgba(0,0,0,.26));}":
".hero-character{position:absolute;left:66%;bottom:0;width:clamp(150px,17vw,258px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}",
".hero-character.is-main{opacity:1;width:clamp(238px,28vw,430px);z-index:22;}":
".hero-character.is-main{opacity:1;left:64%;bottom:0;width:clamp(218px,24vw,358px);z-index:22;}\n.hero-character.is-sportive{left:64%;bottom:0;width:clamp(190px,21vw,310px);z-index:21;}",
"@media (max-width:900px){.hero-character{left:60%;width:clamp(150px,29vw,250px);bottom:-1%;}.hero-character.is-main{width:clamp(210px,42vw,340px);}":
"@media (max-width:900px){.hero-character{left:60%;width:clamp(128px,23vw,192px);bottom:0;}.hero-character.is-main{left:58%;width:clamp(190px,34vw,278px);}.hero-character.is-sportive{left:58%;width:clamp(170px,30vw,245px);}",
"@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:50%;width:clamp(138px,38vw,205px);bottom:4%;}.hero-character.is-main{width:clamp(210px,58vw,300px);bottom:2.5%;}.hero::after{height:40px;}}":
"@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:52%;width:clamp(102px,24vw,145px);bottom:3%;}.hero-character.is-main{left:50%;width:clamp(168px,42vw,225px);bottom:2.5%;}.hero-character.is-sportive{left:50%;width:clamp(150px,38vw,205px);bottom:2.5%;}.hero::after{height:40px;}}",
"<div class=\"hero-character\" data-spread=\"0.18\" data-delay=\"0.03\" data-scale=\".88\" data-opacity=\".94\" data-z=\"20\" style=\"--bp-x:33.333%;--bp-y:0%;\"></div>":
"<div class=\"hero-character is-sportive\" data-spread=\"0.15\" data-delay=\"0.02\" data-scale=\".98\" data-opacity=\".98\" data-z=\"21\" style=\"--bp-x:33.333%;--bp-y:0%;\"></div>",
"const spreadBase=mobile?Math.min(window.innerWidth*.76,330):Math.min(window.innerWidth*.70,1040);":
"const spreadBase=mobile?Math.min(window.innerWidth*.42,180):Math.min(window.innerWidth*.46,620);",
"const mainScale=1.04-settle*.035;":
"const mainScale=1.00-settle*.12;",
"const y=-settle*(mobile?5:12);":
"const y=settle*(mobile?2:5);",
"const targetScale=Number(el.dataset.scale||.75)*(mobile?.88:1);":
"const targetScale=Number(el.dataset.scale||.75)*(mobile?.92:1);",
"const y=(1-local)*(mobile?28:42)-local*(mobile?2:10);":
"const y=(1-local)*(mobile?14:20)+local*(mobile?1:3);"
}

changed=0
for old,new in repls.items():
    if old not in s:
        raise SystemExit('Expected hero fragment missing: '+old[:90])
    s=s.replace(old,new,1)
    changed+=1

p.write_text(s,encoding='utf-8')
print(f'hero balance patch applied ({changed} replacements)')
