#!/usr/bin/env python3
"""Deep Research Companion: automatic pre-verification and the full-research text, without a model.

Usage: python3 kit/build_full.py      (after split_evidence.py and fetch_all.py)
Reads:  report/_evidence/Qxx.md, report/_downloads/ (+ _index.tsv), report/_manual_checks.tsv (optional),
        kit/plan.json, kit/runs.json, kit/coverage_summary.md, report/document.json (optional: tool, date)
Writes: report/FULL_RESEARCH.md, report/_auto_verify.tsv (one row per finding), report/_auto_verify_summary.md

Every finding (the text before a [S1][S2] citation, or a table row with source codes) gets one tag.
Turkish set shown, English in brackets:
  [D, oto]  ([V, auto])   every number of the finding (2+ digits, or with % / $ / x) occurs in a downloaded cited source
  [D]       ([V])         checked by hand (report/_manual_checks.tsv)
  [K]       ([U])         sourced; no numbers to match
  [K, eşleşmedi] / [K, kısmi eşleşme] / [K, kaynak açılamadı]   ([U, no match] / [U, partial match] / [U, source did not open])
  [İ] ([S]) secondary only · [Ç] ([C]) conflict · [Y] ([W]) wrong: hand check; the finding moves to Appendix B
A number match is not a full check: the summary's deciding findings are still read by hand.

report/_manual_checks.tsv (tab-separated, first line is a header):
  url <TAB> text (a piece of the finding, or * for every finding citing the url) <TAB> tag (D/K/Y or V/U/W, extra after a comma) <TAB> note
Optional plan.json keys: "type_names" {"VENDOR-CASE": "vendor case", ...}, "run_notes" {"001_A1": "pilot, constitution v1.0"}.
"""
import json
import re
from collections import Counter
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent
REP = ROOT / "report"
EV = REP / "_evidence"
DL = REP / "_downloads"
PLAN = json.loads((KIT / "plan.json").read_text(encoding="utf-8"))
DOC = json.loads((REP / "document.json").read_text(encoding="utf-8")) if (REP / "document.json").exists() else {}
LANG = "tr" if PLAN.get("lang") == "tr" else "en"

