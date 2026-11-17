#!/usr/bin/env node
/*
 * AXORIA — SEO build. No dependencies (Node 18+).
 *
 *     node tools/seo-build.mjs
 *
 * Run it after changing products in admin.html or texts in index.html, then
 * commit and deploy. It:
 *   1. writes the French texts and the current catalog into index.html, so Google,
 *      WhatsApp/Facebook previews and AI crawlers see real content without running
 *      JavaScript (the page script still refreshes everything on load);
 *   2. writes one page per visible product in /produits/ (title, description, photo,
 *      price, Product schema) from the live Supabase catalog;
 *   3. saves product photos that are stored as base64 in the database to
 *      /assets/products/ so they get a real, indexable URL;
 *   4. updates sitemap.xml.
 * Product page addresses and titles are set in tools/seo-products.json.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SITE = 'https://axoria.ma';
const SUPABASE_URL = 'https://gdemgpkkrmpridqgjmtx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_LcXsTIdML2gITtM8UDqtWw_toCYU4qD'; // public read key, same as the storefront
const WHATSAPP = '212621575115';
const PRODUCTS_DIR = 'produits';
const TODAY = new Date().toISOString().slice(0, 10);

/* ---------- files (keeps each file's existing line endings) ---------- */
const abs = (rel) => path.join(ROOT, ...rel.split('/'));
const eolOf = new Map();
function read(rel) {
  const text = fs.readFileSync(abs(rel), 'utf8');
  eolOf.set(rel, text.includes('\r\n') ? '\r\n' : '\n');
  return text.replace(/\r\n/g, '\n');
}
function write(rel, text) {
  fs.mkdirSync(path.dirname(abs(rel)), { recursive: true });
  const eol = eolOf.get(rel) || '\n';
  fs.writeFileSync(abs(rel), eol === '\n' ? text : text.replace(/\n/g, eol));
}

/* ---------- text helpers ---------- */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const plain = (s) => String(s ?? '').replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '').replace(/\s+/g, ' ').trim();
function clip(s, max) {
  if (s.length <= max) return s;
  const cut = s.slice(0, max - 1);
  return cut.slice(0, cut.lastIndexOf(' ')).replace(/[\s,;:.—-]+$/, '') + '…';
}
const slugify = (s) => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const price = (n) => `${Number(n)} DH`;

/* ---------- read declarations out of the page script ---------- */
// Walks JS source from an opening "{" to its matching "}", skipping strings, templates, comments and regexes.
function matchBrace(src, open) {
  let depth = 0, prev = '';
  for (let i = open; i < src.length;) {
    const c = src[i];
    if (c === '/' && src[i + 1] === '/') { i = src.indexOf('\n', i); if (i < 0) break; continue; }
    if (c === '/' && src[i + 1] === '*') { i = src.indexOf('*/', i + 2) + 2; continue; }
    if (c === "'" || c === '"') { i = skipString(src, i, c); prev = c; continue; }
    if (c === '`') { i = skipTemplate(src, i); prev = '`'; continue; }
    if (c === '/' && (prev === '' || '(,=:[!&|?{};+-*%~^<>'.includes(prev))) { i = skipRegex(src, i); prev = '/'; continue; }
    if (c === '{') depth++;
    else if (c === '}' && --depth === 0) return i + 1;
    if (!/\s/.test(c)) prev = c;
    i++;
  }
  throw new Error('index.html: unbalanced braces in the page script');
}
function skipString(src, i, quote) {
  for (i++; src[i] !== quote; i++) { if (src[i] === '\\') i++; if (i >= src.length) throw new Error('unterminated string'); }
  return i + 1;
}
function skipTemplate(src, i) {
  for (i++; src[i] !== '`';) {
    if (src[i] === '\\') i += 2;
    else if (src[i] === '$' && src[i + 1] === '{') i = matchBrace(src, i + 1);
    else i++;
    if (i >= src.length) throw new Error('unterminated template literal');
  }
  return i + 1;
}
function skipRegex(src, i) {
  let inClass = false;
  for (i++; ; i++) {
    const c = src[i];
    if (c === '\\') { i++; continue; }
    if (c === '\n' || i >= src.length) throw new Error('unterminated regex');
    if (c === '[') inClass = true;
    else if (c === ']') inClass = false;
    else if (c === '/' && !inClass) break;
  }
  for (i++; /[a-z]/i.test(src[i]); i++);
  return i;
}
function declaration(src, head) {
  const start = src.indexOf(head);
  if (start < 0) throw new Error(`index.html: "${head}" not found in the page script`);
  let end = matchBrace(src, src.indexOf('{', start));
  if (src[end] === ';') end++;
  return src.slice(start, end);
}

/* ---------- replace the content of the element that has id="…" ---------- */
function setInner(html, id, inner) {
  const open = new RegExp(`<([a-zA-Z][a-zA-Z0-9]*)\\b[^>]*\\sid="${id}"[^>]*>`).exec(html);
  if (!open) return null;
  const tag = open[1].toLowerCase();
  const start = open.index + open[0].length;
  const tags = new RegExp(`<(/?)${tag}\\b[^>]*>`, 'gi');
  tags.lastIndex = start;
  for (let depth = 1, t; (t = tags.exec(html));) {
    if (!t[1]) { depth++; continue; }
    if (--depth === 0) return html.slice(0, start) + inner + html.slice(t.index);
  }
  throw new Error(`index.html: element #${id} is not closed`);
}

