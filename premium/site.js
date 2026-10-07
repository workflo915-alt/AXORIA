/* AXORIA Phase 5 — lightweight premium storefront */
(() => {
'use strict';

const SUPABASE_URL='https://gdemgpkkrmpridqgjmtx.supabase.co';
const SUPABASE_ANON_KEY='sb_publishable_LcXsTIdML2gITtM8UDqtWw_toCYU4qD';
const sb=(window.supabase&&window.supabase.createClient)?window.supabase.createClient(SUPABASE_URL,SUPABASE_ANON_KEY):null;
const $=(id)=>document.getElementById(id);
const $$=(sel,root=document)=>[...root.querySelectorAll(sel)];
const esc=(v)=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=(v)=>`${Number(v||0).toFixed(Number(v||0)%1?2:0)} DH`;
const clamp=(n,min,max)=>Math.min(max,Math.max(min,n));

const I18N={
  fr:{nav:['Accueil','Produits','À propos','Avis','FAQ'],shop:'Commander',eyebrow:'AXORIA · WELLNESS ESSENTIALS',hero:'Feel better.<br>Move better.',lead:'Des essentiels de bien-être pensés pour le confort, le maintien et vos journées actives.',explore:'Découvrir les produits',why:'Pourquoi AXORIA',products:'Les essentiels du quotidien.',productsCopy:'Des solutions simples, confortables et faciles à intégrer à votre routine.',all:'Tous',story:'Pensé pour bouger avec vous.',s1:'Confort',s1p:'Des matières respirantes et réglables pour rester à l’aise au quotidien.',s2:'Maintien',s2p:'Un soutien ciblé qui accompagne votre posture et votre mobilité sans compliquer votre routine.',s3:'Quotidien',s3p:'Au travail, à la maison ou pendant vos activités : AXORIA s’intègre naturellement à votre journée.',trust:'Achetez en toute confiance.',about:'Le bien-être, sans complication.',aboutp:'AXORIA sélectionne des essentiels accessibles et pratiques pour vous aider à vous sentir mieux dans votre quotidien, avec une expérience d’achat claire et rassurante.',reviews:'Ce que nos clients en disent.',faq:'Questions fréquentes.',final:'Votre routine.<br>En mieux.',finalp:'Découvrez les essentiels AXORIA et choisissez ce qui vous accompagne au quotidien.',cart:'Votre panier',empty:'Votre panier est vide.',total:'Total',checkout:'Finaliser la commande',close:'Fermer',order:'Commander',name:'Nom complet',phone:'Téléphone',city:'Ville',address:'Adresse',notes:'Remarques (optionnel)',required:'Merci de remplir tous les champs obligatoires.',success:'Commande confirmée',failed:'Impossible de passer la commande. Réessayez.',stock:'Rupture de stock',added:'Ajouté au panier',reviewTitle:'Partager votre expérience',comment:'Votre avis',send:'Envoyer mon avis',thanks:'Merci ! Votre avis sera publié après vérification.',reviewFail:'Impossible d’envoyer votre avis maintenant.'},
  en:{nav:['Home','Products','About','Reviews','FAQ'],shop:'Shop now',eyebrow:'AXORIA · WELLNESS ESSENTIALS',hero:'Feel better.<br>Move better.',lead:'Everyday wellness essentials designed for comfort, support and active days.',explore:'Explore products',why:'Why AXORIA',products:'Everyday essentials.',productsCopy:'Simple, comfortable solutions that fit naturally into your routine.',all:'All',story:'Designed to move with you.',s1:'Comfort',s1p:'Breathable, adjustable materials designed for everyday comfort.',s2:'Support',s2p:'Targeted support for posture and mobility without complicating your routine.',s3:'Every day',s3p:'At work, at home or on the move, AXORIA fits naturally into your day.',trust:'Shop with confidence.',about:'Wellness, made simple.',aboutp:'AXORIA selects practical, accessible essentials to help you feel better every day, with a clear and reassuring shopping experience.',reviews:'What our customers say.',faq:'Frequently asked questions.',final:'Your routine.<br>Made better.',finalp:'Discover AXORIA essentials and choose what supports your everyday life.',cart:'Your cart',empty:'Your cart is empty.',total:'Total',checkout:'Checkout',close:'Close',order:'Place order',name:'Full name',phone:'Phone',city:'City',address:'Address',notes:'Notes (optional)',required:'Please fill in all required fields.',success:'Order confirmed',failed:'Unable to place your order. Try again.',stock:'Out of stock',added:'Added to cart',reviewTitle:'Share your experience',comment:'Your review',send:'Send review',thanks:'Thank you! Your review will be published after moderation.',reviewFail:'Unable to submit your review right now.'},
  ar:{nav:['الرئيسية','المنتجات','من نحن','الآراء','الأسئلة'],shop:'اطلب الآن',eyebrow:'AXORIA · WELLNESS ESSENTIALS',hero:'راحة أكثر.<br>حركة أفضل.',lead:'منتجات يومية للراحة والدعم تناسب روتينك وحركتك.',explore:'اكتشف المنتجات',why:'لماذا AXORIA',products:'أساسيات يومية.',productsCopy:'حلول بسيطة ومريحة وسهلة الإضافة إلى روتينك.',all:'الكل',story:'مصمم ليتحرك معك.',s1:'الراحة',s1p:'مواد مريحة وقابلة للتعديل للاستخدام اليومي.',s2:'الدعم',s2p:'دعم عملي للوضعية والحركة بدون تعقيد روتينك.',s3:'كل يوم',s3p:'في العمل أو المنزل أو أثناء النشاط، AXORIA يرافق يومك بسهولة.',trust:'تسوق بثقة.',about:'العناية اليومية ببساطة.',aboutp:'تختار AXORIA منتجات عملية وسهلة الاستخدام لمساعدتك على الشعور براحة أفضل كل يوم.',reviews:'آراء عملائنا.',faq:'أسئلة شائعة.',final:'روتينك.<br>بشكل أفضل.',finalp:'اكتشف منتجات AXORIA واختر ما يناسب يومك.',cart:'سلة التسوق',empty:'السلة فارغة.',total:'المجموع',checkout:'إتمام الطلب',close:'إغلاق',order:'تأكيد الطلب',name:'الاسم الكامل',phone:'الهاتف',city:'المدينة',address:'العنوان',notes:'ملاحظات (اختياري)',required:'المرجو ملء جميع الخانات الضرورية.',success:'تم تأكيد الطلب',failed:'تعذر إرسال الطلب. حاول من جديد.',stock:'نفذ من المخزون',added:'تمت الإضافة للسلة',reviewTitle:'شارك تجربتك',comment:'رأيك',send:'إرسال الرأي',thanks:'شكراً! سيتم نشر رأيك بعد المراجعة.',reviewFail:'تعذر إرسال رأيك الآن.'}
};

let lang=localStorage.getItem('axoria_lang')||'fr';
if(!I18N[lang])lang='fr';
let PRODUCTS=[],CATEGORIES=[],REVIEWS=[],CART=[];
let activeCat='all',modalProduct=null,modalQty=1,selectedStars=5;
let META={enabled:false,pixelId:'',capiEnabled:false},pixelReady=false,pageViewSent=false;

async function storeGet(key){
  if(!sb)return null;
  const {data,error}=await sb.from('axoria_store').select('value').eq('key',key).maybeSingle();
  if(error)throw error;
  return data?.value??null;
}
function readCart(){try{return JSON.parse(localStorage.getItem('axoria_cart')||'[]')||[]}catch{return[]}}
function saveCart(){localStorage.setItem('axoria_cart',JSON.stringify(CART));}

function validPixel(v){return /^\d{5,30}$/.test(String(v||'').trim())}
function eventId(prefix='ax'){return `${prefix}-${Date.now()}-${crypto.randomUUID?crypto.randomUUID():Math.random().toString(36).slice(2)}`}
function cookie(name){const p=`${name}=`;return document.cookie.split(';').map(x=>x.trim()).find(x=>x.startsWith(p))?.slice(p.length)||''}
function ensurePixel(){
  if(!META.enabled||!validPixel(META.pixelId))return false;
  if(!window.fbq){
    const n=window.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    window._fbq=window._fbq||n;n.push=n;n.loaded=true;n.version='2.0';n.queue=[];
    const s=document.createElement('script');s.async=true;s.src='https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(s);
  }
  if(!pixelReady){window.fbq('init',META.pixelId);pixelReady=true;}
  return true;
}
function track(eventName,custom={},user={}){
  if(!META.enabled||!validPixel(META.pixelId))return null;
  const id=eventId(eventName.toLowerCase());
  try{if(ensurePixel())window.fbq('track',eventName,custom,{eventID:id});}catch(e){console.warn('Meta browser event failed',e)}
  if(META.capiEnabled&&sb){
    const body={event_name:eventName,event_id:id,event_time:Math.floor(Date.now()/1000),event_source_url:location.href,user_data:{...user,fbp:cookie('_fbp'),fbc:cookie('_fbc')},custom_data:custom};
    sb.functions.invoke('meta-capi',{body}).then(({error})=>{if(error)console.warn('Meta CAPI event failed',error)}).catch(e=>console.warn('Meta CAPI unavailable',e));
  }
  return id;
}
function trackPurchaseBrowser(placed,custom){
  if(!META.enabled||!validPixel(META.pixelId)||!placed?.order_id)return;
  const id=`purchase-${placed.order_id}`; // Same deterministic ID used by the DB server trigger for deduplication.
  try{if(ensurePixel())window.fbq('track','Purchase',custom,{eventID:id});}catch(e){console.warn('Meta browser Purchase failed',e)}
}
async function loadTracking(){
  try{const raw=await storeGet('axoria_tracking');META={enabled:!!raw?.enabled,pixelId:String(raw?.pixelId||'').trim(),capiEnabled:!!raw?.capiEnabled};if(ensurePixel()&&!pageViewSent){pageViewSent=true;track('PageView')}}catch(e){console.warn('Tracking config unavailable',e)}
}

function t(){return I18N[lang]}
function applyLanguage(){
  const x=t();document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';
  $$('[data-i18n]').forEach(el=>{const k=el.dataset.i18n;if(x[k]!=null)el.innerHTML=x[k]});
  $$('.nav-link').forEach((el,i)=>el.textContent=x.nav[i]||el.textContent);
  if($('langSel'))$('langSel').value=lang;
  renderFilters();renderProducts();renderCart();renderReviews();renderStars();
}

function productAvailable(p){return p&&p.visible!==false&&p.status!=='inactive'&&Number(p.stock||0)>0}
function renderFilters(){
  const host=$('filters');if(!host)return;
  const cats=(CATEGORIES||[]).map(c=>typeof c==='string'?c:c.name).filter(Boolean);
  host.innerHTML=[`<button class="chip ${activeCat==='all'?'active':''}" data-cat="all">${esc(t().all)}</button>`,...cats.map(c=>`<button class="chip ${activeCat===c?'active':''}" data-cat="${esc(c)}">${esc(c)}</button>`)].join('');
  $$('[data-cat]',host).forEach(b=>b.onclick=()=>{activeCat=b.dataset.cat;renderFilters();renderProducts()});
}
function renderProducts(){
  const host=$('productGrid');if(!host)return;
  const visible=PRODUCTS.filter(p=>p.visible!==false&&(activeCat==='all'||p.cat===activeCat));
  host.innerHTML=visible.map((p,i)=>{
    const available=productAvailable(p);const badge=p.badge?`<span class="tag">${esc(p.badge)}</span>`:'';
    return `<article class="product-card" data-product="${esc(p.id)}" data-reveal style="transition-delay:${Math.min(i*70,210)}ms">
      ${badge}<div class="product-image"><img src="${p.img}" alt="${esc(p.name)}" loading="lazy" decoding="async"></div>
      <div class="product-body"><div class="product-topline"><div><h3>${esc(p.name)}</h3><p class="product-desc">${esc(p.desc||'')}</p></div></div>
      <div class="product-foot"><div class="price">${p.oldPrice?`<s style="color:var(--muted);font-size:12px;margin-right:8px">${money(p.oldPrice)}</s>`:''}${money(p.price)}</div>
      ${available?`<button class="add" data-add="${esc(p.id)}" aria-label="Ajouter">+</button>`:`<span style="color:#bb4c4c;font-size:12px;font-weight:800">${esc(t().stock)}</span>`}</div></div></article>`
  }).join('');
  $$('[data-product]',host).forEach(card=>card.onclick=e=>{if(e.target.closest('[data-add]'))return;openProduct(card.dataset.product)});
  $$('[data-add]',host).forEach(btn=>btn.onclick=e=>{e.stopPropagation();addToCart(btn.dataset.add,1)});
  observeReveals();
}
function hydrateHeroProducts(){
  const p=PRODUCTS.filter(p=>p.visible!==false);
  [0,1].forEach(i=>{const img=$(`heroProduct${i+1}`);const card=$(`heroCard${i+1}`);if(img&&p[i]){img.src=p[i].img;img.alt=p[i].name;if(card)card.dataset.label=`${p[i].name} · ${money(p[i].price)}`}});
  const story=$('storyImage');if(story&&p[0]){story.src=p[0].img;story.alt=p[0].name;}
}
function openProduct(id){
  const p=PRODUCTS.find(x=>String(x.id)===String(id));if(!p)return;modalProduct=p;modalQty=1;
  $('productModalName').textContent=p.name;$('productModalDesc').textContent=p.longDesc||p.desc||'';$('productModalImg').src=p.img;$('productModalImg').alt=p.name;updateModalPrice();$('productModal').classList.add('open');document.body.classList.add('lock');
  track('ViewContent',{content_ids:[String(p.id)],content_type:'product',content_name:p.name,value:Number(p.price||0),currency:'MAD'});
}
function closeProduct(){$('productModal')?.classList.remove('open');document.body.classList.remove('lock')}
function updateModalPrice(){if(!modalProduct)return;$('modalQty').textContent=modalQty;$('productModalPrice').textContent=money(Number(modalProduct.price||0)*modalQty)}
function addToCart(id,qty=1){
  const p=PRODUCTS.find(x=>String(x.id)===String(id));if(!productAvailable(p)){toast(t().stock);return}
  const existing=CART.find(x=>String(x.id)===String(id));if(existing)existing.qty=Math.min(Number(p.stock||99),Number(existing.qty||0)+qty);else CART.push({id:p.id,name:p.name,price:Number(p.price||0),img:p.img,qty:Math.min(qty,Number(p.stock||99))});
  saveCart();renderCart();toast(t().added);track('AddToCart',{content_ids:[String(p.id)],content_type:'product',content_name:p.name,value:Number(p.price||0)*qty,currency:'MAD',contents:[{id:String(p.id),quantity:qty,item_price:Number(p.price||0)}]});
}
function cartTotal(){return CART.reduce((s,c)=>s+Number(c.price||0)*Number(c.qty||0),0)}
function renderCart(){
  const count=CART.reduce((s,c)=>s+Number(c.qty||0),0);$$('.cart-count').forEach(el=>el.textContent=count);
  const host=$('cartItems');if(!host)return;
  host.innerHTML=CART.length?CART.map(c=>`<div class="cart-item"><img src="${c.img}" alt="${esc(c.name)}"><div><h4>${esc(c.name)}</h4><small>${money(c.price)}</small><div class="qty"><button data-dec="${esc(c.id)}">−</button><b>${Number(c.qty)}</b><button data-inc="${esc(c.id)}">+</button></div></div><button class="remove" data-remove="${esc(c.id)}">×</button></div>`).join(''):`<p style="color:var(--muted);padding:20px 0">${esc(t().empty)}</p>`;
  $('cartTotal').textContent=money(cartTotal());
  $$('[data-inc]',host).forEach(b=>b.onclick=()=>changeQty(b.dataset.inc,1));$$('[data-dec]',host).forEach(b=>b.onclick=()=>changeQty(b.dataset.dec,-1));$$('[data-remove]',host).forEach(b=>b.onclick=()=>{CART=CART.filter(c=>String(c.id)!==String(b.dataset.remove));saveCart();renderCart()});
}
function changeQty(id,d){const c=CART.find(x=>String(x.id)===String(id));const p=PRODUCTS.find(x=>String(x.id)===String(id));if(!c)return;c.qty=clamp(Number(c.qty)+d,0,Math.max(1,Number(p?.stock||99)));if(c.qty<=0)CART=CART.filter(x=>x!==c);saveCart();renderCart()}
function openCart(){$('cartOverlay').classList.add('open');document.body.classList.add('lock')}
function closeCart(){$('cartOverlay').classList.remove('open');document.body.classList.remove('lock')}
function openCheckout(){
  if(!CART.length){toast(t().empty);return}closeCart();$('checkoutError').textContent='';$('checkoutTotal').textContent=money(cartTotal());$('checkoutOverlay').classList.add('open');document.body.classList.add('lock');
  track('InitiateCheckout',{value:cartTotal(),currency:'MAD',num_items:CART.reduce((s,c)=>s+c.qty,0),content_ids:CART.map(c=>String(c.id)),contents:CART.map(c=>({id:String(c.id),quantity:c.qty,item_price:c.price}))});
}
function closeCheckout(){$('checkoutOverlay').classList.remove('open');document.body.classList.remove('lock')}
async function submitOrder(e){
  e?.preventDefault();const x=t();const err=$('checkoutError');err.textContent='';
  const name=$('ofName').value.trim(),phone=$('ofPhone').value.trim(),city=$('ofCity').value.trim(),address=$('ofAddress').value.trim(),notes=$('ofNotes').value.trim();
  if(!name||!phone||!city||!address){err.textContent=x.required;return}if(!sb){err.textContent=x.failed;return}
  const btn=$('submitOrder');btn.disabled=true;const purchaseCart=CART.map(c=>({...c}));
  try{
    const {data,error}=await sb.rpc('place_order',{p_customer_name:name,p_phone:phone,p_city:city,p_address:address,p_notes:notes||null,p_items:purchaseCart.map(c=>({product_id:c.id,qty:c.qty}))});if(error)throw error;
    const placed=Array.isArray(data)?data[0]:data;const value=Number(placed?.order_total??purchaseCart.reduce((s,c)=>s+c.price*c.qty,0));
    trackPurchaseBrowser(placed,{value,currency:'MAD',content_type:'product',content_ids:purchaseCart.map(c=>String(c.id)),num_items:purchaseCart.reduce((s,c)=>s+c.qty,0),order_id:placed?.order_code||''});
    CART=[];saveCart();renderCart();closeCheckout();['ofName','ofPhone','ofCity','ofAddress','ofNotes'].forEach(id=>$(id).value='');toast(`${x.success}${placed?.order_code?` · ${placed.order_code}`:''}`);
    await loadProducts();
  }catch(ex){console.error('place_order',ex);err.textContent=String(ex?.message||'').includes('stock')?x.stock:x.failed}finally{btn.disabled=false}
}

function renderReviews(){
  const host=$('reviewStrip');if(!host)return;
  host.innerHTML=REVIEWS.map(r=>`<article class="review-card"><div><div class="stars">${'★'.repeat(Math.max(1,Math.min(5,Number(r.rating||5))))}</div><blockquote>“${esc(r.comment||'')}”</blockquote></div><div class="review-meta"><b>${esc(r.name||'Client AXORIA')}</b>${r.loc?` · ${esc(r.loc)}`:''}</div></article>`).join('');
}
function renderStars(){$$('#starInput button').forEach((b,i)=>{b.style.opacity=i<selectedStars?'1':'.28';b.setAttribute('aria-pressed',i<selectedStars?'true':'false')})}
async function submitReview(e){
  e?.preventDefault();const name=$('reviewName').value.trim(),comment=$('reviewComment').value.trim();if(!name||!comment){toast(t().required);return}if(!sb){toast(t().reviewFail);return}
  const btn=$('submitReview');btn.disabled=true;try{const {error}=await sb.from('review_submissions').insert({name,rating:selectedStars,comment,status:'pending'});if(error)throw error;$('reviewName').value='';$('reviewComment').value='';selectedStars=5;renderStars();toast(t().thanks)}catch(ex){console.error(ex);toast(t().reviewFail)}finally{btn.disabled=false}
}

async function loadProducts(){try{const raw=await storeGet('axoria_products');PRODUCTS=Array.isArray(raw)?raw:[]}catch(e){console.error(e);PRODUCTS=[]}renderProducts();hydrateHeroProducts();renderCart()}
async function loadData(){
  CART=readCart();
  if(!sb){renderProducts();renderCart();return}
  const results=await Promise.allSettled([storeGet('axoria_products'),storeGet('axoria_categories'),storeGet('axoria_reviews')]);
  PRODUCTS=results[0].status==='fulfilled'&&Array.isArray(results[0].value)?results[0].value:[];
  CATEGORIES=results[1].status==='fulfilled'&&Array.isArray(results[1].value)?results[1].value:[];
  REVIEWS=results[2].status==='fulfilled'&&Array.isArray(results[2].value)?results[2].value:[];
  renderFilters();renderProducts();hydrateHeroProducts();renderReviews();renderCart();
}

function toast(msg){const el=$('toast');if(!el)return;el.textContent=msg;el.classList.add('show');clearTimeout(toast._t);toast._t=setTimeout(()=>el.classList.remove('show'),2600)}
function observeReveals(){
  if(!('IntersectionObserver'in window)){$$('[data-reveal]').forEach(x=>x.classList.add('in'));return}
  if(!observeReveals.io)observeReveals.io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');observeReveals.io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px',threshold:.08});
  $$('[data-reveal]:not(.in)').forEach(x=>observeReveals.io.observe(x));
}
function initScrollMotion(){
  const root=document.documentElement,nav=$('nav'),story=$('storyPin');let ticking=false;
  const draw=()=>{ticking=false;const y=window.scrollY,h=Math.max(1,document.documentElement.scrollHeight-innerHeight);root.style.setProperty('--progress',clamp(y/h,0,1));root.style.setProperty('--hero-zoom',clamp(y/innerHeight,0,1));root.style.setProperty('--hero-shift',clamp(y/innerHeight,0,1));nav?.classList.toggle('scrolled',y>30);
    if(story){const r=story.getBoundingClientRect(),range=Math.max(1,story.offsetHeight-innerHeight),p=clamp(-r.top/range,0,1);root.style.setProperty('--story-y',p);const idx=p<.34?0:p<.67?1:2;$$('.story-step').forEach((s,i)=>s.classList.toggle('active',i===idx));}
  };
  const onScroll=()=>{if(!ticking){ticking=true;requestAnimationFrame(draw)}};addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',onScroll,{passive:true});draw();
}
function toggleTheme(){
  const apply=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;localStorage.setItem('axoria_theme',next);updateThemeIcon()};
  if(document.startViewTransition&&!matchMedia('(prefers-reduced-motion: reduce)').matches)document.startViewTransition(apply);else apply();
}
function updateThemeIcon(){const b=$('themeBtn');if(b)b.textContent=document.documentElement.dataset.theme==='dark'?'☀':'◐'}
function bind(){
  $('themeBtn').onclick=toggleTheme;$('cartBtn').onclick=openCart;$('closeCart').onclick=closeCart;$('cartOverlay').addEventListener('click',e=>{if(e.target===e.currentTarget)closeCart()});$('checkoutBtn').onclick=openCheckout;$('closeCheckout').onclick=closeCheckout;$('checkoutOverlay').addEventListener('click',e=>{if(e.target===e.currentTarget)closeCheckout()});$('checkoutForm').addEventListener('submit',submitOrder);
  $('productModalClose').onclick=closeProduct;$('productModal').addEventListener('click',e=>{if(e.target===e.currentTarget)closeProduct()});$('modalMinus').onclick=()=>{if(modalQty>1){modalQty--;updateModalPrice()}};$('modalPlus').onclick=()=>{if(modalProduct){modalQty=Math.min(Number(modalProduct.stock||99),modalQty+1);updateModalPrice()}};$('modalAdd').onclick=()=>{if(modalProduct){addToCart(modalProduct.id,modalQty);closeProduct();openCart()}};
  $('langSel').onchange=e=>{lang=e.target.value;localStorage.setItem('axoria_lang',lang);applyLanguage()};
  $('submitReview').onclick=submitReview;$$('#starInput button').forEach((b,i)=>b.onclick=()=>{selectedStars=i+1;renderStars()});
  $$('.faq-q').forEach(btn=>btn.onclick=()=>btn.closest('.faq-item').classList.toggle('open'));
  $$('[data-scroll]').forEach(a=>a.onclick=e=>{e.preventDefault();document.querySelector(a.dataset.scroll)?.scrollIntoView({behavior:'smooth'})});
  $('mobileMenuBtn').onclick=()=>document.querySelector('#products')?.scrollIntoView({behavior:'smooth'});
}

async function init(){
  const saved=localStorage.getItem('axoria_theme');document.documentElement.dataset.theme=saved==='dark'?'dark':'light';updateThemeIcon();bind();applyLanguage();observeReveals();initScrollMotion();
  await Promise.all([loadData(),loadTracking()]);
  requestAnimationFrame(()=>document.body.classList.add('ready'));
}

document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init,{once:true}):init();
})();
