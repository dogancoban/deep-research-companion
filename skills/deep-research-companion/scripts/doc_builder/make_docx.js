// Deep Research Companion: build a styled DOCX from a final text
// (report/FULL_RESEARCH.md, report/SUMMARY.md or report/VERIFICATION.md):
// cover, "About this document", table of contents, chapters, tables, optional glossary and index.
// Usage: node make_docx.js <text.md> <out_raw.docx> <document.json> <full|summary|check> [index.json]
// Project-specific values (language, subtitle, date, glossary, index terms) come from document.json.
const fs = require("fs");
const d = require("docx");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, TableOfContents, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, Header, Footer, PageNumber, NumberFormat,
  LevelFormat, ExternalHyperlink, VerticalAlign, TableLayoutType,
} = d;

const [src, out, cfgFile, kind, idxFile] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(cfgFile, "utf-8"));
if (JSON.stringify(cfg).includes("{{")) { console.error("document.json still has unfilled {{...}} fields."); process.exit(1); }

const LABELS = {
  en: {
    kinds: { full: ["FULL RESEARCH", "Full research"], summary: ["SUMMARY", "Summary"], check: ["VERIFICATION REPORT", "Verification"] },
    about: "About this document", toc: "Contents", glossary: "Glossary", index: "Index", version: "Version",
    indexNote: "Pages where each term appears. Appendices, the glossary and source lists are not indexed.",
    ends: (items) => `The document ends with ${items.join(" and ")}.`, items: { glossary: "a glossary", index: "an index" },
    months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    tool: "an AI search tool", checkTool: "an AI tool", assistant: "an AI assistant",
    noteResearch: (t, a) => `Prepared with Deep Research Companion: sources were collected with ${t}, the text was written by ${a}. Each finding carries a tag showing whether it was verified.`,
    noteCheck: (t, a) => `Prepared with Deep Research Companion: the claims in an answer from ${t} were checked against their sources by ${a}. Each claim carries a tag showing the result.`,
    pending: "(index will be computed)",
  },
  tr: {
    kinds: { full: ["TAM ARAŞTIRMA", "Tam araştırma"], summary: ["ÖZET", "Özet"], check: ["DOĞRULAMA RAPORU", "Doğrulama"] },
    about: "Bu belge hakkında", toc: "İçindekiler", glossary: "Terimler sözlüğü", index: "Dizin", version: "Sürüm",
    indexNote: "Terimlerin geçtiği sayfalar. Ekler, sözlük ve kaynak listeleri dizine alınmamıştır.",
    ends: (items) => `Sonda ${items.join(" ve ")} vardır.`, items: { glossary: "bir terimler sözlüğü", index: "bir konu dizini" },
    months: ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    tool: "bir arama aracı", checkTool: "bir yapay zekâ aracının", assistant: "bir yapay zekâ asistanı",
    noteResearch: (t, a) => `Kanıt Hattı (Deep Research Companion) yöntemiyle hazırlanmıştır: kaynaklar ${t} ile toplandı, metni ${a} yazdı. Her bilginin doğrulama durumu yanındaki etiketle gösterilir.`,
    noteCheck: (t, a) => `Kanıt Hattı (Deep Research Companion) yöntemiyle hazırlanmıştır: ${t} cevabındaki iddialar ${a} tarafından kaynaklarından kontrol edildi. Her iddianın sonucu yanındaki etiketle gösterilir.`,
    pending: "(dizin hesaplanacak)",
  },
};
const T = LABELS[cfg.lang] || LABELS.en;
const KIND = T.kinds[kind];
if (!KIND) { console.error("Kind must be 'full', 'summary' or 'check'."); process.exit(1); }
const INDEX = idxFile && fs.existsSync(idxFile) ? JSON.parse(fs.readFileSync(idxFile, "utf-8")) : [];
const WITH_INDEX = kind === "full" && (cfg.index || []).length > 0;
const GLOSSARY = cfg.glossary || [];
const DATE = cfg.date || `${T.months[new Date().getMonth()]} ${new Date().getFullYear()}`;
const md = fs.readFileSync(src, "utf-8").split("\n");

