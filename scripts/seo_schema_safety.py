from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_image = "          image:p.img?[String(p.img)]:undefined,"
new_image = "          image:(p.img && /^https?:\\/\\//i.test(String(p.img)))?[String(p.img)]:undefined,"
if old_image in s:
    s = s.replace(old_image, new_image, 1)

old_url = "          url:'https://axoria.ma/#produits',"
new_url = "          url:`https://axoria.ma/#product-${encodeURIComponent(String(p.id))}`,"
# Product URL and Offer URL should both point to the stable product card fragment.
s = s.replace(old_url, new_url, 2)

p.write_text(s, encoding='utf-8')
print('AXORIA product schema safety polish applied')
