"""Turn parsed BPSC question booklets into a chapter page.

Usage: python3 src/pyq_to_chapter.py <pyq.json> <answers.json|-> <out.html>
Questions come verbatim from the official booklets; answers.json is optional
and maps "<paper index>-<question no>" to a letter.
"""
import json, io, sys, html, re

pyq, ansf, out = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(io.open(pyq, encoding='utf-8'))
answers = json.load(io.open(ansf, encoding='utf-8')) if ansf != '-' else {}

def dedupe(qs):
    seen = {}
    for q in qs:
        if q['n'] not in seen:          # first copy is the English one
            seen[q['n']] = q
    return [seen[k] for k in sorted(seen)]

PAPERS = [
    {'file': '/papers/bpsc-tre-2023-12-15-computer-science.pdf',
     'name': 'BPSC TRE 2.0 — 15 December 2023',
     'src': 'https://bpsc.bihar.gov.in/wp-content/uploads/BPSC_content/QuestionBooklets/NB-2023-12-15-26.pdf'},
    {'file': '/papers/bpsc-tre-2024-08-09-computer-science.pdf',
     'name': 'BPSC TRE — 9 August 2024',
     'src': 'https://bpsc.bihar.gov.in/wp-content/uploads/BPSC_content/QuestionBooklets/NB-2024-08-09-49.pdf'},
]

parts = ['<section class="chapter" data-title="Previous Year Questions">',
         '<h2>Previous Year Questions</h2>',
         '<h3>Full question papers (PDF)</h3>',
         '<p class="note">BPSC ke official question booklets — poora paper, Hindi aur English dono, '
         'Language + General Studies + Computer Science ke saath.</p>',
         '<div class="paper-dl">']
for pp in PAPERS:
    parts.append(f'<a class="paper" href="{pp["file"]}" download><span class="e">\U0001F4C4</span>'
                 f'<span><b>{html.escape(pp["name"])}</b>'
                 f'<small>Official booklet · 48 pages · PDF</small></span>'
                 f'<span class="go">\u2b07\ufe0f</span></a>')
parts.append('</div>')
parts.append('<p class="note">Source: Bihar Public Service Commission. '
             + ' · '.join(f'<a href="{pp["src"]}" rel="nofollow">{html.escape(pp["name"])} (bpsc.bihar.gov.in)</a>'
                          for pp in PAPERS) + '</p>')
total = 0
for pi, paper in enumerate(data):
    qs = dedupe(paper['questions'])
    total += len(qs)
    parts.append(f'<h3>{html.escape(paper["paper"])}</h3>')
    parts.append(f'<p class="note">Official question booklet se, Computer Science section '
                 f'(Q{qs[0]["n"]}–Q{qs[-1]["n"]}). Kul {len(qs)} questions.</p>')
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
print(f'{total} questions -> {out}')
