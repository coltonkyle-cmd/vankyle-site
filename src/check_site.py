#!/usr/bin/env python3
"""Pre-publish check for lihtcexplained.com. Run from the repo root after the build:

    python3 src/build.py && python3 src/check_site.py

Exits with code 1 if anything is wrong, so nothing goes to main until it passes.
Checks (stdlib only):
  - every page has a title, description, canonical URL, link-preview image and the visitor counter
  - every internal link and image points to a file that exists (and #anchors exist)
  - every <img> has alt text
  - no image or media file over 200 KB, no page over 300 KB
  - every page is in sitemap.xml
Optional (only if Playwright is installed): no page wider than a phone screen at 320/375/414 px.
"""
import os, re, sys, glob, html
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SKIP = {'404.html'}
errors, warnings = [], []
err = lambda f, m: errors.append(f'{f}: {m}')
warn = lambda f, m: warnings.append(f'{f}: {m}')

pages = sorted(p for p in glob.glob('*.html') + glob.glob('*/*.html') if not p.startswith('src/'))
ids_cache = {}
def ids(path):
    if path not in ids_cache:
        ids_cache[path] = set(re.findall(r'\bid="([^"]+)"', open(path, encoding='utf-8').read()))
    return ids_cache[path]

sitemap = open('sitemap.xml').read() if os.path.exists('sitemap.xml') else ''
if not sitemap: err('sitemap.xml', 'missing')
if not os.path.exists('robots.txt'): err('robots.txt', 'missing')

for f in pages:
    s = open(f, encoding='utf-8').read()
    base = os.path.dirname(f)
    if f not in SKIP:
        for label, pat in [('title', r'<title>[^<]{5,}</title>'),
                           ('meta description', r'<meta name="description" content="[^"]{30,}"'),
                           ('canonical URL', r'<link rel="canonical" href="https://www\.lihtcexplained\.com/'),
                           ('og:title', r'<meta property="og:title"'),
                           ('og:image', r'<meta property="og:image" content="https://'),
                           ('twitter:card', r'<meta name="twitter:card" content="summary_large_image"'),
                           ('visitor counter', r'data-goatcounter=')]:
            if not re.search(pat, s): err(f, f'missing {label}')
        if len(re.findall(r'<meta property="og:title"', s)) > 1: err(f, 'duplicate og:title')
        if '<meta name="viewport" content="width=device-width,initial-scale=1"' not in s: err(f, 'missing mobile viewport tag')
        if 'user-scalable=no' in s or 'maximum-scale=1' in s: err(f, 'pinch zoom is disabled')
        loc = 'https://www.lihtcexplained.com/' + ('' if f == 'index.html' else f)
        if sitemap and f'<loc>{loc}</loc>' not in sitemap: err(f, 'not in sitemap.xml')
        if len(re.findall(r'<h1[\s>]', s)) != 1: warn(f, f'{len(re.findall(r"<h1[\\s>]", s))} <h1> headings (should be 1)')
    for tag in re.findall(r'<img\b[^>]*>', s):
        if not re.search(r'\balt="', tag): err(f, f'image without alt text: {tag[:80]}')
    for attr, url in re.findall(r'\b(href|src)="([^"]+)"', s):
        u = html.unescape(url)
        if re.match(r'^(https?:|mailto:|tel:|data:|javascript:|//)', u): continue
        pu = urlparse(u)
        path = unquote(pu.path)
        if path.startswith('/'): target = path.lstrip('/') or 'index.html'
        elif path == '': target = f
        else: target = os.path.normpath(os.path.join(base, path))
        if os.path.isdir(target): target = os.path.join(target, 'index.html')
        if not os.path.exists(target):
            err(f, f'broken link: {url}'); continue
        if pu.fragment and target.endswith('.html') and pu.fragment not in ids(target):
            err(f, f'missing anchor: {url}')
    if os.path.getsize(f) > 300_000: warn(f, f'page is {os.path.getsize(f)//1000} KB')

for m in glob.glob('assets/**/*', recursive=True):
    if re.search(r'\.(jpe?g|png|gif|webp|svg|mp4|webm)$', m, re.I) and os.path.getsize(m) > 200_000:
        err(m, f'{os.path.getsize(m)//1000} KB (keep images under 200 KB)')

# phone-width check (optional)
try:
    from playwright.sync_api import sync_playwright
    import http.server, threading, functools
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    JS = '''()=>{const W=document.documentElement.clientWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>0&&r.right>W+1&&!e.closest('.table-wrap,.hero'))o.push(e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.split(' ')[0]:''))});return o.slice(0,3)}'''
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in (320, 375, 414):
            pg = b.new_page(viewport={'width': w, 'height': 760}, is_mobile=True)
            for f in pages:
                pg.goto(f'http://127.0.0.1:{srv.server_port}/{f}')
                o = pg.evaluate(JS)
                if o: err(f, f'wider than a {w}px phone screen: {", ".join(o)}')
            pg.close()
        b.close()
    srv.shutdown()
    phone = 'phone-width check ran'
except ImportError:
    phone = 'phone-width check skipped (Playwright not installed)'

for w in warnings: print('WARN ', w)
for e in errors: print('ERROR', e)
print(f'\n{len(pages)} pages checked; {phone}. {len(errors)} errors, {len(warnings)} warnings.')
sys.exit(1 if errors else 0)
