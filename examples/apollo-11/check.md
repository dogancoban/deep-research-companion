# Answer check: Apollo 11

This is the skill's reply to "I asked Perplexity about Apollo 11, the answer is in answer.md. Is it right?", from a test run on 26 September 2026. The answer in [answer.md](answer.md) is a test answer written for the check: one wrong fact and one invented link were planted in it.

---

**Mostly right, but one fact is wrong and one of the three links is probably invented.**

9 claims: 8 verified, 1 wrong, 0 not found; misattributions: 1; links: 2/3 open (the third is probably invented).

Tags: [V] means verified in a primary source. A primary source produces the information or is authoritative on it; here that is NASA. [W] means wrong.

| No. | Claim | Cited source | Tag | Correct information or note | Source checked |
|---|---|---|---|---|---|
| 1 | Launched on 16 July 1969 | [1] | [V] | Correct. | 1, 5 |
| 2 | Launched from Kennedy Space Center, Florida | [1] | [V] | Correct. | 1, 5 |
| 3 | Landed on the Moon on 20 July 1969 | [1] | [V] | Correct: landed at 20:17 UTC on 20 July 1969. [1] only dates the moonwalk to 20 July and gives no landing date. | 1, 4, 5 |
| 4 | Armstrong and Aldrin walked on the surface | [2] | [V] | Correct: they were the first and second people to walk on the Moon. | 1, 2, 4 |
| 5 | Collins stayed in orbit | [2] | [V] | Correct: he stayed in lunar orbit in the command module. | 2, 5 |
| 6 | The lunar module was named Columbia | [2] | **[W]** | **Wrong.** The lunar module (the lander) was **Eagle**. Columbia was the command module, the craft that stayed in orbit with Collins. The cited source [2] says so itself. | 1, 2, 4, 5 |
| 7 | About 21.5 hours on the lunar surface | [3] | [V] | Close enough: the exact time is 21 hours 36 minutes. Only Armstrong and Aldrin were there, mostly inside the lunar module; the moonwalk itself took about 2.5 hours [2]. The cited source [3] does not open. | 2, 4 |
| 8 | Mission ended on 24 July 1969 | [1] | [V] | Correct. | 1, 5 |
| 9 | Splashdown in the Pacific Ocean | [1] | [V] | Correct. Misattribution: [1] does not mention the Pacific; [5] does. | 1, 5 |

A misattribution means the fact is right but the cited page doesn't say it.

**Link [3] is probably invented.** It returns "Page Not Found" (404) on nasa.gov. The Internet Archive's Wayback Machine has no copy of it, and a web search for its file name and title found no such document. The number it was cited for is still about right (claim 7), so source [4] replaces it.

**Corrected version**

> Apollo 11 launched on 16 July 1969 from Kennedy Space Center in Florida [1]. It landed on the Moon on 20 July 1969 [4]. Neil Armstrong and Buzz Aldrin walked on the surface while Michael Collins stayed in lunar orbit [2][5]. The lunar module was named Eagle [1][4]; Columbia was the command module [5]. Armstrong and Aldrin spent 21 hours 36 minutes on the lunar surface [4]. The mission ended on 24 July 1969 [1] with a splashdown in the Pacific Ocean [5].

**Sources**

1. [NASA: Apollo 11 mission page](https://www.nasa.gov/mission/apollo-11/). Opens; primary.
2. [Wikipedia: Apollo 11](https://en.wikipedia.org/wiki/Apollo_11). Opens; secondary (it repeats other sources).
3. https://www.nasa.gov/history/apollo-11-surface-time-report-1969.pdf. Does not open (404); probably invented; replaced by [4].
4. **New:** [NASA NSSDCA: Apollo 11 Lunar Module / EASEP](https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1969-059C). Primary. NSSDCA is NASA's official spacecraft data archive.
5. **New:** [NASA NSSDCA: Apollo 11 Command and Service Module](https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1969-059A). Primary.

**Assessment (Claude's view):** You can trust the facts, except one. The dates, launch site and crew roles all match NASA. The error is a swap of the two spacecraft names: Eagle landed, and Columbia stayed in orbit with Collins. The citations are weaker than they look: one link is probably invented, and one NASA page is credited with a fact it doesn't contain. Don't reuse this answer's source list as it is; use [4] and [5] in place of [3].
