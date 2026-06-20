#!/usr/bin/env python3
"""Compress and convert raster images to WebP; update index.html references."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"
HTML = ROOT / "index.html"

HERO = {
    "8d7e3aa384b597937b9504925ead6325",
    "0ab22056b482979979f9203c2db57c87",
}

SMALL_HINTS = {
    "fb783df3c47bb9bdf8432ac158d24131",
    "3e5dd3a1d566a7f5fc0745fff3f0158c",
    "8fec80b0270502eee473a97d551b0561",
    "c25f8ab693de5b24cfd8c069917051b5",
    "162edcaeb5a552d600eb62fbc50e622c",
    "2e4566e258654949d8dff68c39757fcb",
}


def image_size(path: Path) -> tuple[int, int]:
    out = subprocess.check_output(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        text=True,
    )
    w = h = 0
    for line in out.splitlines():
        if "pixelWidth" in line:
            w = int(line.split()[-1])
        if "pixelHeight" in line:
            h = int(line.split()[-1])
    return w, h


def target_width(path: Path, w: int, file_size: int) -> int:
    stem = path.stem
    if stem in HERO:
        return min(w, 960)
    if stem in SMALL_HINTS:
        return min(w, 128)
    if file_size > 500_000 or w > 1400:
        return min(w, 820)
    if file_size > 180_000 or w > 900:
        return min(w, 640)
    if w > 520:
        return min(w, 520)
    return w


def to_webp(src: Path, dst: Path, width: int, quality: int = 80) -> None:
    cmd = ["cwebp", "-quiet", "-q", str(quality), "-m", "6", "-resize", str(width), "0", str(src), "-o", str(dst)]
    subprocess.run(cmd, check=True)


def main() -> None:
    if not IMAGES.exists():
        print("No images dir", file=sys.stderr)
        sys.exit(1)

    mapping: dict[str, str] = {}
    total_before = 0
    total_after = 0

    for src in sorted(IMAGES.iterdir()):
        if src.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        if not src.is_file():
            continue

        total_before += src.stat().st_size
        w, _h = image_size(src)
        tw = target_width(src, w, src.stat().st_size)
        q = 78 if src.stat().st_size > 800_000 else 82

        dst = src.with_suffix(".webp")
        to_webp(src, dst, max(tw, 1), q)
        total_after += dst.stat().st_size

        rel_old = f"assets/images/{src.name}"
        rel_new = f"assets/images/{dst.name}"
        mapping[rel_old] = rel_new
        print(f"{src.name}: {src.stat().st_size // 1024}KB {w}px -> {dst.stat().st_size // 1024}KB webp ({tw}px)")

        src.unlink()

    # Remove orphan webp from partial runs if png was deleted
    for stale in IMAGES.glob("*.webp"):
        stem = stale.stem
        if not any((IMAGES / f"{stem}{ext}").exists() for ext in (".png", ".jpg", ".jpeg")):
            pass  # keep converted webp

    html = HTML.read_text(encoding="utf-8")
    for old, new in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        html = html.replace(old, new)
    HTML.write_text(html, encoding="utf-8")

    # Drop duplicate leftover webp-only files not referenced
    refs = set(re.findall(r"assets/images/[a-zA-Z0-9_.-]+", html))
    for path in IMAGES.iterdir():
        rel = f"assets/images/{path.name}"
        if path.is_file() and rel not in refs and path.suffix == ".webp":
            path.unlink()
            print(f"removed orphan {path.name}")

    print(f"\nTotal: {total_before // 1024}KB -> {total_after // 1024}KB")
    print(f"Updated {HTML}")


if __name__ == "__main__":
    main()
