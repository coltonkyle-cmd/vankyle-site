import json, re, os, sys, html as H
SRC = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SRC)
MODS = json.load(open(f'{SRC}/lessons.json')); GLOS = json.load(open(f'{SRC}/glossary.json'))
LESSONS = [(m, l, j) for m in MODS for j, l in enumerate(m['lessons'])]
BYSLUG = {l['slug']: (m, l, j) for m, l, j in LESSONS}
ANCHOR = {(m['slug'], l['id']): l['slug'] for m, l, j in LESSONS}
TOTAL = len(LESSONS)
import hashlib
CSSV = hashlib.md5(open(f'{ROOT}/styles.css','rb').read()).hexdigest()[:8]
SOCIAL = [("https://www.instagram.com/lihtcexplained/","Instagram"),("https://www.youtube.com/@lihtcexplained","YouTube"),("https://www.facebook.com/lihtcexplained","Facebook"),("https://www.threads.com/@lihtcexplained","Threads"),("https://www.linkedin.com/in/colton-kyle-mba-03282821/","LinkedIn")]
NAV = [("start-here.html","Start here"),("course.html","Course"),("tools.html","Tools")]
MORE = [("glossary.html","Glossary"),("renters.html","For renters"),("sources.html","Sources"),("about.html","About")]
NAVJS = "<script>document.addEventListener('click',function(e){document.querySelectorAll('.nav-more[open]').forEach(function(d){if(!d.contains(e.target))d.removeAttribute('open')})});document.addEventListener('keydown',function(e){if(e.key==='Escape')document.querySelectorAll('.nav-more[open]').forEach(function(d){d.removeAttribute('open');d.querySelector('summary').focus()})})</script>"

def nav(cur, p):
    a = lambda h, t: f'<a href="{p}{h}"' + (' aria-current="page"' if h == cur else '') + f'>{t}</a>'
    top = ''.join(a(h, t) for h, t in NAV)
    on = ' data-current' if any(h == cur for h, _ in MORE) else ''
    menu = ''.join(a(h, t) for h, t in MORE)
    return f'<nav class="nav">{top}<details class="nav-more"{on}><summary>More</summary><div class="nav-menu">{menu}</div></details>{NAVJS}</nav>'
def fonts(p):
    return f'<link rel="preload" href="{p}assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="{p}assets/fonts/archivo-black-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>'
SKIP = '<a class="skip" href="#main">Skip to content</a>'
def header(cur, p):
    return SKIP + f'\n<header class="site-header"><div class="wrap">\n  <a class="brand" href="{p}index.html"><img src="{p}assets/le.svg" alt=""><span>LIHTC Explained</span></a>\n  {nav(cur, p)}\n</div></header>'
NL_NAME = 'LIHTC Explained'  # newsletter name: change here and it updates the signup card, footer and pop-up
KIT_FORM = 'https://app.kit.com/forms/10232563/subscriptions'  # Kit form "Website signup (vankyleproperties.com)"
SIGNUP_JS = "<script>document.addEventListener('submit',function(e){var f=e.target;if(!f.classList||!f.classList.contains('signup-form'))return;e.preventDefault();var m=f.querySelector('.signup-msg'),b=f.querySelector('button');b.disabled=true;fetch(f.action,{method:'POST',body:new FormData(f),headers:{Accept:'application/json'}}).then(function(r){return r.json()}).then(function(d){if(!d||d.status!=='success')throw 0;f.classList.add('done');m.textContent='Almost done: check your inbox for an email from colton@vankyleproperties.com and click the link to confirm.'}).catch(function(){b.disabled=false;m.textContent='That didn\\'t go through. Please try again, or email colton@vankyleproperties.com.'})})</script>"
def signup_form(uid, compact=False):
    return (f'<form class="signup-form{" compact" if compact else ""}" action="{KIT_FORM}" method="post">'
            f'<label class="sr-only" for="su-{uid}">Email address</label>'
            f'<input id="su-{uid}" type="email" name="email_address" placeholder="you@example.com" autocomplete="email" required>'
            f'<button class="btn primary" type="submit">Subscribe</button>'
            f'<p class="signup-msg" role="status" aria-live="polite"></p></form>')
