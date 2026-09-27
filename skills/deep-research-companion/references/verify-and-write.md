# Verification, writing and the two documents (big research, stage 7)

The collected outputs are a pool of evidence, not accepted as true. In this stage you split the evidence by question, check the findings against their sources and produce **two separate documents**, written in the user's language:

| Document | Content | Text file |
|---|---|---|
| `<Name>_Full_Research` (Turkish: `_Tam_Arastirma`) | The whole research: every module and every question with all collected detail; a tag next to every finding | `report/FULL_RESEARCH.md` |
| `<Name>_Summary` (Turkish: `_Ozet`) | Short answers, results table, key numbers, uncertainties, open questions; a roadmap if requested | `report/SUMMARY.md` |

- **Format:** DOCX, PDF or both. Asked in planning and stored in `plan.json` as `output.format`. If it is empty, ask before writing.
- The full research must stand on its own: even if the project folder is deleted, every finding and every source link stays in the document.
- The full research is written first; the summary is drawn from it.

## 1. Split the evidence by question

`python3 kit/split_evidence.py` writes to `report/_evidence/`:
- `Qxx.md`: the question's sections from every run (best status first), cross-module evidence from other runs, and the source rows those texts cite
- `_source_list.md`: every distinct source, which questions cite it, which are PDFs
- `_open_questions.md`: the "points the sources did not answer" sections of the runs

Read module by module; never read all outputs at once.

## 2. Verify

Download sources with `python3 kit/fetch_source.py <name> <url>` → `report/_downloads/<name>.txt`. PDFs are converted with `pdftotext`; on a certificate error the script retries with `-k`; an error page is refused. Find the relevant part with `grep`; do not read whole documents. Read scanned PDFs whose text comes out broken page by page as images. Web fetch tools often fail on PDFs. If a page links to an old PDF, extract the current link from the page's HTML (`curl ... | grep -o 'href="[^"]*\.pdf"'`); documents get updated, use the newest version.

- First verify the findings that will decide the summary's conclusions, then numbers, dates and names in the full research. If quota is short, the rest keep their tags: not every finding has to be verified, but every finding has a tag.
- Check that the finding is really written in the source. Footnote numbers and table codes sometimes do not match; what must be verified is the URL and its content.
- Never open the same page twice. Keep notes in `report/_verification_log.md`: finding, question code, URL, result, date.

## 3. Tags

Every finding carries exactly one tag, from the set that matches the document's language (other languages use the English set). The list is closed. A primary source produces the information first-hand or is authoritative on it; a secondary source repeats it.

| English | Turkish | Meaning |
|---|---|---|
| [V] | [D] | Verified: a primary source was opened and the finding is there |
| [U] | [K] | Sourced: the output gives a primary source, but it was not opened |
| [S] | [İ] | Secondary: only in secondary sources; needs confirmation |
| [C] | [Ç] | Conflict: sources say different things; all are given with source and date |

- Extra information goes after a comma: `[V, 2026-09-24]`, `[U, source did not open]`. Two statuses together: `[V and U]` (Turkish: `[D ve K]`).
- Your own inference is not a finding; it is marked "Assessment" (Turkish: "Değerlendirme").
- If you opened the source and the finding is not there, or says something else, the finding does not enter the text as a finding. It goes to the full research's "Findings that could not be verified" appendix: the claim, the cited source, and what the source actually says.
- The tool's English labels and codes like `[S3]` are not carried into the text: [NOT FOUND] becomes "not found", [SECONDARY ONLY] becomes the secondary tag, [CONFLICT] the conflict tag.

## 4. Writing rules

- Nothing new is added while writing; only findings from the evidence pool, with their tags.
- Written in the user's language, plainly. Terms are explained where they first appear.
- Numbers come with their unit, date and what or whom they cover.
- Every finding has a short source reference next to it; the full link is in the question's source list.

## 5. Full research: `report/FULL_RESEARCH.md`

Not a summary. Every collected detail is kept: numbers, dates, conditions, names, lists, tables, examples. Only repetitions are merged; platform notes and off-topic parts are dropped. Its length follows the evidence; nothing is dropped to make it shorter. The number of modules and questions changes from project to project; the structure comes from `plan.json`. Headings are written in the document's language.

