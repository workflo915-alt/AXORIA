from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def sub1(pattern, repl, label, flags=0):
    global s
    new, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'Expected one match for {label}, got {n}')
    s = new

sub1(r"\.hero-character\{position:absolute;left:[^}]+?filter:drop-shadow\([^}]+?\);\}",
     ".hero-character{position:absolute;left:66%;bottom:0;width:clamp(168px,18.5vw,286px);aspect-ratio:2/3;background-image:url('assets/hero/axoria-hero-characters.webp');background-repeat:no-repeat;background-size:400% 400%;background-position:var(--bp-x) var(--bp-y);transform-origin:50% 100%;will-change:transform,opacity;opacity:0;filter:drop-shadow(0 18px 20px rgba(0,0,0,.22));}",
     'hero-character css')
sub1(r"\.hero-character\.is-main\{[^}]+\}",
     ".hero-character.is-main{opacity:1;left:62.5%;bottom:0;width:clamp(225px,24.5vw,365px);z-index:22;}",
     'main character css')
sub1(r"\.hero-character\.is-sportive\{[^}]+\}",
     ".hero-character.is-sportive{opacity:1;left:71.5%;bottom:0;width:clamp(218px,23.8vw,355px);z-index:21;}",
     'sportive css')
sub1(r"\.hero-character\.is-featured\{[^}]+\}",
     ".hero-character.is-featured{width:clamp(218px,23.8vw,355px);z-index:21;}",
     'featured css')
sub1(r"@media \(max-width:900px\)\{\.hero-character\{[^}]+\}\.hero-character\.is-main\{[^}]+\}\.hero-character\.is-sportive\{[^}]+\}",
     "@media (max-width:900px){.hero-character{left:60%;width:clamp(142px,25vw,215px);bottom:0;}.hero-character.is-main{left:56%;width:clamp(195px,36vw,285px);}.hero-character.is-sportive{left:64%;width:clamp(188px,34vw,278px);}",
     'tablet hero css')
sub1(r"@media \(max-width:600px\)\{\.hero\{min-height:690px;\}\.hero-character\{[^}]+\}\.hero-character\.is-main\{[^}]+\}\.hero-character\.is-sportive\{[^}]+\}",
     "@media (max-width:600px){.hero{min-height:690px;}.hero-character{left:52%;width:clamp(112px,27vw,158px);bottom:3%;}.hero-character.is-main{left:48%;width:clamp(175px,44vw,238px);bottom:2.5%;}.hero-character.is-sportive{left:58%;width:clamp(170px,42vw,230px);bottom:2.5%;}",
     'mobile hero css')
sub1(r"const desktopTargets=\[[^\]]+\];",
     "const desktopTargets=[62.5,71.5,53,78,46,84,39,89,33,93,27,96,22,98];",
     'desktop targets')
if re.search(r"const mobileTargets=\[", s):
    sub1(r"const mobileTargets=\[[^\]]+\];",
         "const mobileTargets=[47,57,40,64,34,70,29,75,24,80,20,84,17,88];",
         'mobile targets')
else:
    s = s.replace(
        "const desktopTargets=[62.5,71.5,53,78,46,84,39,89,33,93,27,96,22,98];",
        "const desktopTargets=[62.5,71.5,53,78,46,84,39,89,33,93,27,96,22,98];\n  const mobileTargets=[47,57,40,64,34,70,29,75,24,80,20,84,17,88];",
        1)
sub1(r"const finalScale=\[[^\]]+\];",
     "const finalScale=[1.03,1.00,.92,.90,.88,.87,.85,.84,.82,.81,.80,.79,.78,.77];",
     'final scales')
sub1(r"const finalAlpha=\[[^\]]+\];",
     "const finalAlpha=[1,1,.97,.96,.95,.94,.93,.92,.90,.89,.88,.86,.84,.82];",
     'final alpha')
sub1(r"const fit=clamp\([^;]+;",
     "const fit=clamp((rect.bottom+40)/(h*.84),.76,1);",
     'fit clamp')
sub1(r"const local=i===0\?1:ease\(clamp\(\(p-delay\)/Math\.max\(\.44-delay,\.10\)\)\);",
     "const local=i<=1?1:ease(clamp((p-delay)/Math.max(.44-delay,.10)));",
     'local reveal')
sub1(r"const rawTarget=desktopTargets\[i\] \?\? basePct;\s*const targetPct=mobile \? 50\+\(rawTarget-66\)\*\.55 : rawTarget;",
     "const rawTarget=desktopTargets[i] ?? basePct;\n      const targetPct=mobile ? (mobileTargets[i] ?? 50) : rawTarget;",
     'target pct', flags=re.S)
s = s.replace('interaction=Math.max(interaction,.30);', 'interaction=Math.max(interaction,.44);', 1)

p.write_text(s, encoding='utf-8')
print('hero split fan patch applied')
