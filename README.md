# ziruili-physics.github.io

李梓瑞的个人主页：理论物理研究、笔记与代码分享。

- 线上地址：<https://ziruili-physics.github.io/>
- 技术栈：MkDocs + Material for MkDocs + mkdocs-static-i18n
- 中文默认，英文页用 `.en.md` 后缀；没有英文版的页面自动回退中文

## 本地开发

推荐用 VSCode：打开仓库后，`Terminal → Run Task` 里有现成任务。

隐私检查需要 PATH 中的 `pdftotext`。本机可用 TeX Live 自带的版本，也可以安装 Poppler。

手动方式（Windows）：

```powershell
# 首次：创建虚拟环境并安装依赖
D:\anaconda3\python.exe -m venv --without-pip .venv
D:\anaconda3\python.exe -m pip --python .venv install -r requirements.txt

# 预览（默认 http://127.0.0.1:8000）
.\.venv\Scripts\python.exe -m mkdocs serve

# 严格构建
.\.venv\Scripts\python.exe -m mkdocs build --strict

# 隐私检查与链接检查
.\.venv\Scripts\python.exe scripts\check_privacy.py
.\.venv\Scripts\python.exe scripts\check_links.py site
```

> 本机 `python` 命令指向 Microsoft Store 的占位程序；请使用 `.venv\Scripts\python.exe`，或在安装 Python 后把 `python` 指向真实解释器。

## 目录结构

```text
data/              会经常变的内容（研究方向、论文、更新）
hooks/content.py   把 data/*.yml 渲染进页面的 token
templates/         新页面 / 笔记 / 文章的模板
scripts/           隐私检查、链接检查
docs/              站点内容
  assets/          图片
  stylesheets/     base / home / academic / life
  javascripts/     site.js / mathjax.js
overrides/         只覆盖了 404 模板
_local/            私有副本（被 gitignore，绝不提交）
.vscode/           任务与编辑器设置
```

## 内容维护

### 改研究方向

研究页的总述和主题卡片来自 `data/research.yml`。`status` 可选 `active` / `ongoing` / `interest`。近期工作和首页的一句简介直接在对应的中英 Markdown 页面里维护。

### 加论文或报告

改 `data/publications.yml` 的 `papers` / `talks`。列表为空时省略对应栏目。共享讲义可写 `url: /notes/downloads/example.pdf`。

### 改首页"最近更新"

改 `data/updates.yml`。

### 加附件和笔记页

以开放系统笔记为例，将可公开的 PDF 放到 `docs/notes/downloads/open-systems.pdf`。

1. 只发 PDF 时，在 `docs/notes/physics.md` 的表格加一行，链接写成 `[开放系统笔记](/notes/downloads/open-systems.pdf)`。在 `physics.en.md` 增加英文条目，链接指向同一份 PDF。
2. 同时发布网页版时，将 `templates/note.md` 复制为 `docs/notes/open-systems.md`，在笔记页写下载链接。将分类表格的链接改成 `[开放系统笔记](open-systems.md)`，英文分类页也用这个 Markdown 路径。
3. 有英文版正文时，另存为 `docs/notes/open-systems.en.md`。否则英语入口会打开中文版正文。

### 加一篇文章

将 `templates/post.md` 复制到对应目录，保存为 `first-post.md`。

- 物理写作放在 `docs/blog/`。
- 生活随笔放在 `docs/life/blog/`。

在同目录的 `index.md` 加一条 `- [文章标题](first-post.md)`，有新文章时把生活随笔的空状态文字删掉。英文列表在 `index.en.md`，链接也写 `first-post.md`。正文只有中文版时，在英文条目旁注明 “in Chinese”。有译文时，将它保存为 `first-post.en.md`。

页面只需通过栏目列表进入时，添加链接即可。只有希望它出现在侧栏或顶栏时，才在 `mkdocs.yml` 的 `nav` 增加中文源文件路径，同时补上 `nav_translations` 中的英文导航名称。主动隐藏的公开栏目可以登记到 `not_in_nav`。

完成后按本地开发一节依次运行严格构建、隐私和站内链接检查。

### 双语约定

- 中文：`docs/foo.md`
- 英文：`docs/foo.en.md`
- 没写英文版时，英文站会显示中文原页（这是 mkdocs-static-i18n 的默认行为）。
- 下载链接用站点绝对路径（`/notes/downloads/...`），英文页也指向同一份文件；不要把 PDF 复制两份。

## 隐私与版权

- 网页邮箱用字符码写在 `data-u` / `data-d` 属性里，由 `site.js` 解码。
- 新增的私有资料放在 `_local/materials/`。现有 `docs/cv/` 原件和归档中的两份含学号作业留在原位，已同时排除出构建和 Git。网页简历由 `docs/cv.md` 和 `docs/cv.en.md` 维护。
- 提交前先构建，再运行隐私检查。脚本检查公开文本和构建后的 PDF。如果用 `--site-dir` 另存产物，将同一路径传给两个检查脚本。
- 下架资料的清单和恢复方法见 `_local/materials/MANIFEST.md`。
- Git 历史里仍保留旧的敏感文件。

## 发布

首次采用新工作流时，在 GitHub 仓库的 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**，然后提交并推送改动。

PR 会运行严格构建、隐私检查和站内链接检查。推送到 `main` 后，工作流将通过检查的同一份 `site/` 上传并发布。需要重新发布时，可在 **Actions → publish site → Run workflow** 选择 `main`。

## 设计说明

- 学术页（首页 / 研究 / 笔记 / 关于 / 归档）是编辑排版风：纸色、衬线标题、细线、留白。
- 生活页（`docs/life/`）是霓虹风，强制深色，不进导航；入口在页脚 `✦` 与右下角悬浮按钮。
- 两套视觉靠 `site.js` 给 `<body>` 打的 `data-zl` 属性切换，CSS 分文件生效。
- MathJax 只在含公式的页面按需加载；没有外部字体、没有统计脚本。
- 需要更复杂交互时，把资源放进 `docs/assets/`，页面里用 `data-widget` 标记，`site.js` 会调用 `window.ZL.mount()`；不要往主题模板里塞逻辑。
