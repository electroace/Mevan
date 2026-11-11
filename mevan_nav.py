"""Zajedničko zaglavlje i glavni meni za sve MEVAN ekrane.

Server ubacuje isti meni u četiri postojeće HTML stranice umjesto da svaka
stranica ima vlastitu navigaciju. Ovdje nema poslovne logike: samo raspored,
nazivi i izgled menija. Funkcije stranica ostaju u njihovim HTML datotekama.
"""
from html import escape

# Stavke glavnog ekrana (index.html) otvaraju se preko data-page; na ostalim
# ekranima isti link vodi na glavni ekran s oznakom stranice u adresi (/#...).
MODULES = (
    ('Finansije', 'Finansije'),
    ('Operacije', 'Operacije'),
    ('Planiranje', 'Planiranje i Supply Chain'),
    ('Ljudi', 'Ljudi i liderstvo'),
    ('Upravljanje', 'Sistem upravljanja'),
)
PAGES = ('workspace', 'company', 'overview', 'finance', 'v2', 'review', 'report', 'plan', 'data')
SCREENS = ('diagnostic', 'guided', 'projects', 'portfolio')

CSS = """<style id="mevan-nav-style">
:root{--mv-ink:#193047;--mv-muted:#566b7c;--mv-line:#dfe7ef;--mv-field:#b3c3d0;--mv-bg:#f3f6fa;--mv-card:#fff;--mv-soft:#f3f7fa;--mv-brand:#0a6485;--mv-brand-hover:#085673;--mv-brand-dark:#142e46;--mv-warn-bg:#fff4dc;--mv-warn-ink:#8a4d00;--mv-warn-line:#e3bd6d;--mv-danger:#a42121;--mv-ok:#12715f;--mv-radius:12px;--mv-radius-s:8px;--mv-font:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
body{margin:0;max-width:none;padding:0;background:var(--mv-bg);color:var(--mv-ink)}
.mv-top{background:#142e46;color:#fff;padding:14px max(18px,calc((100% - 1480px)/2 + 18px));display:flex;align-items:center;gap:14px;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.3}
.mv-top .mv-brand{flex:1;min-width:0}
.mv-top .mv-logo{font-size:22px;font-weight:800;letter-spacing:2px;color:#fff}
.mv-top .mv-logo span{font-size:13px;font-weight:400;letter-spacing:0}
.mv-top .mv-sub{color:#b9c9d7;font-size:12px}
.mv-top .mv-meta{color:#b9c9d7;font-size:12px;white-space:nowrap}
.mv-top .mv-toggle{all:unset;display:none;box-sizing:border-box;cursor:pointer;color:#fff;border:1px solid #5b7890;border-radius:9px;padding:9px 14px;font:650 14px Inter,system-ui,sans-serif}
.mv-top .mv-toggle:focus-visible{outline:3px solid #7cc4e0;outline-offset:2px}
.mv-nav .mv-item:focus-visible,.mv-nav .mv-logout:focus-visible{outline:3px solid var(--mv-brand);outline-offset:-2px}
.mv-shell{display:grid;grid-template-columns:232px minmax(0,1fr);gap:20px;max-width:1480px;margin:0 auto;padding:20px 18px;align-items:start}
.mv-main{min-width:0;font:16px/1.5 var(--mv-font);color:var(--mv-ink)}
.mv-main>main,.mv-main>.rv-page{max-width:none;margin:0;padding:0}
.mv-main h1{font-size:25px;line-height:1.25;margin:0 0 6px}
.mv-main h2{font-size:18px;line-height:1.3}
.mv-main h3{font-size:15px;line-height:1.35}
.mv-main .muted,.mv-main .mv-lead{color:var(--mv-muted)}
.mv-main .panel,.mv-main .card,.mv-main .rv-page section,.mv-main .rv-page details{background:var(--mv-card);border:1px solid var(--mv-line);border-radius:var(--mv-radius)}
.mv-main .big,.mv-main .number{font-size:26px;font-weight:750;line-height:1.2}
.mv-main input:not([type=checkbox]):not([type=radio]):not([type=file]),.mv-main select,.mv-main textarea{border:1px solid var(--mv-field);border-radius:var(--mv-radius-s);padding:10px;min-height:42px;font:inherit;font-weight:400;background:#fff;color:var(--mv-ink)}
.mv-main input:focus-visible,.mv-main select:focus-visible,.mv-main textarea:focus-visible,.mv-main summary:focus-visible,.mv-main a:focus-visible,.mv-main .item:focus-visible{outline:3px solid var(--mv-brand);outline-offset:2px}
.mv-main .warning,.mv-main .warn{color:var(--mv-warn-ink);background:var(--mv-warn-bg);border:1px solid var(--mv-warn-line);border-radius:var(--mv-radius-s);padding:10px 12px;font-size:14px}
.mv-main .note{color:var(--mv-muted);border-left:3px solid var(--mv-line);padding:2px 0 2px 12px;font-size:14px}
.mv-sync{margin:-8px 0 12px;font-size:13px;color:var(--mv-muted);text-align:right;min-height:18px}
.mv-sync.is-error{color:var(--mv-danger);font-weight:650}
.mv-meter{display:flex;align-items:center;gap:10px;margin-top:8px}
.mv-meter .progress{flex:1}
.mv-meter .progress>div{background:var(--mv-brand)}
.mv-meter b{font-size:14px;white-space:nowrap;min-width:84px;text-align:right}
.mv-main details.fx{padding:0}
.mv-main details.fx>summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:6px 14px;align-items:center;padding:14px 18px;border-radius:var(--mv-radius)}
.mv-main details.fx>summary::-webkit-details-marker{display:none}
.mv-main details.fx>summary::before{content:"+";grid-column:3;grid-row:1;font-weight:700;color:var(--mv-brand);width:22px;text-align:center}
.mv-main details.fx[open]>summary::before{content:"–"}
.mv-main details.fx>summary .fx-name{font-weight:700;min-width:0}
.mv-main details.fx>summary .fx-amount{font-weight:700;white-space:nowrap}
.mv-main details.fx>summary .fx-status{grid-column:1/-1;font-size:13px;color:var(--mv-muted)}
.mv-main details.fx>.fx-body{padding:0 18px 18px;border-top:1px solid var(--mv-line)}
.mv-toasts{position:fixed;z-index:1200;left:50%;bottom:16px;transform:translateX(-50%);display:flex;flex-direction:column;gap:8px;width:min(560px,calc(100vw - 24px));font:15px/1.4 var(--mv-font)}
.mv-toast{display:flex;gap:12px;align-items:flex-start;background:var(--mv-brand-dark);color:#fff;border-radius:10px;padding:12px 14px;box-shadow:0 8px 28px #0b1d2c40;white-space:pre-line}
.mv-toast.is-error{background:#7d1a1a}
.mv-toast span{flex:1}
.mv-toast button{all:unset;cursor:pointer;font-weight:700;padding:0 6px;border-radius:6px}
.mv-toast button:focus-visible{outline:2px solid #fff;outline-offset:2px}
.mv-dialog{border:0;border-radius:14px;padding:0;width:min(460px,calc(100vw - 24px));color:var(--mv-ink);font:16px/1.5 var(--mv-font);box-shadow:0 20px 60px #0b1d2c50}
.mv-dialog::backdrop{background:#0b1d2c80}
.mv-dialog form{margin:0;padding:22px}
.mv-dialog h2{font-size:18px;margin:0 0 8px}
.mv-dialog p{margin:0 0 14px;white-space:pre-line}
.mv-dialog label{display:block;font-size:13px;font-weight:650;margin:0 0 5px}
.mv-dialog input{box-sizing:border-box;width:100%;border:1px solid var(--mv-field);border-radius:var(--mv-radius-s);padding:10px;font:inherit;margin-bottom:14px}
.mv-dialog input:focus-visible,.mv-dialog button:focus-visible{outline:3px solid var(--mv-brand);outline-offset:2px}
.mv-dialog .mv-actions{display:flex;flex-direction:row-reverse;gap:10px;justify-content:flex-start;flex-wrap:wrap}
.mv-dialog button{appearance:none;box-sizing:border-box;min-height:44px;padding:9px 16px;border-radius:9px;border:1px solid var(--mv-brand);background:var(--mv-brand);color:#fff;font:650 14px/1.2 var(--mv-font);cursor:pointer}
.mv-dialog button[value=cancel]{background:#fff;color:var(--mv-brand)}
.mv-dialog.is-danger button[value=ok]{background:var(--mv-danger);border-color:var(--mv-danger)}
.mv-nav{background:#fff;border:1px solid #dfe7ef;border-radius:14px;padding:12px 10px 0;box-shadow:0 4px 16px #102b4210;position:sticky;top:16px;max-height:calc(100vh - var(--mv-head,76px) - 32px);overflow:auto;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.mv-nav .mv-group{margin:0 0 6px}
.mv-nav .mv-label{margin:0;padding:6px 10px 3px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#566b7c}
.mv-nav .mv-item{all:unset;display:block;box-sizing:border-box;width:100%;cursor:pointer;border-radius:8px;padding:7px 10px;margin:1px 0;color:#29445a;font-size:14px;line-height:1.3;text-align:left}
.mv-nav .mv-item small{color:#566b7c;font-size:11px}
.mv-nav .mv-item:hover{background:#f1f6f9}
.mv-nav .mv-item.active,.mv-nav .mv-item[aria-current=page]{background:#e8f2f7;color:#075f82;font-weight:700}
.mv-nav .mv-foot{border-top:1px solid #e6edf3;margin-top:6px;padding:8px 0 10px;position:sticky;bottom:0;background:#fff}
.mv-nav form{margin:0}
.mv-nav .mv-logout{all:unset;display:block;box-sizing:border-box;width:100%;cursor:pointer;border-radius:8px;padding:7px 10px;margin:1px 0;color:#8a3b12;font-size:14px;line-height:1.3}
.mv-nav .mv-logout:hover{background:#fdf1ea}
.mv-backdrop{display:none}
.mv-main .btn{appearance:none;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;width:auto;min-height:40px;margin:4px 8px 4px 0;padding:9px 16px;border:1px solid #0a6485;border-radius:9px;background:#0a6485;color:#fff;font:650 14px/1.2 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;text-align:center;text-decoration:none;cursor:pointer}
.mv-main .btn:hover{background:#085673;border-color:#085673}
.mv-main .btn.secondary{background:#fff;color:#0a6485}
.mv-main .btn.secondary:hover{background:#eef6f9;border-color:#0a6485}
.mv-main .btn.danger{background:#fff;color:#a42121;border-color:#dcaaaa}
.mv-main .btn.danger:hover{background:#fdf0f0;border-color:#a42121}
.mv-main .btn.small{min-height:32px;padding:5px 12px;font-size:13px}
.mv-main .btn:disabled{opacity:.45;cursor:not-allowed}
.mv-main .btn:focus-visible{outline:3px solid var(--mv-brand);outline-offset:2px}
.mv-main .btn[hidden]{display:none}
.mv-main .row>.btn{margin:0}
.mv-main .row>.btn.push{margin-left:auto}
.mv-title{font-size:25px;margin:0 0 6px}
.mv-lead{color:#566b7c;font-size:13px;margin:0 0 14px}
@media(max-width:1000px){
.mv-top .mv-toggle{display:inline-block}
.mv-top .mv-meta,.mv-top .mv-sub{display:none}
.mv-top{padding:10px 12px}
.mv-shell{display:block;padding:14px 12px}
.mv-nav{position:fixed;z-index:1000;top:0;left:0;bottom:0;width:min(300px,86vw);max-height:none;border-radius:0 14px 14px 0;transform:translateX(-105%);transition:transform .18s ease;visibility:hidden}
.mv-open .mv-nav{transform:none;visibility:visible}
.mv-open .mv-backdrop{display:block;position:fixed;inset:0;z-index:999;background:#0b1d2c80}
.mv-nav .mv-item,.mv-nav .mv-logout{padding:11px 10px}
.mv-main .btn,.mv-main .btn.small{min-height:44px}
.mv-main details.fx>summary{grid-template-columns:minmax(0,1fr) auto}
.mv-main details.fx>summary .fx-amount{grid-column:1;grid-row:2}
.mv-main details.fx>summary::before{grid-column:2}
.mv-main details.fx>summary .fx-status{grid-row:3}
}
@media(prefers-reduced-motion:reduce){.mv-nav{transition:none}}
@media print{.mv-top,.mv-nav,.mv-backdrop,.mv-toasts,.mv-sync{display:none!important}.mv-shell{display:block;padding:0;max-width:none}}
</style>"""

