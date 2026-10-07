import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const allowedEvents = new Set(['PageView','ViewContent','AddToCart','InitiateCheckout','Purchase']);
const allowedOrigins = new Set(['https://axoria.ma','https://www.axoria.ma']);

function cors(origin:string|null){
  const allow = origin && (allowedOrigins.has(origin) || origin.startsWith('http://localhost:') || origin.startsWith('http://127.0.0.1:')) ? origin : 'https://axoria.ma';
  return {'Access-Control-Allow-Origin':allow,'Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type','Access-Control-Allow-Methods':'POST, OPTIONS','Vary':'Origin'};
}
async function sha256(value:string){
  const bytes = new TextEncoder().encode(value.trim().toLowerCase());
  const digest = await crypto.subtle.digest('SHA-256',bytes);
  return Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
function cleanPhone(v:string){let n=String(v||'').replace(/\D/g,'');if(n.startsWith('0'))n='212'+n.slice(1);return n;}

Deno.serve(async(req:Request)=>{
  const origin=req.headers.get('origin');
  const headers={...cors(origin),'Content-Type':'application/json'};
  if(req.method==='OPTIONS') return new Response('ok',{headers});
  if(req.method!=='POST') return new Response(JSON.stringify({error:'method_not_allowed'}),{status:405,headers});
  if(origin && !allowedOrigins.has(origin) && !origin.startsWith('http://localhost:') && !origin.startsWith('http://127.0.0.1:')){
    return new Response(JSON.stringify({error:'origin_not_allowed'}),{status:403,headers});
  }
  try{
    const body=await req.json();
    const eventName=String(body?.event_name||'');
    if(!allowedEvents.has(eventName)) return new Response(JSON.stringify({error:'invalid_event'}),{status:400,headers});
    const pixelId=String(Deno.env.get('META_PIXEL_ID')||body?.pixel_id||'').trim();
    const token=String(Deno.env.get('META_CAPI_ACCESS_TOKEN')||'').trim();
    if(!/^\d{5,30}$/.test(pixelId)||!token){
      return new Response(JSON.stringify({ok:true,sent:false,reason:'capi_not_configured'}),{status:202,headers});
    }
    const incoming=body?.user_data||{};
    const userData:any={client_user_agent:req.headers.get('user-agent')||undefined};
    const ip=(req.headers.get('x-forwarded-for')||req.headers.get('cf-connecting-ip')||'').split(',')[0].trim();
    if(ip) userData.client_ip_address=ip;
    if(incoming.fbp) userData.fbp=String(incoming.fbp);
    if(incoming.fbc) userData.fbc=String(incoming.fbc);
    if(incoming.ph){const ph=cleanPhone(incoming.ph);if(ph)userData.ph=[await sha256(ph)];}
    if(incoming.fn) userData.fn=[await sha256(String(incoming.fn))];
    if(incoming.ct) userData.ct=[await sha256(String(incoming.ct))];
    if(incoming.country) userData.country=[await sha256(String(incoming.country))];
    if(incoming.external_id) userData.external_id=[await sha256(String(incoming.external_id))];
    const event={event_name:eventName,event_time:Number(body?.event_time)||Math.floor(Date.now()/1000),event_id:String(body?.event_id||crypto.randomUUID()),event_source_url:String(body?.event_source_url||'https://axoria.ma'),action_source:'website',user_data:userData,custom_data:body?.custom_data||{}};
    const testCode=String(Deno.env.get('META_TEST_EVENT_CODE')||'').trim();
    const graphVersion=String(Deno.env.get('META_GRAPH_VERSION')||'').trim();
    const root=graphVersion?`https://graph.facebook.com/${graphVersion}`:'https://graph.facebook.com';
    const payload:any={data:[event]};
    if(testCode)payload.test_event_code=testCode;
    const response=await fetch(`${root}/${encodeURIComponent(pixelId)}/events?access_token=${encodeURIComponent(token)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const result=await response.json();
    return new Response(JSON.stringify({ok:response.ok,sent:response.ok,meta:result}),{status:response.ok?200:502,headers});
  }catch(e){
    console.error(e);
    return new Response(JSON.stringify({error:'invalid_request'}),{status:400,headers});
  }
});
