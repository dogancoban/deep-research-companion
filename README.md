# Deep Research Companion

English | [Türkçe](README.tr.md)

**Research with Perplexity, ChatGPT or Gemini, and know which claims actually hold up.**

AI search tools answer with confidence and citations. Some citations do not say what the answer claims; some do not exist. Deep Research Companion is an agent skill that works next to the AI search tool you already use. It writes the prompt, checks the answer claim by claim against its sources, and for big questions runs a full research project that ends in two documents: a full research and a summary.

Any topic: history, health, science, law, music, markets. The questions come from your topic, not from the skill.

## See it

A real test run. We gave the skill a Perplexity-style answer about Apollo 11 with one planted error and one invented link ([answer.md](examples/apollo-11/answer.md)):

> Apollo 11 launched on 16 July 1969 from Kennedy Space Center in Florida [1]. It landed on the Moon on 20 July 1969 [1]. Neil Armstrong and Buzz Aldrin walked on the surface while Michael Collins stayed in orbit [2]. The lunar module was named Columbia [2]. The astronauts spent about 21.5 hours on the lunar surface [3]. The mission ended on 24 July 1969 with a splashdown in the Pacific Ocean [1].

**You ask:** "Is this right?"

**The skill answers** (shortened; the full reply is in [check.md](examples/apollo-11/check.md)):

> 9 claims: 8 verified, 1 wrong, 0 not found; misattributions: 1; links: 2/3 open (the third is probably invented).

| No. | Claim | Tag | Note |
|---|---|---|---|
| 6 | The lunar module was named Columbia | [W] | Wrong. The lunar module was **Eagle**; Columbia was the command module. The cited source says so itself. |
| 7 | About 21.5 hours on the lunar surface | [V] | Right (21 h 36 min), but the cited PDF returns 404 and has no archived copy: probably invented. Replaced by a NASA source. |
| 9 | Splashdown in the Pacific Ocean | [V] | Right, but the cited NASA page does not say it: a misattribution. |

It caught the planted error and the invented link, plus a misattribution nobody planted. It also gives a corrected version of the answer with working sources.

## Three parts

| Part | You say | You get |
|---|---|---|
| **Prompt writing** | "What should I ask Perplexity about why the Beatles broke up?" | 2–3 questions about your goal, then one paste-ready prompt that asks for primary sources, says "not found" instead of guessing and ends with a source list; plus follow-up prompts |
| **Answer check** | "Is this answer right?" and the answer | Every claim checked against its source: a results table, a dead-link report and a corrected version; DOCX or PDF on request |
| **Big research** | "Let's research X properly" | A plan built with you, paste-ready runs for your tool, verification of the key findings, and two documents: the full research and the summary (DOCX, PDF or both) |

## Install

Pick the place you work. Agent tools get all three parts. Chat apps get prompt writing and answer checks, because big research needs files and scripts.

**Agent tools (all three parts)**

