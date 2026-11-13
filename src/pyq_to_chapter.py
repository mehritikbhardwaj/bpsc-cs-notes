"""Build the BPSC previous-year-questions chapter.

Usage: python3 src/pyq_to_chapter.py <pyq.json> <out.html>

Questions are printed verbatim from the official booklets, with two
repairs: pypdf's ligature codes are mapped back to real symbols, and a
handful of formula questions whose characters came out of the PDF in the
wrong order are corrected by hand in src/data/bpsc_fixes.json.

Answers are NOT written into the page — they are sold separately and get
fetched at runtime, so each question only carries a placeholder.
"""
import json, io, sys, html, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean_text import clean, looks_broken

pyq, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(io.open(pyq, encoding='utf-8'))
fixes = json.load(io.open(os.path.join(HERE, 'data', 'bpsc_fixes.json'), encoding='utf-8'))

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
         '<p class="note">Official booklets — poora paper, Hindi aur English dono.</p>',
         '<div class="paper-dl">']
for pp in PAPERS:
    parts.append(f'<a class="paper" href="{pp["file"]}" download><span class="e">\U0001F4C4</span>'
                 f'<span><b>{html.escape(pp["name"])}</b>'
                 f'<small>Official booklet · 48 pages · PDF</small></span>'
                 f'<span class="go">⬇️</span></a>')
parts.append('</div>')
parts.append('<p class="note">Source: Bihar Public Service Commission. '
             + ' · '.join(f'<a href="{pp["src"]}" rel="nofollow">{html.escape(pp["name"])} (bpsc.bihar.gov.in)</a>'
                          for pp in PAPERS) + '</p>')

def dedupe(qs):
    seen = {}
    for q in qs:
        seen.setdefault(q['n'], q)      # first copy is the English one
    return [seen[k] for k in sorted(seen)]

total = broken = 0
skipped = []
for pi, paper in enumerate(data):
    qs = dedupe(paper['questions'])
    total += len(qs)
    parts.append(f'<h3>{html.escape(paper["paper"])}</h3>')
    parts.append(f'<p class="note">Computer Science section · Q{qs[0]["n"]}–Q{qs[-1]["n"]}</p>')
    for q in qs:
        key = f'{pi}-{q["n"]}'
        fix = fixes.get(key, {})
        stem = clean(fix.get('q', q['q']))
        opts = {k: clean(v) for k, v in q['o'].items()}
        opts.update({k: clean(v) for k, v in fix.get('o', {}).items()})
        unreadable = fix.get('unreadable') or looks_broken(stem) or any(looks_broken(v) for v in opts.values())

        if unreadable:          # symbols did not survive the PDF; a broken question is worse than none
            broken += 1
            skipped.append(str(q['n']))
            continue
        parts.append('<div class="pyq">')
        parts.append(f'<p class="pyq-q"><b>{q["n"]}.</b> {html.escape(stem)}</p>')
        parts.append('<ul class="pyq-o">')
        for letter in sorted(opts):
            parts.append(f'<li><span>{letter}</span> {html.escape(opts[letter])}</li>')
        parts.append('</ul>')
        parts.append(f'<div class="pyq-a" data-ans="{key}"></div>')
        parts.append('</div>')
if skipped:
    parts.append(f'<p class="note">Q{", Q".join(skipped)} formula-based hain; unke symbols PDF se theek nahi '
                 f'nikalte, isliye wo sirf official booklet PDF mein hain.</p>')
parts.append('</section>')
io.open(out, 'w', encoding='utf-8').write('\n'.join(parts))
print(f'{total} questions ({broken} flagged unreadable) -> {out}')
