from pathlib import Path
import re, json

path = Path('index.html')
s = path.read_text(encoding='utf-8')

# SEO copy aligned with AXORIA's broader wellness positioning.
s = s.replace(
    '<title>AXORIA — Feel Better, Every Day</title>',
    '<title>AXORIA Maroc — Feel Better, Every Day | Bien-être & Confort</title>'
)
s = s.replace(
    '<meta name="description" content="AXORIA — correcteur de posture et ceinture amincissante premium. Marque marocaine de bien-être. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta name="description" content="AXORIA, marque marocaine de bien-être et de confort au quotidien. Découvrez nos accessoires sélectionnés avec livraison partout au Maroc et paiement à la livraison.">'
)
s = s.replace(
    '<meta property="og:description" content="Correcteur de posture et ceinture amincissante premium. Livraison partout au Maroc, paiement à la livraison.">',
    '<meta property="og:description" content="Bien-être, confort et accessoires du quotidien par AXORIA. Livraison partout au Maroc et paiement à la livraison.">'
)

# Search/social crawler hints. Avoid duplicates when the workflow is re-run.
head_anchor = '<meta property="og:description" content="Bien-être, confort et accessoires du quotidien par AXORIA. Livraison partout au Maroc et paiement à la livraison.">'
extra_meta = '''\n<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">\n<meta property="og:site_name" content="AXORIA">\n<meta property="og:type" content="website">\n<meta property="og:url" content="https://axoria.ma/">\n<meta name="twitter:card" content="summary_large_image">'''
if 'name="robots"' not in s:
    s = s.replace(head_anchor, head_anchor + extra_meta, 1)
if 'rel="canonical"' not in s:
    s = s.replace('</title>', '</title>\n<link rel="canonical" href="https://axoria.ma/">', 1)

# Enrich the existing Store schema without inventing sales figures or ratings.
store_match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', s, flags=re.S)
if store_match:
    try:
        store = json.loads(store_match.group(1))
        if store.get('@type') == 'Store':
            store.update({
                'url': 'https://axoria.ma/',
                'description': "Marque marocaine de bien-être et de confort au quotidien, avec livraison partout au Maroc et paiement à la livraison.",
                'currenciesAccepted': 'MAD',
                'paymentAccepted': 'Cash on Delivery',
                'areaServed': {'@type': 'Country', 'name': 'Morocco'}
            })
            store.pop('priceRange', None)
            new_block = '<script type="application/ld+json">\n' + json.dumps(store, ensure_ascii=False, indent=2) + '\n</script>'
            s = s[:store_match.start()] + new_block + s[store_match.end():]
    except Exception:
        pass

# Give each product card a stable fragment identifier for semantic linking/schema IDs.
s = s.replace(
    '<div class="pcard reveal in" data-id="${p.id}">',
    '<div class="pcard reveal in" id="product-${p.id}" data-id="${p.id}">'
)

seo_fn = r'''
/* ---------- SEO: live product structured data ---------- */
function updateProductStructuredData(){
  try{
    const products=(Array.isArray(PRODUCTS)?PRODUCTS:[]).filter(p=>p && p.visible);
    let node=document.getElementById('axoriaProductSchema');
    if(!node){
      node=document.createElement('script');
      node.type='application/ld+json';
      node.id='axoriaProductSchema';
      document.head.appendChild(node);
    }
    const itemList={
      '@type':'ItemList',
      name:'Produits AXORIA',
      itemListElement:products.map((p,i)=>({
        '@type':'ListItem',
        position:i+1,
        item:{
          '@type':'Product',
          '@id':`https://axoria.ma/#product-${encodeURIComponent(String(p.id))}`,
          name:String(p.name||''),
          image:p.img?[String(p.img)]:undefined,
          description:String(p.longDesc||p.desc||''),
          brand:{'@type':'Brand',name:'AXORIA'},
          url:'https://axoria.ma/#produits',
          offers:{
            '@type':'Offer',
            priceCurrency:'MAD',
            price:Number(p.price||0),
            availability:Number(p.stock||0)>0?'https://schema.org/InStock':'https://schema.org/OutOfStock',
            url:'https://axoria.ma/#produits',
            seller:{'@type':'Organization',name:'AXORIA'}
          }
        }
      }))
    };
    node.textContent=JSON.stringify({'@context':'https://schema.org','@graph':[itemList]});
  }catch(e){ console.warn('SEO product schema unavailable',e); }
}

'''
if 'function updateProductStructuredData()' not in s:
    s = s.replace('function renderMenuGrid(){', seo_fn + 'function renderMenuGrid(){', 1)
if 'function renderMenuGrid(){\n  updateProductStructuredData();' not in s:
    s = s.replace('function renderMenuGrid(){\n', 'function renderMenuGrid(){\n  updateProductStructuredData();\n', 1)

path.write_text(s, encoding='utf-8')

Path('robots.txt').write_text('''User-agent: *\nAllow: /\nDisallow: /admin.html\n\nSitemap: https://axoria.ma/sitemap.xml\n''', encoding='utf-8')

Path('sitemap.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>https://axoria.ma/</loc><lastmod>2026-10-07</lastmod><priority>1.0</priority></url>\n  <url><loc>https://axoria.ma/shipping-returns.html</loc><lastmod>2026-10-07</lastmod><priority>0.5</priority></url>\n  <url><loc>https://axoria.ma/privacy.html</loc><lastmod>2026-10-07</lastmod><priority>0.3</priority></url>\n  <url><loc>https://axoria.ma/terms.html</loc><lastmod>2026-10-07</lastmod><priority>0.3</priority></url>\n</urlset>\n''', encoding='utf-8')

print('AXORIA SEO foundation applied')