T = {
    "tr": dict(V="D", U="K", S="İ", C="Ç", W="Y", auto="oto", nomatch="eşleşmedi", partial="kısmi eşleşme",
               noopen="kaynak açılamadı", question="Soru", findings="**Bulgular:**", notfound="Bulunamayanlar",
               nf_some="{n} nokta; metinde \"bulunamadı\" olarak ve denenen aramalarla işaretli.", none="yok",
               sources="Kaynaklar", src="kaynak", run="Koşu", cross="Diğer koşulardan ilgili kanıt",
               noev="Hiçbir koşu bu soruya kaynaklı bir cevap getirmedi.", full="Tam Araştırma", sumsuf="_Ozet",
               appA="Ek A. Yöntem ve kapsam", appB="Ek B. Doğrulanamayan bulgular", appC="Ek C. Açılıp okunan belgeler",
               appD="Ek D. Kaynakların cevaplamadığı noktalar", hand="Elle kontrol edilenler:", nothing="Yok.",
               base="Kanıt tabanı: {tool} ile {runs} koşu, {qs} soru, {src} farklı kaynak. Tarih: {date}.",
               notsum="Bu belge özet değildir: toplanan bütün ayrıntı soru soru yer alır. Özet ayrı bir belgedir: {sum}.",
               legend="**Etiketler:** [D] doğrulandı: kaynak açıldı ve bulgu orada · [D, oto] bulgudaki sayıların tamamı indirilen kaynak metninde script ile bulundu (bağlam okunmadı) · [K] kaynak gösterildi, içerik doğrulanmadı (\"eşleşmedi\", \"kısmi eşleşme\", \"kaynak açılamadı\" nedenini söyler) · [İ] yalnızca ikincil kaynakta · [Ç] kaynaklar çelişiyor. \"(kendi beyanı)\": bilgi kaynağın kendisi hakkındaki beyanıdır, bağımsız ölçüm değildir.",
               method="Kaynakları {tool} topladı; her koşu aynı anayasa ve görev kartıyla yapıldı. Kaynaklar script ile indirildi ve bulgulardaki sayılar kaynak metninde arandı; özete giren bulgular ayrıca elle kontrol edildi.",
               m_runs="Koşular: {runs}; sorular: {qs}", m_cov="Kapsam durumu: {cov}",
               m_src="Kaynaklar: {n}; indirilen {ok}, zayıf metin (JavaScript sayfası) {thin}, açılamayan {err}",
               m_tags="Etiketlenen bulgu: {n}; {tags}", source_of="kaynak",
               labels=[(r"\[NOT FOUND\]", "bulunamadı"), (r"\[NOT ACCESSIBLE\]", "(kaynak açılamadı)"),
                       (r"\[NOT PUBLIC\]", "(kamuya açık değil)"), (r"\[OUT OF RUN SCOPE\]", "(kapsam dışı)"),
                       (r"\[SELF-CLAIM\]", "(kendi beyanı)"), (r"\[SYNTHESIS\]", "(birleştirme)"),
                       (r"\[ARCHIVE[^\]]*\]", "(eski kaynak)"), (r"\[OTHER CONTEXT\]", "(başka bağlam)"),
                       (r"\[REQUIRES EXTERNAL EXECUTION\]", "(dış çalışma gerekir)"),
                       (r"\[CROSS-MODULE EVIDENCE:\s*(Q\d+)\s*\]", r"(bkz. \1)")],
               details=("**Ayrıntılar:**", "### Ayrıntılar")),
    "en": dict(V="V", U="U", S="S", C="C", W="W", auto="auto", nomatch="no match", partial="partial match",
               noopen="source did not open", question="Question", findings="**Findings:**", notfound="Not found",
               nf_some="{n} points; marked \"not found\" in the text, with the searches tried.", none="none",
               sources="Sources", src="source", run="Run", cross="Related evidence from other runs",
               noev="No run returned a sourced answer to this question.", full="Full Research", sumsuf="_Summary",
               appA="Appendix A. Method and coverage", appB="Appendix B. Findings that could not be verified",
               appC="Appendix C. Documents opened and read", appD="Appendix D. Points the sources did not answer",
               hand="Checked by hand:", nothing="None.",
               base="Evidence base: {runs} runs with {tool}, {qs} questions, {src} distinct sources. Date: {date}.",
               notsum="This document is not a summary: every collected detail is kept, question by question. The summary is a separate document: {sum}.",
               legend="**Tags:** [V] verified: the source was opened and the finding is there · [V, auto] every number of the finding was found in the downloaded source text by a script (context not read) · [U] sourced, content not verified (\"no match\", \"partial match\", \"source did not open\" give the reason) · [S] secondary only · [C] sources conflict. \"(self-claim)\": the source speaks about itself; not an independent measurement.",
               method="{tool} collected the sources; every run used the same constitution and task card. The sources were downloaded by script and the numbers of every finding were searched in them; the findings behind the summary were also checked by hand.",
               m_runs="Runs: {runs}; questions: {qs}", m_cov="Coverage: {cov}",
               m_src="Sources: {n}; downloaded {ok}, thin text (JavaScript page) {thin}, did not open {err}",
               m_tags="Tagged findings: {n}; {tags}", source_of="source",
               labels=[(r"\[NOT FOUND\]", "not found"), (r"\[NOT ACCESSIBLE\]", "(source did not open)"),
                       (r"\[NOT PUBLIC\]", "(not public)"), (r"\[OUT OF RUN SCOPE\]", "(out of scope)"),
                       (r"\[SELF-CLAIM\]", "(self-claim)"), (r"\[SYNTHESIS\]", "(synthesis)"),
                       (r"\[ARCHIVE[^\]]*\]", "(archive)"), (r"\[OTHER CONTEXT\]", "(other context)"),
                       (r"\[REQUIRES EXTERNAL EXECUTION\]", "(needs outside work)"),
                       (r"\[CROSS-MODULE EVIDENCE:\s*(Q\d+)\s*\]", r"(see \1)")],
               details=("**Details:**", "### Details")),
}[LANG]
TYPES = PLAN.get("type_names", {})
RUN_NOTE = PLAN.get("run_notes", {})
CITE = re.compile(r"(?:\[\s*S\d+(?:[^\]\n]{0,300})\]\s*)+")
FOOT = re.compile(r"\[\^\d+(?:_\d+)?\]")
NUM = re.compile(r"(?<![\w])([$€£]?)(\d+(?:[.,]\d+)*)(\s?%|x\b|X\b)?")
URLRE = re.compile(r"https?://[^\s|)\]>]+")
LETTER = {"D": "V", "K": "U", "İ": "S", "Ç": "C", "Y": "W", "V": "V", "U": "U", "S": "S", "C": "C", "W": "W"}