def signup_card(uid):
    return (f'<div class="signup-card"><strong>{NL_NAME} newsletter</strong>'
            f'<p>Short emails on how affordable housing deals actually get done, with new lessons and rule changes rolled in. Plain English, no spam, unsubscribe anytime.</p>'
            f'{signup_form(uid)}'
            f'<p class="signup-from">Emails come from Colton Kyle (colton@vankyleproperties.com). LIHTC Explained is a VanKyle Properties publication.</p></div>')
POPUP_JS = "<script>(function(){var K='vk_nl_pop',el=document.getElementById('nl-pop');if(!el)return;try{var v=localStorage.getItem(K);if(v&&(v==='subscribed'||Date.now()-Number(v)<2592e6))return}catch(e){}var shown=false,t;function seen(){var c=document.querySelector('main .signup-card'),r=c&&c.getBoundingClientRect();return !!(r&&r.top<innerHeight&&r.bottom>0)}function show(){if(shown)return;if(seen()){shown=true;clearTimeout(t);removeEventListener('scroll',sc);return}shown=true;clearTimeout(t);removeEventListener('scroll',sc);el.hidden=false;addEventListener('scroll',sc2,{passive:true});requestAnimationFrame(function(){requestAnimationFrame(function(){el.classList.add('in')})})}function sc(){var h=document.documentElement;if((h.scrollTop+innerHeight)/h.scrollHeight>=0.6)show()}function sc2(){if(seen()&&!el.contains(document.activeElement)){removeEventListener('scroll',sc2);el.classList.remove('in');setTimeout(function(){el.hidden=true},250)}}function hide(){removeEventListener('scroll',sc2);el.classList.remove('in');setTimeout(function(){el.hidden=true},250);try{localStorage.setItem(K,String(Date.now()))}catch(e){}}t=setTimeout(show,40000);addEventListener('scroll',sc,{passive:true});el.querySelector('.nl-pop-x').addEventListener('click',hide);document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!el.hidden)hide()});document.addEventListener('submit',function(e){var f=e.target;if(f.classList&&f.classList.contains('signup-form')){try{localStorage.setItem(K,'subscribed')}catch(x){}}})})()</script>"
def popup():
    # Slide-in newsletter card: shows once per visitor after 60% scroll or 40 seconds; skipped (or tucked away) on a page when the inline signup card is on screen; closed = hidden 30 days; subscribed = never again.
    return (f'<aside class="nl-pop" id="nl-pop" role="dialog" aria-labelledby="nl-pop-t" hidden>'
            f'<button class="nl-pop-x" type="button" aria-label="Close">&times;</button>'
            f'<strong id="nl-pop-t">Get the {NL_NAME} newsletter</strong>'
            f'<p>How affordable housing deals actually get done, in plain English, with new lessons and rule changes rolled in. No spam, unsubscribe anytime.</p>'
            f'{signup_form("pop")}</aside>' + POPUP_JS)
