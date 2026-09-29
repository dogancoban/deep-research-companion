#!/usr/bin/env bash
# Deep Research Companion: everything from the collected outputs to the full-research text, on this computer, without a model.
# Usage: bash kit/prepare.sh      Then: check the unmatched key findings, write report/SUMMARY.md, run bash kit/finish.sh
set -e
cd "$(dirname "$0")/.."
python3 kit/name_outputs.py | tail -1
python3 kit/coverage.py | tail -1
python3 kit/split_evidence.py
python3 kit/fetch_all.py
python3 kit/build_full.py
echo "Ready: report/FULL_RESEARCH.md, report/_auto_verify.tsv, report/_auto_verify_summary.md"
