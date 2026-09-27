# Output check (pilot and after collection)

First run `python3 kit/name_outputs.py`: it renames the files to `NNN_ID.md`, ticks the checklist and deletes exact duplicates. Read only the answer part of an output; an exported file may repeat the prompt at the start:

```bash
awk '/RUN-ID: <ID> \| CARD:.*Date: [0-9]/{f=1} f' outputs/001_<ID>.md
```

## Pilot checklist

| Check | If there is a problem |
|---|---|
| The header line comes with a real date and the answer ends with `RUN END <ID>` | It may have been cut off: run the same file again |
| Every question section is there with the skeleton's headings | Simplify the card skeleton |
| Factual sentences carry `[S#]` codes; the table has full URLs | Strengthen the constitution's output section |
| Labels come only from the closed list | Define the misused label in the constitution |
| The source types are really primary | Strengthen the source order rule and the site list |
| PDFs: if unreadable, the URL is in the table with `[NOT ACCESSIBLE]` | Add the PDF rule to the constitution (it is in the template) |
| No advice or judgment sentences | Strengthen the role section |
| Numbers come with unit, date and scope | Strengthen the numbers rule (4.5) |

If a problem affects every run, write a **new version file** of the constitution (v1.0 → v1.1). Then update `version` and `constitution_file` in `plan.json`, run `make_runs.py` and write what changed and why in `kit/CHANGELOG.md`. If the pilot's content is usable, do not run it again.

A problem specific to one run does not need a constitution change; that question goes to the extra run.

## Known failure patterns

- **Quick search modes may not open PDFs** (e.g. Perplexity's quick search). The PDF addresses stay in the footnotes. The constitution asks for the PDF in the source table with `[NOT ACCESSIBLE]`; the PDF is read during verification.
- **Cross-module evidence may be misused.** The model may put questions of the same run into that section. The card limits this explicitly.
- **`[CONFLICT]` may be overused.** The model may count a value that changes over time as a conflict. Constitution 4.6 separates the two.
- **The self-check may contradict itself.** The model may write "Is the output complete: no" and still complete it. The line asks "Were all skeleton headings written?".
- **The report may go to a separate file.** Deep research modes may put the report into an attachment; `name_outputs.py` marks such a file `_NOANSWER`. Ask the user to copy the attachment's text.
- **Export limits.** Some tools limit daily exports. The Copy button and the clipboard watcher are not affected.

## After collection

1. `python3 kit/name_outputs.py`, then `python3 kit/coverage.py`.
2. Read `kit/coverage_summary.md`: the status of every question, the `[NOT ACCESSIBLE]` notes and the PDFs to read are there.
3. Build **one** extra run package for the questions in EMPTY, PARTIAL and CONFLICT status. Ask narrower questions in the extra runs and use the sources already found as starting links. Questions in SECONDARY status are mostly settled when the primary source is opened during verification; no extra run is needed.
4. What is still unanswered after the extra runs goes into the summary's "open questions" chapter.