// JSON that is safe inside a <script> element.
const scriptJson = (value) => JSON.stringify(value).replace(/</g, '\\u003c');
// Rewrites `const NAME = …;` between its /*NAME:BEGIN*/ and /*NAME:END*/ markers in the page script.
function setJsConst(html, name, value) {
  const re = new RegExp(`/\\*${name}:BEGIN\\*/[\\s\\S]*?/\\*${name}:END\\*/`);
  if (!re.test(html)) throw new Error(`index.html: markers /*${name}:BEGIN*/ … /*${name}:END*/ not found`);
  return html.replace(re, () => `/*${name}:BEGIN*/\nconst ${name} = ${scriptJson(value)};\n/*${name}:END*/`);
}

/* ---------- data ---------- */
async function loadCatalog() {
  const url = `${SUPABASE_URL}/rest/v1/axoria_store?select=key,value&key=in.(axoria_products,axoria_categories)`;
  const res = await fetch(url, { headers: { apikey: SUPABASE_KEY } });
  if (!res.ok) throw new Error(`Supabase answered ${res.status}: ${await res.text()}`);
  const rows = Object.fromEntries((await res.json()).map((r) => [r.key, r.value]));
  if (!Array.isArray(rows.axoria_products) || !rows.axoria_products.length) throw new Error('No products returned by Supabase — nothing written.');
  return { products: rows.axoria_products, categories: Array.isArray(rows.axoria_categories) ? rows.axoria_categories : [] };
}

// Approved customer reviews: public data, the same list the storefront shows.
async function loadReviews() {
  const base = `${SUPABASE_URL}/rest/v1/review_submissions?status=eq.approved&order=created_at.desc`;
  // Before the product_id column exists in the database, read the reviews without it.
  for (const cols of ['name,rating,comment,created_at,product_id', 'name,rating,comment,created_at']) {
    const res = await fetch(`${base}&select=${cols}`, { headers: { apikey: SUPABASE_KEY } });
    if (!res.ok) continue;
    return (await res.json()).map((r) => ({
      name: String(r.name || ''), rating: Number(r.rating) || 0, comment: String(r.comment || ''), loc: 'Maroc',
      product_id: r.product_id ? String(r.product_id) : '', created_at: r.created_at,
    }));
  }
  console.warn('warning: approved reviews could not be read; pages are built without them');
  return [];
}

/* ---------- reviews on product pages ---------- */
const starsText = (n) => { const k = Math.max(0, Math.min(5, Math.round(Number(n) || 0))); return '★'.repeat(k) + '☆'.repeat(5 - k); };
const reviewDate = (d) => {
  const t = new Date(d);
  return Number.isNaN(t.getTime()) ? '' : t.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Africa/Casablanca' });
};
function reviewSchema(r) {
  return {
    '@type': 'Review', author: { '@type': 'Person', name: plain(r.name) || 'Client AXORIA' },
    datePublished: String(r.created_at || '').slice(0, 10) || undefined, reviewBody: plain(r.comment),
    reviewRating: { '@type': 'Rating', ratingValue: r.rating, bestRating: 5, worstRating: 1 },
  };
}
function reviewsHtml(reviews, avg) {
  if (!reviews.length) return '<p>Aucun avis pour le moment. Vous avez acheté ce produit ? Votre avis aide les autres clients à choisir.</p>';
  const items = reviews.slice(0, 10).map((r) => {
    const day = reviewDate(r.created_at);
    return `<li><span class="st">${starsText(r.rating)}</span> <strong>${esc(r.name)}</strong>${day ? ` <time datetime="${esc(String(r.created_at).slice(0, 10))}">${esc(day)}</time>` : ''}<p>${esc(r.comment)}</p></li>`;
  });
  return `<p class="rating-big"><span class="st">${starsText(avg)}</span> ${avg.toFixed(1)} / 5 · ${reviews.length} avis</p><ul class="reviews">${items.join('')}</ul>`;
}

// Photos stored as base64 in the database become files with a real URL.
function productImage(p) {
  const m = /^data:image\/(jpeg|png|webp);base64,(.+)$/s.exec(String(p.img || ''));
  if (!m) return /^https?:\/\//.test(String(p.img || '')) ? { url: String(p.img), local: null } : { url: null, local: null };
  const rel = `assets/products/${p.id}.${m[1] === 'jpeg' ? 'jpg' : m[1]}`;
  const bytes = Buffer.from(m[2], 'base64');
  if (!fs.existsSync(abs(rel)) || !fs.readFileSync(abs(rel)).equals(bytes)) {
    fs.mkdirSync(path.dirname(abs(rel)), { recursive: true });
    fs.writeFileSync(abs(rel), bytes);
  }
  return { url: `/${rel}`, local: `/${rel}` };
}

