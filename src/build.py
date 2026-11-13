import re, glob, html, sys, json, os

src, out, tplf = sys.argv[1], sys.argv[2], sys.argv[3]
OUTDIR = os.path.dirname(os.path.abspath(out)) or '.'
SITE = 'https://bpsc-cs-notes.vercel.app'

parts = [open(f, encoding='utf-8').read() for f in sorted(glob.glob(src + '/*.html'))]
body = '\n'.join(parts)
EMOJI = {'computer-networking':'🌐','internet-of-things-iot':'📡','dbms-sql':'🗄️','number-system-codes':'🔢',
 'computer-architecture-memory':'🧠','artificial-intelligence-ml':'🤖','multimedia':'🎬','data-structures-algorithms':'🌳',
 'boolean-algebra-digital-electronics':'💡','software-engineering':'🛠️','operating-system':'💻','theory-of-computation':'⚙️',
 'cloud-computing':'☁️','cyber-security':'🛡️','c-object-oriented-programming':'🧩','c-programming-complete':'🅲',
 'computer-fundamentals':'🖥️','python-programming-pandas':'🐍','web-technology':'🕸️','java-basics':'☕',
 'society-law-ethics':'⚖️','emerging-trends':'🚀','quick-revision-one-liners':'⚡','problem-solving':'🧭','understanding-data':'📊'}

def slug(s):
    s = re.sub(r'<[^>]+>', '', s); s = html.unescape(s).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:60]
used = set()
def uniq(s):
    b, i = s, 2
    while s in used: s = f'{b}-{i}'; i += 1
    used.add(s); return s

secs = re.findall(r'<section class="chapter"([^>]*)>(.*?)</section>', body, flags=re.S)
ORDER = ['computer-fundamentals','number-system-codes','boolean-algebra-digital-electronics','computer-architecture-memory',
 'operating-system','problem-solving','data-structures-algorithms','c-programming-complete','c-object-oriented-programming','java-basics',
 'python-programming-pandas','understanding-data','dbms-sql','computer-networking','web-technology','internet-of-things-iot','cloud-computing',
 'cyber-security','software-engineering','theory-of-computation','artificial-intelligence-ml','multimedia',
 'society-law-ethics','emerging-trends','quick-revision-one-liners']
secs.sort(key=lambda s: ORDER.index(slug(re.search(r'data-title="([^"]+)"', s[0]).group(1))))

chapters = []
for n, (attrs, inner) in enumerate(secs, 1):
    title = html.unescape(re.search(r'data-title="([^"]+)"', attrs).group(1))
    pm = re.search(r'data-pages="([^"]+)"', attrs)
    added = 'data-added' in attrs
    cid = uniq(slug(title))
    topics = []
    def do_h3(hm):
        a, t = hm.group(1), hm.group(2)
        sid = uniq(cid + '-' + slug(t))
        topics.append({'id': sid, 't': html.unescape(re.sub(r'<[^>]+>', '', t)), 'a': 'added' in a})
        return f'<h3 id="{sid}"{a}>{t}</h3>'
    inner = re.sub(r'<h3([^>]*)>(.*?)</h3>', do_h3, inner)
    inner = re.sub(r'<h2>.*?</h2>', '', inner, count=1, flags=re.S)
    words = len(re.sub(r'<[^>]+>', ' ', inner).split())
    chapters.append(dict(id=cid, n=n, title=title, pages=pm.group(1) if pm else '', added=added,
                         emoji=EMOJI.get(cid, '📘'), hue=(n * 47) % 360, mins=max(2, round(words / 180)),
                         topics=topics, inner=inner))

# ---------- content links that used to jump inside one big page ----------
chap_ids = {c['id'] for c in chapters}
topic_owner = {t['id']: c['id'] for c in chapters for t in c['topics']}
def fix_links(inner, cid):
    def sub(m):
        target = m.group(1)
        if target in topic_owner:
            owner = topic_owner[target]
            return f'href="#{target}"' if owner == cid else f'href="/{owner}#{target}"'
        if target in chap_ids:
            return f'href="/{target}"' if target != cid else f'href="#{target}"'
        return m.group(0)
    return re.sub(r'href="#([^"]+)"', sub, inner)
for c in chapters:
    c['inner'] = fix_links(c['inner'], c['id'])

