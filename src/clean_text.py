"""Repair the ligature codes pypdf leaves behind in the BPSC booklets."""
import re

FIXES = [
    (':□:', '::'),      # scope resolution operator
    ('(□)', '()'),
    ('/c42', ' * '), ('/c43', ' + '), ('/c45', ' − '),
    ('/c61', ' = '), ('/c180', ' × '), ('/c162', '′'),
    ('□', ' '),
]

def clean(s):
    for a, b in FIXES:
        s = s.replace(a, b)
    s = re.sub(r'\s+([′)])', r'\1', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def looks_broken(s):
    return bool(re.search(r'/c\d{2,3}|□', s))