def footer(p):
    soc = ''.join(f'<a href="{u}">{t}</a>' for u, t in SOCIAL)
    return f'''<footer class="site-footer"><div class="wrap">
  <div><a href="{p}start-here.html">Start here</a><a href="{p}course.html">Course</a><a href="{p}tools.html">Tools</a><a href="{p}glossary.html">Glossary</a><a href="{p}renters.html">Renters</a><a href="{p}sources.html">Sources</a><a href="{p}about.html">About</a><a href="mailto:colton@vankyleproperties.com">colton@vankyleproperties.com</a></div>
  <div class="footer-signup"><strong>Get the {NL_NAME} newsletter</strong>{signup_form('footer', compact=True)}</div>
  <div class="social">{soc}</div>
  <p class="disclaimer">Education only. Not tax, legal or investment advice. Views are my own and don't represent my employer. LIHTC Explained is a VanKyle Properties publication. &copy; 2026 VanKyle Properties, LLC.</p>
</div></footer>
''' + SIGNUP_JS
SITE = 'https://www.lihtcexplained.com'
GC_CODE = 'vankyle'  # GoatCounter site code: https://vankyle.goatcounter.com
OG_IMG = 'assets/og-default.png'
GSV = 'a39eCfTlJxCAAO9445ophKeODE1GGXDesJ9y5xqYO3U'  # Google Search Console ownership tag
BUILT = []
REVIEWED = ('2026-11', 'November 2026')  # bump when lessons are re-checked; a lesson can override with "reviewed": ["YYYY-MM", "Month YYYY"]
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "LIHTC Explained", "parentOrganization": {"@type": "Organization", "name": "VanKyle Properties, LLC"}, "url": SITE + "/", "logo": SITE + "/assets/le.svg", "email": "colton@vankyleproperties.com", "sameAs": [u for u, _ in SOCIAL[:4]]}
PERSON = {"@type": "Person", "@id": SITE + "/#colton", "name": "Colton Kyle", "jobTitle": "Real estate developer", "homeLocation": {"@type": "Place", "name": "Shreveport, Louisiana"}, "url": SITE + "/about.html", "image": SITE + "/assets/colton-kyle.jpg", "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Centenary College of Louisiana"}, {"@type": "CollegeOrUniversity", "name": "Louisiana Tech University"}], "sameAs": [SOCIAL[4][0]]}
def ld(*items):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": list(items)}, separators=(',', ':')) + '</script>'
def crumbs_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate(trail)]}
def title_tag(title):
    t = title if title.startswith('LIHTC Explained') else f'{title} | LIHTC Explained'
    if len(t) > 60: t = title
    if len(t) > 60: t = re.sub(r' \(Lesson [\d.]+\)$', '', t)
    return t
def fit_desc(d, extra=''):
    d = re.sub(r'\s+', ' ', d).strip()
    if len(d) < 70 and extra:
        for x in re.split(r'(?<=[.!?])\s', re.sub(r'\s+', ' ', extra).strip()):
            if not x or x in d: continue
            if len(d) + 1 + len(x) > 160: break
            d += ' ' + x
            if len(d) >= 70: break
        if len(d) < 70: d = re.sub(r'\s+', ' ', extra).strip()
    if len(d) > 160:
        cut = d[:158]; cut = cut[:cut.rfind(' ')].rstrip(',;:')
        d = cut + '…'
    return d
def seo(path, title, desc, data=''):
    url = SITE + '/' + ('' if path == 'index.html' else path)
    t = H.escape(title, quote=True); d = H.escape(desc, quote=True)
    return f'''<!--seo-->
<link rel="canonical" href="{url}">
<meta name="google-site-verification" content="{GSV}">
<meta property="og:site_name" content="LIHTC Explained">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{OG_IMG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="LIHTC Explained with Colton Kyle: how affordable housing actually gets built">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/{OG_IMG}">
{data}
<script data-goatcounter="https://{GC_CODE}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<!--/seo-->'''

def page(path, title, desc, cur, body, extra_head='', data='', pop=True):
    p = '../' * path.count('/')
    desc = fit_desc(desc)
    if 'w-widget' in body or 'VK.' in body: extra_head += f'\n<script src="{p}assets/widgets.js" defer></script>'
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title_tag(title), quote=False)}</title>
<meta name="description" content="{H.escape(desc, quote=True)}">
{seo(path, title, desc, data)}
<link rel="icon" type="image/svg+xml" href="{p}assets/le.svg">
{fonts(p)}
<link rel="stylesheet" href="{p}styles.css?v={CSSV}">{extra_head}
</head>
<body>
{header(cur, p)}

<main id="main">
{body}
</main>