// ---------- look ----------
const C = { ink: "1F2A30", teal: "1F4E5F", accent: "2E7D6B", pale: "E8F1F2", zebra: "F4F7F8", grid: "C9D3D8", gray: "6B7780",
  verified: "2E7D32", sourced: "1565C0", secondary: "C25E00", conflict: "6A1B9A", wrong: "C62828", notfound: "455A64" };
const BODY = "Georgia", SANS = "Arial";
const PAGE_W = 11906, PAGE_H = 16838, MARG_LR = 1304, MARG_TB = 1418;
const CONTENT_W = PAGE_W - 2 * MARG_LR;

// ---------- inline markdown ----------
// Evidence tags, English and Turkish sets: [V]/[D] verified, [U]/[K] sourced, [S]/[İ] secondary, [C]/[Ç] conflict,
// [W]/[Y] wrong, [N]/[B] not found; extras like [V, 24.09.2026] or [V and U].
const TAG = { V: C.verified, D: C.verified, U: C.sourced, K: C.sourced, S: C.secondary, "İ": C.secondary,
  C: C.conflict, "Ç": C.conflict, W: C.wrong, Y: C.wrong, N: C.notfound, B: C.notfound };
const TAG_RE = "\\[(?:V|U|S|C|W|N|D|K|İ|Ç|Y|B)(?:(?:, | and | ve )[^\\]]*)?\\]";
function inline(text, base = {}) {
  const runs = [];
  const re = new RegExp(`(\\*\\*[^*]+\\*\\*)|(\\[[^\\]]+\\]\\([^)]+\\))|(\`[^\`]+\`)|(${TAG_RE})`, "g");
  let last = 0, m;
  const push = (t, o = {}) => t && runs.push(new TextRun({ text: t, ...base, ...o }));
  const tag = (t) => push(t, { bold: true, color: TAG[t[1]] || C.sourced, font: SANS, size: (base.size || 21) - 3 });
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (m[1]) {
      // tags inside bold keep their color
      tok.slice(2, -2).split(new RegExp(`(${TAG_RE})`)).forEach((p) => {
        if (!p) return;
        if (new RegExp(`^${TAG_RE}$`).test(p)) tag(p); else push(p, { bold: true });
      });
    } else if (m[2]) {
      const [, label, url] = tok.match(/\[([^\]]+)\]\(([^)]+)\)/);
      runs.push(new ExternalHyperlink({ link: url, children: [new TextRun({ text: label, ...base, color: C.sourced, underline: {} })] }));
    } else if (m[3]) {
      push(tok.slice(1, -1), { font: "Courier New", size: (base.size || 21) - 3, color: C.teal });
    } else {
      tag(tok);
    }
    last = re.lastIndex;
  }
  push(text.slice(last));
  return runs;
}

