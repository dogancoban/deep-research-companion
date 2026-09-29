#!/usr/bin/env python3
"""Download every source in report/_evidence/_source_list.md to report/_downloads/ (text copies).

Usage: python3 kit/fetch_all.py      (after split_evidence.py)
Names: src001, src002 ... in source-list order; report/_downloads/_index.tsv maps name -> url -> status.
Already downloaded sources are skipped, so the script can be run again after a network problem.
Status: ok | thin (page text under 1500 characters: probably built by JavaScript; open it by hand) | error
"""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
DL = ROOT / "report" / "_downloads"
SRC = ROOT / "report" / "_evidence" / "_source_list.md"


def urls():
    out = []
    for line in SRC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(https?://[^\s|]+)\s*\|", line)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def fetch(item):
    name, url = item
    txt = DL / f"{name}.txt"
    if not txt.exists():
        r = subprocess.run([sys.executable, str(KIT / "fetch_source.py"), name, url],
                           capture_output=True, text=True, timeout=150)
        if not txt.exists():
            return name, url, "error", (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
    size = len(txt.read_text(encoding="utf-8", errors="replace"))
    return name, url, "ok" if size >= 1500 else "thin", [f"{size} characters"]


def main():
    DL.mkdir(parents=True, exist_ok=True)
    items = [(f"src{i:03d}", u) for i, u in enumerate(urls(), 1)]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch, items))
    lines = ["name\turl\tstatus\tnote"] + [f"{n}\t{u}\t{s}\t{note[0]}" for n, u, s, note in res]
    (DL / "_index.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    c = {k: sum(1 for r in res if r[2] == k) for k in ("ok", "thin", "error")}
    print(f"{len(res)} sources: {c['ok']} ok, {c['thin']} thin (JavaScript page?), {c['error']} error -> report/_downloads/_index.tsv")


if __name__ == "__main__":
    main()
