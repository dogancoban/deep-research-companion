#!/usr/bin/env bash
# Deep Research Companion: build the final documents in the chosen format (docx, pdf or both).
#
# Big research:    bash kit/doc_builder/build.sh [format]
#   report/FULL_RESEARCH.md and report/SUMMARY.md -> report/<Name>_Full_Research and report/<Name>_Summary
#   (Turkish documents: <Name>_Tam_Arastirma and <Name>_Ozet). Without a format, kit/plan.json > output.format is used.
# Single document: bash kit/doc_builder/build.sh <format> <text.md> <full|summary|check>
#   e.g. build.sh pdf VERIFICATION.md check -> report/<Name>_Verification.pdf (Turkish: _Dogrulama)
#
# Settings: report/document.json (copy of assets/document.json). Language: document.json > lang (en or tr).
# Name: plan.json > output.file_name, else document.json > file_name, else the project name.
# The table of contents is updated by a LibreOffice macro. With index terms, the full research is built twice:
# page numbers come from the first PDF, the second pass writes the final files.
# Needs: node, LibreOffice (soffice), poppler (pdftotext, pdfinfo).
set -e
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
CFG="$ROOT/report/document.json"
[ -f "$CFG" ] || { echo "report/document.json is missing: create it from the skill's assets/document.json."; exit 1; }
read_cfg() { python3 - "$ROOT/kit/plan.json" "$CFG" "$1" <<'PY'
import json, os, sys, unicodedata
plan = json.load(open(sys.argv[1], encoding="utf-8")) if os.path.exists(sys.argv[1]) else {}
cfg = json.load(open(sys.argv[2], encoding="utf-8")); output = plan.get("output", {})
what = sys.argv[3]
if what == "format":
    print(output.get("format", ""))
elif what == "lang":
    print("tr" if cfg.get("lang") == "tr" else "en")
elif what == "index":
    print(1 if cfg.get("index") else 0)
else:
    name = output.get("file_name") or cfg.get("file_name") or plan.get("project") or "Document"
    name = name.translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU", "'’"))
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    print("_".join("".join(c if c.isalnum() else " " for c in name).split()))
PY
}
FORMAT="${1:-$(read_cfg format)}"
case "$FORMAT" in
  docx|pdf|both) ;;
  *) echo "No or invalid format ('$FORMAT'). Ask the user (docx, pdf or both) and record it in kit/plan.json > output.format."; exit 1 ;;
esac
NAME="$(read_cfg name)"
LANG_="$(read_cfg lang)"
WITH_INDEX="$(read_cfg index)"
suffix() {
  if [ "$LANG_" = tr ]; then
    case "$1" in full) echo Tam_Arastirma ;; summary) echo Ozet ;; check) echo Dogrulama ;; esac
  else
    case "$1" in full) echo Full_Research ;; summary) echo Summary ;; check) echo Verification ;; esac
  fi
}
SOFFICE="$(command -v soffice || true)"
[ -n "$SOFFICE" ] || SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
[ -x "$SOFFICE" ] || { echo "LibreOffice (soffice) not found."; exit 1; }
[ -d node_modules/docx ] || npm install --silent
PROF="$PWD/lo_prof"
if [ ! -f "$PROF/user/basic/Standard/Module1.xba" ]; then
  SAL_USE_VCLPLUGIN=svp "$SOFFICE" -env:UserInstallation=file://$PROF --headless --terminate_after_init >/dev/null 2>&1
  cp Module1.xba "$PROF/user/basic/Standard/Module1.xba"
fi
lo() { SAL_USE_VCLPLUGIN=svp "$SOFFICE" -env:UserInstallation=file://$PROF --headless --invisible "macro:///Standard.Module1.UpdateAndExport(\"$PWD/$1\",\"$PWD/$2\",\"$3\")" 2>/dev/null; }

build() {  # $1 text file in report/, $2 kind (full|summary|check)
  local md="$ROOT/report/$1" t="$2" target
  target="$ROOT/report/${NAME}_$(suffix "$t")"
  [ -f "$md" ] || { echo "report/$1 is missing."; exit 1; }
  rm -f $t.pdf $t.docx ${t}_p1.docx ${t}_p1.pdf ${t}_raw.docx ${t}_index.json ${t}_index2.json
  if [ "$t" = full ] && [ "$WITH_INDEX" = 1 ]; then
    NODE_NO_WARNINGS=1 node make_docx.js "$md" ${t}_p1.docx "$CFG" $t >/dev/null
    lo ${t}_p1.docx ${t}_p1.pdf ""
    [ -s ${t}_p1.pdf ] || { echo "LibreOffice produced no PDF ($1, first pass)."; exit 1; }
    python3 make_index.py ${t}_p1.pdf ${t}_index.json "$CFG"
    NODE_NO_WARNINGS=1 node make_docx.js "$md" ${t}_raw.docx "$CFG" $t ${t}_index.json >/dev/null
  else
    NODE_NO_WARNINGS=1 node make_docx.js "$md" ${t}_raw.docx "$CFG" $t >/dev/null
  fi
  lo ${t}_raw.docx $t.pdf "$PWD/$t.docx"
  [ -s $t.pdf ] && [ -s $t.docx ] || { echo "LibreOffice produced no document ($1)."; exit 1; }
  if [ -f ${t}_index.json ]; then
    python3 make_index.py $t.pdf ${t}_index2.json "$CFG" >/dev/null
    cmp -s ${t}_index.json ${t}_index2.json || echo "WARNING: index pages changed in the second pass; run build.sh once more."
  fi
  rm -f "$target.docx" "$target.pdf"
  [ "$FORMAT" = pdf ] || cp $t.docx "$target.docx"
  [ "$FORMAT" = docx ] || cp $t.pdf "$target.pdf"
  echo "$(basename "$target"): $(pdfinfo $t.pdf | awk '/^Pages/{print $2}') pages"
}

if [ -n "$2" ]; then
  [ -n "$3" ] || { echo "Single document: build.sh <format> <text.md> <full|summary|check>"; exit 1; }
  build "$2" "$3"
else
  build FULL_RESEARCH.md full
  build SUMMARY.md summary
fi
echo "Format: $FORMAT -> $ROOT/report/"
