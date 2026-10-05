from pathlib import Path
import re

path = Path('admin.html')
text = path.read_text(encoding='utf-8')

old_pattern = r"async function replaceImage\(id,file\)\{.*?\}\n\$\('addProduct'\)\.onclick="

replacement = r"""const PRODUCT_IMAGE_BUCKET='product-images';
function productImageStoragePath(url){
  const marker=`/storage/v1/object/public/${PRODUCT_IMAGE_BUCKET}/`;
  const value=String(url||'');
  const i=value.indexOf(marker);
  if(i<0)return null;
  return decodeURIComponent(value.slice(i+marker.length).split('?')[0]);
}
function safeUploadName(name){
  return String(name||'image').normalize('NFKD').replace(/[^a-zA-Z0-9._-]+/g,'-').replace(/^-+|-+$/g,'')||'image';
}
async function replaceImage(id,file){
  if(!file)return;
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)){toast('Format image non supporté');return;}
  if(file.size>5*1024*1024){toast('Image trop lourde (5 Mo max)');return;}
  const p=PRODUCTS.find(x=>String(x.id)===String(id));
  if(!p)return;
  const oldUrl=p.img||'';
  const filename=safeUploadName(file.name);
  const objectPath=`products/${encodeURIComponent(String(id))}/${Date.now()}-${Math.random().toString(36).slice(2,10)}-${filename}`;
  try{
    const {error:uploadError}=await sb.storage.from(PRODUCT_IMAGE_BUCKET).upload(objectPath,file,{cacheControl:'3600',upsert:false,contentType:file.type});
    if(uploadError)throw uploadError;
    const {data:publicData}=sb.storage.from(PRODUCT_IMAGE_BUCKET).getPublicUrl(objectPath);
    const newUrl=publicData?.publicUrl;
    if(!newUrl)throw new Error('Public image URL unavailable');
    p.img=newUrl;
    try{
      await setStore('axoria_products',PRODUCTS);
    }catch(saveError){
      p.img=oldUrl;
      await sb.storage.from(PRODUCT_IMAGE_BUCKET).remove([objectPath]);
      throw saveError;
    }
    const oldPath=productImageStoragePath(oldUrl);
    if(oldPath && oldPath!==objectPath){
      const {error:removeError}=await sb.storage.from(PRODUCT_IMAGE_BUCKET).remove([oldPath]);
      if(removeError)console.warn('Old product image cleanup failed',removeError);
    }
    renderProducts();
    toast('Image mise à jour');
  }catch(e){
    console.error(e);
    toast('Échec de sauvegarde image');
  }
}
$('addProduct').onclick="""

new_text, n = re.subn(old_pattern, replacement, text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Expected one replaceImage block, found {n}')

if "PRODUCT_IMAGE_BUCKET='product-images'" not in new_text:
    raise SystemExit('Storage patch validation failed')
if 'r.readAsDataURL(file)' in new_text:
    raise SystemExit('Legacy base64 image upload still present')

path.write_text(new_text, encoding='utf-8')
print('admin.html now uploads product images to Supabase Storage')