function descriptionParts(p) {
  const lines = String(p.desc || '').split(/\n+/).map((l) => l.trim()).filter(Boolean);
  const bullets = lines.filter((l) => l.startsWith('✅')).map(plain);
  // Delivery/payment lines and the slogan are covered by the trust list on the page.
  const paragraphs = lines.filter((l) => !l.startsWith('✅') && !/livraison|paiement|feel better/i.test(l)).map(plain);
  const details = plain(p.longDesc) && plain(p.longDesc) !== plain(p.desc) ? [plain(p.longDesc)] : [];
  return { bullets, paragraphs, details };
}

/* ---------- guides linked from product pages (internal linking for SEO) ---------- */
const GUIDES = {
  posture: [
    { href: '/fr/guides/correcteur-posture-guide.html', title: 'Correcteur de posture : comment le choisir et le porter' },
    { href: '/fr/guides/posture-bureau.html', title: 'Comment améliorer sa posture au bureau ?' },
  ],
  massage: [
    { href: '/fr/guides/nuque-epaules-detente.html', title: 'Nuque et épaules tendues : une routine simple après le travail' },
    { href: '/fr/guides/recuperation-sportive.html', title: 'Récupération après le sport : les bases' },
  ],
};
const guidesFor = (p) => (/massage|détente/i.test(String(p.cat || '')) ? GUIDES.massage : GUIDES.posture);

/* ---------- product feed: Meta Commerce Manager (catalog ads) + Google Merchant Center ---------- */
const FEED_CATEGORY = {
  'Support & Récupération': 'Health & Beauty > Health Care > Supports & Braces',
  'Massage & Détente': 'Health & Beauty > Personal Care > Massage & Relaxation > Massagers',
};
function feedDescription(p) {
  const { bullets, paragraphs, details } = descriptionParts(p);
  return [...paragraphs, ...bullets.map((b) => `${b.replace(/[.!]+$/, '')}.`), ...details].join(' ').trim();
}
function productFeedXml(products, pages, config, policy) {
  const x = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
  const mad = (n) => `${Number(n).toFixed(2)} MAD`;
  // Same delivery terms as the product pages (OFFER_POLICY in index.html).
  const ship = policy.shippingDetails;
  const shipping = `      <g:shipping>\n        <g:country>${x(ship.shippingDestination.addressCountry)}</g:country>\n        <g:price>${mad(ship.shippingRate.value)}</g:price>\n      </g:shipping>`;
  const items = products.map((p) => {
    const page = pages[String(p.id)];
    const cfg = config[String(p.id)] || {};
    const image = page.imageUrl.startsWith('http') ? page.imageUrl : `${SITE}${page.imageUrl}`;
    const inStock = p.stock === undefined || p.stock === null || Number(p.stock) > 0;
    // A crossed-out price on the site becomes price + sale_price, so catalog ads show the discount too.
    const onSale = Number(p.oldPrice) > Number(p.price);
    const fields = [
      ['g:id', p.id], ['g:title', page.name], ['g:description', feedDescription(p) || page.name],
      ['g:link', `${SITE}${page.url}`], ['g:image_link', image], ['g:brand', 'AXORIA'], ['g:condition', 'new'],
      ['g:availability', inStock ? 'in_stock' : 'out_of_stock'],
      ['g:price', mad(onSale ? p.oldPrice : p.price)], ['g:sale_price', onSale ? mad(p.price) : undefined],
      ['g:identifier_exists', 'no'], ['g:product_type', p.cat],
      ['g:google_product_category', FEED_CATEGORY[p.cat]], ['g:item_group_id', cfg.group], ['g:color', cfg.color],
    ];
    return `    <item>\n${fields.filter(([, v]) => v !== undefined && v !== '').map(([k, v]) => `      <${k}>${x(v)}</${k}>`).join('\n')}\n${shipping}\n    </item>`;
  });
  return `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n  <channel>\n    <title>AXORIA — catalogue</title>\n    <link>${SITE}/</link>\n    <description>Produits AXORIA, livraison gratuite partout au Maroc et paiement à la livraison.</description>\n${items.join('\n')}\n  </channel>\n</rss>\n`;
}

