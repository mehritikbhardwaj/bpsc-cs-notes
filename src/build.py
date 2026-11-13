import re, glob, html, sys, json
src, out, tplf = sys.argv[1], sys.argv[2], sys.argv[3]
parts = [open(f, encoding='utf-8').read() for f in sorted(glob.glob(src + '/*.html'))]
body = '\n'.join(parts)
EMOJI = {'computer-networking':'🌐','internet-of-things-iot':'📡','dbms-sql':'🗄️','number-system-codes':'🔢',
 'computer-architecture-memory':'🧠','artificial-intelligence-ml':'🤖','multimedia':'🎬','data-structures-algorithms':'🌳',
 'boolean-algebra-digital-electronics':'💡','software-engineering':'🛠️','operating-system':'💻','theory-of-computation':'⚙️',
 'cloud-computing':'☁️','cyber-security':'🛡️','c-object-oriented-programming':'🧩','c-programming-complete':'🅲',
 'computer-fundamentals':'🖥️','python-programming-pandas':'🐍','web-technology':'🕸️','java-basics':'☕',
 'society-law-ethics':'⚖️','emerging-trends':'🚀','quick-revision-one-liners':'⚡'}
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
 'operating-system','data-structures-algorithms','c-programming-complete','c-object-oriented-programming','java-basics',
 'python-programming-pandas','dbms-sql','computer-networking','web-technology','internet-of-things-iot','cloud-computing',
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
html_out = []
for i, c in enumerate(chapters):
    prev = chapters[i-1] if i else None; nxt = chapters[i+1] if i + 1 < len(chapters) else None
    chips = ''.join(f'<a class="chip" href="#{t["id"]}">{html.escape(t["t"])}</a>' for t in c['topics'])
    pager = '<nav class="pager">' + (f'<a class="pg prev" href="#{prev["id"]}"><small>← Previous</small><b>{prev["emoji"]} {html.escape(prev["title"])}</b></a>' if prev else '<span></span>') \
        + (f'<a class="pg next" href="#{nxt["id"]}"><small>Next →</small><b>{nxt["emoji"]} {html.escape(nxt["title"])}</b></a>' if nxt else '<span></span>') + '</nav>'
    html_out.append(f'''<section class="chapter" id="{c['id']}" style="--h:{c['hue']}">
<header class="banner"><div class="b-emoji">{c['emoji']}</div><div class="b-text"><div class="kicker">Chapter {c['n']}</div><h2>{html.escape(c['title'])}</h2>
<div class="b-meta">{len(c['topics'])} topics · ~{c['mins']} min read</div></div>
<button class="done-btn" data-done="{c['id']}">☐ Mark as done</button></header>
<div class="chips-wrap"><div class="chips">{chips}</div></div>
<div class="content">{c['inner']}</div>{pager}</section>''')
meta = [{k: c[k] for k in ('id','n','title','pages','added','emoji','hue','mins','topics')} for c in chapters]
tpl = open(tplf, encoding='utf-8').read()
tpl = tpl.replace('{{BODY}}', '\n'.join(html_out)).replace('{{META}}', json.dumps(meta, ensure_ascii=False).replace('</', '<\\/')).replace('{{COUNT}}', str(len(chapters)))
open(out, 'w', encoding='utf-8').write(tpl)
print('chapters', len(chapters), 'topics', sum(len(c['topics']) for c in chapters), 'bytes', len(tpl))
