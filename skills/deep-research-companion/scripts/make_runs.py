#!/usr/bin/env python3
"""Deep Research Companion: build run files, run index, checklist and coverage list from kit/plan.json.

Usage (from anywhere):  python3 <project>/kit/make_runs.py
Reads:   kit/plan.json, kit/<constitution_file>
Writes:  runs/NNN_<ID>_<MODE>.txt, kit/runs.json, CHECKLIST.md, COVERAGE.md
Re-running rewrites all run files; ticks in CHECKLIST.md and statuses in COVERAGE.md are kept.
The card scaffolding exists in English and Turkish (plan.json "lang": "en" or "tr"); other languages use English.
"""
import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent

L = {
    "tr": {
        "intro": "Önce anayasa, sonra görev kartı gelir. İkisine de uy.",
        "card": "GÖREV KARTI",
        "qs_of_run": "Bu koşunun soruları",
        "goal_h": "1. AMAÇ",
        "goal": "Aşağıdaki soruları yayımlanmış kaynaklara dayanarak cevapla; bulguları, sayıları ve tarihleri kaynaktaki gibi kaydet. Senaryo için anayasanın senaryo bölümüne bak.",
        "qs_h": "2. SORULAR",
        "record": "Her soru için kaydet: bulgunun kendisi; kimin söylediği (kaynak ve kaynaktaki yeri); sayılar (birim, tarih, kapsam); koşullar ve istisnalar; senaryodaki durumlara göre farklar.",
        "note": "Bu kart için ek talimat: ",
        "links_h": "3. BAŞLANGIÇ BAĞLANTILARI (yalnızca arama için; açıp okumadan kaynak gösterme)",
        "none": "- yok",
        "skel_h": "4. ÇIKTI İSKELETİ (aynen kullan; çıktın RUN END satırıyla biter)",
        "header_h": "BAŞLIK",
        "short": "Kısa cevap: 1-3 cümle, kaynak kodlu. Bulunamadıysa [NOT FOUND] (aramalar: ...).",
        "details": "Ayrıntılar: kaydedilecek her şey (sayılar, tarihler, koşullar, adlar, örnekler); her cümle kaynak kodlu.",
        "level": "Kaynak düzeyi: bu cevabı destekleyen en yüksek kaynak türü; yalnızca ikincil kaynak varsa [SECONDARY ONLY].",
        "conflict": "Çelişkiler: [CONFLICT] ile ayrıntı ya da \"yok\".",
        "x_h": "X. KAYNAKLARIN CEVAPLAMADIĞI NOKTALAR",
        "x": "Kaynakların cevaplamadığı noktalar; her biri [REQUIRES EXTERNAL EXECUTION] ile ve nasıl cevaplanabileceği (kime sorulacağı, neyin ölçüleceği ya da kiminle görüşüleceği) yazılarak. Tavsiye yok.",
        "y_h": "Y. ÇAPRAZ KANIT",
        "y": "Yalnızca bu koşunun soruları dışındaki bir soruya ait bulgular; satır başına bir bulgu, [CROSS-MODULE EVIDENCE: <soru kodu>] etiketi ve kaynak koduyla; yoksa \"yok\".",
        "z_h": "Z. KAYNAK TABLOSU (anayasadaki çıktı bölümüne göre)",
        "sc_h": "ÖZ KONTROL",
        "sc": ["| Kontrol | Cevap |",
               "| Cevaplanan soru / boş kalan soru | n / n |",
               "| Birincil kaynakla desteklenen soru sayısı | n |",
               "| [SECONDARY ONLY] ya da [CONFLICT] taşıyan soru kodları | ... |",
               "| Kaynaksız bulgu cümlesi var mı | evet / hayır |",
               "| Tavsiye ya da yargı var mı | evet / hayır |",
               "| İskeletin tüm başlıkları yazıldı mı | evet / hayır |"],
        "rem_h": "5. HATIRLATMA: EN ÖNEMLİ BEŞ KURAL (bu bölümü çıktına yazma)",
        "rem": "1) Uydurma yok: bulgu, sayı ve tarih kaynaktaki gibi, birimi ve tarihiyle. 2) Önce birincil kaynak; yalnızca ikincil kaynak varsa [SECONDARY ONLY]. 3) Her bulgu cümlesi kaynak kodlu. 4) İskelete aynen uy; tavsiye, yargı, giriş ve sonuç yok. 5) İstenen dilde metin, İngilizce etiketler, tam kaynak tablosu, bitiş satırı.",
        "ck_title": "# Kontrol listesi",
        "ck_note": "Biten koşuları `kit/name_outputs.py` işaretler.",
        "pilot": "  ← ÖNCE BU: çıktısını asistana ver, onaylayınca diğerlerine geç",
        "kp_title": "# Kapsam listesi",
        "kp_note": "Her soru bir ya da daha fazla koşuya bağlı. Durumları `kit/coverage.py` yazar: CEVAPLANDI · İKİNCİL (yalnızca ikincil kaynak) · ÇELİŞKİ · KISMİ (kısmen bulunamadı) · BOŞ.",
        "kp_cols": "| Soru | Konu | Koşu | Durum |",
    },
    "en": {
        "intro": "The constitution comes first, then the task card. Follow both.",
        "card": "TASK CARD",
        "qs_of_run": "Questions of this run",
        "goal_h": "1. GOAL",
        "goal": "Answer the questions below from published sources; record findings, numbers and dates exactly as the sources give them. See the scenario section of the constitution.",
        "qs_h": "2. QUESTIONS",
        "record": "For each question record: the finding itself; who states it (source and where in it); numbers (unit, date, scope); conditions and exceptions; differences between the scenario's cases.",
        "note": "Extra instruction for this card: ",
        "links_h": "3. STARTING LINKS (for searching only; never cite without opening and reading)",
        "none": "- none",
        "skel_h": "4. OUTPUT SKELETON (use exactly; your output ends with the RUN END line)",
        "header_h": "HEADER",
        "short": "Short answer: 1-3 sentences with source codes. If not found: [NOT FOUND] (queries: ...).",
        "details": "Details: everything to be recorded (numbers, dates, conditions, names, examples); every sentence with a source code.",
        "level": "Source level: the highest source type supporting this answer; if only secondary sources exist, [SECONDARY ONLY].",
        "conflict": "Conflicts: details with [CONFLICT], or \"none\".",
        "x_h": "X. POINTS THE SOURCES DID NOT ANSWER",
        "x": "Points the sources did not answer, each with [REQUIRES EXTERNAL EXECUTION] and how it could be answered (whom to ask, what to measure, whom to interview). No recommendations.",
        "y_h": "Y. CROSS-MODULE EVIDENCE",
        "y": "Only findings that belong to questions outside this run; one per line, with [CROSS-MODULE EVIDENCE: <question code>] and a source code; otherwise \"none\".",
        "z_h": "Z. SOURCE TABLE (as defined in the constitution's output section)",
        "sc_h": "SELF-CHECK",
        "sc": ["| Check | Answer |",
               "| Questions answered / empty | n / n |",
               "| Questions supported by primary sources | n |",
               "| Question codes carrying [SECONDARY ONLY] or [CONFLICT] | ... |",
               "| Any factual sentence without a source code | yes / no |",
               "| Any recommendation or judgment | yes / no |",
               "| All skeleton headings written | yes / no |"],
        "rem_h": "5. REMINDER: THE FIVE MOST IMPORTANT RULES (do not reproduce this section)",
        "rem": "1) No invention: findings, numbers and dates as published, with unit and date. 2) Primary sources first; if only secondary exists, [SECONDARY ONLY]. 3) Every factual sentence carries a source code. 4) Follow the skeleton exactly; no recommendations, judgments, introduction or conclusion. 5) Text in the requested language, English labels, full source table, end line.",
        "ck_title": "# Checklist",
        "ck_note": "`kit/name_outputs.py` ticks finished runs.",
        "pilot": "  ← FIRST: give its output to your assistant and wait for approval",
        "kp_title": "# Coverage list",
        "kp_note": "Each question is tied to one or more runs. `kit/coverage.py` writes the status: ANSWERED · SECONDARY · CONFLICT · PARTIAL · EMPTY.",
        "kp_cols": "| Question | Topic | Run | Status |",
    },
}


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def card(run, plan, const, t, lang):
    ver = f"{plan['code']} {plan['version']}"
    Q = plan["questions"]
    up = tr_upper if lang == "tr" else str.upper
    out = [f"RUN {run['id']}: {run['goal']}", t["intro"], "", const.rstrip(), "",
           f"=== {t['card']} {ver}: {run['scope']} ===", f"RUN-ID: {run['id']}",
           f"{t['qs_of_run']}: {', '.join(run['questions'])}", "", t["goal_h"], t["goal"], "", t["qs_h"]]
    out += [f"{q} {Q[q][2]}" for q in run["questions"]]
    out.append(plan.get("record_text") or t["record"])
    if run.get("note"):
        out += ["", t["note"] + run["note"]]
    out += ["", t["links_h"]]
    out += [f"- {u}" for u in run.get("links", [])] or [t["none"]]
    out += ["", t["skel_h"], "", t["header_h"],
            f"RUN-ID: {run['id']} | CARD: {ver} | CONSTITUTION: {ver} | Date: <today> | Scope: {run['scope']}", ""]
    for q in run["questions"]:
        out += [f"{q}. {up(Q[q][1])}", t["short"], t["details"], t["level"], t["conflict"], ""]
    out += [t["x_h"], t["x"], "", t["y_h"], t["y"], "", t["z_h"], "", t["sc_h"], *t["sc"], "",
            f"=== RUN END {run['id']} ===", "", t["rem_h"], t["rem"]]
    return "\n".join(out) + "\n"