// ---------- tables ----------
const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: C.grid };
function splitRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((s) => s.trim());
}
function colWidths(rows) {
  const n = rows[0].length;
  const clean = (t) => (t || "").replace(/\*\*|\[([^\]]*)\]\([^)]*\)/g, "$1");
  const mins = [], weights = [];
  for (let c = 0; c < n; c++) {
    const cells = rows.map((r) => clean(r[c]));
    const lens = cells.map((t) => t.length);
    const mx = Math.max(...lens), avg = lens.reduce((a, b) => a + b, 0) / lens.length;
    const longest = Math.max(...cells.flatMap((t) => t.split(/[\s/]+/)).map((w) => w.length), 1);
    const tiny = mx <= 3;
    mins.push(tiny ? 480 : Math.max(700, longest * 105 + 240));
    weights.push(tiny ? 0 : Math.max(4, Math.min(120, 0.4 * mx + 0.6 * avg)));
  }
  let px = mins.slice();
  const sumMin = px.reduce((a, b) => a + b, 0);
  if (sumMin >= CONTENT_W) {
    px = px.map((x) => Math.floor((x * CONTENT_W) / sumMin));
  } else {
    const rest = CONTENT_W - sumMin, wsum = weights.reduce((a, b) => a + b, 0) || 1;
    px = px.map((x, i) => x + Math.floor((rest * weights[i]) / wsum));
  }
  px[px.length - 1] += CONTENT_W - px.reduce((a, b) => a + b, 0);
  return px;
}
function table(lines) {
  const rows = lines.filter((l) => !/^\s*\|\s*:?-{2,}/.test(l)).map(splitRow);
  const n = Math.max(...rows.map((r) => r.length));
  rows.forEach((r) => { while (r.length < n) r.push(""); });
  const widths = colWidths(rows);
  const small = n >= 5 ? 16 : 17;
  const trows = rows.map((r, i) => {
    const head = i === 0;
    const section = !head && r.slice(1).every((x) => !x) && /^\*\*/.test(r[0]);
    if (section) {
      return new TableRow({ cantSplit: true, children: [new TableCell({
        columnSpan: r.length, width: { size: CONTENT_W, type: WidthType.DXA },
        borders: { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder },
        shading: { type: ShadingType.CLEAR, fill: C.pale, color: "auto" }, margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ keepNext: true, spacing: { before: 0, after: 0 }, children: [new TextRun({ text: r[0].replace(/\*\*/g, ""), bold: true, font: SANS, size: small, color: C.teal })] })],
      })] });
    }
    return new TableRow({
      tableHeader: head, cantSplit: true,
      children: r.map((cell, c) => new TableCell({
        width: { size: widths[c], type: WidthType.DXA },
        borders: { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder },
        shading: head ? { type: ShadingType.CLEAR, fill: C.teal, color: "auto" }
          : i % 2 === 0 ? { type: ShadingType.CLEAR, fill: C.zebra, color: "auto" } : undefined,
        margins: { top: 70, bottom: 70, left: 100, right: 100 },
        verticalAlign: VerticalAlign.TOP,
        children: [new Paragraph({
          spacing: { before: 0, after: 0, line: 252 },
          children: head ? [new TextRun({ text: cell.replace(/\*\*/g, ""), bold: true, color: "FFFFFF", font: SANS, size: small })]
            : inline(cell, { font: SANS, size: small }),
        })],
      })),
    });
  });
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: trows }),
    new Paragraph({ spacing: { before: 0, after: 120 }, children: [] })];
}

