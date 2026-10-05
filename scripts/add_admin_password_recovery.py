from pathlib import Path
import re

path = Path('admin.html')
text = path.read_text(encoding='utf-8')

required_existing = ["id=\"loginView\"", "id=\"loginBtn\"", "sb.auth.signInWithPassword", "id=\"logoutBtn\""]
missing_existing = [m for m in required_existing if m not in text]
if missing_existing:
    raise SystemExit('admin.html structure changed; missing: ' + ', '.join(missing_existing))

if 'id="forgotBtn"' in text:
    required = [
        'id="forgotView"',
        'id="passwordView"',
        'resetPasswordForEmail',
        'updateUser({password:newPassword})',
        "PASSWORD_RECOVERY",
        'id="changePasswordBtn"',
    ]
    missing = [m for m in required if m not in text]
    if missing:
        raise SystemExit('Password recovery is only partially installed; missing: ' + ', '.join(missing))
    print('Admin password recovery already installed and validated.')
    raise SystemExit(0)

css = ".auth-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.auth-actions .btn{flex:1}.msg.ok{color:var(--ok)}.password-hint{font-size:11.5px;color:var(--muted);line-height:1.45;margin-top:-4px}"
text = text.replace('</style>', css + '\n</style>', 1)

old_login = '''  <button id="loginBtn" class="btn primary" style="width:100%">Se connecter</button>\n  <div id="loginMsg" class="msg"></div>\n</div>'''
new_login = '''  <button id="loginBtn" class="btn primary" style="width:100%">Se connecter</button>\n  <button id="forgotBtn" class="btn ghost" style="width:100%;margin-top:9px">Mot de passe oublié ?</button>\n  <div id="loginMsg" class="msg"></div>\n</div>\n\n<div id="forgotView" class="login card hidden">\n  <h1>Réinitialiser le mot de passe</h1>\n  <p>Entrez l’adresse e-mail de votre compte administrateur. Un lien sécurisé de réinitialisation sera envoyé par Supabase.</p>\n  <div class="field"><label>Email administrateur</label><input id="forgotEmail" type="email" autocomplete="email"></div>\n  <button id="sendResetBtn" class="btn primary" style="width:100%">Envoyer le lien</button>\n  <button id="backToLoginBtn" class="btn ghost" style="width:100%;margin-top:9px">Retour à la connexion</button>\n  <div id="forgotMsg" class="msg"></div>\n</div>\n\n<div id="passwordView" class="login card hidden">\n  <h1 id="passwordViewTitle">Nouveau mot de passe</h1>\n  <p id="passwordViewText">Choisissez un nouveau mot de passe pour votre compte administrateur.</p>\n  <div class="field"><label>Nouveau mot de passe</label><input id="newPassword" type="password" autocomplete="new-password"></div>\n  <div class="password-hint">Utilisez au moins 8 caractères et évitez de réutiliser un ancien mot de passe.</div>\n  <div class="field"><label>Confirmer le mot de passe</label><input id="confirmPassword" type="password" autocomplete="new-password"></div>\n  <button id="savePasswordBtn" class="btn primary" style="width:100%">Enregistrer le nouveau mot de passe</button>\n  <button id="cancelPasswordBtn" class="btn ghost" style="width:100%;margin-top:9px">Annuler</button>\n  <div id="passwordMsg" class="msg"></div>\n</div>'''
if old_login not in text:
    raise SystemExit('Could not find login block')
text = text.replace(old_login, new_login, 1)

old_top = '''      <button id="logoutBtn" class="btn ghost">Déconnexion</button>'''
new_top = '''      <div class="actions"><button id="changePasswordBtn" class="btn ghost">Changer le mot de passe</button><button id="logoutBtn" class="btn ghost">Déconnexion</button></div>'''
if old_top not in text:
    raise SystemExit('Could not find admin top actions')
text = text.replace(old_top, new_top, 1)