/* ---------- product page ---------- */
function productPageHtml(p, page, ctx) {
  const { bullets, paragraphs, details } = descriptionParts(p);
  const url = `${SITE}${page.url}`;
  const inStock = p.stock === undefined || p.stock === null || Number(p.stock) > 0;
  const image = page.imageUrl ? (page.imageUrl.startsWith('http') ? page.imageUrl : `${SITE}${page.imageUrl}`) : `${SITE}/assets/brand/og-axoria.jpg`;
  const summary = bullets.length
    ? `${bullets.slice(0, 2).map((b, i) => (i ? b.charAt(0).toLowerCase() + b.slice(1) : b)).join(', ')}.`
    : (paragraphs[0] || plain(p.desc));
  const metaDescription = clip(`${page.name} à ${price(p.price)}. Livraison gratuite partout au Maroc, paiement à la livraison. ${summary}`, 158);
  const waText = inStock
    ? `Bonjour AXORIA ! Je souhaite commander : ${page.name} (${price(p.price)}).\n${url}`
    : `Bonjour AXORIA ! Prévenez-moi quand ce produit est de retour en stock : ${page.name}.\n${url}`;
  const waLink = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(waText)}`;
  const faqs = (ctx.i18n.faqs || []).slice(0, 5);
  const others = ctx.pages.filter((o) => o.id !== page.id);
  const reviews = (ctx.reviews || []).filter((r) => r.product_id === String(p.id) && r.rating > 0);
  const avg = reviews.length ? Math.round((reviews.reduce((s, r) => s + r.rating, 0) / reviews.length) * 10) / 10 : 0;
  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Product',
        '@id': `${url}#product`,
        name: page.name,
        image: [image],
        description: plain([summary, ...paragraphs, ...details].join(' ')),
        sku: String(p.id),
        category: p.cat || undefined,
        brand: { '@type': 'Brand', name: 'AXORIA' },
        aggregateRating: reviews.length ? { '@type': 'AggregateRating', ratingValue: avg, reviewCount: reviews.length, bestRating: 5, worstRating: 1 } : undefined,
        review: reviews.length ? reviews.slice(0, 10).map(reviewSchema) : undefined,
        offers: {
          '@type': 'Offer',
          url,
          priceCurrency: 'MAD',
          price: Number(p.price),
          availability: inStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
          itemCondition: 'https://schema.org/NewCondition',
          seller: { '@type': 'Organization', name: 'AXORIA', url: `${SITE}/` },
          ...ctx.policy,
        },
      },
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Accueil', item: `${SITE}/` },
          { '@type': 'ListItem', position: 2, name: page.name, item: url },
        ],
      },
    ],
  };
  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(page.name)} | AXORIA Maroc</title>
