#!/usr/bin/env python3
"""检查公开源码与新构建的站点。

用法：python scripts/check_privacy.py [site-dir]
PDF 文本提取依赖 Poppler 的 pdftotext。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

CHECKS = {
    "明文 Gmail": re.compile(r"ziruili6039\s*@\s*gmail\.com", re.IGNORECASE),
    "明文 QQ 邮箱": re.compile(r"ziruili6039\s*@\s*qq\.com", re.IGNORECASE),
    "明文 SJTU 邮箱": re.compile(r"ziruili6039\s*@\s*sjtu\.edu\.cn", re.IGNORECASE),
    "学号": re.compile(r"2237" r"7056"),
    "已下架资料文件名": re.compile(r"高等代数教材|第五版航概答案|科研课堂大作业|2022-2023学年理科数分|2022秋理科高代"),
}

TEXT_SUFFIXES = {".md", ".html", ".yml", ".yaml", ".js", ".css", ".txt", ".json", ".py", ".tex"}


def scan(directory: Path, pdftotext: str | None = None) -> list[str]:
    hits = []
    for path in directory.rglob("*"):
        if not path.is_file() or path.is_relative_to(DOCS / "cv"):
            continue
        relative_path = path.relative_to(directory)
        label = f"{directory.name}/{relative_path.as_posix()}"
        content = ""
        try:
            suffix = path.suffix.lower()
            if suffix in TEXT_SUFFIXES:
                content = path.read_text(encoding="utf-8")
            elif suffix == ".pdf" and pdftotext is not None:
                content = subprocess.run(
                    [pdftotext, "-enc", "UTF-8", str(path), "-"],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    check=True,
                ).stdout
        except (OSError, UnicodeError, subprocess.CalledProcessError):
            hits.append(f"无法读取文件内容: {label}")

        for description, pattern in CHECKS.items():
            if pattern.search(relative_path.as_posix()) or pattern.search(content):
                hits.append(f"{description}: {label}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", type=Path, default=ROOT / "site")
    site = parser.parse_args().site_dir.resolve()
    if not site.is_dir():
        parser.error(f"构建目录不存在，请先运行 mkdocs build --strict：{site}")
    pdftotext = shutil.which("pdftotext")
    if pdftotext is None:
        parser.error("找不到 pdftotext。请安装 Poppler 或将 TeX Live 的 pdftotext 加入 PATH。")

    hits = scan(DOCS) + scan(site, pdftotext)
    if hits:
        print("隐私检查未通过：")
        for hit in sorted(set(hits)):
            print("  -", hit)
        return 1

    print("隐私检查通过：未发现明文邮箱、学号或已下架资料文件名。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
