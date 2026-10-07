from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = "document.getElementById('newsBtn').onclick = (e)=>{ e.preventDefault(); const v=document.getElementById('newsEmail').value.trim(); if(v){ toast('Merci pour votre inscription !'); document.getElementById('newsEmail').value=''; } };"
new = """document.getElementById('newsBtn').onclick = async (e)=>{\n    e.preventDefault();\n    const input=document.getElementById('newsEmail');\n    const btn=document.getElementById('newsBtn');\n    const email=input.value.trim().toLowerCase();\n    const valid=/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(email);\n    const msg={\n      fr:{invalid:'Entrez une adresse email valide.',ok:'Merci ! Votre inscription est confirmée.',exists:'Cette adresse est déjà inscrite.',fail:\"Impossible de vous inscrire pour le moment.\"},\n      en:{invalid:'Enter a valid email address.',ok:'Thank you! Your subscription is confirmed.',exists:'This email is already subscribed.',fail:'Unable to subscribe right now.'},\n      ar:{invalid:'أدخل بريداً إلكترونياً صالحاً.',ok:'شكراً! تم تأكيد اشتراكك.',exists:'هذا البريد مشترك بالفعل.',fail:'تعذر الاشتراك حالياً.'}\n    }[currentLang] || {invalid:'Entrez une adresse email valide.',ok:'Merci ! Votre inscription est confirmée.',exists:'Cette adresse est déjà inscrite.',fail:\"Impossible de vous inscrire pour le moment.\"};\n    if(!valid){ toast(msg.invalid); return; }\n    if(!sb){ toast(msg.fail); return; }\n    btn.disabled=true;\n    try{\n      const {error}=await sb.from('newsletter_subscribers').insert({email,locale:currentLang,source:'storefront'});\n      if(error){\n        if(error.code==='23505'){ toast(msg.exists); input.value=''; return; }\n        throw error;\n      }\n      input.value='';\n      toast(msg.ok);\n    }catch(err){\n      console.error('newsletter subscription failed',err);\n      toast(msg.fail);\n    }finally{\n      btn.disabled=false;\n    }\n  };"""
if old not in s:
    raise SystemExit('newsletter handler anchor not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

Path('supabase/newsletter_subscribers.sql').write_text(r'''create table if not exists public.newsletter_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  locale text not null default 'fr' check (locale in ('fr','en','ar')),
  source text not null default 'storefront',
  created_at timestamptz not null default now(),
  constraint newsletter_email_length check (char_length(email) between 5 and 254),
  constraint newsletter_email_format check (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

create unique index if not exists newsletter_subscribers_email_lower_idx
  on public.newsletter_subscribers (lower(email));

alter table public.newsletter_subscribers enable row level security;

drop policy if exists storefront_insert_newsletter on public.newsletter_subscribers;
create policy storefront_insert_newsletter
on public.newsletter_subscribers
for insert
to anon, authenticated
with check (
  locale in ('fr','en','ar')
  and source = 'storefront'
  and char_length(email) between 5 and 254
);

grant insert on public.newsletter_subscribers to anon, authenticated;
revoke select, update, delete on public.newsletter_subscribers from anon, authenticated;
''', encoding='utf-8')
print('Newsletter persistence wired to Supabase')
