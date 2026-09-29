#!/usr/bin/env bash
# Deep Research Companion: rebuild the full research (hand checks included), check both texts, build the documents.
# Usage: bash kit/finish.sh [docx|pdf|both]      Without a format, kit/plan.json > output.format is used.
set -e
cd "$(dirname "$0")/.."
python3 kit/build_full.py
python3 kit/check_report.py > report/_check_report.txt || true
tail -6 report/_check_report.txt
[ -f report/document.json ] || { echo "report/document.json is missing: copy the skill's assets/document.json and fill it in."; exit 1; }
bash kit/doc_builder/build.sh "$@"
