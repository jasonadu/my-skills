---
name: bilingual-reading
description: 双语阅读——将英文 PDF（技术书、教程、手册等）转换为逐段中英对照、图片 base64 内嵌、带左侧可折叠目录导航的多文件 HTML 阅读版。触发场景：用户提供英文 PDF 并希望双语对照阅读、中英对照翻译成 HTML 阅读版、逐段翻译做双语网页、或提到"英文 PDF 转双语 HTML / 双语阅读 / 中英对照阅读版"等需求。核心规则：原文逐段全译不概要、一章一文件、代码块保持英文、中文段浅蓝底左色条、每译完原书一页加页码标记、文件名小写连字符、🌐 按钮循环中英显示模式。
---

# 双语阅读（Bilingual Reading）

## 概述

把一本英文技术 PDF 变成**逐段中英对照**的离线 HTML 阅读版：每章一个自包含
HTML（UTF-8、图片 base64 内嵌、单文件可离线打开），左侧固定可折叠目录，
右下角 🌐 悬浮按钮在「仅英文 / 仅中文 / 中英对照」间循环，翻页后保持。

## 触发与输入

- 输入：英文版 PDF（本地路径或 URL，先下载到本地）。
- 输出：`index.html` + 前置/结语页 + `chapter-NN.html`（一章一文件），
  最终打包 zip 交付。
- 若 PDF 带书签（`get_toc()`），章节结构以书签为准并先与用户确认，
  用户确认"不拆分"后再批量生产。

## 核心规则（不可违反）

1. 原文**逐段全译**，不做概要/合并。
2. **一章一文件**，不拆章；章内按原书页顺序逐段排版。
3. 代码块（`<pre><code>`）**保留英文不翻译**；含花括号的代码不写进 f-string。
4. 中文段落浅蓝底 + 左侧 4px 色条，与英文段区分；列表项中文同规格。
5. 图片压缩后 base64 内嵌；**每译完原书一页后，单独加一行页码标记**
   （`page_mark(pdf_page)`）显示原 PDF 页码。
6. 文件名小写连字符（`chapter-01.html`、`front-matter.html`）。
7. 目录条目按书签层级（l2/l3）生成；上下章链接串联，首尾章置灰。

## 工作流总览

```
① 定页范围 → ② 抽文本 → ③ 抽图片 → ④ 压图转 base64
→ ⑤ 读原文翻译 → ⑥ 写 build_chN.py → ⑦ 补花括号 → ⑧ 运行生成
→ ⑨ 串联导航 → 验证 → 交付
```

先做**样板章**（通常 ch1）给用户验收样式，确认后沉淀/复用 `book_theme.py`
再连续批量生产，中途无需再确认。前置/结语页与 `index.html` 最后统一收尾。

## 步骤详解

### ① 定页范围

输入：全书 TOC / 章号。用 PyMuPDF 读书签：

```python
import fitz
doc = fitz.open("book.pdf")
toc = doc.get_toc()          # [[level, title, page_1based], ...]
```

按 1-based 页码换算为 PyMuPDF 0-based 区间。**书签页码与物理页常有偏移，
以书签为准**；向用户列出章节划分并确认后再开工。

### ② 抽文本

```python
text = "".join(doc[p].get_text("text", sort=True) for p in range(start0, end0+1))
open("chN_raw.txt", "w", encoding="utf-8").write(text)
```

`sort=True` 保证阅读顺序，多栏不混淆。每章写 `chN_raw.txt` 存原文。

### ③ 抽图片

用 `scripts/extract_assets.py`：

```bash
python3 extract_assets.py book.pdf <start_page_1based> <end_page_1based> --out assets
```

- `page.get_images(full=True)` 按 xref 去重 → `extract_image(xref)`。
- jpx(JPEG2000)、RGBA、P 模式统一转 RGB 再存 JPEG（浏览器兼容）。

### ④ 压图转 base64

