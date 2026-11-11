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
body{margin:0;max-width:none;padding:0}
.mv-top{background:#142e46;color:#fff;padding:14px max(18px,calc((100% - 1480px)/2 + 18px));display:flex;align-items:center;gap:14px;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.3}
.mv-top .mv-brand{flex:1;min-width:0}
.mv-top .mv-logo{font-size:22px;font-weight:800;letter-spacing:2px;color:#fff}
.mv-top .mv-logo span{font-size:13px;font-weight:400;letter-spacing:0}
.mv-top .mv-sub{color:#b9c9d7;font-size:12px}
.mv-top .mv-meta{color:#b9c9d7;font-size:12px;white-space:nowrap}
.mv-top .mv-toggle{all:unset;display:none;box-sizing:border-box;cursor:pointer;color:#fff;border:1px solid #5b7890;border-radius:9px;padding:9px 14px;font:650 14px Inter,system-ui,sans-serif}
.mv-top .mv-toggle:focus-visible,.mv-nav .mv-item:focus-visible,.mv-nav .mv-logout:focus-visible{outline:3px solid #7cc4e0;outline-offset:2px}
.mv-shell{display:grid;grid-template-columns:232px minmax(0,1fr);gap:20px;max-width:1480px;margin:0 auto;padding:20px 18px;align-items:start}
.mv-main{min-width:0}
.mv-nav{background:#fff;border:1px solid #dfe7ef;border-radius:14px;padding:12px 10px;box-shadow:0 4px 16px #102b4210;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.mv-nav .mv-group{margin:0 0 6px}
.mv-nav .mv-label{margin:0;padding:6px 10px 3px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#697d8e}
.mv-nav .mv-item{all:unset;display:block;box-sizing:border-box;width:100%;cursor:pointer;border-radius:8px;padding:7px 10px;margin:1px 0;color:#29445a;font-size:14px;line-height:1.3;text-align:left}
.mv-nav .mv-item small{color:#697d8e;font-size:11px}
.mv-nav .mv-item:hover{background:#f1f6f9}
.mv-nav .mv-item.active,.mv-nav .mv-item[aria-current=page]{background:#e8f2f7;color:#075f82;font-weight:700}
.mv-nav .mv-foot{border-top:1px solid #e6edf3;margin-top:6px;padding-top:8px}
.mv-nav form{margin:0}
.mv-nav .mv-logout{all:unset;display:block;box-sizing:border-box;width:100%;cursor:pointer;border-radius:8px;padding:7px 10px;margin:1px 0;color:#8a3b12;font-size:14px;line-height:1.3}
.mv-nav .mv-logout:hover{background:#fdf1ea}
.mv-backdrop{display:none}
.mv-title{font-size:25px;margin:0 0 6px}
.mv-lead{color:#697d8e;font-size:13px;margin:0 0 14px}
@media(max-width:1000px){
.mv-top .mv-toggle{display:inline-block}
.mv-top .mv-meta,.mv-top .mv-sub{display:none}
.mv-top{padding:10px 12px}
.mv-shell{display:block;padding:14px 12px}
.mv-nav{position:fixed;z-index:1000;top:0;left:0;bottom:0;width:min(300px,86vw);max-height:none;border-radius:0 14px 14px 0;transform:translateX(-105%);transition:transform .18s ease;visibility:hidden}
.mv-open .mv-nav{transform:none;visibility:visible}
.mv-open .mv-backdrop{display:block;position:fixed;inset:0;z-index:999;background:#0b1d2c80}
.mv-nav .mv-item,.mv-nav .mv-logout{padding:11px 10px}
}
@media(prefers-reduced-motion:reduce){.mv-nav{transition:none}}
@media print{.mv-top,.mv-nav,.mv-backdrop{display:none!important}.mv-shell{display:block;padding:0;max-width:none}}
</style>"""

JS = """<script id="mevan-nav-script">
(function(){
 var root=document.documentElement,toggle=document.getElementById('mvToggle'),nav=document.getElementById('mvNav'),backdrop=document.getElementById('mvBackdrop');
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
            + '<form method="post" action="/logout"><button class="mv-logout" type="submit">Odjava</button></form></div>')
    return f'<nav class="mv-nav" id="mvNav" aria-label="Glavni meni">{body}{foot}</nav>'


def shell_start(active: str) -> str:
    return ('<header class="mv-top">'
            '<button type="button" class="mv-toggle" id="mvToggle" aria-controls="mvNav" aria-expanded="false">Meni</button>'
            '<div class="mv-brand"><div class="mv-logo">MEVAN <span>DIAGNOSTIC</span></div>'
            '<div class="mv-sub">Operational &amp; Business Performance Transformation · PRIVATE DEMO v2.0 · SIMULACIJA</div></div>'
            '<div class="mv-meta">61 kriterij · 5 dimenzija · BS</div></header>'
            '<div class="mv-backdrop" id="mvBackdrop"></div>'
            f'<div class="mv-shell">{nav_html(active)}<div class="mv-main">')


SHELL_END = '</div></div>' + JS


def render_page(html: str, active: str) -> str:
    """Ubaci zajednički meni u stranicu koja ima tri oznake mjesta."""
    for marker in ('<!--MEVAN_NAV_CSS-->', '<!--MEVAN_SHELL_START-->', '<!--MEVAN_SHELL_END-->'):
        if html.count(marker) != 1:
            raise ValueError('Stranica nema ispravnu oznaku menija: ' + marker)
    return (html.replace('<!--MEVAN_NAV_CSS-->', CSS)
                .replace('<!--MEVAN_SHELL_START-->', shell_start(active))
                .replace('<!--MEVAN_SHELL_END-->', SHELL_END))