JS = """<script id="mevan-nav-script">
(function(){
 var root=document.documentElement,toggle=document.getElementById('mvToggle'),nav=document.getElementById('mvNav'),backdrop=document.getElementById('mvBackdrop');
 // Meni staje u visinu ekrana ispod zaglavlja, pa je „Odjava” vidljiva bez pomjeranja stranice.
 function fitNav(){root.style.setProperty('--mv-head',document.querySelector('.mv-top').offsetHeight+'px')}
 fitNav();window.addEventListener('resize',fitNav);
 function setOpen(open){root.classList.toggle('mv-open',open);toggle.setAttribute('aria-expanded',open?'true':'false')}
 toggle.addEventListener('click',function(){setOpen(!root.classList.contains('mv-open'))});
 backdrop.addEventListener('click',function(){setOpen(false)});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&root.classList.contains('mv-open')){setOpen(false);toggle.focus()}});
 nav.addEventListener('click',function(e){
  var item=e.target.closest('.mv-item');if(!item)return;
  if(item.hasAttribute('data-mv-guided')){
   if(typeof openDiagnosticReview==='function')openDiagnosticReview();
   else if(item.getAttribute('aria-current')!=='page')location.href='/#guided';
  }
  setOpen(false);
 });
})();
// Poruke i potvrde u aplikaciji (umjesto sistemskih prozora preglednika).
(function(){
 var toasts=document.getElementById('mvToasts'),dialog=document.getElementById('mvDialog');
 window.mvNotify=function(message,isError){
  var item=document.createElement('div'),text=document.createElement('span'),close=document.createElement('button');
  item.className='mv-toast'+(isError?' is-error':'');if(isError)item.setAttribute('role','alert');
  text.textContent=String(message);close.type='button';close.textContent='×';close.setAttribute('aria-label','Zatvori poruku');
  close.onclick=function(){item.remove()};item.append(text,close);toasts.append(item);
  if(!isError)setTimeout(function(){item.remove()},7000);
 };
 function ask(options){
  return new Promise(function(resolve){
   var input=dialog.querySelector('input'),label=dialog.querySelector('label'),ok=dialog.querySelector('[value=ok]');
   dialog.querySelector('h2').textContent=options.title||'Potvrda';
   dialog.querySelector('p').textContent=options.message||'';dialog.querySelector('p').hidden=!options.message;
   var wantsText=options.label!==undefined;label.hidden=input.hidden=!wantsText;
   label.textContent=options.label||'';input.value=options.value||'';
   ok.textContent=options.okLabel||'Potvrdi';dialog.classList.toggle('is-danger',!!options.danger);
   dialog.returnValue='cancel';
   dialog.onclose=function(){var yes=dialog.returnValue==='ok';resolve(wantsText?(yes?input.value:null):yes)};
   dialog.showModal();(wantsText?input:dialog.querySelector('[value=cancel]')).focus();if(wantsText)input.select();
  });
 }
 window.mvConfirm=function(message,options){options=options||{};return ask({title:options.title,message:message,okLabel:options.okLabel,danger:options.danger})};
 window.mvAsk=function(label,value,options){options=options||{};return ask({title:options.title||'Unos',message:options.message,label:label,value:value,okLabel:options.okLabel||'Sačuvaj',danger:options.danger})};
 // Svaki vidljivi natpis polja povezuje se s poljem ispod njega (čitači ekrana, klik na natpis).
 var main=document.querySelector('.mv-main'),counter=0,queued=false,CONTROL='input:not([type=hidden]),select,textarea';
 function linkLabels(){
  queued=false;
  main.querySelectorAll('label:not([for])').forEach(function(label){
   if(label.querySelector(CONTROL))return;
   var node=label.nextElementSibling,control=null;
   while(node&&node.tagName!=='LABEL'&&!control){
    if(node.matches(CONTROL))control=node;
    else if(!node.querySelector('label'))control=node.querySelector(CONTROL);
    node=node.nextElementSibling;
   }
   if(!control||(control.id&&main.querySelector('label[for="'+CSS.escape(control.id)+'"]')))return;
   if(!control.id)control.id='mvf-'+(++counter);
   label.htmlFor=control.id;
  });
 }
 window.mvLinkLabels=linkLabels;linkLabels();
 new MutationObserver(function(){if(!queued){queued=true;requestAnimationFrame(linkLabels)}}).observe(main,{childList:true,subtree:true});
})();
</script>"""