# ---------- chapter section markup ----------
def section(c, i, heading='h1'):
    prev = chapters[i-1] if i else None
    nxt = chapters[i+1] if i + 1 < len(chapters) else None
    chips = ''.join(f'<a class="chip" href="#{t["id"]}">{html.escape(t["t"])}</a>' for t in c['topics'])
    pager = '<nav class="pager">' \
        + (f'<a class="pg prev" href="/{prev["id"]}"><small>← Previous</small><b>{prev["emoji"]} {html.escape(prev["title"])}</b></a>' if prev else '<span></span>') \
        + (f'<a class="pg next" href="/{nxt["id"]}"><small>Next →</small><b>{nxt["emoji"]} {html.escape(nxt["title"])}</b></a>' if nxt else '<span></span>') \
        + '</nav>'
    return f'''<section class="chapter show" id="{c['id']}" style="--h:{c['hue']}">
<header class="banner"><div class="b-emoji">{c['emoji']}</div><div class="b-text"><div class="kicker">Chapter {c['n']}</div><{heading}>{html.escape(c['title'])}</{heading}>
<div class="b-meta">{len(c['topics'])} topics · ~{c['mins']} min read</div></div>
<button class="done-btn" data-done="{c['id']}">☐ Mark as done</button></header>
<div class="chips-wrap"><div class="chips">{chips}</div></div>
<div class="content">{c['inner']}</div>{pager}</section>'''

# ---------- page shell ----------
tpl = open(tplf, encoding='utf-8').read()
meta_lite = [{'id': c['id'], 'n': c['n'], 'title': c['title'], 'emoji': c['emoji'],
              'hue': c['hue'], 'mins': c['mins'], 'tc': len(c['topics'])} for c in chapters]
META_JSON = json.dumps(meta_lite, ensure_ascii=False).replace('</', '<\\/')

def page(path, title, desc, canonical, bodyhtml, topics=None, current='', head_extra=''):
    h = tpl
    h = h.replace('{{TITLE}}', html.escape(title))
    h = h.replace('{{DESC}}', html.escape(desc))
    h = h.replace('{{CANONICAL}}', canonical)
    h = h.replace('{{HEAD_EXTRA}}', head_extra)
    h = h.replace('{{CURRENT}}', current)
    h = h.replace('{{BODY}}', bodyhtml)
    h = h.replace('{{META}}', META_JSON)
    h = h.replace('{{TOPICS}}', json.dumps(topics or [], ensure_ascii=False).replace('</', '<\\/'))
    h = h.replace('{{COUNT}}', str(len(chapters)))
    open(os.path.join(OUTDIR, path), 'w', encoding='utf-8').write(h)
    return len(h)

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

written = []

# ---------- one page per chapter ----------
for i, c in enumerate(chapters):
    tnames = ', '.join(t['t'] for t in c['topics'][:5])
    desc = f"{c['title']} ke complete notes Hindi mein — {tnames}. STET aur BPSC TRE Computer Science exam ke liye."
    if len(desc) > 158: desc = desc[:155].rsplit(' ', 1)[0] + '…'
    url = f'{SITE}/{c["id"]}'
    ld = jsonld({
        '@context': 'https://schema.org', '@type': 'Article',
        'headline': c['title'], 'description': desc, 'inLanguage': 'hi-IN',
        'mainEntityOfPage': url, 'articleSection': 'Computer Science',
        'about': [t['t'] for t in c['topics'][:10]],
        'isPartOf': {'@type': 'Course', 'name': 'STET / BPSC TRE Computer Science Notes', 'url': SITE},
    }) + jsonld({
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'CS Notes', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': c['title'], 'item': url},
        ],
    })
    written.append(page(f'{c["id"]}.html',
        f'{c["title"]} Notes in Hindi | STET & BPSC TRE CS',
        desc, url, section(c, i, 'h1'), c['topics'], c['id'], ld))

# ---------- landing page ----------
cards = ''.join(
    f'<a class="card" style="--h:{c["hue"]}" href="/{c["id"]}" data-card="{c["id"]}">'
    f'<span class="num">{c["n"]}</span><span class="e">{c["emoji"]}</span>'
    f'<b>{html.escape(c["title"])}</b><small>{len(c["topics"])} topics · ~{c["mins"]} min</small></a>'
    for c in chapters)