同上一步一并完成（脚本内置）：PIL 打开；宽 >800px 等比缩到 800（LANCZOS）；
JPEG q≈68 重存；base64 写 `assets/figN-M.txt`。单图压到 30~80KB。

### ⑤ 读原文并翻译

- 分段 Read `chN_raw.txt`（每次 500~600 行），**逐段翻译**，并记录图注对应
  （书中的图，如乌鸦图示，转成对应文字"笔记"）。
- 代码段跳过翻译；表格转 HTML table；清单类内容也逐条翻译不合并。

### ⑥ 写构建脚本

`build_chN.py` 顶部 `from book_theme import P, LI, CODE, INLINE, H, img_b64, page_mark, page`，
正文写在 f-string `body` 里。**f-string 内 P()/LI() 必须写成 `{P(...)}` 才会求值**；
代码块抽成普通字符串变量 `CODE_X = '''...'''` 再用 `+ CODE_X` 拼接。
完整模板见 `scripts/book_theme.py` 文件头 docstring。

### ⑦ 后处理补花括号

```bash
python3 scripts/fix_braces.py build_chN.py
```

遍历行：以 `P('`/`LI('` 开头的行首补 `{`，向后找第一个以 `)` 结尾的行尾补 `}`。
不处理 `img_b64(`/`page(` 调用行，避免误把 `}` 加到末尾 `page()` 行。

### ⑧ 运行生成

```bash
python3 build_chN.py     # 脚本打印文件名与 KB 数即成功
```

### ⑨ 串联导航

prev/next 按章号填（ch1 prev=front-matter.html，末章 next=None），
首尾章用 disabled 占位（page() 内已处理）。

### 收尾

- front-matter.html、closing.html（含/不含推荐书目，先与用户约定）、
  `index.html` 总入口（链接全部章节）。
- 用 `python3 -m zipfile -c bilingual_reading.zip *.html` 打包，交付 zip。

## 分支与异常处理

| 触发条件 | 处理方式 |
|---|---|
| 图为 jpx / RGBA / P 模式 | extract_assets.py 统一 convert 为 RGB 再存 JPEG |
| f-string 里含代码块花括号（JSON dict） | 不写在 f-string 里；抽成 `CODE_X = '''...'''` 再 `+ CODE_X` 拼接 |
| `{<P(` 误写 | `sed 's/{<P(/{P(/g'` 修正 |
| 批量补 `}` 误加到末尾 `page()` 行 | fix_braces.py 已避免；仍出现则手动删除该行尾多余的 `}` |
| 用户要求"先看效果再继续" | 只做样板章，暂停等反馈 |
| 用户要求"代码不翻译" | 所有 `<pre><code>` 保留英文原文（默认即如此） |
| 更多排查项 | 见 `references/troubleshooting.md` |

## 资源索引

- `scripts/book_theme.py` — **核心共享模块**：CSS/JS/页面骨架 + P、LI、CODE、
  INLINE、H、img_b64、page_mark、page 函数。改样式只改这里。
- `scripts/extract_assets.py` — 步骤 ③④：抽图、压缩、转 base64 写 assets/。
- `scripts/fix_braces.py` — 步骤 ⑦：批量补 f-string 花括号。
- `references/style-guide.md` — 样式与交互规范细节（配色、布局、组件、验收对照）。
- `references/troubleshooting.md` — 问题排查表与可复用经验。

## 验收清单

- [ ] 样板章样式经用户确认（中文浅蓝底、列表项中文同规格、页码标记存在）
- [ ] 原文逐段全译、代码块未翻译、图片 base64 内嵌可离线打开
- [ ] 每章 HTML 可独立打开，目录可折叠，锚点跳转正常
- [ ] 🌐 按钮三态循环，翻页后保持（localStorage）
- [ ] 上下章链接串联正确，首尾章按钮置灰
- [ ] 全部文件 UTF-8、文件名小写连字符，zip 打包交付
