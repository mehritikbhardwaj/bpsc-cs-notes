"""Build the STET previous-year-questions chapter from parsed response sheets.

Usage: python3 src/stet_to_chapter.py <stet.json> <answers.json|-> <out.html>

The questions are Bihar STET exam content, re-typeset from the official
response sheets; no third-party PDF is redistributed.
"""
import json, io, sys, html

stet, ansf, out = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(io.open(stet, encoding='utf-8'))
answers = json.load(io.open(ansf, encoding='utf-8')) if ansf != '-' else {}

parts = ['<section class="chapter" data-title="STET Previous Year Questions">',
         '<h2>STET Previous Year Questions</h2>',
         '<p class="note">Bihar STET 2025 Paper II (Class 11–12, Computer Science) ke official '
         'question papers — teen shifts, kul {} questions. Bihar Board question papers alag se '
         'publish nahi karti, isliye ye official response sheets se liye gaye hain.</p>'
         .format(sum(len(p['questions']) for p in data))]
total = 0
for pi, paper in enumerate(data):
    qs = paper['questions']
    total += len(qs)
    parts.append(f'<h3>{html.escape(paper["paper"])}</h3>')
    parts.append(f'<p class="note">{len(qs)} questions.</p>')
    for q in qs:
        parts.append('<div class="pyq">')
        parts.append(f'<p class="pyq-q"><b>{q["n"]}.</b> {html.escape(q["q"])}</p>')
        parts.append('<ul class="pyq-o">')
        for letter in sorted(q['o']):
            parts.append(f'<li><span>{letter}</span> {html.escape(q["o"][letter])}</li>')
        parts.append('</ul>')
        key = answers.get(f'{pi}-{q["n"]}')
        if key:
            parts.append(f'<details class="pyq-a"><summary>Answer</summary>'
                         f'<p><b>({key})</b> {html.escape(q["o"].get(key, ""))}</p></details>')
        parts.append('</div>')
parts.append('</section>')
io.open(out, 'w', encoding='utf-8').write('\n'.join(parts))
print(f'{total} STET questions -> {out}')