total_topics = sum(len(c['topics']) for c in chapters)
home_body = f'''<section class="hero">
  <h1>Computer Science Notes — STET &amp; BPSC TRE</h1>
  <p>Chapter-wise notes, Hindi + English, mobile ke liye banaye gaye</p>
  <button class="bigsearch" data-open-search>🔍 &nbsp;Search… (subnet, K-map, deadlock)</button>
  <div class="stats">
    <div class="stat"><b>{len(chapters)}</b>Chapters</div>
    <div class="stat"><b>{total_topics}</b>Topics</div>
    <div class="stat"><b data-done-count>0</b>Done</div>
  </div>
  <div class="pbar"><i data-done-bar></i></div>
</section>
<a class="continue" id="continue" href="/"><span class="e">📖</span><span><small>Continue reading</small><b id="contTitle"></b></span><span class="go">→</span></a>
<div class="sec-title"><h2>Saare chapters</h2><span>{total_topics} topics</span></div>
<div class="grid">{cards}</div>
<div class="content" style="margin-top:28px">
<p>Ye notes Bihar STET aur BPSC TRE ke Computer Science paper ke liye hain. Har chapter alag page par hai,
topic-wise divided, taaki mobile par bhi aaram se padha ja sake. Search se kisi bhi topic par seedha pahunch sakte hain,
aur padhe hue chapters ko "Mark as done" se track kar sakte hain.</p>
</div>'''
home_ld = jsonld({
    '@context': 'https://schema.org', '@type': 'WebSite',
    'name': 'CS Notes — STET / BPSC TRE', 'url': SITE, 'inLanguage': 'hi-IN',
}) + jsonld({
    '@context': 'https://schema.org', '@type': 'ItemList',
    'itemListElement': [{'@type': 'ListItem', 'position': c['n'], 'name': c['title'],
                         'url': f'{SITE}/{c["id"]}'} for c in chapters],
})
written.append(page('index.html',
    'Computer Science Notes in Hindi — STET & BPSC TRE',
    f'Bihar STET aur BPSC TRE Computer Science ke complete notes Hindi mein — {len(chapters)} chapters, {total_topics} topics. Networking, DBMS, OS, DSA, Digital Electronics aur more.',
    SITE + '/', home_body, [], '', home_ld))

# ---------- print-everything page (paid users) ----------
all_body = '\n'.join(section(c, i, 'h2') for i, c in enumerate(chapters))
written.append(page('complete.html', 'Complete notes — CS Notes',
    'Complete printable notes.', SITE + '/complete', all_body, [], '',
    '<meta name="robots" content="noindex,nofollow">'))

# ---------- search index ----------
idx = []
for c in chapters:
    pieces = re.split(r'(<h3[^>]*id="([^"]+)"[^>]*>)', c['inner'])
    for k in range(1, len(pieces), 3):
        tid = pieces[k + 1]
        txt = re.sub(r'<[^>]+>', ' ', pieces[k + 2] if k + 2 < len(pieces) else '')
        txt = html.unescape(re.sub(r'\s+', ' ', txt)).strip()[:500]
        t = next((x['t'] for x in c['topics'] if x['id'] == tid), tid)
        idx.append({'i': tid, 't': t, 'c': c['id'], 'ct': c['title'], 'e': c['emoji'], 'x': txt})
open(os.path.join(OUTDIR, 'search-index.json'), 'w', encoding='utf-8').write(
    json.dumps(idx, ensure_ascii=False, separators=(',', ':')))

# ---------- sitemap + robots ----------
urls = [(SITE + '/', '1.0')] + [(f'{SITE}/{c["id"]}', '0.8') for c in chapters]
open(os.path.join(OUTDIR, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(f'  <url><loc>{u}</loc><priority>{p}</priority></url>' for u, p in urls)
    + '\n</urlset>\n')
open(os.path.join(OUTDIR, 'robots.txt'), 'w', encoding='utf-8').write(
    f'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /complete\n\nSitemap: {SITE}/sitemap.xml\n')

print(f'chapters {len(chapters)} topics {total_topics} -> {len(written)} pages, '
      f'avg {sum(written)//len(written)//1024} KB each')
