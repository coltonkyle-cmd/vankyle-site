import json, re, os, sys, html as H
SRC = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SRC)
MODS = json.load(open(f'{SRC}/lessons.json')); GLOS = json.load(open(f'{SRC}/glossary.json'))
LESSONS = [(m, l, j) for m in MODS for j, l in enumerate(m['lessons'])]
BYSLUG = {l['slug']: (m, l, j) for m, l, j in LESSONS}
ANCHOR = {(m['slug'], l['id']): l['slug'] for m, l, j in LESSONS}
TOTAL = len(LESSONS)
import hashlib
CSSV = hashlib.md5(open(f'{ROOT}/styles.css','rb').read()).hexdigest()[:8]
SOCIAL = [("https://www.instagram.com/vankyle_properties/","Instagram"),("https://www.youtube.com/@vankyle_properties","YouTube"),("https://www.facebook.com/VanKyleProp","Facebook"),("https://www.threads.com/@vankyle_properties","Threads"),("https://www.linkedin.com/in/colton-kyle-mba-03282821/","LinkedIn")]
NAV = [("start-here.html","Start here"),("course.html","Course"),("tools.html","Tools")]
MORE = [("glossary.html","Glossary"),("renters.html","For renters"),("sources.html","Sources"),("about.html","About")]
NAVJS = "<script>document.addEventListener('click',function(e){document.querySelectorAll('.nav-more[open]').forEach(function(d){if(!d.contains(e.target))d.removeAttribute('open')})});document.addEventListener('keydown',function(e){if(e.key==='Escape')document.querySelectorAll('.nav-more[open]').forEach(function(d){d.removeAttribute('open');d.querySelector('summary').focus()})})</script>"

def nav(cur, p):
    a = lambda h, t: f'<a href="{p}{h}"' + (' aria-current="page"' if h == cur else '') + f'>{t}</a>'
    top = ''.join(a(h, t) for h, t in NAV)
    on = ' data-current' if any(h == cur for h, _ in MORE) else ''
    menu = ''.join(a(h, t) for h, t in MORE)
    return f'<nav class="nav">{top}<details class="nav-more"{on}><summary>More</summary><div class="nav-menu">{menu}</div></details>{NAVJS}</nav>'
def header(cur, p):
    return f'<header class="site-header"><div class="wrap">\n  <a class="brand" href="{p}index.html"><img src="{p}assets/vk.svg" alt=""><span>VanKyle Properties</span></a>\n  {nav(cur, p)}\n</div></header>'
def footer(p):
    soc = ''.join(f'<a href="{u}">{t}</a>' for u, t in SOCIAL)
    return f'''<footer class="site-footer"><div class="wrap">
  <div><a href="{p}start-here.html">Start here</a><a href="{p}course.html">Course</a><a href="{p}tools.html">Tools</a><a href="{p}glossary.html">Glossary</a><a href="{p}renters.html">Renters</a><a href="{p}sources.html">Sources</a><a href="{p}about.html">About</a><a href="mailto:colton@vankyleproperties.com">colton@vankyleproperties.com</a></div>
  <div class="social">{soc}</div>
  <p class="disclaimer">Education only. Not tax, legal or investment advice. Views are my own and don't represent my employer. &copy; 2026 VanKyle Properties, LLC.</p>
</div></footer>'''
SITE = 'https://www.vankyleproperties.com'
GC_CODE = 'vankyle'  # GoatCounter site code: https://vankyle.goatcounter.com
OG_IMG = 'assets/og-default.png'
BUILT = []
def seo(path, title, desc):
    url = SITE + '/' + ('' if path == 'index.html' else path)
    t = H.escape(title, quote=True); d = H.escape(desc, quote=True)
    return f'''<!--seo-->
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="VanKyle Properties">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{OG_IMG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="LIHTC Explained by VanKyle Properties: how affordable housing actually gets built">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/{OG_IMG}">
<script data-goatcounter="https://{GC_CODE}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<!--/seo-->'''

def page(path, title, desc, cur, body, extra_head=''):
    p = '../' * path.count('/')
    if 'w-widget' in body or 'VK.' in body: extra_head += f'\n<script src="{p}assets/widgets.js" defer></script>'
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | VanKyle Properties</title>
<meta name="description" content="{H.escape(desc, quote=True)}">
{seo(path, title, desc)}
<link rel="icon" type="image/svg+xml" href="{p}assets/vk.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}styles.css?v={CSSV}">{extra_head}
</head>
<body>
{header(cur, p)}

<main>
{body}
</main>

