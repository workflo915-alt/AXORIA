from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""    // Let the bridge settle deeper into the viewport before the fan starts opening.\n    const enterStart=vh*.76;\n    const enterEnd=vh*.34;\n    const scrollP=clamp((enterStart-rect.top)/Math.max(enterStart-enterEnd,1));\n    const p=Math.max(scrollP,interaction);"""
new="""    // Mobile uses a later reveal so secondary characters first sit behind\n    // the athlete duo, then fan out only after the bridge is clearly visible.\n    const enterStart=mobile ? vh*.58 : vh*.76;\n    const enterEnd=mobile ? vh*.18 : vh*.34;\n    const scrollP=clamp((enterStart-rect.top)/Math.max(enterStart-enterEnd,1));\n    const p=Math.max(scrollP,interaction);"""
if old not in s:
    raise RuntimeError('fan timing anchor not found')
s=s.replace(old,new,1)

old2="""      const local=isAthlete ? 1 : ease(clamp((p-delay)/Math.max(.58-delay,.16)));"""
new2="""      const mobileDelay=mobile ? Math.max(delay,.12) : delay;\n      const mobileSpan=mobile ? .72 : .58;\n      const local=isAthlete ? 1 : ease(clamp((p-mobileDelay)/Math.max(mobileSpan-mobileDelay,.18)));"""
if old2 not in s:
    raise RuntimeError('fan local progress anchor not found')
s=s.replace(old2,new2,1)

old3="""      const y=isAthlete ? 0 : (1-local)*(mobile?10:14)+local*(mobile?1:2);"""
new3="""      const y=isAthlete ? 0 : (1-local)*(mobile?5:14)+local*(mobile?1:2);"""
if old3 not in s:
    raise RuntimeError('fan vertical anchor not found')
s=s.replace(old3,new3,1)

p.write_text(s,encoding='utf-8')
print('Mobile character stack/fan timing fixed')
