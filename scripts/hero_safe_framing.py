from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Keep the athlete duo fully inside the hero while preserving their visual presence.
# Enlarge supporting characters slightly on desktop, but keep mobile rules untouched.
override = """
/* hero-safe-framing-v3 */
@media (min-width:901px){
  .hero-character{width:clamp(154px,18vw,268px);}
  .hero-character.is-main{bottom:-1.2%;width:clamp(210px,23vw,342px);}
  .hero-character.is-featured{bottom:-1.2%;width:clamp(210px,22.7vw,332px);}
}
@media (min-width:901px) and (max-height:780px){
  .hero-character.is-main{width:clamp(198px,21vw,310px);}
  .hero-character.is-featured{width:clamp(198px,20.5vw,304px);}
}
"""

marker='/* hero-safe-framing-v3 */'
if marker not in s:
    pos=s.find('</style>')
    if pos<0:
        raise SystemExit('style closing tag not found')
    s=s[:pos]+override+'\n'+s[pos:]

# Reduce only the final scale of the two athlete leads so heads/feet never clip.
m=re.search(r"const\s+finalScale\s*=\s*\[([^\]]+)\];",s)
if not m:
    raise SystemExit('finalScale array not found')
vals=[v.strip() for v in m.group(1).split(',')]
if len(vals)<2:
    raise SystemExit('finalScale array too short')
vals[0]='.94'
vals[1]='.94'
new_arr='const finalScale=['+','.join(vals)+'];'
s=s[:m.start()]+new_arr+s[m.end():]

p.write_text(s,encoding='utf-8')
print('hero safe framing applied')
