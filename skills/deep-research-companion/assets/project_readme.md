# {{PROJECT_NAME}}

<!-- Write this README in the user's language. Replace every {{...}} ({{ASSISTANT}} = the assistant running the skill, e.g. Claude, ChatGPT or Gemini) and delete this comment. -->

{{GOAL: 2-3 sentences: what the research is about, what the result will be used for, its limits.}}

{{TOOL}} only collects sources. {{ASSISTANT}} checks every finding against its source and writes the two documents: the full research and the summary ({{FORMAT: DOCX, PDF or both}}). {{DEADLINE: e.g. "The tool subscription ends on 29 September; finish the runs before then." Delete this sentence if there is no deadline.}}

## Folders

| Folder / file | What is inside | What you do |
|---|---|---|
| `runs/` | Paste-ready run files, numbered by priority | Open them one by one |
| `outputs/` | The answers copied from the tool | Every answer is saved here |
| `CHECKLIST.md` | The list of runs | Look at it; a script ticks it |
| `COVERAGE.md` | Questions, their runs and their status | Look at it |
| `kit/` | Plan, constitution, scripts, change log | Leave it alone |
| `report/` | The two final documents: `<Name>_Full_Research` and `<Name>_Summary` | Read them |

## For every run

1. Open the next file in `runs/`.
2. In {{TOOL}}, start a **new chat**. Choose the mode named at the end of the file name: {{MODES: e.g. `QUICK` → **Search**, `DEEP` → **Deep Research**}}.
3. Copy the **whole** file, paste it, send it. Add nothing, remove nothing.
4. When the answer is finished, press the **Copy** button under it. If the clipboard watcher is running, the answer is saved automatically:

```bash
python3 {{PROJECT_PATH}}/kit/clipboard_watch.py
```

   Without the watcher, paste the answer into a new file in `outputs/` (any file name works; a script renames it).

## Rules

- Every run happens in a new chat; never write "fix it" or "continue" in the same chat.
- Do not edit the run or output files.
- **The first run is the pilot.** Give its output to {{ASSISTANT}} and wait for approval before the others.
- The order does not matter technically; the numbers are the priority order. Broad scans one at a time, the others two or three in parallel.
- When all are done, tell {{ASSISTANT}} "done" in one message. {{ASSISTANT}} builds one extra package for the gaps.

## Status

- **{{DATE}}:** Package ready. Constitution {{CODE}} {{VERSION}}, {{RUN_COUNT}} runs, {{QUESTION_COUNT}} questions. Pilot: {{PILOT}}.
