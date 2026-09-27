"""Deep Research Companion: compute the index from the rendered PDF: printed page numbers where each term of
document.json "index" appears.

Usage: python3 make_index.py <pdf> <out.json> <document.json>
Not indexed: pages without an arabic page number (cover, front matter) and everything from the first page
that opens with an appendix heading ("Appendix A. ...", "Appendices", "Sources", "Glossary", "Index" or the
Turkish "Ek A. ...", "Ekler", "Kaynaklar", "Terimler sözlüğü", "Dizin").
document.json may override that stop rule with "index_stop" (a regex matched against whole lines).
"""
import json, re, subprocess, sys

pdf, out, cfg_file = sys.argv[1:4]
cfg = json.load(open(cfg_file, encoding="utf-8"))
TERMS = cfg.get("index", [])
STOP = re.compile(cfg.get("index_stop", r"^(Appendix [A-Z0-9]{1,3}[.:] .+|Ek [A-ZÇĞİÖŞÜ0-9]{1,3}[.:] .+|"
                                        r"Appendices|Ekler|Sources|Kaynaklar|Glossary|Terimler sözlüğü|Index|Dizin)$"))


def pages_of(mode):
    return subprocess.run(["pdftotext", mode, pdf, "-"], capture_output=True, text=True).stdout.split("\f")


pages = {}
for lay, raw in zip(pages_of("-layout"), pages_of("-raw")):
    lines = [l.strip() for l in lay.splitlines() if l.strip()]
    if len(lines) < 2 or not lines[-1].isdigit():
        continue                                           # cover and roman-numbered front matter
    if any(STOP.match(re.sub(r"\s+", " ", l)) for l in lines[1:3]):
        break
    body = re.sub(r"-\n(?=[A-ZÇĞİÖŞÜ])", "-", raw)         # rejoin words broken at a hyphen
    body = re.sub(r"\s+", " ", body).replace(re.sub(r"\s+", " ", lines[0]), " ")   # drop the running header
    pages[int(lines[-1])] = body


def rng(ps):
    ps = sorted(set(ps)); out = []; s = p = ps[0]
    for x in ps[1:]:
        if x == p + 1: p = x; continue
        out.append(f"{s}–{p}" if p > s else str(s)); s = p = x
    out.append(f"{s}–{p}" if p > s else str(s)); return ", ".join(out)


entries = []
for name, rx in TERMS:
    rxs = rx.replace(" ", r"\s*")   # justified text can lose spaces in extraction
    hit = [p for p, txt in pages.items() if re.search(rxs, txt)]
    if hit: entries.append((name, rng(hit)))
ORDER = "0123456789AaBbCcÇçDdEeFfGgĞğHhIıİiJjKkLlMmNnOoÖöPpQqRrSsŞşTtUuÜüVvWwXxYyZz"   # Turkish order, works for English
key = lambda s: [ORDER.index(ch) if ch in ORDER else 999 for ch in s]
entries.sort(key=lambda e: key(e[0]))
groups = {}
for name, pg in entries:
    L = "0–9" if name[0].isdigit() else ("İ" if name[0] == "i" and cfg.get("lang") == "tr" else name[0].upper())
    groups.setdefault(L, []).append({"term": name, "pages": pg})
json.dump([{"letter": k, "entries": v} for k, v in groups.items()], open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(pages)} body pages, {len(entries)}/{len(TERMS)} terms found, {len(groups)} letter groups")