{footer(p)}{popup() if pop else ''}
</body>
</html>
'''
    os.makedirs(os.path.dirname(f'{ROOT}/{path}') or ROOT, exist_ok=True)
    open(f'{ROOT}/{path}', 'w').write(out)
    BUILT.append(path)

def strip(s): return H.unescape(re.sub(r'<[^>]+>', '', s))
def summary(l):
    t = strip(re.search(r'<p>(.*?)</p>', l['body'], re.S).group(1))
    return re.split(r'(?<=[.!?])\s', t)[0]
def meta_desc(l):
    t = strip(re.search(r'<p>(.*?)</p>', l['body'], re.S).group(1))
    parts = re.split(r'(?<=[.!?])\s', t); d = parts[0]
    for x in parts[1:]:
        if len(d) >= 70: break
        d += ' ' + x
    return fit_desc(d, strip(l['body']))
def fix_links(s):
    def rep(mo):
        mod, frag = mo.group(1), mo.group(2)
        if frag and (mod, frag[1:]) in ANCHOR: return f'href="{ANCHOR[(mod, frag[1:])]}.html"'
        return f'href="../{mod}.html{frag or ""}"'
    mods = '|'.join(re.escape(m['slug']) for m in MODS)
    return re.sub(rf'href="({mods})\.html(#[^"]*)?"', rep, s)
FOLLOW = '<div class="follow-strip"><strong>Watch it in 30 seconds.</strong> Lessons also come out as carousels and short videos. ' + ' &middot; '.join(f'<a href="{u}">{t}</a>' for u, t in SOCIAL[:4]) + '</div>'
DISC = '<p class="sources">Education only. Not tax, legal or investment advice. Rules have details and exceptions; talk to a qualified professional about any specific deal. Example numbers are made up and labeled.</p>'
TOOLINFO = {'capital-stack': ('Capital stack calculator', 'Change costs, rents, rates and credit prices, flip between 9% and 4%, and watch the financing gap move.'),
            'rent-cap': ('Rent cap calculator', 'Turn an income limit into maximum rents by apartment size, with the utility allowance taken out.')}

def terms_for(l):
    txt = strip(l['body'] + l.get('more', '')).lower()
    out = []
    for g in GLOS:
        short = re.sub(r'\s*\(.*?\)', '', g['term']).lower()
        abbr = re.search(r'\((.*?)\)', g['term'])
        keys = [short] + ([abbr.group(1).lower()] if abbr else [])
        if g['lesson'] == l['slug'] or any(re.search(r'\b' + re.escape(k) + r'\b', txt) for k in keys if len(k) > 2):
            out.append(g)
    return out[:10]

# glossary pop-ups: first mention of each glossary term in a lesson becomes a link with a hover/tap definition
def _gl_keys(g):
    short = re.sub(r'\s*\(.*?\)', '', g['term']).strip()
    abbr = re.search(r'\((.*?)\)', g['term'])
    ks = [short] + ([abbr.group(1)] if abbr else [])
    out = []
    for k in ks:
        cs = k == k.upper()  # acronyms (AMI, HOME, GP) match exact case only
        out.append(re.compile(r'(?<![\w-])(' + re.escape(k) + r'(?:s|es)?)(?![\w-])', 0 if cs else re.I))
    return out
GL_KEYS = sorted(((len(k.pattern), k, g) for g in GLOS for k in _gl_keys(g)), key=lambda x: -x[0])
GL_SKIP = {'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'button', 'code', 'script', 'style', 'summary', 'label', 'select', 'option', 'textarea', 'th'}
def gloss_link(s, p='../'):
    done = set()
    for _, rx, g in GL_KEYS:
        if g['id'] in done: continue
        parts = re.split(r'(<[^>]+>)', s); depth = 0; hit = False
        for i, t in enumerate(parts):
            if t.startswith('<'):
                m = re.match(r'<(/?)([a-zA-Z0-9]+)', t)
                if m and m.group(2).lower() in GL_SKIP and not t.endswith('/>'):
                    depth += -1 if m.group(1) else 1
                continue
            if depth or hit: continue
            mo = rx.search(t)
            if not mo: continue
            a = (f'<a class="gl" href="{p}glossary.html#{g["id"]}" data-t="{H.escape(g["term"], quote=True)}" '
                 f'data-d="{H.escape(g["def"], quote=True)}">{mo.group(1)}</a>')
            parts[i] = t[:mo.start()] + a + t[mo.end():]; hit = True
        if hit:
            done.add(g['id']); s = ''.join(parts)
    return s
GLOSS_JS = """<script>(function(){var tip,cur,ht,st,pd=0,fine=matchMedia('(hover:hover) and (pointer:fine)').matches;
function mk(){tip=document.createElement('div');tip.className='gl-tip';tip.id='gl-tip';tip.setAttribute('role','tooltip');tip.hidden=true;document.body.appendChild(tip);
tip.addEventListener('mouseenter',function(){clearTimeout(ht)});tip.addEventListener('mouseleave',hideSoon)}
function show(a){if(!tip)mk();clearTimeout(ht);if(cur===a&&!tip.hidden)return;cur=a;tip.innerHTML='';
var b=document.createElement('strong');b.textContent=a.dataset.t;var d=document.createElement('p');d.textContent=a.dataset.d;
var l=document.createElement('a');l.href=a.href;l.textContent='Full glossary entry \\u2192';tip.append(b,d,l);tip.hidden=false;a.setAttribute('aria-describedby','gl-tip');
var r=a.getBoundingClientRect(),w=Math.min(320,innerWidth-24);tip.style.width=w+'px';
var x=Math.max(12,Math.min(r.left+r.width/2-w/2,innerWidth-w-12)),h=tip.offsetHeight,y=r.bottom+8;
if(y+h>innerHeight-8&&r.top-h-8>8)y=r.top-h-8;tip.style.left=(x+scrollX)+'px';tip.style.top=(y+scrollY)+'px'}
function hide(){if(tip){tip.hidden=true}if(cur){cur.removeAttribute('aria-describedby');cur=null}}
function hideSoon(){clearTimeout(st);ht=setTimeout(hide,180)}
document.addEventListener('mouseover',function(e){if(!fine)return;var a=e.target.closest&&e.target.closest('a.gl');if(a){clearTimeout(st);st=setTimeout(function(){show(a)},120)}});
document.addEventListener('mouseout',function(e){if(!fine)return;var a=e.target.closest&&e.target.closest('a.gl');if(a&&!a.contains(e.relatedTarget)){clearTimeout(st);hideSoon()}});
document.addEventListener('pointerdown',function(){pd=Date.now()},true);
document.addEventListener('focusin',function(e){if(Date.now()-pd<600)return;var a=e.target.closest&&e.target.closest('a.gl');if(a)show(a);else if(!(tip&&tip.contains(e.target)))hide()});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a.gl');
if(a&&!fine){if(cur!==a||!tip||tip.hidden){e.preventDefault();show(a)}return}if(tip&&!tip.contains(e.target))hide()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&cur){var a=cur;hide();a.focus()}});
addEventListener('scroll',function(){if(cur&&!fine)hide()},{passive:true});addEventListener('resize',hide)})()</script>"""

# renter call to action (Module 5 + lesson 1.4)
RENTER_SLUGS = {'who-can-live-there'}
def renter_cta(p):
    return f'<div class="callout next-step renter-cta"><b>Renting or looking for a place?</b> The <a href="{p}renters.html">renter page</a> has your county&rsquo;s income and rent limits, links to find tax credit properties near you, and where to get help if something goes wrong. <a href="{p}renters.html">Go to the renter page &rarr;</a></div>'

# lesson pages
for i, (m, l, j) in enumerate(LESSONS):
    n = m['num']; num = f'{n}.{j+1}'
    prev = LESSONS[i-1] if i > 0 else None; nxt = LESSONS[i+1] if i < TOTAL-1 else None
    tool = ''
    if l.get('tool'):
        tt, td = TOOLINFO[l['tool']]
        tool = f'<a class="tool-cta" href="../tools/{l["tool"]}.html"><small>Try it</small><strong>{tt} &rarr;</strong><span>{td}</span></a>'
    terms = terms_for(l)
    rv = l.get('reviewed', REVIEWED)
    tl = ''.join(f'<li><a class="gl" href="../glossary.html#{g["id"]}" data-t="{H.escape(g["term"], quote=True)}" data-d="{H.escape(g["def"], quote=True)}">{g["term"]}</a></li>' for g in terms)
    src = ''.join(f'<li>{s}</li>' for s in l['sources'])
    lnav = '<nav class="module-nav">'
    lnav += f'<a class="prev" href="{prev[1]["slug"]}.html"><small>&larr; Lesson {prev[0]["num"]}.{prev[2]+1}</small>{prev[1]["title"]}</a>' if prev else '<a class="prev" href="../course.html"><small>&larr; Back to</small>The course</a>'
    lnav += f'<a class="next" href="{nxt[1]["slug"]}.html"><small>Lesson {nxt[0]["num"]}.{nxt[2]+1} &rarr;</small>{nxt[1]["title"]}</a>' if nxt else '<a class="next" href="../course.html"><small>Done &rarr;</small>The course</a>'
    lnav += '</nav>'
    body = f'''<div class="page-hero"><div class="wrap">
  <div class="eyebrow">Module {n} &middot; Lesson {num}</div>
  <h1>{l["title"]}</h1>
  <p>{summary(l)}</p>
