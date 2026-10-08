from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''  .hero{height:100svh;min-height:620px;}\n  .hero-content{padding:0 18px 46px;}'''
new='''  .hero{height:auto;min-height:0;display:block;padding:46px 0 28px;}\n  .hero-content{padding:0 18px 24px;}'''
if old not in s:
    raise RuntimeError('mobile hero anchor not found')
s=s.replace(old,new,1)

old2='''  .hero{min-height:600px;}\n  .hero h1{font-size:37px;}'''
new2='''  .hero{min-height:0;padding-top:38px;}\n  .hero h1{font-size:37px;}'''
if old2 not in s:
    raise RuntimeError('360 hero anchor not found')
s=s.replace(old2,new2,1)

p.write_text(s,encoding='utf-8')
print('Compact mobile hero applied')
