#!/usr/bin/env python3
"""Deep Research Companion: show short snippets around patterns in a downloaded source, instead of reading the whole page.

Usage: python3 kit/snip.py <srcNNN|url> <regex> [<regex> ...]
Prints the hit count and up to two 220-character snippets per pattern from report/_downloads/<srcNNN>.txt.
"""
import re, sys
from pathlib import Path
DL = Path(__file__).resolve().parent.parent / "report" / "_downloads"
key = sys.argv[1]
if not key.startswith("src"):
    key = next((l.split("\t")[0] for l in (DL / "_index.tsv").read_text().splitlines() if l.split("\t")[1:2] == [key]), key)
p = DL / f"{key}.txt"
if not p.exists():
    sys.exit(f"{key}: no text")
t = re.sub(r"\s+", " ", p.read_text(errors="replace"))
print(f"== {key} ({len(t)} chars)")
for pat in sys.argv[2:]:
    hits = [m for m in re.finditer(pat, t, re.I)][:2]
    print(f"-- {pat}: {len(list(re.finditer(pat, t, re.I)))} hits")
    for m in hits:
        print("   …" + t[max(0, m.start()-110):m.end()+110] + "…")