</div></div>

<section><div class="wrap article lesson-page">
  <p class="crumbs"><a href="../course.html">The course</a> / <a href="../{m["slug"]}.html">Module {n}: {m["title"]}</a> / Lesson {num}</p>
  <p class="reviewed">Last reviewed <time datetime="{rv[0]}">{rv[1]}</time></p>
  {gloss_link(fix_links(l["body"]) + "\n  " + fix_links(l.get("more", "")))}
  {tool}
  {renter_cta('../') if (m['slug'] == 'living-there' or l['slug'] in RENTER_SLUGS) else ''}
  {'<div class="terms"><strong>Terms in this lesson</strong><ul>' + tl + '</ul></div>' if tl else ''}
  <div class="lesson-sources open"><strong>Sources</strong><ul class="sources">{src}</ul></div>
  {lnav}
  {signup_card('lesson')}
  {FOLLOW}
  {DISC}
</div></section>{GLOSS_JS}'''
    body = re.sub(r'(<table class="cmp">.*?</table>)', r'<div class="table-wrap">\1</div>', body, flags=re.S)
    url = f'learn/{l["slug"]}.html'
    art = {"@type": "Article", "headline": l["title"], "description": meta_desc(l), "dateModified": rv[0], "inLanguage": "en", "url": f'{SITE}/{url}', "author": {"@id": PERSON["@id"]}, "publisher": {"@id": ORG["@id"]}, "image": f'{SITE}/{OG_IMG}', "isAccessibleForFree": True}
    data = ld(art, crumbs_ld([("The course", "course.html"), (f'Module {n}: {strip(m["title"])}', f'{m["slug"]}.html'), (l["title"], url)]), PERSON, ORG)
    page(url, f'{l["title"]} (Lesson {num})', meta_desc(l), 'course.html', body, data=data, pop=m['slug'] != 'living-there' and l['slug'] not in RENTER_SLUGS)

# module overview pages
for i, m in enumerate(MODS):
    n = m['num']
    cards = ''.join(f'<a class="lesson-card" href="learn/{l["slug"]}.html"><span class="lnum">{n}.{j+1}</span><strong>{l["title"]}</strong><span>{summary(l)}</span></a>' for j, l in enumerate(m['lessons']))
    prev = MODS[i-1] if i > 0 else None; nxt = MODS[i+1] if i < len(MODS)-1 else None
    mnav = '<nav class="module-nav">'
    mnav += f'<a class="prev" href="{prev["slug"]}.html"><small>&larr; Module {prev["num"]}</small>{prev["title"]}</a>' if prev else '<a class="prev" href="course.html"><small>&larr; Back to</small>All modules</a>'
    mnav += f'<a class="next" href="{nxt["slug"]}.html"><small>Module {nxt["num"]} &rarr;</small>{nxt["title"]}</a>' if nxt else '<a class="next" href="course.html"><small>Done &rarr;</small>All modules</a>'
    mnav += '</nav>'
    body = f'''<div class="page-hero"><div class="wrap">
  <div class="eyebrow">Module {n} of {len(MODS)}</div>
  <h1>{m["title"]}</h1>
  <p>{m["blurb"]}</p>