def _page(key, label, on_diagnostic):
    # Na glavnom ekranu stavku aktivira postojeći render(); drugdje je običan link.
    return f'<a class="mv-item" href="/#{escape(key)}" data-page="{escape(key)}">{escape(label)}</a>'


def _screen(href, label, active):
    current = ' aria-current="page"' if active else ''
    return f'<a class="mv-item" href="{href}"{current}>{escape(label)}</a>'


def nav_html(active: str) -> str:
    if active not in SCREENS:
        raise ValueError('Nepoznat ekran za meni')
    diag = active == 'diagnostic'
    modules = ''.join(_page('m:' + key, label, diag) for key, label in MODULES)
    guided_current = ' aria-current="page"' if active == 'guided' else ''
    guided = ('<button type="button" class="mv-item" data-mv-guided'
              ' aria-label="Vođeno prikupljanje i završni izvještaji"'
              f'{guided_current}>Vođeno prikupljanje</button>')
    groups = (
        ('Kompanija', _page('workspace', 'Kompanije i dijagnostike', diag) + _page('company', 'Profil kompanije', diag)),
        ('Procjena', _page('overview', 'Pregled', diag) + f'<div id="navModules">{modules}</div>'
         + _page('finance', 'Finansijski efekti', diag)),
        ('Analiza i izvještaji', guided + _page('v2', 'Integrisana analiza (AI)', diag)
         + _page('review', 'Analiza i odobravanje', diag) + _page('report', 'Izvještaji', diag)
         + _page('plan', 'Plan 90 dana', diag)),
        ('Projekti', _screen('/projects-ui', 'Projekti', active == 'projects')
         + _screen('/dashboard-ui', 'Pregled portfolija', active == 'portfolio')),
    )
    body = ''.join(f'<div class="mv-group"><p class="mv-label">{escape(title)}</p>{items}</div>'
                   for title, items in groups)
    foot = ('<div class="mv-foot">' + _page('data', 'Podaci i sigurnost', diag)
            + '<form method="post" action="/logout"><input type="hidden" name="csrf_token" value="__MEVAN_LOGOUT_TOKEN__">'
            '<button class="mv-logout" type="submit">Odjava</button></form></div>')
    return f'<nav class="mv-nav" id="mvNav" aria-label="Glavni meni">{body}{foot}</nav>'