old_require = "async function requireSession(){const {data:{session}}=await sb.auth.getSession();if(!session){$('loginView').classList.remove('hidden');$('appView').classList.add('hidden');return false;}$('loginView').classList.add('hidden');$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();return true;}"
new_require = """let recoveryMode=false;let passwordFlow='change';\nfunction hideAuthViews(){['loginView','forgotView','passwordView'].forEach(id=>$(id).classList.add('hidden'));}\nfunction showLogin(message='',ok=false){hideAuthViews();$('appView').classList.add('hidden');$('loginView').classList.remove('hidden');$('loginMsg').textContent=message;$('loginMsg').classList.toggle('ok',ok);}\nfunction showForgot(){hideAuthViews();$('appView').classList.add('hidden');$('forgotView').classList.remove('hidden');$('forgotMsg').textContent='';$('forgotMsg').classList.remove('ok');$('forgotEmail').value=$('loginEmail').value.trim();}\nfunction showPasswordEditor(mode='change'){passwordFlow=mode;hideAuthViews();$('appView').classList.add('hidden');$('passwordView').classList.remove('hidden');$('newPassword').value='';$('confirmPassword').value='';$('passwordMsg').textContent='';$('passwordMsg').classList.remove('ok');$('passwordViewTitle').textContent=mode==='recovery'?'Créer un nouveau mot de passe':'Changer le mot de passe';$('passwordViewText').textContent=mode==='recovery'?'Le lien de récupération a été validé. Choisissez maintenant un nouveau mot de passe.':'Choisissez un nouveau mot de passe pour votre compte administrateur.';}\nasync function requireSession(){const {data:{session}}=await sb.auth.getSession();if(recoveryMode){showPasswordEditor('recovery');return !!session;}if(!session){showLogin();return false;}hideAuthViews();$('appView').classList.remove('hidden');$('sessionLabel').textContent=session.user.email||'Session authentifiée';await loadProducts();await loadOrders();return true;}"""
if old_require not in text:
    raise SystemExit('Could not find requireSession')
text = text.replace(old_require, new_require, 1)

pattern = re.compile(r"\$\('loginBtn'\)\.onclick=.*?sb\.auth\.onAuthStateChange\(\(_e,s\)=>\{if\(!s\)\{\$\('loginView'\)\.classList\.remove\('hidden'\);\$\('appView'\)\.classList\.add\('hidden'\);\}\}\);", re.S)
replacement = r'''$('loginBtn').onclick=async()=>{const email=$('loginEmail').value.trim(),password=$('loginPassword').value;if(!email||!password){$('loginMsg').textContent='Email et mot de passe requis.';return;}const b=$('loginBtn');b.disabled=true;$('loginMsg').textContent='';$('loginMsg').classList.remove('ok');const {error}=await sb.auth.signInWithPassword({email,password});b.disabled=false;if(error){$('loginMsg').textContent='Connexion refusée.';return;}await requireSession();};
$('loginPassword').addEventListener('keydown',e=>{if(e.key==='Enter')$('loginBtn').click();});
$('forgotBtn').onclick=showForgot;
$('backToLoginBtn').onclick=()=>showLogin();
$('sendResetBtn').onclick=async()=>{const email=$('forgotEmail').value.trim();if(!email){$('forgotMsg').textContent='Entrez votre adresse e-mail.';return;}const b=$('sendResetBtn');b.disabled=true;$('forgotMsg').textContent='';$('forgotMsg').classList.remove('ok');const options={};if(location.protocol==='https:'||location.protocol==='http:'){options.redirectTo=location.href.split('#')[0].split('?')[0];}const {error}=await sb.auth.resetPasswordForEmail(email,options);b.disabled=false;if(error){console.error(error);$('forgotMsg').textContent='Impossible d’envoyer le lien pour le moment. Réessayez dans quelques minutes.';return;}$('forgotMsg').textContent='Lien envoyé. Vérifiez votre boîte mail et vos spams.';$('forgotMsg').classList.add('ok');};
$('changePasswordBtn').onclick=()=>showPasswordEditor('change');
$('cancelPasswordBtn').onclick=async()=>{recoveryMode=false;await requireSession();};
$('savePasswordBtn').onclick=async()=>{const newPassword=$('newPassword').value,confirmPassword=$('confirmPassword').value;if(newPassword.length<8){$('passwordMsg').textContent='Le mot de passe doit contenir au moins 8 caractères.';return;}if(newPassword!==confirmPassword){$('passwordMsg').textContent='Les deux mots de passe ne correspondent pas.';return;}const b=$('savePasswordBtn');b.disabled=true;$('passwordMsg').textContent='';const {error}=await sb.auth.updateUser({password:newPassword});b.disabled=false;if(error){console.error(error);$('passwordMsg').textContent='Impossible de modifier le mot de passe.';return;}if(passwordFlow==='recovery'){recoveryMode=false;await sb.auth.signOut();showLogin('Mot de passe modifié. Connectez-vous avec le nouveau mot de passe.',true);}else{toast('Mot de passe modifié');await requireSession();}};
$('confirmPassword').addEventListener('keydown',e=>{if(e.key==='Enter')$('savePasswordBtn').click();});
$('logoutBtn').onclick=async()=>{await sb.auth.signOut();location.reload();};
sb.auth.onAuthStateChange((event,s)=>{if(event==='PASSWORD_RECOVERY'){recoveryMode=true;showPasswordEditor('recovery');return;}if(!s&&!recoveryMode)showLogin();});'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Could not replace auth handlers: {count}')

for marker in ['id="forgotBtn"','id="forgotView"','id="passwordView"','resetPasswordForEmail','updateUser({password:newPassword})',"PASSWORD_RECOVERY",'id="changePasswordBtn"']:
    if marker not in text:
        raise SystemExit('Missing generated marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Installed secure password recovery and password-change flow in admin.html')
