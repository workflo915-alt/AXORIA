from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def r(old,new,label):
    global s
    if old not in s:
        if new in s:
            print(f'[skip] {label}')
            return
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

r(
"finalCtaTitle:'Prêt(e) à améliorer votre quotidien ?', finalCtaText:'Rejoignez des centaines de clients au Maroc qui font déjà confiance à AXORIA pour plus de confort et de bien-être au quotidien.', finalCtaBtn:'Commander maintenant'",
"finalCtaTitle:'Prêt(e) à améliorer votre quotidien ?', finalCtaText:'Découvrez les essentiels AXORIA pensés pour le confort et le bien-être au quotidien, avec livraison partout au Maroc et paiement à la livraison.', finalCtaBtn:'Commander maintenant'",
'fr final CTA'
)
r(
"finalCtaTitle:'Ready to feel better every day?', finalCtaText:'Join hundreds of customers across Morocco who already trust AXORIA for everyday comfort and wellbeing.', finalCtaBtn:'Order Now'",
"finalCtaTitle:'Ready to feel better every day?', finalCtaText:'Discover AXORIA essentials designed for everyday comfort and wellbeing, with delivery across Morocco and cash on delivery.', finalCtaBtn:'Order Now'",
'en final CTA'
)
r(
"finalCtaTitle:'مستعد لتشعر بتحسن كل يوم؟', finalCtaText:'انضم إلى مئات العملاء في المغرب الذين يثقون في أكسوريا لمزيد من الراحة والعناية في حياتهم اليومية.', finalCtaBtn:'اطلب الآن'",
"finalCtaTitle:'مستعد لتشعر بتحسن كل يوم؟', finalCtaText:'اكتشف أساسيات أكسوريا المصممة للراحة والعناية اليومية، مع التوصيل لجميع مدن المغرب والدفع عند الاستلام.', finalCtaBtn:'اطلب الآن'",
'ar final CTA'
)
r(
'<button class="fab top" id="topBtn"><svg',
'<button class="fab top" id="topBtn" aria-label="Back to top"><svg',
'top button aria label'
)

p.write_text(s,encoding='utf-8')
print('Phase 5 truthful copy patch applied.')
