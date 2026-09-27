#!/usr/bin/env python3
"""Deep Research Companion: split the collected answers by question, as the base of the full-research write-up.

Usage: python3 <project>/kit/split_evidence.py      (after name_outputs.py; needs coverage.py in the same folder)
Writes report/_evidence/ (rewritten on every run):
  Qxx.md               every section written for Qxx in any run (best status first), cross-module lines
                       from other runs, and the source-table rows those texts cite (S-codes are per run)
  _source_list.md      every distinct URL with the questions and runs that cite it
  _open_questions.md   the "points the sources did not answer" sections of all runs
Platform footnote numbers like [3] are dropped; everything else is copied unchanged.
"""
import json
import re
from pathlib import Path

from coverage import ANSWER_HEADER, Q_HEAD, RANK, names, status

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
OUT = ROOT / "outputs"
DEST = ROOT / "report" / "_evidence"

PART = re.compile(r"^[#*\s]*([XYZ])\.\s", re.M)
CROSS = re.compile(r"\[CROSS-MODULE EVIDENCE:\s*(Q\d{2,3})\s*\]")
CITE = re.compile(r"\[([^\]\n]*\bS\d+\b[^\]\n]*)\]")
FOOTNOTE = re.compile(r"(?:\[\^?\d{1,3}\](?:\([^)\s]*\))?)+")
URL = re.compile(r"https?://[^\s|)\]>]+")


def codes(text):
    found = {c for m in CITE.finditer(text) for c in re.findall(r"\bS\d+\b", m.group(1))}
    return sorted(found, key=lambda c: int(c[1:]))


def parse(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    m = ANSWER_HEADER.search(text)
    if not m:
        return None
    ans = FOOTNOTE.sub("", text[m.start():])
    marks = {}
    for p in PART.finditer(ans):
        marks.setdefault(p.group(1), p.start())

    def part(k):
        if k not in marks:
            return ""
        later = [v for v in marks.values() if v > marks[k]]
        return ans[marks[k]:min(later) if later else len(ans)]

    body = ans[:min(marks.values()) if marks else len(ans)]
    heads = list(Q_HEAD.finditer(body))
    sections = {}
    for i, h in enumerate(heads):
        sec = body[h.start():heads[i + 1].start() if i + 1 < len(heads) else len(body)].strip()
        sections[h.group(1)] = sections[h.group(1)] + "\n\n" + sec if h.group(1) in sections else sec
    rows = {}
    for line in ans.splitlines():
        s = line.strip()
        cells = [c.strip().strip("*").strip() for c in s.strip("|").split("|")] if s.startswith("|") else []
        if cells and re.fullmatch(r"S\d+", cells[0]):
            u = URL.search(s)
            rows[cells[0]] = {"line": s, "url": u.group(0).rstrip(".,;") if u else "", "cells": cells}
    cross = [(q, line.strip().lstrip("-*• ").strip()) for line in part("Y").splitlines() for q in CROSS.findall(line)]
    x = part("X").strip().split("\n", 1)
    x = x[1].strip() if len(x) > 1 else ""
    return {"run_id": m.group(1), "sections": sections, "rows": rows, "cross": cross,
            "x": "" if x.lower().strip(".-*• ") in ("", "yok", "none") else x}


def main():
    plan = json.loads((KIT / "plan.json").read_text(encoding="utf-8"))
    nm = names(plan)
    runs = {r["run_id"]: r for r in json.loads((KIT / "runs.json").read_text(encoding="utf-8"))}
    got = []
    for f in sorted(OUT.glob("[0-9][0-9][0-9]_*.md")):
        if "_NOANSWER" in f.name:
            continue
        p = parse(f)
        if p and p["run_id"] in runs:
            p.update(stem=f.stem, mode=runs[p["run_id"]]["mode"])
            got.append(p)
    DEST.mkdir(parents=True, exist_ok=True)
    for old in DEST.glob("*.md"):
        old.unlink()
    sources = {}

    def cite(p, text, q):
        out = []
        for c in codes(text):
            r = p["rows"].get(c)
            if not r:
                out.append(f"| {c} | (not in the source table) |")
                continue
            out.append(r["line"])
            if r["url"]:
                s = sources.setdefault(r["url"], {"cells": r["cells"], "qs": set(), "runs": set()})
                s["qs"].add(q)
                s["runs"].add(p["stem"])
        return out

    empty = []
    for q, (mod, short, full) in plan["questions"].items():
        secs = sorted(((p, p["sections"][q]) for p in got if q in p["sections"]),
                      key=lambda ps: (-RANK.index(status(ps[1])), ps[0]["stem"]))
        cross = [(p, line) for p in got for cq, line in p["cross"] if cq == q]
        lines = [f"# {q}. {short}", "", f"Module: {mod} {plan['modules'].get(mod, '')}", f"Question: {full}", ""]
        if not cross and all(status(sec) == "EMPTY" for _, sec in secs):
            empty.append(q)
        if not secs and not cross:
            lines.append("No run has a section for this question.")
        for p, sec in secs:
            lines += [f"## {p['stem']} ({p['mode']}) · {nm[status(sec)]}", "", sec, ""]
            rows = cite(p, sec, q)
            if rows:
                lines += ["Sources:", *rows, ""]
        if cross:
            lines += ["## Cross-module evidence from other runs", ""]
            for p, line in cross:
                lines.append(f"- {p['stem']}: {line}")
                lines += [f"  {r}" for r in cite(p, line, q)]
            lines.append("")
        (DEST / f"{q}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    xs = ["# Points the sources did not answer (X sections of the runs)", ""]
    for p in got:
        if p["x"]:
            xs += [f"## {p['stem']}", "", p["x"], ""]
    (DEST / "_open_questions.md").write_text("\n".join(xs) + "\n", encoding="utf-8")

    ks = ["# Sources", "", f"{len(sources)} distinct sources; most-used first.", "",
          "| URL | Title | Publisher | Date | Type | Questions | Runs |", "|---|---|---|---|---|---|---|"]
    for url, s in sorted(sources.items(), key=lambda kv: (-len(kv[1]["qs"]), kv[0])):
        c = s["cells"] + [""] * 8
        ks.append(f"| {url} | {c[2]} | {c[3]} | {c[4]} | {c[6]} | {', '.join(sorted(s['qs']))} | {', '.join(sorted(s['runs']))} |")
    (DEST / "_source_list.md").write_text("\n".join(ks) + "\n", encoding="utf-8")

    pdfs = sum(1 for u in sources if re.search(r"\.pdf($|[?#])", u, re.I))
    total = len(plan["questions"])
    print(f"{len(got)} outputs read; questions with a sourced answer: {total - len(empty)}/{total}"
          + (f" (unsourced: {', '.join(empty)})" if empty else "")
          + f"; {len(sources)} distinct sources, {pdfs} PDF -> report/_evidence/")


if __name__ == "__main__":
    main()
