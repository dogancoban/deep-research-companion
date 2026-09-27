#!/usr/bin/env python3
"""Deep Research Companion: rename collected answers in outputs/ by the RUN-ID inside them and tick the checklist.

Usage: python3 <project>/kit/name_outputs.py
Search tools name exported files after the thread title, so names are random.
Each answer starts with "RUN-ID: <id> | CARD: ... | Date: YYYY-MM-DD"; the echoed
prompt also contains that line but with "<today>", so only a real date counts.

Result: outputs/<seq>_<RUN-ID>.md  (reruns get _rerun2, _rerun3 ...)
        outputs/<seq>_<RUN-ID>_NOANSWER.md  when the export holds only the prompt
        (e.g. the tool put its report into a separate attachment).
Exact duplicates (the same clipboard saved twice) are deleted.
"""
import hashlib
import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
OUT = ROOT / "outputs"
CHECKLIST = ROOT / "CHECKLIST.md"

# the echoed prompt has "Date: <today>"; the answer has a real date in any format
ANSWER_HEADER = re.compile(r"RUN-ID:\s*([A-Z0-9-]+)\s*\|\s*CARD:[^\n]*?Date:\s*(?!\\?<today>)[^|\n]*\d")
PROMPT_TITLE = re.compile(r"^#?\s*RUN ([A-Z0-9-]+):", re.M)
DONE_NAME = re.compile(r"^\d{3}_[A-Z0-9-]+(_rerun\d+|_NOANSWER)?\.md$")


def run_index():
    runs = json.loads((KIT / "runs.json").read_text(encoding="utf-8"))
    return {r["run_id"]: r["seq"] for r in runs}


def target(seq, run_id, suffix=""):
    base = f"{seq:03d}_{run_id}{suffix}"
    path, n = OUT / f"{base}.md", 2
    while path.exists():
        path = OUT / f"{base}_rerun{n}.md"
        n += 1
    return path


def main():
    idx = run_index()
    report, done = [], set()
    seen = {}  # content hash -> file name, to drop exact duplicates
    for f in sorted(OUT.glob("*.md")):
        if DONE_NAME.match(f.name):
            seen.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(), f.name)
    for f in sorted(OUT.glob("*.md")):
        if not DONE_NAME.match(f.name):
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            if h in seen:
                f.unlink()
                report.append((f.name, "(deleted)", f"exact copy of {seen[h]}"))
                continue
            seen[h] = f.name
        if DONE_NAME.match(f.name) and "_NOANSWER" not in f.name:
            done.add(re.match(r"^\d{3}_([A-Z0-9-]+)", f.name).group(1))
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = ANSWER_HEADER.search(text)
        if m and m.group(1) in idx:
            run_id = m.group(1)
            answer = text[m.start():]
            notes = []
            if f"RUN END {run_id}" not in answer:
                notes.append("NO END LINE (may be cut off)")
            if "SOURCE TABLE" not in answer and "KAYNAK TABLOSU" not in answer:
                notes.append("NO SOURCE TABLE")
            new = target(idx[run_id], run_id)
            f.rename(new)
            done.add(run_id)
            report.append((f.name, new.name, "; ".join(notes) or "ok"))
            continue
        if f.name.endswith("_NOANSWER.md"):
            continue  # still no answer inside; already named
        t = PROMPT_TITLE.search(text)
        if t and t.group(1) in idx:
            new = target(idx[t.group(1)], t.group(1), "_NOANSWER")
            f.rename(new)
            report.append((f.name, new.name, "no answer: the report may be in a separate attachment"))
            continue
        report.append((f.name, "(unchanged)", "no run id found"))

    if CHECKLIST.exists():
        text = CHECKLIST.read_text(encoding="utf-8")
        for run_id in done:
            text = re.sub(rf"- \[ \] (\d{{3}}_{re.escape(run_id)}_)", r"- [x] \1", text)
        CHECKLIST.write_text(text, encoding="utf-8")

    for old, new, note in report:
        print(f"{old!r:75} -> {new:35} {note}")
    print(f"finished runs: {len(done)}")


if __name__ == "__main__":
    main()
