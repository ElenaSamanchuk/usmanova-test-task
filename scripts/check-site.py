#!/usr/bin/env python3
"""Smoke-check images, links, and interactive hooks in index.html."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
FORM_DESKTOP = "ltBlock2235774933"
FORM_MOBILE = "ltBlock2235774935"
FORM_BUTTON_IDS = ("button5772404", "button4154228", "button2930836")


def main() -> int:
    html = HTML.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []

    for ref in set(re.findall(r"assets/images/[a-zA-Z0-9_.-]+", html)):
        if not (ROOT / ref).exists():
            errors.append(f"Missing image: {ref}")

    if re.search(r"https://fs[^\"'\s]+\.(png|jpg|svg|webp)", html):
        errors.append("External image URLs still present")

    if not re.search(r"assets/images/.*\.webp", html):
        errors.append("WebP images not referenced")

    if "js/site-fixup.js" not in html:
        errors.append("site-fixup.js not included")

    if ".js__accept_cookies_policy" not in html:
        errors.append("Cookie button missing")

    if html.count('class="faq-question"') < 5:
        errors.append("FAQ questions missing")

    if "UsmanovaSport_bot" not in html:
        errors.append("Telegram link missing")

    if FORM_DESKTOP not in html or FORM_MOBILE not in html:
        errors.append("Contact form blocks missing")

    fixup = (ROOT / "js/site-fixup.js").read_text(encoding="utf-8", errors="replace")
    for button_id in FORM_BUTTON_IDS:
        if button_id not in fixup:
            errors.append(f"Form scroll handler missing for {button_id}")

    if "ltBlock2235774933" not in fixup or "ltBlock2235774935" not in fixup:
        errors.append("Responsive form anchor logic missing in site-fixup.js")

    if "class=\"btn\">Подробнее" not in html and "class='btn'>Подробнее" not in html:
        errors.append("Program detail buttons missing")

    if errors:
        print("CHECK FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("CHECK OK")
    print(f"- images: {len(set(re.findall(r'assets/images/', html)))} refs")
    print(f"- faq items: {html.count('faq-item')}")
    print(f"- cookie banner: yes")
    print(f"- site-fixup: yes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
