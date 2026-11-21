#!/usr/bin/env python3
"""检查构建产物里的站内绝对链接是否都能找到目标文件。

用法：
    python scripts/check_links.py _local/site

只检查以 / 开头的站内链接（含 /en/），不检查外链、锚点和 mailto。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"""(?:href|src)=["'](/[^"'#?]+)(?:[?#][^"']*)?["']""")


def target_exists(site: Path, raw: str) -> bool:
    path = unquote(raw)
    candidate = site / path.lstrip("/")
    if candidate.is_file():
        return True
    if candidate.is_dir() and (candidate / "index.html").is_file():
        return True
    if not candidate.suffix and (candidate / "index.html").is_file():
        return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/check_links.py <site-dir>")
        return 2
    site = Path(sys.argv[1]).resolve()
    if not site.is_dir():
        print(f"site directory not found: {site}")
        return 2

    missing: dict[str, set[str]] = {}
    for page in site.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="ignore")
        for raw in LINK_RE.findall(text):
            if raw.startswith("//"):
                continue
            if not target_exists(site, raw):
                missing.setdefault(raw, set()).add(str(page.relative_to(site)))

    if not missing:
        print(f"link check passed: {site}")
        return 0

    print(f"missing link targets in {site}:")
    for raw, pages in sorted(missing.items()):
        sample = ", ".join(sorted(pages)[:3])
        print(f"  - {raw}  (from {sample})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
