"""把 data/ 里的内容渲染进 Markdown 页面。

设计目标：
- 研究方向、论文、最近更新这类"会经常变"的内容只维护 YAML；
- 页面里只留一个 token，不写重复的 HTML；
- 英文站（`.en.md`）自动取 `en` 字段，缺字段回退中文；
- 只读取页面引用的数据，格式错误时报告文件名。

支持的 token：
    {{RESEARCH_UMBRELLA}}   一句话研究总主题
    {{RESEARCH_THEMES}}     研究主题卡片网格
    {{RESEARCH_CHIPS}}      首页用的紧凑标签
    {{PUBLICATIONS}}        论文与报告
    {{LATEST_UPDATES}}      最近更新时间线

数据文件位于仓库根目录的 data/ 下。
"""

from __future__ import annotations

import html
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

import yaml
from mkdocs.exceptions import PluginError

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

STATUS_LABELS = {
    "active": ("主要关注", "Focus"),
    "ongoing": ("进行中", "Ongoing"),
    "interest": ("感兴趣", "Interest"),
}

EMPTY_ZH = '<div class="zl-empty">暂无。</div>'
EMPTY_EN = '<div class="zl-empty">None yet.</div>'


def _load(name: str) -> Any:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    expected_type = list if name == "updates.yml" else dict
    if data is None:
        return expected_type()
    if not isinstance(data, expected_type):
        raise ValueError(f"根节点应为 {'列表' if expected_type is list else '映射'}")
    return data


def _entries(value: Any, field: str) -> list[dict]:
    if not isinstance(value, list):
        raise ValueError(f"{field} 应为列表")
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{field} 第 {index} 项应为映射")
    return value


def _theme_info(theme: dict, lang: str) -> dict:
    for locale in ("zh", "en"):
        if locale in theme and not isinstance(theme[locale], dict):
            raise ValueError(f"themes 中的 {locale} 应为映射")
    return theme.get(lang) or theme.get("zh") or {}


def _lang(page: Any) -> str:
    return "en" if page.file.src_uri.endswith(".en.md") else "zh"


def _text(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("zh") or "")
    return "" if value is None else str(value)


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _empty(lang: str) -> str:
    return EMPTY_EN if lang == "en" else EMPTY_ZH


def _localise_url(url: Any, lang: str) -> str:
    value = str(url or "")
    if (
        lang == "en"
        and value.startswith("/")
        and not value.startswith(("//", "/en/"))
        and not PurePosixPath(urlsplit(value).path).suffix
    ):
        return "/en" + value
    return value


def _umbrella(data: dict, lang: str) -> str:
    text = _text(data.get("umbrella"), lang)
    return f'<p class="zl-umbrella">{_esc(text)}</p>' if text else ""


def _themes(data: dict, lang: str) -> str:
    themes = _entries(data.get("themes", []), "themes")
    if not themes:
        return _empty(lang)
    cards = []
    for theme in themes:
        info = _theme_info(theme, lang)
        title = _esc(info.get("title", ""))
        blurb = _esc(info.get("blurb", ""))
        status = str(theme.get("status", "interest"))
        label = STATUS_LABELS.get(status, STATUS_LABELS["interest"])[0 if lang == "zh" else 1]
        tags = theme.get("tags", [])
        if not isinstance(tags, list):
            raise ValueError("themes 中的 tags 应为列表")
        tag_html = "".join(f'<span class="zl-tag">{_esc(tag)}</span>' for tag in tags)
        cards.append(
            f'<article class="zl-theme" data-status="{_esc(status)}">'
            f'<div class="zl-theme__meta"><span class="zl-badge">{_esc(label)}</span>'
            f'<span class="zl-tags">{tag_html}</span></div>'
            f'<h3 class="zl-theme__title">{title}</h3>'
            f'<p class="zl-theme__blurb">{blurb}</p>'
            "</article>"
        )
    return '<div class="zl-theme-grid">' + "".join(cards) + "</div>"