def tag(key, extra=""):
    return T[key] + (f", {extra}" if extra else "")


IDX = {}
if (DL / "_index.tsv").exists():
    for line in (DL / "_index.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        n, u, s, *_ = line.split("\t") + ["", ""]
        IDX[u] = (n, s)
TEXT = {}


def src_text(url):
    if url not in TEXT:
        n, _ = IDX.get(url, ("", "error"))
        p = DL / f"{n}.txt"
        TEXT[url] = p.read_text(encoding="utf-8", errors="replace").lower() if n and p.exists() else None
    return TEXT[url]


MANUAL = []
if (REP / "_manual_checks.tsv").exists():
    for line in (REP / "_manual_checks.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            u, t, g, *note = line.split("\t") + ["", ""]
            head, _, rest = g.strip().partition(",")
            MANUAL.append((u.strip(), t.strip(), tag(LETTER.get(head.strip(), "U"), rest.strip()), note[0].strip()))


def variants(num):
    v = {num, num.replace(".", ""), num.replace(",", "")}
    if "," in num and "." not in num:
        v.add(num.replace(",", "."))
    if "." in num and "," not in num:
        v.add(num.replace(".", ","))
    if "," in num and "." in num:
        v.add(num.replace(".", "#").replace(",", ".").replace("#", ","))
    return {x for x in v if x}


def numbers(seg):
    out = []
    for m in NUM.finditer(seg):
        cur, n, suf = m.group(1), m.group(2), (m.group(3) or "").strip()
        if re.fullmatch(r"(19|20)\d\d", n) or (len(re.sub(r"\D", "", n)) < 2 and not cur and not suf):
            continue
        out.append(n)
    return out


def found(n, text):
    return any(re.search(r"(?<![\d.,])" + re.escape(v) + r"(?![.,]?\d)", text) for v in variants(n))


def judge(seg, urls):
    for u in urls:
        for mu, mt, mg, note in MANUAL:
            if mu == u and (mt == "*" or mt.lower() in seg.lower()):
                return mg, [], "manual" + (": " + note if note else "")
    if "[CONFLICT]" in seg:
        return tag("C"), [], "conflict"
    if "[SECONDARY ONLY]" in seg:
        return tag("S"), [], "secondary"
    if not urls:
        return tag("U"), [], "no url"
    texts = [t for t in (src_text(u) for u in urls) if t]
    if not texts:
        return tag("U", T["noopen"]), [], "not downloaded"
    nums = numbers(re.sub(r"\((?:bkz\.|see) Q\d+\)|\bQ\d{2,3}\b|\bS\d+\b", "", seg))
    if not nums:
        return tag("U"), [], "no numbers"
    miss = [n for n in nums if not found(n, "\n".join(texts))]
    if not miss:
        return tag("V", T["auto"]), [], "numbers found"
    return (tag("U", T["partial"]) if len(miss) < len(nums) else tag("U", T["nomatch"])), miss, "numbers missing"


def scodes(s):
    out = []
    for a, b in re.findall(r"\bS(\d+)(?:\s*[-–]\s*S?(\d+))?", s):
        out += [f"S{i}" for i in range(int(a), int(b) + 1)] if b and 0 <= int(b) - int(a) < 40 else [f"S{a}"]
    return out


def clean(t):
    t = FOOT.sub("", t).replace("\\&", "&").replace("\\$", "$").replace("\\_", "_")
    for a, b in T["labels"]:
        t = re.sub(a, b, t)
    t = re.sub(r"\[(?:SECONDARY ONLY|CONFLICT)\]", "", t)
    for k, v in TYPES.items():
        t = re.sub(rf"\b{re.escape(k)}\b", v, t)
    for d in T["details"]:
        t = t.replace(d, T["findings"])
    return re.sub(r"[ \t]+([.,;:])", r"\1", re.sub(r"[ \t]{2,}", " ", t))


def section_sources(rows):
    m = {}
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        u = URLRE.search(r)
        if cells and re.fullmatch(r"S\d+", cells[0]) and u:
            m[cells[0]] = {"url": u.group(0).rstrip(".,;"), "cells": cells}
    return m


LOG, TAGS, BAD = [], Counter(), []


def tag_text(text, smap, q, stem, qsrc):
    def ref(codes):
        nums = []
        for c in codes:
            s = smap.get(c)
            if s:
                if s["url"] not in qsrc:
                    qsrc[s["url"]] = (len(qsrc) + 1, s["cells"])
                n = str(qsrc[s["url"]][0])
                if n not in nums:
                    nums.append(n)
        return nums

    def record(seg, codes):
        urls = [smap[c]["url"] for c in codes if c in smap]
        tg, miss, why = judge(seg, urls)
        LOG.append((q, stem, tg, " ".join(miss), " ".join(urls), re.sub(r"\s+", " ", seg.strip())[:160]))
        TAGS[tg.split(",")[0]] += 1
        if tg.split(",")[0] == T["W"]:
            BAD.append((q, seg.strip(), urls, why))
        nums = ref(codes)
        return f"[{tg}]" + (f" ({T['src']} {', '.join(nums)})" if nums else "")

    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("|") and re.search(r"\bS\d+\b", line) and not re.match(r"^\s*\|\s*:?-", line):
            mark = record(line, scodes(" ".join(re.findall(r"\bS\d+(?:\s*[-–]\s*S?\d+)?", line))))
            line = re.sub(r"(?:\[?\s*S\d+(?:\s*[,;]\s*S?\d+)*\s*\]?\s*)+(?=\|\s*$)", mark + " ", line)
            line = re.sub(r"\bS\d+(?:\s*,\s*S\d+)*\b", "", CITE.sub("", line))
            out.append(line)
            continue
        pos, buf = 0, []
        for m in CITE.finditer(line):
            buf.append(line[pos:m.start()].rstrip() + " " + record(line[pos:m.start()], scodes(m.group(0))) + " ")
            pos = m.end()
        buf.append(line[pos:])
        out.append("".join(buf).rstrip())
    return "\n".join(out)


def parse_evidence(q):
    text = (EV / f"{q}.md").read_text(encoding="utf-8")
    secs, cross = [], []
    for p in re.split(r"^## (?=\d{3}_|Cross-module)", text, flags=re.M)[1:]:
        if p.startswith("Cross-module"):
            cross = p.splitlines()[1:]
            continue
        head, _, body = p.partition("\n")
        body, _, src = body.partition("\nSources:\n")
        secs.append((head.split(" ")[0], body.strip(), src.splitlines()))
    return secs, cross


def question_block(q):
    _, short, full = PLAN["questions"][q]
    secs, cross = parse_evidence(q)
    L = [f"### {q}. {short}", "", f"**{T['question']}:** {full}", ""]
    qsrc, nf = {}, 0
    for stem, body, rows in secs:
        smap = section_sources(rows)
        body = re.sub(r"^[#*\s]*Q\d+\.\s[^\n]*\n", "", body.strip() + "\n", count=1)
        body = re.sub(r"^#{1,3} ", "#### ", body, flags=re.M)
        nf += len(re.findall(r"\[NOT FOUND\]", body))
        body = tag_text(body, smap, q, stem, qsrc)
        if len(secs) > 1 or stem in RUN_NOTE:
            L += [f"#### {T['run']} {stem}" + (f" ({RUN_NOTE[stem]})" if stem in RUN_NOTE else ""), ""]
        L += [clean(body).strip(), ""]
    if cross:
        L += [f"**{T['cross']}:**", ""] + [clean(CITE.sub("", l)) for l in cross if l.startswith("- ")] + [""]
    if not secs and not cross:
        L += [T["noev"], ""]
    L += [f"**{T['notfound']}:** " + (T["nf_some"].format(n=nf) if nf else T["none"]), "", f"**{T['sources']}:**", ""]
    for url, (n, cells) in sorted(qsrc.items(), key=lambda kv: kv[1][0]):
        c = [clean(x).strip() for x in cells] + [""] * 8
        L.append(f"{n}. {c[2]} — {c[3]}, {c[4]} ({TYPES.get(c[6], c[6])}). {url}")
    return L + [""]


def main():
    by_mod = {}
    for q, (mod, *_r) in PLAN["questions"].items():
        by_mod.setdefault(mod, []).append(q)
    body = []
    for mod, name in PLAN["modules"].items():
        body += [f"## {mod}. {name}", ""]
        for q in sorted(by_mod.get(mod, []), key=lambda x: int(x[1:])):
            body += question_block(q)
    runs = json.loads((KIT / "runs.json").read_text(encoding="utf-8"))
    tool = DOC.get("tool") or PLAN.get("tool") or "the search tool"
    date = DOC.get("date", "")
    name = PLAN.get("output", {}).get("file_name") or re.sub(r"\W+", "_", PLAN["project"])
    cs = KIT / "coverage_summary.md"
    cov = cs.read_text(encoding="utf-8").splitlines()[2] if cs.exists() else ""
    st = Counter(s for _, s in IDX.values())
    total = sum(TAGS.values())
    tags = ", ".join(f"[{k}] {v}" for k, v in TAGS.most_common())
    extra = PLAN.get("output", {}).get("intro", "")
    intro = [f"# {PLAN['project']} — {T['full']}", ""] + ([extra, ""] if extra else []) + [
             T["base"].format(tool=tool, runs=len(runs), qs=len(PLAN["questions"]), src=len(IDX), date=date), "",
             T["notsum"].format(sum=name + T["sumsuf"]), "", T["legend"], ""]
    app = [f"## {T['appA']}", "", T["method"].format(tool=tool), "",
           "- " + T["m_runs"].format(runs=len(runs), qs=len(PLAN["questions"])), "- " + T["m_cov"].format(cov=cov),
           "- " + T["m_src"].format(n=len(IDX), ok=st.get("ok", 0), thin=st.get("thin", 0), err=st.get("error", 0)),
           "- " + T["m_tags"].format(n=total, tags=tags), "", f"## {T['appB']}", ""]
    app += [f"- {q}: {clean(CITE.sub('', s))[:400]} — {T['source_of']}: {', '.join(u)}; {w}" for q, s, u, w in BAD] or [T["nothing"]]
    app += ["", f"## {T['appC']}", ""] + [f"- {u}" for u, (_, s) in IDX.items() if s == "ok"]
    hand = sorted({u for u, *_ in MANUAL})
    if hand:
        app += ["", T["hand"], ""] + [f"- {u}" for u in hand]
    oq = EV / "_open_questions.md"
    if oq.exists():
        t = re.sub(r"^# .*\n", "", clean(CITE.sub("", oq.read_text(encoding="utf-8"))))
        app += ["", f"## {T['appD']}", "", re.sub(r"^## ", f"#### {T['run']} ", t, flags=re.M).strip(), ""]
    (REP / "FULL_RESEARCH.md").write_text("\n".join(intro + body + app) + "\n", encoding="utf-8")
    (REP / "_auto_verify.tsv").write_text("q\trun\ttag\tmissing\turls\tfinding\n" + "\n".join(
        "\t".join(x.replace("\t", " ") for x in r) for r in LOG) + "\n", encoding="utf-8")
    byq = Counter((r[0], r[2].split(",")[0]) for r in LOG)
    keys = [T[k] for k in ("V", "U", "S", "C", "W")]
    s = [f"# Auto pre-verification", "", f"{total} findings: {tags}", "",
         "| Q | " + " | ".join(keys) + " |", "|---" * (len(keys) + 1) + "|"]
    s += [f"| {q} | " + " | ".join(str(byq.get((q, k), 0)) for k in keys) + " |" for q in PLAN["questions"]]
    (REP / "_auto_verify_summary.md").write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"FULL_RESEARCH.md written; {total} findings: {tags}")


if __name__ == "__main__":
    main()