def main():
    plan = json.loads((KIT / "plan.json").read_text(encoding="utf-8"))
    lang = plan.get("lang", "en") if plan.get("lang") in L else "en"
    t = L[lang]
    const = (KIT / plan["constitution_file"]).read_text(encoding="utf-8")
    if "{{" in const:
        raise SystemExit("The constitution still has unfilled {{...}} fields.")
    Q, runs = plan["questions"], plan["runs"]
    bad = [q for r in runs for q in r["questions"] if q not in Q]
    if bad:
        raise SystemExit(f"plan.json: undefined question(s) in runs: {bad}")
    runs_dir = ROOT / "runs"
    runs_dir.mkdir(exist_ok=True)
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "report").mkdir(exist_ok=True)
    for f in runs_dir.glob("*.txt"):
        f.unlink()
    index, q_to_run = [], {}
    for seq, run in enumerate(runs, 1):
        name = f"{seq:03d}_{run['id']}_{run['mode']}"
        (runs_dir / f"{name}.txt").write_text(card(run, plan, const, t, lang), encoding="utf-8")
        index.append({"seq": seq, "run_id": run["id"], "mode": run["mode"], "file": f"{name}.txt", "questions": run["questions"]})
        for q in run["questions"]:
            q_to_run.setdefault(q, []).append(f"{seq:03d}_{run['id']}")
    (KIT / "runs.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    orphan = sorted(set(Q) - set(q_to_run))
    if orphan:
        raise SystemExit(f"Question(s) not tied to any run: {orphan}")

    modes = plan.get("modes", {})
    ck = ROOT / "CHECKLIST.md"
    ticked = set(re.findall(r"- \[x\] (\d{3}_[A-Z0-9-]+)_", ck.read_text(encoding="utf-8"))) if ck.exists() else set()
    lines = [t["ck_title"], "", t["ck_note"], ""]
    for r in index:
        key = f"{r['seq']:03d}_{r['run_id']}"
        box = "x" if key in ticked else " "
        flag = t["pilot"] if r["run_id"] == plan.get("pilot") else ""
        lines.append(f"- [{box}] {key}_{r['mode']}  ({modes.get(r['mode'], r['mode'])}; {', '.join(r['questions'])}){flag}")
    ck.write_text("\n".join(lines) + "\n", encoding="utf-8")

    kp = ROOT / "COVERAGE.md"
    old = dict(re.findall(r"^\| (Q\d+) \|.*\| ([^|]*) \|$", kp.read_text(encoding="utf-8"), re.M)) if kp.exists() else {}
    lines = [t["kp_title"], "", t["kp_note"], ""]
    for mod, title in plan["modules"].items():
        lines += [f"## {mod} {title}", "", t["kp_cols"], "|---|---|---|---|"]
        for code, (m, short, _) in Q.items():
            if m == mod:
                lines.append(f"| {code} | {short} | {', '.join(q_to_run[code])} | {old.get(code, '–')} |")
        lines.append("")
    kp.write_text("\n".join(lines), encoding="utf-8")

    sizes = [(r["file"], len((runs_dir / r["file"]).read_text(encoding="utf-8"))) for r in index]
    big = max(sizes, key=lambda s: s[1])
    print(f"{len(index)} runs, {len(Q)} questions; largest file {big[0]} ({big[1]} characters)")
    if big[1] > 14000:
        print("WARNING: a run file exceeds 14,000 characters and may be cut off when pasted. Split its questions.")
    if plan.get("output", {}).get("format") not in ("docx", "pdf", "both"):
        print("NOTE: plan.json has no output.format. Ask the user for the document format (docx, pdf or both) and record it.")


if __name__ == "__main__":
    main()
