#!/usr/bin/env python3
"""Deep Research Companion: check the two final texts before the documents are built.

Usage: python3 <project>/kit/check_report.py
Reads report/FULL_RESEARCH.md, report/SUMMARY.md, kit/plan.json and the evidence
(report/_evidence/, report/_verification_log.md, report/_downloads/*.txt, outputs/*.md). Reports:
  1. modules and questions of plan.json with no heading in the full research (errors)
  2. question sections with no tag and no "not found" / "bulunamadı"
  3. tool codes left in either text ([S3], [NOT FOUND], [SECONDARY ONLY] ...)
  4. numbers of 3+ digits found nowhere in the evidence, by line number: open only those lines
  5. numbers in the summary that the full research does not contain
  6. tag counts of the full research, for its method appendix
Tags: English [V] [U] [S] [C] [W] [N] or Turkish [D] [K] [İ] [Ç] [Y] [B].
Exit code 1 when a module or question heading is missing, else 0.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
R = ROOT / "report"
TAG = re.compile(r"\[(V|U|S|C|W|N|D|K|İ|Ç|Y|B)(?:(?:, | and | ve )[^\]]*)?\]")
MEANING = {"V": "verified", "D": "verified", "U": "sourced", "K": "sourced", "S": "secondary", "İ": "secondary",
           "C": "conflict", "Ç": "conflict", "W": "wrong", "Y": "wrong", "N": "not found", "B": "not found"}
TOOL = re.compile(r"\[S\d+\b[^\]]*\]|\[(?:NOT FOUND|NOT ACCESSIBLE|NOT PUBLIC|OUT OF RUN SCOPE|SECONDARY ONLY|CONFLICT|SYNTHESIS|"
                  r"SELF-CLAIM|ARCHIVE|OTHER CONTEXT|CROSS-MODULE EVIDENCE[^\]]*|REQUIRES EXTERNAL EXECUTION)\]")
NUM = re.compile(r"(?<!\w)\d(?:[\d.,]*\d)?")
DATE = re.compile(r"\d{1,2}[./]\d{1,2}[./]\d{4}")
GROUPED = re.compile(r"(?<=\d)[    ](?=\d{3}\b)")
LIMIT = 40


def keys(tok):
    """Numbers are compared without separators; dates by their year; short numbers are ignored."""
    if DATE.fullmatch(tok):
        return [p for p in re.split(r"[./]", tok) if len(p) >= 3]
    k = re.sub(r"[.,]", "", tok)
    return [k] if len(k) >= 3 else []


def numbers(text):
    return {k for t in NUM.findall(text) for k in keys(t)}


def unknown_lines(text, known):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        bad = [t for t in NUM.findall(line) if any(k not in known for k in keys(t))]
        if bad:
            out.append(f"    {n}: {', '.join(dict.fromkeys(bad))} | {line.strip()[:110]}")
    return out


def show(title, items):
    print(f"  {title}: " + ("none" if not items else f"{len(items)}"))
    for it in items[:LIMIT]:
        print(it)
    if len(items) > LIMIT:
        print(f"    … {len(items) - LIMIT} more lines")


def main():
    plan = json.loads((KIT / "plan.json").read_text(encoding="utf-8"))
    full_f, summary_f = R / "FULL_RESEARCH.md", R / "SUMMARY.md"
    if not full_f.exists():
        sys.exit("report/FULL_RESEARCH.md does not exist.")
    full = full_f.read_text(encoding="utf-8")
    summary = summary_f.read_text(encoding="utf-8") if summary_f.exists() else None

    ev = [p.read_text(encoding="utf-8", errors="replace")
          for pat in ("report/_evidence/*.md", "report/_verification_log.md", "report/_downloads/*.txt", "outputs/*.md")
          for p in ROOT.glob(pat)]
    ev_text = "\n".join(ev) + json.dumps(plan, ensure_ascii=False)
    known = numbers(ev_text) | numbers(GROUPED.sub("", ev_text))

    print("FULL_RESEARCH.md")
    mods = set(re.findall(r"^## ([^\s.]+)", full, re.M))
    qheads = list(re.finditer(r"^### (Q\d{2,3})\b", full, re.M))
    miss = [m for m in plan["modules"] if m not in mods] + [q for q in plan["questions"] if q not in {h.group(1) for h in qheads}]
    total = len(plan["modules"]) + len(plan["questions"])
    print(f"  Module and question headings: {total - len(miss)}/{total}" + (f"; ERROR, missing: {', '.join(miss)}" if miss else ""))
    bounds = [m.start() for m in re.finditer(r"^#{1,3} ", full, re.M)] + [len(full)]
    untagged = []
    for h in qheads:
        sec = full[h.start():min(b for b in bounds if b > h.start())]
        if not TAG.search(sec) and not re.search(r"[Bb]ulunamad|[Nn]ot found", sec):
            untagged.append(h.group(1))
    print("  Question sections without a tag: " + (", ".join(untagged) or "none"))
    if not ev:
        print("  WARNING: no evidence files found (report/_evidence, outputs); the number check means nothing.")
    for name, text in (("FULL_RESEARCH.md", full), ("SUMMARY.md", summary)):
        if text is None:
            print("SUMMARY.md does not exist")
            continue
        if name == "SUMMARY.md":
            print("SUMMARY.md")
        show("Tool codes left in the text", [f"    {n}: {m.group(0)}" for n, line in enumerate(text.splitlines(), 1) for m in TOOL.finditer(line)])
        show("Lines with a number not found in the evidence", unknown_lines(text, known))
        if name == "SUMMARY.md":   # the open-questions list may also come from report/_evidence/_open_questions.md
            ask = R / "_evidence" / "_open_questions.md"
            base = numbers(full) | (numbers(ask.read_text(encoding="utf-8")) if ask.exists() else set())
            show("Lines with a number not in the full research", unknown_lines(text, base))
    c = Counter(MEANING[m.group(1)] for m in TAG.finditer(full))
    print("Tags in the full research: " + " · ".join(f"{k} {c.get(k, 0)}" for k in ("verified", "sourced", "secondary", "conflict", "wrong", "not found")))
    print("Result: " + ("ERROR, missing headings" if miss else "all headings present"))
    sys.exit(1 if miss else 0)


if __name__ == "__main__":
    main()