</div></div>

<section><div class="wrap article">
  <p class="crumbs"><a href="course.html">The course</a> / Module {n}</p>
  <div class="lesson-list">{cards}</div>
  {renter_cta('') if m['slug'] == 'living-there' else ''}
  <div class="btns"><a class="btn primary" href="learn/{m["lessons"][0]["slug"]}.html">Start lesson {n}.1</a></div>
  {mnav}
  {FOLLOW}
</div></section>'''
    page(f'{m["slug"]}.html', f'Module {n}: {m["title"]}', strip(m['blurb']), 'course.html', body, data=ld(crumbs_ld([("The course", "course.html"), (f'Module {n}: {strip(m["title"])}', f'{m["slug"]}.html')])), pop=m['slug'] != 'living-there')

# course index
cards = ''
for m in MODS:
    items = ''.join(f'<li><a href="learn/{l["slug"]}.html"><span class="lnum">{m["num"]}.{j+1}</span> {l["title"]}</a></li>' for j, l in enumerate(m['lessons']))
    cards += f'<div class="module-card"><div class="mnum">Module {m["num"]}</div><h3><a href="{m["slug"]}.html">{m["title"]}</a></h3><p>{m["blurb"]}</p><ol class="plain">{items}</ol></div>'
body = f'''<div class="page-hero"><div class="wrap">
  <div class="eyebrow">The course</div>
  <h1>LIHTC, start to finish</h1>
  <p>{len(MODS)} modules, {TOTAL} lessons. How affordable housing gets financed, built and run, in plain English.</p>