def shell_start(active: str) -> str:
    return ('<header class="mv-top">'
            '<button type="button" class="mv-toggle" id="mvToggle" aria-controls="mvNav" aria-expanded="false">Meni</button>'
            '<div class="mv-brand"><div class="mv-logo">MEVAN <span>DIAGNOSTIC</span></div>'
            '<div class="mv-sub">Operational &amp; Business Performance Transformation · PRIVATE DEMO v2.0 · SIMULACIJA</div></div>'
            '<div class="mv-meta">61 kriterij · 5 dimenzija · BS</div></header>'
            '<div class="mv-backdrop" id="mvBackdrop"></div>'
            f'<div class="mv-shell">{nav_html(active)}<div class="mv-main">')


OVERLAYS = ('<div class="mv-toasts" id="mvToasts" aria-live="polite"></div>'
            '<dialog class="mv-dialog" id="mvDialog" aria-labelledby="mvDialogTitle"><form method="dialog">'
            '<h2 id="mvDialogTitle"></h2><p></p><label for="mvDialogInput"></label><input id="mvDialogInput" autocomplete="off">'
            '<div class="mv-actions"><button value="ok">Potvrdi</button><button value="cancel" formnovalidate>Odustani</button></div>'
            '</form></dialog>')

SHELL_END = '</div></div>' + OVERLAYS + JS


def render_page(html: str, active: str) -> str:
    """Ubaci zajednički meni u stranicu koja ima tri oznake mjesta."""
    for marker in ('<!--MEVAN_NAV_CSS-->', '<!--MEVAN_SHELL_START-->', '<!--MEVAN_SHELL_END-->'):
        if html.count(marker) != 1:
            raise ValueError('Stranica nema ispravnu oznaku menija: ' + marker)
    return (html.replace('<!--MEVAN_NAV_CSS-->', CSS)
                .replace('<!--MEVAN_SHELL_START-->', shell_start(active))
                .replace('<!--MEVAN_SHELL_END-->', SHELL_END))
