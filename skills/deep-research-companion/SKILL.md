---
name: deep-research-companion
description: "Deep Research Companion (Turkish name: Kanıt Hattı): topic-independent, evidence-first research alongside AI search tools such as Perplexity, ChatGPT and Gemini. Three parts: Prompt writing (turns a question into one strong, source-demanding research prompt), Answer check (checks every claim of an AI answer against its sources; flags wrong facts, dead or invented links and misattributions) and Big research (many controlled runs, source verification, then a full research and a summary as DOCX and/or PDF). Use it whenever the user wants to research anything, asks what to type into Perplexity, ChatGPT or Gemini, wants a research prompt, asks whether an AI answer or its sources are right, or wants a verified report, even without naming the skill; also in folders with COVERAGE.md and kit/plan.json. Turkish requests too: \"araştırma yapalım\", \"Perplexity'ye ne yazayım\", \"prompt yaz\", \"bu cevabı kontrol et\", \"kaynakları doğru mu\"."
---

# Deep Research Companion

AI search tools find sources fast, but they can invent facts, cite pages that do not say what they claim, return outdated information or fail to read PDFs. This skill divides the work: **the search tool collects; you, the assistant running this skill, check every finding against its source and write.** The method's Turkish name is Kanıt Hattı.

**Topic-independent.** The skill holds no topic knowledge, no ready-made question list and no topic-specific rule. Questions, source order and outputs are produced every time from the topic and the user's goal.

**Language.** Talk to the user in their language. Prompts and documents are in the user's language too; if the best sources are in another language, the search language is named inside the prompt. These instructions are in English only so they can be shared; they never set the conversation language.

## Three parts

| Part | When | Instructions |
|---|---|---|
| **Prompt writing** | The user wants to research a topic, asks what to type into a tool, or does not know where to start. If unsure, start here. | `references/prompt-writing.md` |
| **Answer check** | The user brings an AI answer and asks whether it is right | `references/answer-check.md` |
| **Big research** | Any of these: the research has many parts; every finding must be verified; documents (full research and summary) are wanted at the end; the folder holds a project with `COVERAGE.md` and `kit/plan.json` | `references/big-research.md` |

Read the chosen part's file and follow it; do not read the other parts' files unless needed.

The parts connect:
- If prompt writing shows the topic is too big for one prompt, big research is suggested.
- When the tool's answer arrives, the answer check follows.

The user decides whether to switch.

## Rules for every part

- Write short and plain. Explain a technical term the first time you use it.
- If the user asks a question, answer it and suggest the next step in one line. If they ask for work, do it. If they say "let's plan first", produce no files.
- Ask only questions that change the work and fit the topic. Never ask what is obvious or unrelated to the topic.
- Scope decisions belong to the user. Personal curiosity questions asked along the way are answered in the chat; they enter the research only if the user asks.
- Do not carry context from memory or other projects into a research unless the user asks.
- No invention: information comes from sources. Your own inference is marked "Assessment".
- Keep unnecessary personal data out of prompts; they go to third-party tools.
- Save quota: mechanical work (downloading, matching, assembling, building documents) runs as scripts on the user's computer; read only the lines you need, never whole pages or whole files; do not reread files; start agents only when needed.
- Every job that needs files gets its own folder (`~/Documents/<Name>`, ASCII characters only), never inside another project. Copy results elsewhere only if the user asks; ask before overwriting a file there.

## Tags

All parts use the same tags; in the documents they are colored. Use the set that matches the document's language (other languages: the English set). A primary source produces the information first-hand or is authoritative on it; a secondary source repeats it.

| English | Turkish | Meaning |
|---|---|---|
| [V] | [D] | Verified: a primary source was opened and the information is there |
| [U] | [K] | Sourced: a source is given but was not opened |
| [S] | [İ] | Secondary: only in secondary sources; needs confirmation |
| [C] | [Ç] | Conflict: sources say different things |
| [W] | [Y] | Wrong: a primary source says something else (answer check) |
| [N] | [B] | Not found: not in the cited source and not found elsewhere (answer check) |

## Files

| File | Part | Purpose |
|---|---|---|
| `references/prompt-writing.md` | Prompt writing | Questions, research types, prompt parts, tool and mode |
| `references/answer-check.md` | Answer check | Claim extraction, verification, results table |
| `references/big-research.md` | Big research | The 7-stage flow |
| `references/planning.md` | Big research, stages 1–2 | Topic-specific questions, topic map, source rule |
| `references/plan-json.md` | Big research, stage 3 | plan.json schema and run design |
| `references/output-qa.md` | Big research, stages 4 and 6 | Checks after the pilot and after collection |
| `references/verify-and-write.md` | Big research, stage 7 | Verification, the two documents' structure, building them |
| `scripts/make_runs.py`, `name_outputs.py`, `coverage.py`, `clipboard_watch.py` | Big research | Run files, naming outputs, coverage list, clipboard watcher (macOS, Windows, Linux) |
| `scripts/split_evidence.py`, `check_report.py` | Big research | Splitting evidence by question; checking the texts before the documents |
| `scripts/check_links.py` | Answer check, big research | Checks whether every link in a text opens |
| `scripts/fetch_source.py` | Answer check, big research | Downloads a source and converts it to text (`curl`, `pdftotext`) |
| `scripts/prepare.sh`, `fetch_all.py`, `build_full.py`, `finish.sh` | Big research, stage 7 | Local-first verification: download every source, tag every finding automatically, assemble the full research, check, build the documents |
| `scripts/snip.py` | Answer check, big research | Short snippets around a pattern in a downloaded source, instead of reading the whole page |
| `scripts/doc_builder/` | When documents are wanted | DOCX and/or PDF with cover, contents, tables, glossary, index; needs Node and LibreOffice |
| `assets/` | Big research, documents | Constitution templates (EN, TR), project README template, document settings template |
