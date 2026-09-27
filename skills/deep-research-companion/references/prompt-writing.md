# Prompt writing (quick part)

Turns the user's question into one strong prompt to paste into an AI search tool (Perplexity, ChatGPT, Gemini or similar). It takes a few minutes. This file holds no topic knowledge; the questions and the prompt come from the topic and the user's goal.

## 1. Clarify

Ask at most 2–3 short questions, only those whose answer changes the prompt.
- Do not ask what the message already says.
- If an AskUserQuestion tool is available, offer options that fit the topic.
- If the user says "just write it", write it without questions and state your assumptions under the prompt.

What usually needs to be clear:
- **Goal:** What will the result be used for?
- **Limits:** Period, place, person or group, sub-topic.
- **Depth and form:** A short answer, a detailed breakdown or a table.
- **Tool:** Which tool and which mode.

## 2. Pick the research type

Types are forms of question, not topics; they work the same for any subject. One prompt combines at most two types.

| Type | When | What the prompt asks for |
|---|---|---|
| Overview | Getting to know a subject | Main headings, key concepts, the most important sources |
| Single fact | One exact answer | The answer, its source and date; "not found" if it cannot be found |
| Comparison | Two or more options | A table with the same criteria for each; every cell sourced |
| Timeline | How something developed | Events in date order, each sourced |
| Full list | Every example in a field | A table with defined columns; the scope and limits of the search |
| Claim check | Is a claim true? | The strongest evidence for and against, and the kind of evidence |
| How-to | A process | Steps, conditions, common mistakes |
| Cause and effect | Causes or effects | Each explanation with the strength of its evidence; alternative explanations |

## 3. Build the prompt

Write these parts in order; skip what does not fit the topic:
1. **Context:** Who is asking and why (1–2 sentences). No unnecessary personal data; the prompt goes to a third-party tool.
2. **Task:** A clear request for the chosen type. Number the questions if there are several.
3. **Limits:** Period, place, group. From which date does a source count as current?
4. **Source rule:**
   - The most reliable source types for this topic come first: sources that produce the information first-hand or are authoritative.
   - Sponsored lists, SEO articles and self-promotional sources are not evidence.
5. **Evidence rule:**
   - Every claim has its source next to it.
   - What cannot be found is written as "not found"; no guessing.
   - Where sources disagree, each view is given with its basis.
   - Numbers come with their unit and date.
6. **Output form:**
   - headings or table columns
   - length
   - answer language
   - at the end, a source list with full links (title, publisher, date)
7. **Judgment limit (if needed):** If the user wants findings, not advice, say so.

**Language:**
- Write the prompt in the user's language; the user must be able to read and edit what they paste. The answer language is also the user's language.
- If the best sources for the topic are in another language, add one line to the prompt naming the search languages, e.g. "Search sources in English and Turkish; answer in Turkish." Search tools mostly search in the prompt's language; this line keeps the prompt in the user's language while telling the tool to look at sources in the other language too.
- If the user wants, also give a version of the prompt in that other language.

**Tool and mode:**
- Short, precise questions: the tool's quick search mode. Broad scans: its deep research mode. Examples: Perplexity's search and research modes, Deep Research in ChatGPT and Gemini. Mode names change; use the names the user sees.
- If the tool puts its answer into a separate file or attachment, ask for the answer to be written directly in the reply.
- Very long prompts get cut off in some tools; keep the prompt short and clear.

**Check before presenting:** Does the prompt have context, limits, the source rule, the "not found" rule, the output form, the source list and the answer language?

## 4. Present

- Give the prompt in a single code block, ready to copy.
- Add at most 4 lines under it: which tool and mode, the assumptions, why this form.
- Suggest 2–3 follow-up prompts to send in the same chat once the answer is in:
  - ask for what is missing
  - ask for the primary source of one claim
  - open up a conflict
- If the user wants, save the prompt to a file.

## 5. Size check

One prompt is not enough if any of these is true:
- There are more than 4 separate questions or more than two types.
- The result will support an important decision and every finding needs to be verified one by one.
- A full list and the details of every item are wanted together.
- The user wants documents at the end (full research and summary).

Then suggest the "Big research" part with a concrete estimate, e.g. "about 4 modules and 12 runs". The user decides.

## 6. When the answer arrives

If the user brings the tool's answer, move to the "Answer check" part (`references/answer-check.md`).