```
# <Project name>
Topic, date, evidence base (<n> runs, <n> questions), what the tags mean.
The summary is a separate document: <Name>_Summary.

## <Module code>. <Module name>        in plan.json order, every module
### Qxx. <Short title>                 every question of the module; none is skipped
**Question:** the full question from plan.json
**Short answer:** 1–3 sentences, tagged
**Findings:** bullets and tables; every finding tagged (in tables, the tag sits in the cell)
**Conflicts:** what the sources say differently, with sources and dates; otherwise "none"
**Not found:** "Not found: … (searched: …)"; otherwise "none"
**Sources:** short name, publisher, date, full link

## Appendix A. Method and coverage        tool, dates, run and question counts, coverage statuses, tag counts
## Appendix B. Findings that could not be verified     "none" if there are none
## Appendix C. Documents opened and read              from _verification_log.md: document, date, link
```

(Turkish documents: `Ek A.`, `Ek B.`, `Ek C.`.) A question with no evidence at all is still written with its heading ("No run returned a sourced answer to this question.") and added to the summary's open questions.

**Large projects:** Write module by module: `report/full/00_intro.md`, then `01_<module code>.md`, `02_…` in plan order and `99_appendices.md` last. Then join them: `cat report/full/*.md > report/FULL_RESEARCH.md`. With more than 20 questions, give modules to sub-agents: at most 5 at a time; a cheaper model is enough. Give each agent the module's `_evidence/Qxx.md` files, `_verification_log.md` and sections 3–5 of this file. The agent writes only its own module file; it adds nothing new and opens no sources.

## 6. Summary: `report/SUMMARY.md`

Written after the full research, using only what is in it. The summary's conclusions (a firm answer, a decision or a recommendation) rest only on verified findings. A sourced, secondary or conflicting finding may appear in the summary with its tag, but never as the only basis for a conclusion; that topic goes to the "uncertainties" or "open questions" chapter. Every point gives the place of its detail with the question code: "(details: Q07)".

```
# <Project name>
Topic, date, what the tags mean. All findings and sources: <Name>_Full_Research.

## 1. Short answers          at most 1–2 pages: the research's main questions and short answers
## 2. Results table          question or decision, answer, deciding findings (tagged), strength of the evidence
## 3. Key numbers            value, unit, date, scope, source, tag
## 4. Uncertainties and conflicts
## 5. Open questions         what the sources did not answer: whom to ask or how to find out
## 6. Roadmap                only if the user asked: steps in order, each resting on a verified finding
## 7. Corrected information  information that turned out wrong in the chat or the runs and was corrected (if any)
## 8. Key sources            the documents the conclusions rest on
```

Extra sections chosen in planning are added to this structure. A section with nothing to say is dropped; for example, a topic without numbers has no "Key numbers" section.

## 7. Check

`python3 kit/check_report.py` lists:
- modules and questions without a heading in the full research (an error: no documents are built)
- question sections without a tag
- tool codes left in the text
- numbers not found word for word in the evidence, with line numbers
- numbers in the summary that the full research does not contain
- tag counts (for Appendix A)

Open and fix only the flagged lines; never reread the whole text. A correct number that does not appear word for word in the evidence (e.g. a sum of two values) is marked "Assessment".

## 8. Build the documents

1. `kit/doc_builder/` should have been copied when the package was built; otherwise copy the skill's `scripts/doc_builder/`.
2. Copy the skill's `assets/document.json` to `report/document.json` and fill it in: language (`en` or `tr`), cover subtitle, topics, date, tool. The glossary and the index are optional. Glossary definitions come only from verified findings; the glossary goes into both documents. The index goes only into the full research; its terms are regular expressions, with backslashes doubled in JSON (`\\b`).
3. Run `bash kit/doc_builder/build.sh`. It reads the format from `plan.json`; it can also be given by hand (`build.sh pdf`). The result: `report/<Name>_Full_Research` and `report/<Name>_Summary` (Turkish: `_Tam_Arastirma`, `_Ozet`) in the chosen format. `<Name>` is `output.file_name`, otherwise the ASCII form of the project name.
4. Visual check: open a few pages of each document as images (cover, contents, a table page, the index). If a word breaks in a narrow column, raise the minimums in `colWidths` in `make_docx.js`.
5. If `plan.json` has `output.copy`, copy the two documents there in the chosen format; ask before overwriting a file there.

Technical notes: The table of contents is a Word field. A LibreOffice macro (`Module1.xba`) updates it and writes the PDF and the updated DOCX; the macro route was chosen because LibreOffice's own Python does not run on some Macs. The index is computed from the first pass's PDF with real page numbers. Pages after appendix headings such as "Appendix A." are not indexed.
