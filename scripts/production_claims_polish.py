from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls={
"'posture corrector':'Redresse les épaules et soutient le dos pour une meilleure posture au quotidien, dès les premières minutes de port.'":"'posture corrector':'Aide au retour et au maintien vers un alignement naturel, avec un soutien postural confortable au quotidien.'",
"'wrist support':'Soutien du poignet pour soulager la tension liée aux gestes répétitifs.'":"'wrist support':'Soutien confortable du poignet pour accompagner les gestes répétitifs et les activités du quotidien.'",
"'ankle support':'Stabilise la cheville, réduit les risques de gêne pendant l\\'effort.'":"'ankle support':'Maintien ajustable de la cheville pour accompagner le mouvement pendant vos activités.'",
"'elbow support':'Compression légère pour soulager la douleur au coude.'":"'elbow support':'Compression légère et maintien confortable du coude pendant les activités du quotidien.'",
"'back support belt':'Ceinture lombaire ajustable pour soutenir le bas du dos.'":"'back support belt':'Ceinture ajustable pensée pour apporter un maintien confortable au bas du dos.'",
"'neck support pillow':'Coussin ergonomique qui soulage les tensions de la nuque.'":"'neck support pillow':'Coussin ergonomique pensé pour favoriser une position confortable de la nuque au repos.'",
"'reusable ice/hot pack':'Compresse réutilisable chaude ou froide pour soulager rapidement.'":"'reusable ice/hot pack':'Compresse réutilisable chaude ou froide pour une sensation de confort ciblée selon votre routine.'",
"'compression socks':'Chaussettes de compression pour stimuler la circulation et réduire la fatigue des jambes.'":"'compression socks':'Chaussettes de compression conçues pour offrir un maintien ajusté et un confort régulier des jambes.'",
"return genDesc(cat, name) + \" Fabriqué avec des matériaux résistants et respirants, ce produit AXORIA est conçu pour un usage quotidien prolongé, que ce soit au bureau, à la maison ou pendant le sport. Réglable et ajustable pour s'adapter à toutes les morphologies.\";":"return genDesc(cat, name) + \" Sélectionné pour son confort et sa praticité, ce produit AXORIA s'intègre facilement à une routine au bureau, à la maison ou pendant vos activités, selon son usage et votre confort.\";"
}
for old,new in repls.items():
    if old not in s: raise RuntimeError('missing claim anchor: '+old[:45])
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('production claims polished')