def _chips(data: dict, lang: str) -> str:
    chips = []
    for theme in _entries(data.get("themes", []), "themes"):
        info = _theme_info(theme, lang)
        title = info.get("title", "")
        if title:
            chips.append(f'<span class="zl-chip">{_esc(title)}</span>')
    return '<div class="zl-chips">' + "".join(chips) + "</div>" if chips else _empty(lang)


def _updates(items: list, lang: str) -> str:
    if not items:
        return _empty(lang)
    rows = []
    for item in _entries(items, "更新"):
        date = _esc(item.get("date", ""))
        text = _esc(_text({lang: item.get(lang), "zh": item.get("zh")}, lang))
        url = _localise_url(item.get("url"), lang)
        body = f'<a href="{_esc(url)}">{text}</a>' if url else text
        rows.append(f'<li class="zl-update"><time>{date}</time><span>{body}</span></li>')
    return '<ol class="zl-timeline">' + "".join(rows) + "</ol>"


def _publications(data: dict, lang: str) -> str:
    papers = _entries(data.get("papers", []), "papers")
    talks = _entries(data.get("talks", []), "talks")

    parts = []
    if papers:
        heading = "Papers & preprints" if lang == "en" else "论文与预印本"
        rows = []
        for paper in papers:
            title = _esc(_text({"zh": paper.get("title_zh"), "en": paper.get("title_en")}, lang) or paper.get("title", ""))
            authors = _esc(paper.get("authors", ""))
            venue = _esc(_text({"zh": paper.get("venue_zh"), "en": paper.get("venue_en")}, lang))
            year = _esc(paper.get("year", ""))
            url = str(paper.get("url") or "")
            link = f' <a class="zl-pub__link" href="{_esc(url)}">PDF / arXiv</a>' if url else ""
            meta = f'{authors}{" · " if authors and venue else ""}{venue}'
            rows.append(
                f'<li class="zl-pub"><span class="zl-pub__year">{year}</span>'
                f'<div><strong>{title}</strong><span class="zl-pub__meta">{meta}</span>{link}</div></li>'
            )
        parts.append(f'## {heading}\n\n<ol class="zl-pubs">' + "".join(rows) + "</ol>")

    if talks:
        heading = "Research talks" if lang == "en" else "学术报告"
        rows = []
        for talk in talks:
            title = _esc(_text({"zh": talk.get("title_zh"), "en": talk.get("title_en")}, lang) or talk.get("title", ""))
            venue = _esc(_text({"zh": talk.get("venue_zh"), "en": talk.get("venue_en")}, lang))
            date = _esc(talk.get("date", ""))
            url = _localise_url(talk.get("url"), lang)
            slides = "Slides" if lang == "en" else "讲义"
            link = f' <a class="zl-pub__link" href="{_esc(url)}">{slides}</a>' if url else ""
            rows.append(
                f'<li class="zl-pub"><span class="zl-pub__year">{date}</span>'
                f'<div><strong>{title}</strong><span class="zl-pub__meta">{venue}</span>{link}</div></li>'
            )
        parts.append(f'## {heading}\n\n<ol class="zl-pubs">' + "".join(rows) + "</ol>")

    return "\n\n".join(parts)


RENDERERS = {
    "{{RESEARCH_UMBRELLA}}": ("research.yml", _umbrella),
    "{{RESEARCH_THEMES}}": ("research.yml", _themes),
    "{{RESEARCH_CHIPS}}": ("research.yml", _chips),
    "{{PUBLICATIONS}}": ("publications.yml", _publications),
    "{{LATEST_UPDATES}}": ("updates.yml", _updates),
}


def on_page_markdown(markdown: str, page: Any, config: Any, files: Any) -> str:
    lang = _lang(page)
    data_by_file = {}
    for token, (name, render) in RENDERERS.items():
        if token not in markdown:
            continue
        try:
            if name not in data_by_file:
                data_by_file[name] = _load(name)
            value = render(data_by_file[name], lang)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
            raise PluginError(f"data/{name}: {error}") from error
        markdown = markdown.replace(token, value)
    return markdown
