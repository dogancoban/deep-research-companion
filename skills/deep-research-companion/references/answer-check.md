# Answer check

Checks a single answer from an AI tool (Perplexity, ChatGPT, Gemini or similar) against its sources: which claims are right, which are wrong, which have no source. This file holds no topic knowledge.

## 1. Get the answer

- The user pastes the answer or gives it as a file. The source links must come with it; if they are missing, ask for them.
- **Short answer (at most 5 claims):** No folder.
  - Save the answer to a temporary file.
  - Run `python3 <skill>/scripts/check_links.py <file>`.
  - Read the pages with your web fetch tool.
  - Do not run `fetch_source.py` from the skill folder; it writes its downloads next to itself.
- **Long answer, or documents wanted:** Set up a working folder.
  - Folder: `~/Documents/<Topic>-Check/` (ASCII characters only).
  - Copy the skill's `scripts/` folder into it as `kit/`.
  - Save the answer as `answer.md`.

## 2. Check the links

`python3 kit/check_links.py answer.md` shows for every link:
- whether it opens
- whether it is a PDF or a page
- its title

The script reads only the start of each page; that does not count as reading it. To verify, download and read a page once; never download the same page twice.

- **blocked (401/403/429):** Usually bot protection; try your web fetch tool.
- **broken (404, 410):** The page may have moved. When you verify the claims that cite it, search for its file name or for the title given in the answer's source list (the title the script shows belongs to the error page), and look for an old copy on web.archive.org (`https://archive.org/wayback/available?url=<link>` also works). Only if both find nothing, write "does not open, probably invented"; if the archive could not be checked, say so. Never state "invented" as a fact.
- **opens:** A working link does not prove the claim; the page has to be read.

## 3. Extract the claims

- Split the answer into checkable claims, one piece of information per line: a number, date, name, event or cause-and-effect claim.
- If one sentence carries several pieces of information, split it. For example, "X happened in Y on date T" is two claims: the date and the place.
- Opinions and general sentences cannot be checked; mark them "opinion".
- Number every claim and write the source the answer cites next to it.
- In a long answer, first pick the claims that matter for the user's goal, usually at most 20–30. The rest stay [U]. Tell the user which ones you picked.

## 4. Verify

- Open the cited source: download it with `python3 kit/fetch_source.py <name> <url>` and find the relevant part in `report/_downloads/` with `grep` (or Python). Web fetch tools often fail on PDFs. Check that the claim is really written in the source.
- **Primary and secondary sources:**
  - A primary source produces the information first-hand or is authoritative on it. A secondary source repeats it.
  - A claim seen only in secondary sources gets [S]; if it is also found in a primary source, it gets [V].
  - Calling a claim [W] needs a stronger source than the answer's, preferably a primary one.
- **The source opens but the claim is not in it:** Look for a stronger source.
  - If the claim is found elsewhere, tag it by that source and write in the note "misattribution: not in the cited source".
  - If it is found nowhere, it gets [N].
- **The cited source supports only part of the claim:** Tag the claim by the source that supports all of it and write "partly in the cited source" in the note; it counts as a misattribution.
- **The cited source contradicts the claim:** If that source is primary, this is enough for [W]; if it is secondary, confirm with a primary source first.
- **The source does not open:** A correct claim whose cited source is dead or invented is tagged by its new source. The dead link is noted separately and counted with the links, not as a misattribution. Tag [U] only if the claim could not be checked anywhere.
- **Correct claim, secondary source:** If the cited source is secondary and states the claim correctly, check it against a primary source where you can ([V]); otherwise tag [S].
- **Rounded numbers:** A rounded value is [V] if rounding the primary source's exact value gives it ("about 21.5" for 21 h 36 min); put the exact value in the note. If sources give different values, it is [C].
- Tag each result (use the Turkish set for Turkish reports):

| English | Turkish | Meaning |
|---|---|---|
| [V] | [D] | Verified: a primary source was opened and the claim is there |
| [U] | [K] | Sourced: a source is cited but was not opened |
| [S] | [İ] | Secondary: only in secondary sources |
| [C] | [Ç] | Conflict: sources say different things |
| [W] | [Y] | Wrong: a primary source says something else; the correct information is given with its source |
| [N] | [B] | Not found: not in the cited source and not found anywhere else |

## 5. Present the result

By default in the chat, in the user's language:
1. **One-line summary** with the count for every tag used: "N claims: a [V], b [W], c [N], d [S]…; misattributions: e; links: k/n open (f probably invented)."
2. **Table:** No. | Claim | Cited source | Tag | Correct information or note | Source checked
   - "Source checked" holds the numbers of the sources that decided the tag. New sources get new numbers and are marked "new" in the source list.
3. **Corrected version:** A short rewrite of the answer with only the verified and corrected information.
   - Nothing new is added; corrections come from primary sources. A correction may carry a short explanation from the same source (e.g. what the two confused names really refer to).
   - Source numbers are kept. The source that replaces a dead link is shown in the list.
4. **Assessment:** Clearly marked as your own view: which parts of the answer can be trusted and which cannot.

**If the user wants a document:**
1. Ask for the format: DOCX, PDF or both.
2. Copy the skill's `assets/document.json` to `report/document.json`. Fill it in and add a `"file_name"` field.
3. Write the text as `report/VERIFICATION.md`: first line `# Title`, then a short description, then chapters starting with `## `.
4. Run `bash kit/doc_builder/build.sh <format> VERIFICATION.md check`. The result is `report/<file_name>_Verification` (Turkish: `_Dogrulama`) in the chosen format.

## 6. Afterwards

If many claims are wrong or not found, suggest rebuilding the question with "Prompt writing". If the topic is big, suggest "Big research". The user decides.