</div></div>
<section><div class="wrap">
  <div class="section-head"><p>New here? Read <a href="start-here.html">Start here</a> first; it's the five-minute version. Then work through the modules in order, or jump to what you need. Every lesson lists its sources, and the <a href="glossary.html">glossary</a> and <a href="tools.html">calculators</a> are there when you need them.</p></div>
  <div class="module-grid">{cards}</div>
  {FOLLOW}
</div></section>'''
page('course.html', 'The LIHTC Course', f'A free {TOTAL}-lesson LIHTC course: how credits are sized, how deals are won and financed, what renters should know, and what happens after year 15.', 'course.html', body)

# glossary
letters = sorted({g['term'][0].upper() for g in GLOS})
items = ''.join(f'<div class="gterm" id="{g["id"]}"><dt>{g["term"]}</dt><dd>{g["def"]} <a href="learn/{g["lesson"]}.html">Lesson: {BYSLUG[g["lesson"]][1]["title"]} &rarr;</a></dd></div>' for g in GLOS)
body = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Glossary</div><h1>Affordable housing terms</h1><p>{len(GLOS)} terms you'll run into, each in a sentence or two, with a link to the lesson that explains it.</p></div></div>
<section><div class="wrap article"><p class="reviewed">Last reviewed <time datetime="{REVIEWED[0]}">{REVIEWED[1]}</time></p><dl class="glossary">{items}</dl>{DISC}</div></section>'''
page('glossary.html', 'Glossary of LIHTC and affordable housing terms', 'Plain-English definitions of LIHTC and affordable housing terms: AMI, eligible basis, QAP, QCT, DDA, recapture, Year 15 and more.', 'glossary.html', body)

