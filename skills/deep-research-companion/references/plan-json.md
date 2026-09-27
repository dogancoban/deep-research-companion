# kit/plan.json

`make_runs.py`, `coverage.py`, `split_evidence.py`, `check_report.py` and `doc_builder/build.sh` read this file. Its content is produced in planning for the topic; below is only the schema. Codes stay fixed: if a question is dropped, its code is left unused, never renumbered (the outputs and the coverage list depend on the codes).

```json
{
  "project": "<Project name>",
  "lang": "en",
  "code": "AB",
  "version": "v1.0",
  "constitution_file": "CONSTITUTION-AB_v1.0.txt",
  "pilot": "M1A",
  "modes": {"QUICK": "Search", "DEEP": "Deep Research"},
  "modules": {
    "M1": "<Module name>",
    "M2": "<Module name>"
  },
  "questions": {
    "Q01": ["M1", "Short title (shown in capitals in the skeleton)", "Full question: what to record, which details are needed."],
    "Q02": ["M2", "…", "…"]
  },
  "runs": [
    {
      "id": "M1A",
      "mode": "QUICK",
      "questions": ["Q01"],
      "goal": "First line of the run file: what this run records, in one sentence.",
      "scope": "SCOPE NAME SHOWN IN THE HEADER LINE",
      "note": "Optional card instruction, e.g. table columns, also search in another language.",
      "links": ["https://… only URLs you have seen exist"]
    }
  ],
  "record_text": "The 'For each question record' sentence settled in planning for this topic.",
  "output": {"format": "both"}
}
```

## Fields

| Field | Meaning |
|---|---|
| `lang` | Language of the card scaffolding: `en` or `tr` (other languages use `en`). Pick the constitution template in the user's language. |
| `code`, `version` | Shown in the header line as `CARD: AB v1.0`. When the constitution changes, update `version` and `constitution_file` together. |
| `pilot` | The run marked "FIRST" in the checklist. |
| `modes` | Mode code in the file name → the name of the button in the tool. Codes use capitals, digits and hyphens. |
| `modules`, `questions` | Produced in planning for the topic. `questions`: `code: [module, short title, full question]`. |
| `runs` | Order = priority = file number. `id` uses capitals, digits and hyphens. |
| `record_text` | What the tool records for each question; written in planning step 4 for this topic. If empty, a generic text is used. |
| `output` | `format`: the document format, `docx`, `pdf` or `both`; asked in planning, read by `doc_builder/build.sh`. Optional `file_name`: the ASCII start of the document names (otherwise derived from the project name). Optional `copy`: a folder the documents are also copied to. |

## Extra runs

After collection, add `EX1`, `EX2`… to the end of `runs` for the questions left empty and run `make_runs.py` again. The new files get the next numbers; the ticks of earlier runs are kept. A question may be tied to more than one run; `coverage.py` takes the best result.

## Run design

- 2–4 questions per run. One heavy question (a full list, a broad scan) is a run of its own.
- A run file should stay under 14,000 characters (`make_runs.py` warns). Otherwise split its questions.
- Expensive or limited modes (such as Deep Research) only for broad scans: every option or example in a field. Where a table is needed, give its columns in `note`.
- Numbering = priority: questions whose answers change the scope of others come first.
- Starting links are only URLs you have seen exist in your own search; invented links push the tool the wrong way.