// ---------- parse markdown into blocks ----------
let numInstance = 0;
function para(text, opts = {}) {
  return new Paragraph({ ...opts, children: inline(text, opts.runBase || {}) });
}
function parse(lines) {
  const out = [];
  let i = 0, inNumbered = false;
  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, "");
    if (!line.trim() || /^---\s*$/.test(line)) { if (!line.trim() && !/^\s*[-\d]/.test(lines[i + 1] || "")) inNumbered = false; i++; continue; }
    if (/^\s*\|/.test(line)) {
      const block = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) block.push(lines[i++]);
      out.push(...table(block));
      continue;
    }
    let m;
    if ((m = line.match(/^#{1,2} (.*)/))) { out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(m[1])] })); i++; continue; }
    if ((m = line.match(/^### (.*)/))) { out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(m[1])] })); i++; continue; }
    if ((m = line.match(/^#{4,} (.*)/))) { out.push(para(`**${m[1]}**`, { keepNext: true, spacing: { before: 200, after: 80 } })); i++; continue; }
    if ((m = line.match(/^(\s*)(\d+)\. (.*)/)) && m[1].length === 0) {
      if (!inNumbered) { numInstance++; inNumbered = true; }
      out.push(para(m[3], { numbering: { reference: "num", level: 0, instance: numInstance }, spacing: { after: 60 } }));
      i++; continue;
    }
    if ((m = line.match(/^(\s*)[-*] (.*)/))) {
      const ind = m[1].length;
      const level = ind === 0 ? 0 : ind <= 3 ? 1 : 2;
      const lvl = inNumbered && ind > 0 ? Math.max(0, level - 1) : level;
      out.push(para(m[2], { numbering: { reference: inNumbered && ind > 0 ? "bulletInNum" : "bullet", level: lvl }, spacing: { after: 50 } }));
      i++; continue;
    }
    inNumbered = false;
    const label = /^\*\*[^*]+:\*\*|^\*\*[^*]+\*\*[^.]*:$/.test(line.trim());
    out.push(para(line.trim(), label ? { keepNext: true, spacing: { before: 220, after: 100 } } : { alignment: AlignmentType.JUSTIFIED, spacing: { after: 140 } }));
    i++;
  }
  return out;
}

// ---------- split the text: "# Title", front matter, chapters ("## ") ----------
const firstH2 = md.findIndex((l) => l.startsWith("## "));
if (!md[0].startsWith("# ") || firstH2 < 0) { console.error(`${src}: the first line must be "# Title" and there must be at least one "## " chapter.`); process.exit(1); }
const title = md[0].replace(/^# /, "").trim();
const about = md.slice(1, firstH2);
const body = md.slice(firstH2);

// ---------- document pieces ----------
function coverSection() {
  const sp = (n) => new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "", size: n })] });
  const note = cfg.cover_note || (kind === "check" ? T.noteCheck(cfg.tool || T.checkTool, cfg.assistant || T.assistant) : T.noteResearch(cfg.tool || T.tool, cfg.assistant || T.assistant));
  return {
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARG_TB, bottom: MARG_TB, left: MARG_LR, right: MARG_LR } } },
    children: [
      sp(600), sp(600), sp(600),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: KIND[0], font: SANS, size: 22, bold: true, color: C.accent, characterSpacing: 60 })] }),
      new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: C.teal, space: 12 } }, spacing: { after: 360 },
        children: [new TextRun({ text: title, font: SANS, size: 60, bold: true, color: C.teal })] }),
      ...(cfg.subtitle ? [new Paragraph({ spacing: { after: 200, line: 320 }, children: [new TextRun({ text: cfg.subtitle, font: BODY, size: 30, color: C.ink })] })] : []),
      ...(cfg.topics ? [new Paragraph({ spacing: { after: 1400, line: 300 }, children: [new TextRun({ text: cfg.topics, font: BODY, size: 22, italics: true, color: C.gray })] })] : []),
      sp(600), sp(600), sp(600), sp(600), sp(600), sp(600),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: `${DATE} · ${T.version} ${cfg.version || "1.0"}`, font: SANS, size: 20, bold: true, color: C.ink })] }),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: note, font: SANS, size: 17, color: C.gray })] }),
    ],
  };
}

const HEADER_TEXT = `${title} · ${KIND[1]} · ${DATE}`;
function header() {
  return new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.grid, space: 4 } },
    children: [new TextRun({ text: HEADER_TEXT, font: SANS, size: 15, color: C.gray })] })] });
}
function footer() {
  return new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], font: SANS, size: 17, color: C.gray })] })] });
}
const pageProps = (fmt, start) => ({
  page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARG_TB, bottom: MARG_TB, left: MARG_LR, right: MARG_LR, header: 700, footer: 700 },
    pageNumbers: { start, formatType: fmt } },
});

function frontSection() {
  const extras = [GLOSSARY.length && T.items.glossary, WITH_INDEX && T.items.index].filter(Boolean);
  const children = [
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(T.about)] }),
    ...parse(about),
    ...(extras.length ? [new Paragraph({ spacing: { before: 200, after: 140 }, alignment: AlignmentType.JUSTIFIED, children: inline(T.ends(extras)) })] : []),
    new Paragraph({ pageBreakBefore: true, spacing: { after: 300 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.teal, space: 8 } },
      children: [new TextRun({ text: T.toc, font: SANS, size: 36, bold: true, color: C.teal })] }),
    new TableOfContents(T.toc, { hyperlink: true, headingStyleRange: "1-2" }),
  ];
  return { properties: pageProps(NumberFormat.LOWER_ROMAN, 1), headers: { default: header() }, footers: { default: footer() }, children };
}

