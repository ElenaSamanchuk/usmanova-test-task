#!/usr/bin/env python3
"""Download all images referenced in index.html into assets/images/."""

from __future__ import annotations

import hashlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
ASSETS = ROOT / "assets" / "images"

IMAGE_RE = re.compile(
    r"https?:https?://[^\s\"')>]+\.(?:png|jpg|jpeg|webp|gif|svg)|"
    r"https://[^\s\"')>]+\.(?:png|jpg|jpeg|webp|gif|svg)",
    re.I,
)


def normalize_url(url: str) -> str:
    url = url.strip()
    url = re.sub(r"^https?:https?://", "https://", url, flags=re.I)
    return url


def local_name(url: str) -> str:
    path = urlparse(url).path
    match = re.search(r"/h/([a-f0-9]+)\.", path, re.I)
    ext = Path(path).suffix.lower() or ".bin"
    if match:
        return f"{match.group(1)}{ext}"
    digest = hashlib.sha1(url.encode()).hexdigest()[:16]
    return f"{digest}{ext}"


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; mirror/1.0)"},
    )
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
        if len(data) > 100:
            dest.write_bytes(data)
            return True
    except Exception:
        pass

    # Thumbnail hosts often 500 — try /download/ URL from hash in path.
    match = re.search(r"/h/([a-f0-9]+)\.(png|jpg|jpeg|webp|gif|svg)", url, re.I)
    sc_match = re.search(r"/a/934144/sc/(\d+)/", url)
    if match:
        ext = match.group(2).lower()
        file_id = match.group(1)
        sc = sc_match.group(1) if sc_match else "68"
        fallback = f"https://fs.getcourse.ru/fileservice/file/download/a/934144/sc/{sc}/h/{file_id}.{ext}"
        try:
            data = urllib.request.urlopen(
                urllib.request.Request(fallback, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=60,
            ).read()
            if len(data) > 100:
                dest.write_bytes(data)
                return True
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {exc} {fallback}")
            return False
    print(f"FAIL {url}")
    return False


def main() -> None:
    html = HTML.read_text(encoding="utf-8", errors="replace")
    html = re.sub(r"https?:https?://", "https://", html, flags=re.I)

    raw_urls = {normalize_url(u) for u in IMAGE_RE.findall(html)}
    print(f"Found {len(raw_urls)} image URLs")

    mapping: dict[str, str] = {}
    ok = 0
    for url in sorted(raw_urls):
        name = local_name(url)
        dest = ASSETS / name
        rel = f"assets/images/{name}"
        if download(url, dest):
            mapping[url] = rel
            ok += 1
            print(f"OK  {name}")
        else:
            print(f"SKIP {url}")

    for url, rel in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        html = html.replace(url, rel)

    def add_src(match: re.Match[str]) -> str:
        tag = match.group(0)
        if " src=" in tag:
            return tag
        ds = re.search(r'data-src="([^"]+)"', tag)
        if ds and ds.group(1).startswith("assets/"):
            return tag.replace("<img ", f'<img src="{ds.group(1)}" ', 1)
        return tag

    html = re.sub(r'<img[^>]+class="lazyload"[^>]*>', add_src, html)

    HTML.write_text(html, encoding="utf-8")
    print(f"Downloaded {ok}/{len(raw_urls)} -> {ASSETS}")
    print(f"Updated {HTML}")


if __name__ == "__main__":
    main()
    print("Run: python3 scripts/optimize-images.py")
