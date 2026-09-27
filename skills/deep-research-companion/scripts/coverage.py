#!/usr/bin/env python3
"""Deep Research Companion: give every question a status from the named outputs and update COVERAGE.md.

Usage: python3 <project>/kit/coverage.py      (run kit/name_outputs.py first)
Writes: COVERAGE.md (status column) and kit/coverage_summary.md
        (per-question status with the file it came from, [NOT ACCESSIBLE] notes, PDF links to read).

Status of a question section, best one wins across runs:
  ANSWERED  cited, no [NOT FOUND] in the short answer, no [CONFLICT] / [SECONDARY ONLY]
  SECONDARY cited but only [SECONDARY ONLY]
  CONFLICT  cited and carries [CONFLICT]
  PARTIAL   cited but the short answer also says [NOT FOUND]
  EMPTY     no source code in the section, or the section is missing
"""
import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
OUT = ROOT / "outputs"

NAMES = {
    "tr": {"ANSWERED": "CEVAPLANDI", "SECONDARY": "İKİNCİL", "CONFLICT": "ÇELİŞKİ", "PARTIAL": "KISMİ", "EMPTY": "BOŞ"},
    "en": {"ANSWERED": "ANSWERED", "SECONDARY": "SECONDARY", "CONFLICT": "CONFLICT", "PARTIAL": "PARTIAL", "EMPTY": "EMPTY"},
}
RANK = ["EMPTY", "PARTIAL", "CONFLICT", "SECONDARY", "ANSWERED"]
ANSWER_HEADER = re.compile(r"RUN-ID:\s*([A-Z0-9-]+)\s*\|\s*CARD:[^\n]*?Date:\s*(?!\\?<today>)[^|\n]*\d")
Q_HEAD = re.compile(r"^[#*\s]*(Q\d{2,3})\.\s", re.M)
END_OF_QS = re.compile(r"^[#*\s]*X\.\s", re.M)
SHORT = re.compile(r"^[*\s]*(Kısa cevap|Short answer)", re.M | re.I)
PDF = re.compile(r"https?://[^\s)\]|>]+\.pdf", re.I)


def names(plan):
    return NAMES.get(plan.get("lang", "en"), NAMES["en"])


def status(section):
    if not re.search(r"\[S\d+", section):
        return "EMPTY"
    m = SHORT.search(section)
    short = section[m.start():section.find("\n", m.start())] if m else section
    if "[NOT FOUND]" in short:
        return "PARTIAL"
    if "[CONFLICT]" in section:
        return "CONFLICT"
    if "[SECONDARY ONLY]" in section:
        return "SECONDARY"
    return "ANSWERED"


def main():
    plan = json.loads((KIT / "plan.json").read_text(encoding="utf-8"))
    nm = names(plan)
    runs = {r["run_id"]: r for r in json.loads((KIT / "runs.json").read_text(encoding="utf-8"))}
    best, notes, pdfs = {}, [], set()
    for f in sorted(OUT.glob("[0-9][0-9][0-9]_*.md")):
        if "_NOANSWER" in f.name:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = ANSWER_HEADER.search(text)
        if not m or m.group(1) not in runs:
            continue
        ans = text[m.start():]
        end = END_OF_QS.search(ans)
        body = ans[:end.start()] if end else ans
        heads = list(Q_HEAD.finditer(body))
        found = {}
        for i, h in enumerate(heads):
            sec = body[h.start():heads[i + 1].start() if i + 1 < len(heads) else len(body)]
            found[h.group(1)] = status(sec)
        for q in runs[m.group(1)]["questions"]:
            s = found.get(q, "EMPTY")
            if q not in best or RANK.index(s) > RANK.index(best[q][0]):
                best[q] = (s, f.stem)
        for line in ans.splitlines():
            if "[NOT ACCESSIBLE]" in line:
                notes.append(f"- {f.stem}: {line.strip()[:300]}")
        pdfs.update(PDF.findall(ans))

    kp = ROOT / "COVERAGE.md"
    text = kp.read_text(encoding="utf-8")

    def repl(mt):
        q = mt.group(1)
        if q not in best:
            return mt.group(0)
        s, src = best[q]
        return f"{mt.group(0)[:mt.start(3) - mt.start(0)]}{nm[s]} ({src}) |"
    text = re.sub(r"^\| (Q\d+) \|(.*)\| ([^|]*) \|$", repl, text, flags=re.M)
    kp.write_text(text, encoding="utf-8")

    counts = {k: 0 for k in RANK}
    for s, _ in best.values():
        counts[s] += 1
    all_q = list(plan["questions"])
    missing = [q for q in all_q if q not in best]
    summary = ["# Coverage summary", "",
               " · ".join(f"{nm[k]}: {counts[k]}" for k in reversed(RANK)) + f" · no output: {len(missing)}", "",
               "## Questions", ""]
    summary += [f"- {q}: {nm[best[q][0]]} ({best[q][1]})" if q in best else f"- {q}: no output" for q in all_q]
    summary += ["", "## [NOT ACCESSIBLE] notes", ""] + (notes or ["- none"])
    summary += ["", "## PDFs mentioned in the outputs (read them during verification)", ""] + ([f"- {u}" for u in sorted(pdfs)] or ["- none"])
    (KIT / "coverage_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(summary[2])
    need = [q for q in all_q if q not in best or best[q][0] in ("EMPTY", "PARTIAL", "CONFLICT")]
    print(f"candidates for the extra run package ({len(need)}): {', '.join(need) or 'none'}")


if __name__ == "__main__":
    main()