| Tool | Install |
|---|---|
| Claude Code | `npx skills add dogancoban/deep-research-companion -g -a claude-code` |
| Claude Code, as a plugin | `/plugin marketplace add dogancoban/deep-research-companion`, then `/plugin install deep-research-companion@deep-research-companion` |
| Codex (OpenAI) | `npx skills add dogancoban/deep-research-companion -g -a codex` |
| Antigravity CLI (Google's successor to Gemini CLI) | `npx skills add dogancoban/deep-research-companion -g -a antigravity-cli` |
| Gemini CLI (still on Google's enterprise licenses) | `gemini skills install https://github.com/dogancoban/deep-research-companion.git --path skills/deep-research-companion` |
| Any other [Agent Skills](https://agentskills.io) tool | `npx skills add dogancoban/deep-research-companion -g`, then pick your tool |

Manual: copy `skills/deep-research-companion/` into your tool's skills folder (Claude Code: `~/.claude/skills/`).

**Chat apps (prompt writing and answer check)**

| App | Set up |
|---|---|
| ChatGPT | Open a Project or create a custom GPT. Paste [chat-apps/instructions.md](chat-apps/instructions.md) into its instructions and turn on web search. |
| ChatGPT workspace (Business, Enterprise, Edu) | Download `deep-research-companion.zip` from [Releases](https://github.com/dogancoban/deep-research-companion/releases/latest) and upload it as a skill (Skills → Create → Upload). |
| Gemini | Create a Gem and paste [chat-apps/instructions.md](chat-apps/instructions.md) into its instructions. |
| claude.ai | Upload `deep-research-companion.zip` from [Releases](https://github.com/dogancoban/deep-research-companion/releases/latest) in Settings → Capabilities → Skills. |

Then just talk to it:
- "Help me research how the James Webb telescope finds exoplanets."
- "What should I type into Perplexity to compare these three running shoes?"
- "Is this answer right?" (paste the answer with its sources)

## Tags

Every finding carries one tag, and the documents color them.

| Tag | Meaning |
|---|---|
| [V] | Verified: a primary source was opened and says this |
| [U] | Sourced: a source is cited but was not opened |
| [S] | Secondary: found only in secondary sources |
| [C] | Conflict: sources say different things |
| [W] | Wrong: a primary source says something else |
| [N] | Not found: not in the cited source and not found elsewhere |

Turkish documents use [D] [K] [İ] [Ç] [Y] [B].

## Requirements

- **Prompt writing and answer check:** nothing extra. The link check needs Python 3 and curl, which come with macOS and most Linux systems.
- **Big research:** Python 3, curl and Poppler (`pdftotext`) to download the sources and check them on your computer. On macOS: `brew install poppler`.
- **DOCX and PDF documents:** Node.js 18+, LibreOffice and Poppler. On macOS: `brew install node poppler && brew install --cask libreoffice`.

## Languages

The skill talks to you in your language and writes prompts and documents in it. If the best sources are in another language, the prompt tells the search tool to look there too. Documents come with an English or a Turkish layout; other languages use the English layout.

## How it works

- **The search tool collects, your assistant verifies.** Search tools are fast at finding sources and unreliable at reporting them. The assistant running the skill (Claude, ChatGPT, Gemini…) opens the sources and checks what they actually say.
- **Big research follows fixed rules.** Every run gets the same rules (a "constitution"), questions are tracked on a coverage list, and one pilot run is checked before the others.
- **Nothing new at the end.** Only collected, tagged findings go into the documents. The assistant's own conclusions are marked "Assessment".
- **Your computer does the mechanical work.** In big research, scripts download every source, check each finding's numbers against the downloaded text, assemble the full research and build the documents. The assistant reads by hand only the findings that decide the summary, so verification is faster and uses far fewer tokens.
- **Topic-independent.** The skill has no topic lists. It works out the questions, the source ranking and what to record from your topic and your goal.

## Status and limits

- **Tested:** Claude Code on macOS, with all three parts, the scripts and the DOCX and PDF builds. The chat edition was tested in the ChatGPT and Gemini apps with the Apollo example: both caught the wrong fact and reported the dead link instead of citing it.
- **Chat edition limit:** In those tests, both apps missed the misattribution (a correct fact that the cited page does not contain). The agent version, which opens and searches each source with scripts, caught it every time.
- **Local-first verification:** tested in Claude Code on macOS on a 24-run project with 280 sources: the scripts downloaded 225 sources and verified 569 findings automatically in a few minutes; the assistant checked the rest of the summary's key findings by hand.
- **Not tested yet:** Codex, Antigravity CLI, Gemini CLI and claude.ai. They read the same open skill format, so they should work; reports are welcome.
- Big research uses the tool you already pay for. You paste the run prompts yourself and bring the answers back; no API keys are needed.
- A check is only as good as the sources that can be opened. Paywalled or blocked pages stay [U]; bot checks and CAPTCHAs are never bypassed. `[V, auto]` means the numbers were found in the source by a script; the context was not read.

## Credits

Ideas were adapted, not copied, from [claude-skill-perplexity-prompting](https://github.com/joelhelbling/claude-skill-perplexity-prompting), from fact-checking skills, and from the citation checks in [academic-research-skills](https://github.com/Imbad0202/academic-research-skills).

The method was first built in Turkish under the name **Kanıt Hattı** ("evidence line").

## License

[MIT](LICENSE)