function bodySection() {
  const glossary = GLOSSARY.length ? [
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(T.glossary)] }),
    ...GLOSSARY.map(([t, def]) => new Paragraph({ spacing: { after: 100 }, indent: { left: 360, hanging: 360 },
      children: [new TextRun({ text: t, bold: true, font: SANS, size: 19, color: C.teal }), new TextRun({ text: " — " + def, font: BODY, size: 20 })] })),
  ] : [];
  const indexHead = WITH_INDEX ? [
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(T.index)] }),
    new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: T.indexNote, italics: true, size: 18, color: C.gray })] }),
  ] : [];
  return { properties: pageProps(NumberFormat.DECIMAL, 1), headers: { default: header() }, footers: { default: footer() },
    children: [...parse(body), ...glossary, ...indexHead] };
}

function indexSection() {
  const kids = [];
  for (const grp of INDEX) {
    kids.push(new Paragraph({ keepNext: true, spacing: { before: 160, after: 60 }, children: [new TextRun({ text: grp.letter, font: SANS, size: 22, bold: true, color: C.teal })] }));
    for (const e of grp.entries) kids.push(new Paragraph({ spacing: { after: 40 }, indent: { left: 240, hanging: 240 },
      children: [new TextRun({ text: e.term, font: BODY, size: 19 }), new TextRun({ text: ", " + e.pages, font: SANS, size: 17, color: C.gray })] }));
  }
  if (!kids.length) kids.push(new Paragraph({ children: [new TextRun(T.pending)] }));
  return { properties: { type: d.SectionType.CONTINUOUS, column: { count: 2, space: 567 },
    page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARG_TB, bottom: MARG_TB, left: MARG_LR, right: MARG_LR, header: 700, footer: 700 } } },
    headers: { default: header() }, footers: { default: footer() }, children: kids };
}

const bulletLevels = (a, b, c) => [
  { level: 0, format: LevelFormat.BULLET, text: a, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } }, run: { color: C.accent } } },
  { level: 1, format: LevelFormat.BULLET, text: b, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 760, hanging: 260 } }, run: { color: C.accent } } },
  { level: 2, format: LevelFormat.BULLET, text: c, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1160, hanging: 260 } }, run: { color: C.accent } } },
];

const doc = new Document({
  creator: "Deep Research Companion", title: `${title} — ${KIND[1]}`, description: `${title}: ${KIND[1].toLowerCase()}`,
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: BODY, size: 21, color: C.ink }, paragraph: { spacing: { line: 288 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS, size: 36, bold: true, color: C.teal },
        paragraph: { pageBreakBefore: true, outlineLevel: 0, spacing: { before: 0, after: 300 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.teal, space: 8 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS, size: 26, bold: true, color: C.accent },
        paragraph: { outlineLevel: 1, keepNext: true, spacing: { before: 320, after: 140 } } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal", run: { font: SANS, size: 21, bold: true, color: C.teal }, paragraph: { spacing: { before: 140, after: 40 } } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal", run: { font: BODY, size: 20 }, paragraph: { indent: { left: 360 }, spacing: { before: 0, after: 30 } } },
    ],
  },
  numbering: { config: [
    { reference: "bullet", levels: bulletLevels("•", "–", "·") },
    { reference: "bulletInNum", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 760, hanging: 260 } }, run: { color: C.accent } } },
      { level: 1, format: LevelFormat.BULLET, text: "·", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1160, hanging: 260 } }, run: { color: C.accent } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 400, hanging: 400 } }, run: { bold: true, color: C.teal, font: SANS } } }] },
  ] },
  sections: [coverSection(), frontSection(), bodySection(), ...(WITH_INDEX ? [indexSection()] : [])],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("written:", out, b.length, "bytes"); });