<meta name="description" content="${esc(metaDescription)}">
<link rel="canonical" href="${url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="product">
<meta property="og:site_name" content="AXORIA">
<meta property="og:locale" content="fr_MA">
<meta property="og:url" content="${url}">
<meta property="og:title" content="${esc(page.name)} — ${esc(price(p.price))}">
<meta property="og:description" content="${esc(metaDescription)}">
<meta property="og:image" content="${esc(image)}">
<meta property="product:price:amount" content="${Number(p.price)}">
<meta property="product:price:currency" content="MAD">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/brand/favicon-48.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<meta name="theme-color" content="#0A1220">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">${scriptJson(schema)}</script>
<style>
:root{--bg:#0A1220;--surface:#101E33;--line:#1E2E47;--text:#EAF1FB;--soft:#9FB0C8;--blue:#2F80ED;--teal:#20BFA9;--gold:#C9A227;--wa:#1FA855}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;max-width:1120px;margin:auto;padding:14px 20px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-family:Unbounded,sans-serif;font-weight:800;text-decoration:none;letter-spacing:.02em}
.top nav{display:flex;gap:18px;font-size:14px;font-weight:600}
.top nav a{text-decoration:none;color:var(--soft)}
.top nav a:hover{color:var(--text)}
.wrap{max-width:1120px;margin:auto;padding:18px 20px 64px}
.crumbs{font-size:13px;color:var(--soft);margin-bottom:18px}
.crumbs a{text-decoration:none}
.product{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:40px;align-items:start}
.media{background:#fff;border-radius:24px;overflow:hidden;aspect-ratio:1/1}
.media img{width:100%;height:100%;object-fit:contain;display:block}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
h1{font-family:Unbounded,sans-serif;font-size:clamp(26px,4vw,40px);line-height:1.15;margin:10px 0 14px}
h2{font-family:Unbounded,sans-serif;font-size:22px;margin:0 0 14px}
h3{font-size:16px;margin:18px 0 6px}
.price{display:flex;align-items:baseline;gap:12px;font-size:30px;font-weight:800}
.price s{font-size:18px;color:var(--soft);font-weight:600}
.stock{display:inline-block;margin:10px 0 16px;padding:5px 12px;border-radius:999px;font-size:13px;font-weight:700}
.stock.in{background:rgba(31,168,85,.15);color:#4ADE80}
.stock.out{background:rgba(211,71,71,.15);color:#F87171}
.lead{color:var(--soft);margin:0 0 12px}
.ticks{list-style:none;padding:0;margin:0 0 18px}
.ticks li{padding-left:26px;position:relative;margin:6px 0}
.ticks li::before{content:'✓';position:absolute;left:0;color:var(--teal);font-weight:800}
.ctas{display:grid;gap:10px;margin:18px 0}
.btn{display:block;text-align:center;padding:15px 18px;border-radius:14px;font-weight:700;text-decoration:none;font-size:16px}
.btn.primary{background:linear-gradient(100deg,#0A4D9B,var(--blue));color:#fff}
.btn.wa{background:var(--wa);color:#fff}
.btn.disabled{background:var(--surface);color:var(--soft);border:1px solid var(--line);pointer-events:none}
.trust{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:8px;font-size:14px;color:var(--soft)}
.trust li::before{content:'•';color:var(--gold);margin-right:8px}
section{margin-top:44px;padding-top:28px;border-top:1px solid var(--line)}
section p{color:var(--soft);margin:0 0 12px}
.others{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;list-style:none;padding:0;margin:0}
.others a{display:block;padding:16px;border:1px solid var(--line);border-radius:16px;background:var(--surface);text-decoration:none;font-weight:600}
.others span{display:block;color:var(--gold);font-size:14px;margin-top:4px}
.st{color:#FFC107;letter-spacing:1px}
.rating{display:inline-flex;align-items:center;gap:8px;margin:8px 0 0;color:var(--soft);font-size:14px;font-weight:600;text-decoration:none}
.rating[hidden]{display:none}
section p.rating-big{font-size:17px;font-weight:700;color:var(--text)}
.reviews{list-style:none;padding:0;margin:0 0 18px;display:grid;gap:12px}
.reviews li{border:1px solid var(--line);border-radius:16px;padding:14px 16px;background:var(--surface)}
section .reviews li p{margin:6px 0 0;color:var(--text)}
.reviews time{color:var(--soft);font-size:13px;margin-left:6px}
.btn.ghost{display:inline-block;border:1px solid var(--line);color:var(--text);background:transparent;padding:12px 18px;font-size:15px}
footer{border-top:1px solid var(--line);padding:24px 20px;text-align:center;font-size:13px;color:var(--soft)}
footer a{margin:0 8px;text-decoration:none}
@media (max-width:760px){.product{grid-template-columns:1fr;gap:22px}.top nav{gap:12px;font-size:13px}}
</style>
</head>
<body>
<header class="top">
  <a class="brand" href="/"><img src="/assets/brand/axoria-logo-128.webp" alt="" width="36" height="36">AXORIA</a>
  <nav><a href="/#menu">Produits</a><a href="/guides.html">Guides</a><a href="https://wa.me/${WHATSAPP}" rel="noopener">WhatsApp</a></nav>
</header>
<main class="wrap">
  <nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="/#menu">Produits</a> › <span>${esc(page.name)}</span></nav>
  <article class="product">
    <div class="media"><img src="${esc(page.imageUrl || '/assets/brand/og-axoria.jpg')}" alt="${esc(page.name)} — AXORIA" width="800" height="800" fetchpriority="high"></div>
    <div class="info">
      <span class="eyebrow">${esc(p.cat || 'AXORIA')}</span>
      <h1>${esc(page.name)}</h1>
      <div class="price"><span id="pPrice">${esc(price(p.price))}</span>${p.oldPrice ? ` <s id="pOld">${esc(price(p.oldPrice))}</s>` : ''}</div>
      <a class="rating" id="pRating" href="#avis"${reviews.length ? '' : ' hidden'}>${reviews.length ? `<span class="st">${starsText(avg)}</span> ${avg.toFixed(1)} · ${reviews.length} avis` : ''}</a>
      <span class="stock ${inStock ? 'in' : 'out'}" id="pStock">${inStock ? 'En stock — livraison gratuite en 24 à 72h' : 'Rupture de stock'}</span>
${paragraphs.map((t) => `      <p class="lead">${esc(t)}</p>`).join('\n')}
${bullets.length ? `      <ul class="ticks">${bullets.map((b) => `<li>${esc(b)}</li>`).join('')}</ul>` : ''}
      <div class="ctas">
        ${inStock ? `<a class="btn primary" id="pOrder" href="/?commander=${encodeURIComponent(p.id)}">Commander maintenant</a>` : `<span class="btn disabled" id="pOrder">Rupture de stock</span>`}
        <a class="btn wa" id="pWa" href="${esc(waLink)}" target="_blank" rel="noopener">${inStock ? 'Commander sur WhatsApp' : 'Être prévenu(e) sur WhatsApp'}</a>
      </div>
      <ul class="trust"><li>Livraison gratuite partout au Maroc</li><li>Paiement à la livraison, en espèces</li><li><a href="/shipping-returns.html">Retour possible sous 7 jours</a></li><li>Conseils et suivi sur WhatsApp 7j/7</li></ul>
    </div>
  </article>
${details.length ? `  <section>\n    <h2>Description</h2>\n${details.map((t) => `    <p>${esc(t)}</p>`).join('\n')}\n  </section>` : ''}
  <section id="avis">
    <h2>Avis clients</h2>
    <div id="pReviews">${reviewsHtml(reviews, avg)}</div>
    <a class="btn ghost" href="/?avis=${encodeURIComponent(p.id)}">Donner mon avis</a>
  </section>
  <section>
    <h2>Questions fréquentes</h2>
${faqs.map(([q, a]) => `    <h3>${esc(q)}</h3>\n    <p>${esc(a)}</p>`).join('\n')}
  </section>
${others.length ? `  <section>\n    <h2>Autres produits AXORIA</h2>\n    <ul class="others">${others.map((o) => `<li><a href="${o.url}">${esc(o.name)}<span>${esc(price(o.price))}</span></a></li>`).join('')}</ul>\n  </section>` : ''}
  <section>
    <h2>Guides utiles</h2>
    <ul class="others">${guidesFor(p).map((g) => `<li><a href="${g.href}">${esc(g.title)}<span>Lire le guide →</span></a></li>`).join('')}</ul>
  </section>
</main>
<footer>
  <a href="/">Boutique</a><a href="/guides.html">Guides</a><a href="/shipping-returns.html">Livraison &amp; retours</a><a href="/privacy.html">Confidentialité</a><a href="/terms.html">Conditions générales</a>
  <p>© ${new Date().getFullYear()} AXORIA — Feel Better, Every Day.</p>
</footer>
<script>
/* Keeps price and stock exact if the catalog changed since this page was generated. */
(function(){
  var ID=${JSON.stringify(String(p.id))};
  fetch(${JSON.stringify(`${SUPABASE_URL}/rest/v1/axoria_store?select=value&key=eq.axoria_products`)},{headers:{apikey:${JSON.stringify(SUPABASE_KEY)}}})
    .then(function(r){return r.ok?r.json():null;})
    .then(function(rows){
      var list=rows&&rows[0]&&rows[0].value; if(!Array.isArray(list)) return;
      var p=list.filter(function(x){return String(x.id)===ID;})[0];
      var order=document.getElementById('pOrder'), stock=document.getElementById('pStock');
      if(!p||p.visible===false){ stock.className='stock out'; stock.textContent='Produit indisponible'; order.outerHTML='<a class="btn primary" id="pOrder" href="/#menu">Voir les produits disponibles</a>'; return; }
      document.getElementById('pPrice').textContent=p.price+' DH';
      var old=document.getElementById('pOld'); if(old){ if(p.oldPrice) old.textContent=p.oldPrice+' DH'; else old.remove(); }
      var inStock=p.stock==null||Number(p.stock)>0;
      stock.className='stock '+(inStock?'in':'out'); stock.textContent=inStock?'En stock — livraison gratuite en 24 à 72h':'Rupture de stock';
      if(inStock&&order.tagName!=='A') order.outerHTML='<a class="btn primary" id="pOrder" href="/?commander='+encodeURIComponent(ID)+'">Commander maintenant</a>';
      if(!inStock&&order.tagName==='A') order.outerHTML='<span class="btn disabled" id="pOrder">Rupture de stock</span>';
    })
    .catch(function(){});
})();
</script>
<script>
/* Shows the reviews approved since this page was generated. */
(function(){
  var ID=${JSON.stringify(String(p.id))}, box=document.getElementById('pReviews'), link=document.getElementById('pRating');
  if(!box) return;
  var esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
  var stars=function(n){var k=Math.max(0,Math.min(5,Math.round(Number(n)||0)));return '★★★★★'.slice(0,k)+'☆☆☆☆☆'.slice(0,5-k);};
  fetch(${JSON.stringify(`${SUPABASE_URL}/rest/v1/review_submissions?select=name,rating,comment,created_at&status=eq.approved&order=created_at.desc&limit=10`)}+'&product_id=eq.'+encodeURIComponent(ID),{headers:{apikey:${JSON.stringify(SUPABASE_KEY)}}})
    .then(function(r){return r.ok?r.json():null;})
    .then(function(list){
      if(!Array.isArray(list)||!list.length) return;
      var n=list.length, avg=Math.round(list.reduce(function(s,r){return s+(Number(r.rating)||0);},0)/n*10)/10;
      box.innerHTML='<p class="rating-big"><span class="st">'+stars(avg)+'</span> '+avg.toFixed(1)+' / 5 · '+n+' avis</p><ul class="reviews">'+list.map(function(r){
        var d=new Date(r.created_at), day=isNaN(d.getTime())?'':d.toLocaleDateString('fr-FR',{day:'numeric',month:'long',year:'numeric'});
        return '<li><span class="st">'+stars(r.rating)+'</span> <strong>'+esc(r.name)+'</strong>'+(day?' <time>'+day+'</time>':'')+'<p>'+esc(r.comment)+'</p></li>';
      }).join('')+'</ul>';
      if(link){ link.hidden=false; link.innerHTML='<span class="st">'+stars(avg)+'</span> '+avg.toFixed(1)+' · '+n+' avis'; }
    })
    .catch(function(){});
})();
</script>
<script>
/* Ads: product pages are where ads land. Remember the Meta ad click (fbclid) for the order
   that may follow, and on the live site only tell the Pixel which product was viewed. */
(function(){
  var now=Date.now(), fbclid=new URLSearchParams(location.search).get('fbclid');
  var get=function(n){ var m=document.cookie.match(new RegExp('(?:^|; )'+n+'=([^;]*)')); return m?m[1]:''; };
  var set=function(n,v){ document.cookie=n+'='+v+'; path=/; max-age=7776000; SameSite=Lax'; };
  try{
    if(fbclid && get('_fbc').slice(-fbclid.length)!==fbclid) set('_fbc','fb.1.'+now+'.'+fbclid);
    if(!get('_fbp')) set('_fbp','fb.1.'+now+'.'+Math.floor(Math.random()*1e10));
  }catch(e){}
  if(!/^(www\\.)?axoria\\.ma$/.test(location.hostname)) return;
  fetch(${JSON.stringify(`${SUPABASE_URL}/rest/v1/axoria_store?select=value&key=eq.axoria_tracking`)},{headers:{apikey:${JSON.stringify(SUPABASE_KEY)}}})
    .then(function(r){return r.ok?r.json():[];})
    .then(function(rows){
      var cfg=(rows&&rows[0]&&rows[0].value)||{}, pixel=String(cfg.pixelId||'').trim();
      if(!cfg.enabled||!/^\\d{5,30}$/.test(pixel)) return;
      var start=function(){
        if(!window.fbq){
          var n=window.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments);};
          if(!window._fbq)window._fbq=n; n.push=n; n.loaded=true; n.version='2.0'; n.queue=[];
          var s=document.createElement('script'); s.async=true; s.src='https://connect.facebook.net/en_US/fbevents.js'; document.head.appendChild(s);
        }
        window.fbq('init',pixel);
        window.fbq('track','PageView');
        window.fbq('track','ViewContent',{content_ids:[${JSON.stringify(String(p.id))}],content_type:'product',content_name:${JSON.stringify(page.name)},value:${Number(p.price)},currency:'MAD'});
        var wa=document.getElementById('pWa'); if(wa) wa.addEventListener('click',function(){ window.fbq('track','Contact',{content_name:'WhatsApp'}); });
      };
      // Load the Pixel once the page is shown, so it never slows the product page down.
      if(document.readyState==='complete') setTimeout(start,1200); else addEventListener('load',function(){ setTimeout(start,1200); });
    })
    .catch(function(){});
})();
</script>
</body>
</html>
`;
}

/* ---------- main ---------- */
async function main() {
  let html = read('index.html');
  const config = JSON.parse(read('tools/seo-products.json'));
  const [{ products, categories }, reviews] = await Promise.all([loadCatalog(), loadReviews()]);
  const visible = products.filter((p) => p && p.visible !== false && p.status !== 'inactive');

  // 1. Product pages map (also used by the page script for links and schema).
  const pages = {};
  for (const p of visible) {
    const id = String(p.id);
    config[id] = config[id] || {};
    config[id].slug = config[id].slug || `${slugify(p.name)}-${id}`;
    const img = productImage(p);
    pages[id] = { url: `/${PRODUCTS_DIR}/${config[id].slug}.html`, name: config[id].name || p.name, ...(img.local ? { image: img.local } : {}), imageUrl: img.url };
  }
  const jsPages = Object.fromEntries(Object.entries(pages).map(([id, { url, name, image }]) => [id, image ? { url, name, image } : { url, name }]));
  html = setJsConst(html, 'PRODUCT_PAGES', jsPages);

  // 2. Run the page's own rendering code with the French texts and the live catalog.
  const recorded = new Map();
  const element = (id) => {
    if (!recorded.has(id)) recorded.set(id, { html: '' });
    const rec = recorded.get(id);
    return {
      set innerHTML(v) { rec.html = String(v); }, get innerHTML() { return rec.html; },
      set textContent(v) { rec.html = esc(v); }, get textContent() { return rec.html; },
      querySelectorAll: () => [], querySelector: () => null, addEventListener() {}, setAttribute() {},
      classList: { add() {}, remove() {}, toggle() {}, contains: () => false }, style: {}, dataset: {},
    };
  };
  // Same catalog without base64 photos (replaced by their file URL), for the grid and the snapshot.
  const forGrid = products.map((p) => (String(p.img || '').startsWith('data:') ? { ...p, img: pages[String(p.id)]?.image || '' } : p));
  const KEEP = ['id', 'cat', 'name', 'price', 'oldPrice', 'discount', 'badge', 'stock', 'status', 'visible', 'desc', 'longDesc', 'img'];
  html = setJsConst(html, 'PRERENDERED_PRODUCTS', forGrid.map((p) => Object.fromEntries(KEEP.filter((k) => p[k] !== undefined).map((k) => [k, p[k]]))));
  html = setJsConst(html, 'PRERENDERED_REVIEWS', reviews);
  const sandbox = {
    document: { documentElement: {}, getElementById: element, querySelectorAll: () => [], createElement: () => ({}), head: { appendChild() {} } },
    currentLang: 'fr', currentCategory: 'all', FAVS: [], PRODUCTS: forGrid, CATEGORIES: categories.length ? categories : [], PRODUCT_PAGES: jsPages,
    REVIEWS: reviews, REVIEW_PRODUCT_PRESET: '',
    attachFaqEvents() {}, animateStats() {}, updateProductStructuredData() {},
  };
  const code = ['const I18N = ', 'const ICONS = ', 'const OFFER_POLICY = ', 'function badgeLogoSVG(', 'function applyStaticText(', 'function catNames(', 'function fmtPrice(', 'function productPage(', 'function escapeReviewHtml(', 'function productRating(', 'function ratingStarsText(', 'function renderReviewProductOptions(', 'function renderCatFilters(', 'function renderMenuGrid(']
    .map((head) => declaration(html, head)).join('\n');
  vm.runInNewContext(`${code}\napplyStaticText(); renderCatFilters(); renderMenuGrid(); globalThis.__fr = I18N.fr; globalThis.__policy = OFFER_POLICY;`, sandbox, { timeout: 5000 });
  const i18n = sandbox.__fr;
  // Delivery and returns for Google, defined once in index.html (OFFER_POLICY).
  const policy = JSON.parse(JSON.stringify(sandbox.__policy));

  let missing = [];
  for (const [id, { html: inner }] of recorded) {
    // Counters animate from 0 in the browser; crawlers get the final values.
    const content = id === 'statsRow' ? inner.replace(/data-final="([^"]*)">0</g, 'data-final="$1">$1<') : inner;
    const next = setInner(html, id, content);
    if (next === null) missing.push(id); else html = next;
  }
  if (missing.length) console.warn(`warning: not found in index.html: ${missing.join(', ')}`);

  // 3. Static product structured data (the page script refreshes it with live data).
  const schemaItems = visible.map((p, i) => {
    const page = pages[String(p.id)];
    const url = `${SITE}${page.url}`;
    const image = page.imageUrl ? (page.imageUrl.startsWith('http') ? page.imageUrl : `${SITE}${page.imageUrl}`) : undefined;
    return {
      '@type': 'ListItem', position: i + 1,
      item: {
        '@type': 'Product', '@id': url, name: page.name, image: image ? [image] : undefined,
        description: plain(p.longDesc || p.desc), brand: { '@type': 'Brand', name: 'AXORIA' }, sku: String(p.id), url,
        offers: { '@type': 'Offer', priceCurrency: 'MAD', price: Number(p.price), availability: Number(p.stock ?? 1) > 0 ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock', itemCondition: 'https://schema.org/NewCondition', url, seller: { '@type': 'Organization', name: 'AXORIA' }, ...policy },
      },
    };
  });
  html = setInner(html, 'axoriaProductSchema', scriptJson({ '@context': 'https://schema.org', '@graph': [{ '@type': 'ItemList', name: 'Produits AXORIA', itemListElement: schemaItems }] }));
  write('index.html', html);

  // 4. Product pages (and removal of pages whose product is gone or hidden).
  const pageList = visible.map((p) => ({ id: String(p.id), url: pages[String(p.id)].url, name: pages[String(p.id)].name, price: p.price }));
  const written = new Set();
  // Sitemap dates only move when a page really changed, so Google keeps trusting them.
  const prevLastmod = new Map([...read('sitemap.xml').matchAll(/<loc>([^<]+)<\/loc><lastmod>([^<]+)<\/lastmod>/g)].map((m) => [m[1], m[2]]));
  const lastmod = new Map();
  for (const p of visible) {
    const page = { id: String(p.id), ...pages[String(p.id)] };
    const rel = page.url.slice(1);
    const next = productPageHtml(p, page, { i18n, pages: pageList, policy, reviews });
    const before = fs.existsSync(abs(rel)) ? fs.readFileSync(abs(rel), 'utf8').replace(/\r\n/g, '\n') : null;
    lastmod.set(page.url, (before === next && prevLastmod.get(`${SITE}${page.url}`)) || TODAY);
    eolOf.set(rel, '\n');
    write(rel, next);
    written.add(path.basename(rel));
  }
  for (const f of fs.existsSync(abs(PRODUCTS_DIR)) ? fs.readdirSync(abs(PRODUCTS_DIR)) : []) {
    if (f.endsWith('.html') && !written.has(f)) { fs.unlinkSync(abs(`${PRODUCTS_DIR}/${f}`)); console.log(`removed ${PRODUCTS_DIR}/${f} (product hidden or deleted)`); }
  }

  // 5. Sitemap: keep the other pages, list current product pages, refresh the home page date.
  const sitemap = read('sitemap.xml');
  const urls = [...sitemap.matchAll(/<url>[\s\S]*?<\/url>/g)].map((m) => m[0]).filter((u) => !u.includes(`/${PRODUCTS_DIR}/`));
  const entries = urls.map((u) => (u.includes(`<loc>${SITE}/</loc>`) ? u.replace(/<lastmod>[^<]*<\/lastmod>/, `<lastmod>${TODAY}</lastmod>`) : u));
  const productEntries = pageList.map((p) => `<url><loc>${SITE}${p.url}</loc><lastmod>${lastmod.get(p.url) || TODAY}</lastmod><priority>0.9</priority></url>`);
  entries.splice(1, 0, ...productEntries);
  write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries.map((e) => `  ${e.trim()}`).join('\n')}\n</urlset>\n`);

  // 6. Product feed for Meta Commerce Manager and Google Merchant Center (both read this URL daily).
  write('feeds/products.xml', productFeedXml(visible, pages, config, policy));

  // 7. Remember slugs for new products.
  write('tools/seo-products.json', `${JSON.stringify(config, null, 2)}\n`);

  console.log(`index.html: ${recorded.size} blocks pre-rendered, ${visible.length} products in the grid and schema`);
  for (const p of pageList) console.log(`  ${p.url}  —  ${p.name}`);
  console.log('sitemap.xml and feeds/products.xml updated. Next: review the pages, commit and deploy.');
}

main().catch((e) => { console.error(`seo-build failed: ${e.message}`); process.exit(1); });
