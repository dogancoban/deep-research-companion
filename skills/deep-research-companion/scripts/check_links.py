#!/usr/bin/env python3
"""Deep Research Companion: check every link in one or more text files.

Usage: python3 check_links.py <file> [<file> ...]
Works on any text: a pasted AI answer, report/_evidence/_source_list.md, a run output.
Needs only Python 3 and curl. For each distinct URL prints the result, HTTP status, type and title:
  opens     the link opens (a working link still has to be read)
  blocked   401/403/429: often bot protection; try fetching it another way or in a browser
  broken    404, 410, other errors, unknown host: often an invented or moved source
  timeout   no answer within 20 seconds
"""
import concurrent.futures as cf
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

URL = re.compile(r"https?://[^\s<>\"'`|\]\)\*]+")
SSL_ERRORS = {35, 51, 58, 60}


def urls(paths):
    seen = []
    for p in paths:
        for u in URL.findall(Path(p).read_text(encoding="utf-8", errors="replace")):
            u = u.rstrip(".,;:")
            if u not in seen:
                seen.append(u)
    return seen


def fetch(url, insecure=False):
    with tempfile.NamedTemporaryFile(suffix=".bin") as tmp:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "20", "-A", "Mozilla/5.0 (Macintosh)", "-r", "0-65535",
                            *(["-k"] if insecure else []), "-o", tmp.name, "-w", "%{http_code} %{content_type}", url],
                           capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), Path(tmp.name).read_bytes()[:65536]


def check(url):
    rc, out, head = fetch(url)
    note = ""
    if rc in SSL_ERRORS:
        rc, out, head = fetch(url, insecure=True)
        note = " (certificate problem)"
    code, _, ctype = out.partition(" ")
    if rc == 28:
        return "timeout", "-", "", ""
    if not code.isdigit() or code == "000":
        return "broken", "-", "", f"connection error{note}"
    status = int(code)
    kind = "PDF" if head.startswith(b"%PDF") or "pdf" in ctype.lower() else "page"
    title = ""
    if kind == "page":
        m = re.search(rb"<title[^>]*>(.*?)</title>", head, re.I | re.S)
        if m:
            title = re.sub(r"\s+", " ", html.unescape(m.group(1).decode("utf-8", "replace"))).strip()[:80]
    if 200 <= status < 300:
        result = "opens"
    elif status in (401, 403, 429):
        result = "blocked"
    else:
        result = "broken"
    return result, str(status), kind, (title + note).replace("|", "/")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    found = urls(sys.argv[1:])
    if not found:
        print("No links found.")
        return
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(check, found))
    print("| Result | Code | Type | Title | URL |")
    print("|---|---|---|---|---|")
    for u, (res, code, kind, title) in zip(found, results):
        print(f"| {res} | {code} | {kind} | {title} | {u} |")
    counts = {}
    for res, *_ in results:
        counts[res] = counts.get(res, 0) + 1
    print(f"\n{len(found)} links: " + " · ".join(f"{k}: {v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
