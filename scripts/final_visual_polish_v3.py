from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
text=INDEX.read_text(encoding='utf-8')

old="""    const vh=Math.max(window.innerHeight,1);\n    const enterStart=vh*.92;\n    const enterEnd=vh*.46;\n    const scrollP=clamp((enterStart-rect.top)/Math.max(enterStart-enterEnd,1));"""
new="""    const vh=Math.max(window.innerHeight,1);\n    // Let the bridge settle deeper into the viewport before the fan starts opening.\n    const enterStart=vh*.76;\n    const enterEnd=vh*.34;\n    const scrollP=clamp((enterStart-rect.top)/Math.max(enterStart-enterEnd,1));"""
if old not in text:
    raise RuntimeError('scroll fan timing anchor not found')
text=text.replace(old,new,1)

# Make the reveal feel a touch more gradual after the delayed start.
old2="const local=isAthlete ? 1 : ease(clamp((p-delay)/Math.max(.48-delay,.12)));"
new2="const local=isAthlete ? 1 : ease(clamp((p-delay)/Math.max(.58-delay,.16)));"
if old2 not in text:
    raise RuntimeError('fan easing anchor not found')
text=text.replace(old2,new2,1)

INDEX.write_text(text,encoding='utf-8')
print('Final visual polish v3 applied.')
