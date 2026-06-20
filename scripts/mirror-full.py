#!/usr/bin/env python3
"""Produce a near-identical mirror of usmanovafit.gymteam.ru/mainpage."""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://usmanovafit.gymteam.ru/mainpage"
BASE = "https://usmanovafit.gymteam.ru"
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".source.html"
OUT = ROOT / "index.html"


def fetch_source() -> str:
    if len(sys.argv) > 1 and sys.argv[1] == "--fetch":
        html = urllib.request.urlopen(SOURCE_URL, timeout=90).read().decode("utf-8", "replace")
        SOURCE.write_text(html, encoding="utf-8")
        return html
    if SOURCE.exists():
        return SOURCE.read_text(encoding="utf-8", errors="replace")
    html = urllib.request.urlopen(SOURCE_URL, timeout=90).read().decode("utf-8", errors="replace")
    SOURCE.write_text(html, encoding="utf-8")
    return html


def absolutize(html: str) -> str:
    html = re.sub(r'(\s(?:href|src|action))="/', rf'\1="{BASE}/', html)
    html = re.sub(r"(\s(?:href|src|action))='/", rf"\1='{BASE}/", html)
    html = re.sub(r'(\s(?:href|src))="//', r'\1="https://', html)
    html = re.sub(r"(\s(?:href|src))='//", r"\1='https://", html)
    html = re.sub(r"url\('/fileservice/", f"url('{BASE}/fileservice/", html)
    html = re.sub(r'url\("/fileservice/', f'url("{BASE}/fileservice/', html)
    html = re.sub(r"url\('//", "url('https://", html)
    html = re.sub(r'url\("//', 'url("https://', html)
    html = re.sub(r'(\scontent)="//', r'\1="https://', html)
    html = re.sub(r'data-img-src="//', 'data-img-src="https://', html)
    html = re.sub(r'data-src="//', 'data-src="https://', html)
    html = re.sub(r"https?:https?://", "https://", html, flags=re.I)
    return html


def cleanup(html: str) -> str:
    # Analytics only — layout/assets stay untouched.
    html = re.sub(r"<!-- Yandex\.Metrika counter -->[\s\S]*?<!-- /Yandex\.Metrika counter -->", "", html)
    html = re.sub(r'<script async src="https://usmanovafit\.gymteam\.ru/chtm/s/metric/clarity\.js"></script>', "", html)
    html = re.sub(r'<script src="https://usmanovafit\.gymteam\.ru/public/js/gccounter-new\.js\?1"></script>', "", html)

    # Hide GetCourse editor chrome if any leaks through.
    html = html.replace(
        "</head>",
        """  <style>
    .common-setting-link, .add-redesign-subblock, .box-setting-link { display: none !important; }
    .lt-invisible-block { display: block !important; }
  </style>
</head>""",
        1,
    )

    if "<html" not in html[:200]:
        html = html.replace("<!DOCTYPE html>", '<!DOCTYPE html>\n<html lang="ru">', 1)
        html = html.rstrip() + "\n</html>\n"

    return html


def main() -> None:
    html = cleanup(absolutize(fetch_source()))
    OUT.write_text(html, encoding="utf-8")
    print(f"Mirrored {OUT} ({OUT.stat().st_size} bytes)")
    print("Run: python3 scripts/localize-images.py")


if __name__ == "__main__":
    main()
