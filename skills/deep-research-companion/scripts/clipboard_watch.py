#!/usr/bin/env python3
"""Deep Research Companion: watch the clipboard and save every copied run answer into outputs/.

Usage: python3 <project>/kit/clipboard_watch.py   (stop with Ctrl+C)
Press the search tool's Copy button under each answer. Anything copied that does not contain
"RUN-ID:" is ignored. Works on macOS (pbpaste), Windows (PowerShell) and Linux (wl-paste, xclip or xsel).
Messages follow plan.json "lang" (en or tr).
"""
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent
OUT = KIT.parent / "outputs"

MSG = {
    "en": {"start": "Watching the clipboard. Press the Copy button under each answer in your search tool.\n"
                    "Each saved answer shows a line here. Stop with Ctrl+C when you are done.\n",
           "saved": "saved", "chars": "characters", "cut": "   ⚠ no end line: the answer may have been copied only in part",
           "stop": "Stopped. Answers saved: {n}.", "none": "No clipboard tool found. Install wl-clipboard, xclip or xsel."},
    "tr": {"start": "Pano izleniyor. Arama aracında her cevabın altındaki Kopyala düğmesine sırayla bas.\n"
                    "Her kayıtta burada bir satır göreceksin. Bitince Ctrl+C ile durdur.\n",
           "saved": "kaydedildi", "chars": "karakter", "cut": "   ⚠ bitiş satırı yok: cevap eksik kopyalanmış olabilir",
           "stop": "Durduruldu. Kaydedilen cevap: {n}.", "none": "Pano aracı bulunamadı. wl-clipboard, xclip ya da xsel kur."},
}


def reader():
    if sys.platform == "darwin":
        return ["pbpaste"]
    if sys.platform.startswith("win"):
        return ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"]
    for cmd in (["wl-paste", "--no-newline"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]):
        if shutil.which(cmd[0]):
            return cmd
    return None


def main():
    try:
        lang = json.loads((KIT / "plan.json").read_text(encoding="utf-8")).get("lang", "en")
    except (OSError, ValueError):
        lang = "en"
    m_ = MSG.get(lang, MSG["en"])
    cmd = reader()
    if not cmd:
        sys.exit(m_["none"])
    OUT.mkdir(exist_ok=True)

    def clipboard():
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

    print(m_["start"])
    last = hashlib.sha256(clipboard().encode()).hexdigest()  # ignore whatever was copied before the start
    saved = 0
    try:
        while True:
            text = clipboard()
            h = hashlib.sha256(text.encode()).hexdigest()
            if h != last:
                last = h
                m = re.search(r"RUN-ID:\s*([A-Z0-9-]+)", text)
                if m:
                    path = OUT / f"copy_{datetime.datetime.now():%H%M%S_%f}.md"
                    path.write_text(text, encoding="utf-8")
                    saved += 1
                    warn = "" if "RUN END" in text else m_["cut"]
                    print(f"{saved:2}. {m_['saved']}: {m.group(1)} ({len(text)} {m_['chars']}){warn}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + m_["stop"].format(n=saved))


if __name__ == "__main__":
    main()
