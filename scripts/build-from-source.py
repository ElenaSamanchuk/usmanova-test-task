#!/usr/bin/env python3
"""Build index.html by extracting exact GetCourse blocks from the source page."""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://usmanovafit.gymteam.ru/mainpage"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.html"

# Global styles + 3 screens (desktop/mobile pairs)
BLOCK_IDS = [
    "ltBlock2235313335",  # Gilroy + global raw CSS
    "ltBlock2235313316",  # button styles
    "ltBlock2235313467",  # hero desktop
    "ltBlock2235313425",  # hero mobile
    "ltBlock2235663707",  # programs desktop
    "ltBlock2235664572",  # programs mobile
    "ltBlock2235774933",  # contact desktop
    "ltBlock2235774935",  # contact mobile
]

CSS_LINKS = [
    "/nassets/css/superlite-block-3b3d45c8c82d97c135d0a114931a83b4.css?v=1781882360",
    "/nassets/79a2fae1/css/button.css?v=1765633901",
    "/nassets/86fb0827/css/als-granate-vf-new.css?v=1777450802",
    "/public/fonts/gfonts/open-sans/open-sans-cyr-swap.css",
    "/public/fonts/gfonts/roboto/roboto-cyr-swap.css",
]

BASE = "https://usmanovafit.gymteam.ru"


def fetch_html() -> str:
    cache = ROOT / ".source.html"
    if len(sys.argv) > 1 and sys.argv[1] == "--fetch":
        html = urllib.request.urlopen(SOURCE_URL, timeout=60).read().decode("utf-8", "replace")
        cache.write_text(html)
        return html
    if cache.exists():
        return cache.read_text(encoding="utf-8", errors="replace")
    html = urllib.request.urlopen(SOURCE_URL, timeout=60).read().decode("utf-8", "replace")
    cache.write_text(html)
    return html


def find_block_region(html: str, block_id: str) -> tuple[int, int]:
    """Return slice [start, end) covering styles + full block markup."""
    div_marker = f'<div id="{block_id}"'
    div_start = html.find(div_marker)
    if div_start < 0:
        raise ValueError(f"Block not found: {block_id}")

    style_start = div_start
    search_from = div_start
    for _ in range(20):
        prev_style = html.rfind("<style>", 0, search_from)
        if prev_style < 0:
            break
        style_end = html.find("</style>", prev_style) + len("</style>")
        chunk = html[prev_style:style_end]
        if block_id in chunk or f"#{block_id}" in chunk:
            style_start = prev_style
            search_from = prev_style
            continue
        break

    # Walk div tags from block root until the outer ltBlock closes.
    pos = div_start
    depth = 0
    started = False
    div_end = div_start
    while pos < len(html):
        next_open = html.find("<div", pos)
        next_close = html.find("</div>", pos)
        if next_close < 0:
            break
        if next_open >= 0 and next_open < next_close:
            depth += 1
            started = True
            pos = next_open + 4
            continue
        depth -= 1
        pos = next_close + len("</div>")
        if started and depth == 0:
            div_end = pos
            break

    return style_start, div_end


def clean_chunk(chunk: str) -> str:
    chunk = re.sub(r"<script[\s\S]*?</script>", "", chunk, flags=re.I)
    chunk = re.sub(r"<div class=\"add-redesign-subblock\"[\s\S]*?</div>", "", chunk)
    chunk = re.sub(r"<div class=\"common-setting-link[\s\S]*?</div>", "", chunk)
    chunk = re.sub(r"\sdata-editable=true", "", chunk)
    chunk = re.sub(r"\sdata-setting-editable=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-image-editable=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-raw-editable=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-param=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-item-name=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-title=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-animation-mode=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-path=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-animation-order=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-block-id=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-has-css=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-has-limited-visibility=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sdata-code=\"[^\"]*\"", "", chunk)
    chunk = re.sub(r"\sclass=\"lazyload\"", ' class=""', chunk)
    chunk = re.sub(r"<img([^>]*)\sdata-src=", r"<img\1 src=", chunk)
    chunk = re.sub(r"//fs-", "https://fs-", chunk)
    chunk = re.sub(r"//fs\.", "https://fs.", chunk)
    chunk = re.sub(r"src=\"/fileservice/", f'src="{BASE}/fileservice/', chunk)
    chunk = re.sub(r"url\('/fileservice/", f"url('{BASE}/fileservice/", chunk)
    chunk = re.sub(r'url\("/fileservice/', f'url("{BASE}/fileservice/', chunk)
    chunk = re.sub(r"href=\"/fileservice/", f'href="{BASE}/fileservice/', chunk)
    chunk = re.sub(r"style=\"margin-bottom:[^\"]*border-radius: ; \"", "", chunk)
    chunk = re.sub(r"style=\"border-radius: ; \"", "", chunk)
    chunk = re.sub(r"style=\"color: #FFFFFF; border-radius: ; \"", "", chunk)
    return chunk


def build(html: str) -> str:
    parts: list[str] = []
    for block_id in BLOCK_IDS:
        start, end = find_block_region(html, block_id)
        parts.append(clean_chunk(html[start:end]))

    css_tags = "\n".join(
        f'  <link rel="stylesheet" href="{BASE}{href}" />' for href in CSS_LINKS
    )

    body = "\n\n".join(parts)

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Фитнес с Катей Усмановой — похудение, фигура, зал, форма после родов</title>
  <meta name="description" content="Авторские фитнес-программы чемпионки: похудеть, подтянуть попу и живот, набрать форму в зале, восстановиться после родов. Без диет." />
{css_tags}
  <style>
    html {{ scroll-behavior: smooth; }}
    .lt-invisible-block {{ display: block !important; }}
    .add-redesign-subblock, .common-setting-link {{ display: none !important; }}
  </style>
</head>
<body class="gc-user-guest">
<div class="lite-page block-set">
{body}
</div>
<script src="js/fixup.js"></script>
</body>
</html>
"""


def main() -> None:
    html = fetch_html()
    OUT.write_text(build(html), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
