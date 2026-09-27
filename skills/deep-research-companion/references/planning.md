# Planning (big research, stages 1–2): smart questions for any topic

This skill holds no topic knowledge; you know the topic. For every research, work out the following from the topic and the user's goal, settle them with the user and write them into the project's own files (`plan.json`, the constitution, the README):
- modules and questions
- source order
- what to record for each question
- extra summary sections

This file only describes how to do that.

If the user says "let's plan first", write the plan and produce no files. Scope decisions belong to the user.

## 1. Understand the goal

First work out what the user's first message already says. Then ask at most 3–5 short questions.
- Ask only questions whose answer changes the scope of the research.
- Do not ask what the message already says, what is obvious, or what has nothing to do with the topic.
- Phrase the questions in the topic's own terms. Never read out a generic list.
- If an AskUserQuestion tool is available, offer options that fit the topic.

What needs to be clear (decide from the topic which of these to ask):
- **Goal:** What is the research for? Curiosity, learning, a decision, a piece of writing or a product, a comparison or a plan.
- **User and depth:** Who will use the result and how much detail do they want?
- **Limits:** Which period, place, person, group or sub-topic?
- **Starting point:** What does the user already know, and what are they unsure about?
- **Out of scope:** What must stay out?

## 2. Map the topic

Scan the topic with your own knowledge: what would someone who works deeply in this field look at, which questions would they ask? Place the user's questions on that map, then look for gaps.

To find gaps, apply the generic questions below to the topic in your head. They are thinking tools, not a list to read out to the user. Skip any that have no meaning for the topic.

| Generic question | Applied to the topic |
|---|---|
| What? | Are the concepts and scope clear; what is inside, what is left out? |
| Who? | Who is affected, who is decisive, who says what? |
| How much? | Which numbers are needed, in which unit? |
| When, where? | Which period and place does the information apply to? |
| How? | Process, mechanism, steps |
| Why? | Causes, effects, connections |
| How sure? | How strong is the evidence; where do experts and sources disagree? |
| Under what conditions? | What changes by person or situation; what are the exceptions? |
| Compared with what? | Alternatives, comparisons, downsides |
| What changed, what is changing? | Outdated information, new developments |
| Common errors | Claims believed to be true with weak sources; what partisan sources say |

Only propose headings that serve the user's goal. Do not add a dimension the user did not mention on your own; if you think it is needed, ask in one sentence. Do not carry context from memory or from other projects into this research unless the user asks.

## 3. Present your proposal; the user chooses

Give a short map: modules and questions. Mark which are the user's and which are your proposals, and say in one sentence how each proposal serves the goal.
- The user chooses; do not add anything they did not choose.
- Personal curiosity questions asked along the way are answered in the chat. They do not enter the research unless the user asks.
- **Order:** If the answer to one question changes the scope of others, it comes first.

## 4. Deepen the questions

For every chosen question, decide which details the answer needs to be useful:
- which numbers (unit, date, scope)
- which conditions and exceptions
- which examples, comparisons or tables

Write these into the question texts and into `record_text` in `plan.json`. That is where the search tool learns what to record for each question.

## 5. Set the source rule for this topic

For this topic:
- Who produces the information first-hand, or is authoritative?
- Which sources are independent and reviewed?
- Which sources only repeat others?
- Which are partisan or self-promotional?

Rank the source types from most to least reliable. Write the result into the constitution's `SOURCE_TYPES` and `SOURCE_ORDER` fields. Set the search languages and the priority sites here too (`SEARCH`). The only fixed rule: primary sources come before secondary ones.

## 6. Separate what desk research cannot give

Tell the user honestly. These do not go into the runs; they go into the summary's "open questions" chapter or a separate step:
1. Answers only someone authoritative can give (unpublished information, decisions not yet made)
2. Things that depend on the person's own situation (scenarios can be written for these)
3. Things to be learned by measuring, trying or interviewing

## 7. Settle the output

- **Documents:** Two documents come out: the full research and the summary. Ask for the format: DOCX, PDF or both. Record the answer in `plan.json` as `output.format`.
- **Place:** The documents are produced in the project folder. If they should also be copied elsewhere, ask where and record it as `output.copy`.
- **Summary sections:** The base structure is in `verify-and-write.md`. If the topic needs an extra section, choose it with the user here. Ask whether they want a roadmap only if the goal is a decision or a plan; in research for curiosity or learning, do not ask.

## 8. The plan

Write the plan with these sections:
- goal and use
- limits
- modules and questions (the origin of each: the user or a proposal)
- order
- source rule
- what desk research cannot give
- method: who collects, who verifies, how many runs, which mode, deadline
- output

## Quick check (before building runs)

Check the 3–6 critical assumptions the plan rests on against primary sources with web search or fetch. Building dozens of runs on a wrong premise is the most expensive mistake in this method: the user's question may assume that something exists or is true while the primary source says otherwise. Tell the user about a corrected assumption with its source, and build the plan on it.

## Third eye (optional, one agent)

If the user asks, or if a wrong result could seriously harm the user, start **one** independent agent that criticises the plan from scratch. The agent does not see your context, so the prompt must stand on its own. Include:
- **Context:** The user's goal and limits. Unverified assumptions are marked clearly.
- **Plan:** The user's questions and the current plan (modules and runs).
- **Task:** Criticise the plan with three eyes: an expert in this topic, the person who will use the result, and a sceptic. Pick the roles to fit the topic. Find gaps and risky assumptions.
- **Limits:** At most 8 web searches. Findings are labelled "verified" or "estimate", with URLs. At most 25 points in priority order, at most 700 words. No files written.

While the agent works, do your own quick check; do not search the same things twice. Anything the agent calls "verified" that you have not opened and read is only a hint for the user.