{footer(p)}
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
    return d
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
    tl = ''.join(f'<li><a href="../glossary.html#{g["id"]}">{g["term"]}</a></li>' for g in terms)
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
  {fix_links(l["body"])}
  {fix_links(l.get("more", ""))}
  {tool}
  {renter_cta('../') if (m['slug'] == 'living-there' or l['slug'] in RENTER_SLUGS) else ''}
  {'<div class="terms"><strong>Terms in this lesson</strong><ul>' + tl + '</ul></div>' if tl else ''}
  <div class="lesson-sources open"><strong>Sources</strong><ul class="sources">{src}</ul></div>
  {lnav}
  {FOLLOW}
  {DISC}
</div></section>'''
    body = re.sub(r'(<table class="cmp">.*?</table>)', r'<div class="table-wrap">\1</div>', body, flags=re.S)
    page(f'learn/{l["slug"]}.html', f'{l["title"]} (Lesson {num})', meta_desc(l), 'course.html', body)

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
    page(f'{m["slug"]}.html', f'Module {n}: {m["title"]}', strip(m['blurb']), 'course.html', body)

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
page('course.html', 'The LIHTC Course', f'A free {TOTAL}-lesson course on the Low-Income Housing Tax Credit: how credits are sized, how deals are won and financed, what renters should know, and what happens after year 15.', 'course.html', body)

# glossary
letters = sorted({g['term'][0].upper() for g in GLOS})
items = ''.join(f'<div class="gterm" id="{g["id"]}"><dt>{g["term"]}</dt><dd>{g["def"]} <a href="learn/{g["lesson"]}.html">Lesson: {BYSLUG[g["lesson"]][1]["title"]} &rarr;</a></dd></div>' for g in GLOS)
body = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Glossary</div><h1>Affordable housing terms</h1><p>{len(GLOS)} terms you'll run into, each in a sentence or two, with a link to the lesson that explains it.</p></div></div>
<section><div class="wrap article"><dl class="glossary">{items}</dl>{DISC}</div></section>'''
page('glossary.html', 'Glossary of LIHTC and affordable housing terms', 'Plain-English definitions of LIHTC and affordable housing terms: AMI, eligible basis, QAP, QCT, DDA, recapture, Year 15 and more.', 'glossary.html', body)

# sources library
CHANGES = json.load(open(f'{SRC}/changes.json'))
KEY = json.load(open(f'{SRC}/key_sources.json'))
ch = ''.join(f'<li><b>{c["date"]}:</b> {c["text"]}</li>' for c in CHANGES)
ks = ''.join(f'<h3>{grp}</h3><ul class="sources">' + ''.join(f'<li><a href="{u}">{t}</a>{(" &mdash; " + d) if d else ""}</li>' for t, u, d in items) + '</ul>' for grp, items in KEY)
by = ''.join(f'<li><a href="learn/{l["slug"]}.html">{m["num"]}.{j+1} {l["title"]}</a><ul>' + ''.join(f'<li>{s}</li>' for s in l['sources']) + '</ul></li>' for m, l, j in LESSONS)
body = f'''<div class="page-hero"><div class="wrap"><div class="eyebrow">Sources</div><h1>Sources and updates</h1><p>Where the numbers and rules on this site come from, and what's changed recently.</p></div></div>
<section><div class="wrap article">
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
    page(meta['path'], meta['title'], meta['desc'], meta['cur'], body, meta.get('head', ''))

# patch nav/footer on hand-written pages
for f in ['index.html', 'start-here.html', 'about.html']:
    s = open(f'{ROOT}/{f}').read()
    cur = 'start-here.html' if f == 'start-here.html' else ('about.html' if f == 'about.html' else '')
    s = re.sub(r'<nav class="nav">.*?</nav>', nav(cur, ''), s, flags=re.S)
    s = re.sub(r'<footer class="site-footer">.*?</footer>', footer(''), s, flags=re.S)
    s = re.sub(r'href="styles\.css(\?v=[^"]*)?"', f'href="styles.css?v={CSSV}"', s)
    ogt = re.search(r'<meta property="og:title" content="(.*?)"', s); ogd = re.search(r'<meta property="og:description" content="(.*?)"', s)
    s = re.sub(r'\n?<!--seo-->.*?<!--/seo-->', '', s, flags=re.S)
    title = H.unescape(ogt.group(1)) if ogt else re.search(r'<title>(.*?)</title>', s).group(1).replace(' | VanKyle Properties', '')
    desc = H.unescape((ogd or re.search(r'<meta name="description" content="(.*?)"', s)).group(1))
    s = re.sub(r'\n<meta (property="og:(type|title|description)"|name="twitter:card")[^>]*>', '', s)
    s = s.replace('</head>', seo(f, title, desc) + '\n</head>', 1)
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
