#!/usr/bin/env python3
"""Deep Research Companion: download a URL (PDF or web page) and write a plain-text copy for searching.

Usage: python3 kit/fetch_source.py <name> <url>
Run from a project's kit/ folder, files land in report/_downloads/: <name>.txt, plus <name>.pdf for PDFs or
<name>.html for pages (kept so the page's own links can be followed without downloading it again).
PDFs are converted with pdftotext; on a certificate error the download is retried once with -k.
An error page (HTTP 4xx/5xx) is not the source: nothing is written and the script exits with an error.
"""
import html as h
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

name, url = sys.argv[1], sys.argv[2]
p = urllib.parse.urlsplit(url)
url = urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path)), p.query, p.fragment))
here = Path(__file__).resolve().parent
here = here.parent / "report" / "_downloads" if here.name == "kit" else here
here.mkdir(parents=True, exist_ok=True)
raw = here / f"{name}.bin"
code = ""
for extra in ([], ["-k"]):
    r = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", "Mozilla/5.0", *extra, "-o", str(raw), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    code = r.stdout.strip()
    if r.returncode == 0 and raw.exists() and raw.stat().st_size > 500:
        break
if code.isdigit() and int(code) >= 400:
    raw.unlink(missing_ok=True)
    sys.exit(f"{name}: HTTP {code}, the page does not open; no text written. {url[:100]}")
head = raw.read_bytes()[:5] if raw.exists() else b""
out = here / f"{name}.txt"
if head.startswith(b"%PDF"):
    raw.rename(here / f"{name}.pdf")
    subprocess.run(["pdftotext", "-layout", str(here / f"{name}.pdf"), str(out)])
else:
    page = raw.read_text(errors="replace") if raw.exists() else ""
    page = re.sub(r"(?is)<(script|style).*?</\1>", " ", page)
    txt = h.unescape(re.sub(r"<[^>]+>", " ", page))
    out.write_text(re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", txt)), encoding="utf-8")
    if raw.exists():
        raw.rename(here / f"{name}.html")
print(name, url[:100], "->", out.stat().st_size if out.exists() else 0, "characters")
