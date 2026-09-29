# Big research

Turns a many-part research into two documents whose findings are checked against their sources: the **full research**, with every finding and its tag, and the **summary**.

Principles:
- Collection always follows the same rules (the constitution and the task cards).
- Whether anything is missing is known from a list, not guessed (the coverage list).
- One pilot run is checked before the rest are made.
- Nothing new is added while writing.

Modules, questions, source order, what to record for each question and the extra summary sections are produced in planning for this topic and written into the project's own files.

## Flow

| Stage | What you do | What the user does |
|---|---|---|
| 1. Planning | Understands the goal; settles the questions, modules, source rule and document format with the user | Goal and scope decisions; format: DOCX, PDF or both |
| 2. Quick check | Checks the critical assumptions against primary sources; on request, starts one "third eye" agent | — |
| 3. Package | Folder, constitution, plan.json, run files, README | "go" |
| 4. Pilot | Checks the first output; if needed, fixes the constitution in a new version | "001 done" |
| 5. Collection | — | Does all runs, then says "done" in one message |
| 6. Coverage and extra package | Works out the statuses; builds one extra run package for the gaps | Does the extra runs, "done" |
| 7. Verification and writing | Verifies findings against their sources; produces the full research and the summary as two documents | Reads, comments |

## 1–2. Planning and quick check

Details are in `references/planning.md`. In short:

1. **Understand the goal:** Ask at most 3–5 short questions, only those that change the scope, in the topic's own terms.
2. **Topic map:** Map the topic from your own knowledge. Find gaps with the generic thinking questions: what, who, how much, when, how, why, how sure, under what conditions, compared with what. Do not add a dimension the user's goal does not include.
3. **Proposal and depth:** Present your proposal; the user chooses. Deepen the chosen questions and set the source rule for this topic.
4. **Limits and output:** Separate what desk research cannot answer. Ask for the document format: DOCX, PDF or both. Record it in `plan.json` as `"output": {"format": "docx" | "pdf" | "both"}`. If planning was skipped, ask in stage 7 before writing.

Before designing runs, check the 3–6 critical assumptions the plan rests on against primary sources with web search and fetch. Building dozens of runs on a wrong premise is the most expensive mistake in this method. Tell the user about any corrected assumption, with its source.

## 3. Package

```
<Project>/
├── README.md       instructions and status for the user (assets/project_readme.md)
├── CHECKLIST.md    the runs; name_outputs.py ticks them
├── COVERAGE.md     question → run → status; coverage.py fills it in
├── runs/           NNN_<ID>_<MODE>.txt, ready to paste
├── outputs/        the answers; name_outputs.py renames them
├── kit/            plan.json, CONSTITUTION-<CODE>_vX.Y.txt, scripts (doc_builder/ included), runs.json, CHANGELOG.md
└── report/         _evidence/, _downloads/, _verification_log.md, FULL_RESEARCH.md, SUMMARY.md, document.json and the two documents
```

1. **Folder:** Create the folder `<Project-Name>` (ASCII characters only) where SKILL.md says job folders go: the user's folder rule if there is one, otherwise `~/Documents/`. Copy everything in the skill's `scripts/` folder (`doc_builder/` included) into `kit/`.
2. **Constitution:**
   - The constitution and the runs are written in the user's language. Copy `assets/constitution_en.txt` or `constitution_tr.txt` to `kit/CONSTITUTION-<CODE>_v1.0.txt`. For another language, translate the template into it.
   - Fill in the `{{…}}` fields with what planning settled: role, scenario, target context, time, source types and order, search, output language.
   - Put only situations that change the answers into the scenario; no unnecessary personal data.
   - If the sources are in other languages, write the search languages into the `SEARCH` field.
   - The labels are a closed list and stay in English, so scripts can check the outputs.
3. **plan.json:** The schema and run design rules are in `references/plan-json.md`. Write the details settled in planning into `record_text`. Run rules:
   - 2–4 questions per run
   - the expensive mode only for broad scans
   - the numbering is the priority order
   - starting links only if you have seen that they exist
4. **Build:** Run `python3 kit/make_runs.py`. It writes the run files, `runs.json`, the checklist and the coverage list. It catches undefined questions, questions tied to no run, files that are too large and a missing document format.
5. **README and log:** Fill in the README from the template. Write the v1.0 entry in `kit/CHANGELOG.md`.
6. **Tell the user** briefly: how many runs, which one is the pilot, what to do first.

## 4. Pilot

When the user says the pilot is done, run `python3 kit/name_outputs.py` and check the output with `references/output-qa.md`. If there is a problem that affects every run:
1. write a new version file of the constitution
2. update `plan.json`
3. rebuild the files
4. log the change

Then tell the user:
- They can do the remaining runs; the order does not matter technically, the numbers are only the priority.
- Expensive modes one at a time, the others in parallel; every run in a new chat.
- Keep the clipboard watcher running.
- When everything is done, say "done" in one message.

## 5–6. Collection, coverage and a single extra package

```bash
python3 <project>/kit/name_outputs.py   # renames the outputs, ticks the checklist
python3 <project>/kit/coverage.py       # writes the statuses into COVERAGE.md and kit/coverage_summary.md
```

Build **one** extra run package for the questions in EMPTY, PARTIAL and CONFLICT status: add runs EX1, EX2… to `plan.json` and run `make_runs.py`. Questions in SECONDARY status are usually settled in verification, when the primary source is opened. If the tool has an end date (e.g. a subscription), plan for the extra package to finish before it.

## 7. Verification and writing

Local-first: scripts on the user's computer do the mechanical work (downloading, matching, assembling, building); the assistant does only what needs judgment. The rules, tags, both documents' structure and the hand-check rules are in `references/verify-and-write.md`. In short:

1. If `plan.json` has no `output.format`, ask the user: DOCX, PDF or both. Fill in `report/document.json` from the skill's `assets/document.json`.
2. `bash kit/prepare.sh` (the user may run it): names the outputs, updates coverage, splits the evidence, downloads every source (`fetch_all.py`) and writes `report/FULL_RESEARCH.md` with a tag on every finding (`build_full.py`). A finding whose numbers all occur in its downloaded source gets `[V, auto]`.
3. Hand checks, only where they matter: the findings that will decide the summary and are not `[V, auto]` in `report/_auto_verify.tsv`. Search downloaded texts with `python3 kit/snip.py`; fetch only the lines you need from pages that did not download. Record every result in `report/_manual_checks.tsv` and `report/_verification_log.md`. Other findings keep their automatic tags.
4. Write `report/SUMMARY.md` from the full research: read the short answers and table rows you need, never the whole text. Conclusions rest only on verified findings. If the user asked for a roadmap, build it from verified findings only.
5. `bash kit/finish.sh`: rebuilds the full research with the hand checks, runs `check_report.py` and builds the two documents. Fix only the lines it flags and run it again. If `output.copy` is set, copy the documents there.

Neither text adds anything new. What stays unanswered goes into the summary's "open questions" chapter.
