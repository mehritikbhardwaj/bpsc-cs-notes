import re, glob, html, sys
src = sys.argv[1]; out = sys.argv[2]
parts = [open(f, encoding='utf-8').read() for f in sorted(glob.glob(src + '/*.html'))]
body = '\n'.join(parts)
def slug(s):
    s = re.sub(r'<[^>]+>', '', s); s = html.unescape(s).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-'); return s[:60]
toc_orig, toc_add, cards = [], [], []
used = set()
def uniq(s):
    b = s; i = 2
    while s in used: s = f'{b}-{i}'; i += 1
    used.add(s); return s
n = 0
def do_section(m):
    global n
    n += 1
    attrs, inner = m.group(1), m.group(2)
    title = html.unescape(re.search(r'data-title="([^"]+)"', attrs).group(1))
    pages = re.search(r'data-pages="([^"]+)"', attrs)
    added = 'data-added' in attrs
    cid = uniq(slug(title))
    subs = []
    def do_h3(hm):
        a, t = hm.group(1), hm.group(2)
        sid = uniq(cid + '-' + slug(t))
        subs.append((sid, re.sub(r'<[^>]+>', '', t), 'added' in a))
        return f'<h3 id="{sid}"{a}>{t}</h3>'
    inner = re.sub(r'<h3([^>]*)>(.*?)</h3>', do_h3, inner)
    inner = re.sub(r'<h2>(.*?)</h2>', lambda h: f'<h2><span class="num">{n}</span>{h.group(1)}'
                   + (f'<span class="src">Notes p. {pages.group(1)}</span>' if pages else '<span class="src new">Added chapter</span>') + '</h2>', inner, count=1)
    li = ''.join(f'<li><a href="#{s}">{html.escape(t)}{" <i>+</i>" if a else ""}</a></li>' for s, t, a in subs)
    entry = f'<li class="ch"><a class="chl" href="#{cid}"><span>{n}.</span> {html.escape(title)}</a><ul>{li}</ul></li>'
    (toc_add if added else toc_orig).append(entry)
    cards.append(f'<a class="card{" new" if added else ""}" href="#{cid}"><b>{n}. {html.escape(title)}</b><span>{len(subs)} topics · {"Notes p. "+pages.group(1) if pages else "Added"}</span></a>')
    cls = 'chapter added-ch' if added else 'chapter'
    return f'<section class="{cls}" id="{cid}">{inner}</section>'
body = re.sub(r'<section class="chapter"([^>]*)>(.*?)</section>', do_section, body, flags=re.S)
tpl = open(sys.argv[3], encoding='utf-8').read()
tpl = tpl.replace('{{TOC_ORIG}}', ''.join(toc_orig)).replace('{{TOC_ADD}}', ''.join(toc_add))
tpl = tpl.replace('{{CARDS}}', ''.join(cards)).replace('{{BODY}}', body).replace('{{COUNT}}', str(n))
open(out, 'w', encoding='utf-8').write(tpl)
print('chapters', n, 'topics', len(used) - n, 'bytes', len(tpl))