# sources library
CHANGES = json.load(open(f'{SRC}/changes.json'))
KEY = json.load(open(f'{SRC}/key_sources.json'))
ch = ''.join(f'<li><b>{c["date"]}:</b> {c["text"]}</li>' for c in CHANGES)
ks = ''.join(f'<h3>{grp}</h3><ul class="sources">' + ''.join(f'<li><a href="{u}">{t}</a>{(" &mdash; " + d) if d else ""}</li>' for t, u, d in items) + '</ul>' for grp, items in KEY)
by = ''.join(f'<li><a href="learn/{l["slug"]}.html">{m["num"]}.{j+1} {l["title"]}</a><ul>' + ''.join(f'<li>{s}</li>' for s in l['sources']) + '</ul></li>' for m, l, j in LESSONS)
body = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Sources</div><h1>Sources and updates</h1><p>Where the numbers and rules on this site come from, and what's changed recently.</p></div></div>
<section><div class="wrap article">
<p class="reviewed">Last reviewed <time datetime="{REVIEWED[0]}">{REVIEWED[1]}</time></p>
<h2 id="changes">What changed</h2><ul class="changes">{ch}</ul>
<h2 id="primary">Primary sources</h2>{ks}
<h2 id="by-lesson">Sources by lesson</h2><ul class="sources by-lesson">{by}</ul>
{DISC}</div></section>'''
page('sources.html', 'Sources and updates', 'The laws, IRS guidance, HUD data and research behind every lesson, plus a log of recent rule and number changes.', 'sources.html', body)

# static pages from src/pages/*.html (body fragments with a front-matter line)
for fn in sorted(os.listdir(f'{SRC}/pages')):
    raw = open(f'{SRC}/pages/{fn}').read()
    meta, body = raw.split('\n---\n', 1)
    meta = json.loads(meta)
    if meta['path'].startswith('tools/'):
        body = re.sub(r'(<section><div class="wrap[^"]*">)', r'\1' + f'<p class="reviewed">Last reviewed <time datetime="{REVIEWED[0]}">{REVIEWED[1]}</time></p>', body, count=1)
    page(meta['path'], meta['title'], meta['desc'], meta['cur'], body, meta.get('head', ''), pop=meta['path'] not in ('renters.html', 'limits.html'))

# patch nav/footer on hand-written pages
for f in ['index.html', 'start-here.html', 'about.html']:
    s = open(f'{ROOT}/{f}').read()
    cur = 'start-here.html' if f == 'start-here.html' else ('about.html' if f == 'about.html' else '')
    s = re.sub(r'<nav class="nav">.*?</nav>', nav(cur, ''), s, flags=re.S)
    s = re.sub(r'<footer class="site-footer">.*?</footer>(\n<script>document\.addEventListener\(\'submit\'.*?</script>)*', lambda m: footer(''), s, flags=re.S)
    s = re.sub(r'href="styles\.css(\?v=[^"]*)?"', f'href="styles.css?v={CSSV}"', s)
    s = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?rel="stylesheet">|<link rel="preload" href="assets/fonts/inter.*?crossorigin><link rel="preload" href="assets/fonts/archivo.*?crossorigin>', fonts(''), s, count=1, flags=re.S)
    if SKIP not in s: s = s.replace('<body>\n', '<body>\n' + SKIP + '\n', 1)
    s = s.replace('<main>', '<main id="main">', 1)
    if f == 'index.html':
        s = re.sub(r'\n?<section class="signup-band">.*?</section>', '', s, flags=re.S)
        s = s.replace('\n</main>', '\n<section class="signup-band"><div class="wrap">' + signup_card('home') + '</div></section>\n</main>', 1)
    ogt = re.search(r'<meta property="og:title" content="(.*?)"', s); ogd = re.search(r'<meta property="og:description" content="(.*?)"', s)
    s = re.sub(r'\n?<!--seo-->.*?<!--/seo-->', '', s, flags=re.S)
    title = H.unescape(ogt.group(1)) if ogt else re.search(r'<title>(.*?)</title>', s).group(1).replace(' | LIHTC Explained', '').replace(' | VanKyle Properties', '')
    desc = H.unescape((ogd or re.search(r'<meta name="description" content="(.*?)"', s)).group(1))
    s = re.sub(r'\n<meta (property="og:(type|title|description)"|name="twitter:card")[^>]*>', '', s)
    data = {'index.html': ld({"@type": "WebSite", "@id": SITE + "/#site", "name": "LIHTC Explained", "alternateName": "VanKyle Properties", "url": SITE + "/", "publisher": {"@id": ORG["@id"]}}, ORG, PERSON), 'about.html': ld({"@type": "ProfilePage", "url": SITE + "/about.html", "mainEntity": {"@id": PERSON["@id"]}}, PERSON, ORG)}.get(f, '')
    s = s.replace('</head>', seo(f, title, desc, data) + '\n</head>', 1)
    open(f'{ROOT}/{f}', 'w').write(s)
    BUILT.append(f)

# sitemap + robots
import datetime
today = datetime.date.today().isoformat()
urls = sorted(set(BUILT), key=lambda x: (x != 'index.html', x.count('/'), x))
sm = ''.join(f'<url><loc>{SITE}/{"" if u == "index.html" else u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)
open(f'{ROOT}/sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
open(f'{ROOT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {SITE}/sitemap.xml\n')
print(TOTAL, 'lessons built')
