#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""book_theme.py — 英文 PDF 双语 HTML 阅读版共享页面主题模块。

SOP 中的自建共享模块：统一 CSS/JS/页面骨架，以及 P / LI / CODE / INLINE /
H / img_b64 / page_mark / page 函数。每个 build_chN.py 只写正文内容，
样式一处改、全局生效。

用法（build_chN.py 顶部）:
    from book_theme import P, LI, CODE, INLINE, H, img_b64, page_mark, page

    entries = [
        (2, "Section 1", "第 1 节", "sec-1"),
        (3, "Subsection 1.1", "第 1.1 小节", "sec-1-1"),
    ]
    body = (
        H(2, "sec-1", "Section 1", "第 1 节")
        + P("English paragraph.", "中文译文。")
        + LI("English list item.", "中文条目。")
        + CODE('''{"key": "value"}''')
        + INLINE("run_config")
        + img_b64("assets/fig1-1.txt", "Fig. 1.1 caption.", "图 1.1 图注。")
        + page_mark(12)
    )
    html = page("chapter-01.html", "Chapter 1", "Chapter 1: Getting Started",
                "第 1 章：入门", entries, body, "front-matter.html", "chapter-02.html")
    with open("chapter-01.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("chapter-01.html", len(html.encode("utf-8")) // 1024, "KB")
"""

# ---------------------------------------------------------------- 配色常量
ACCENT = "#2563eb"      # 强调色：标题条、按钮、链接 hover、中文块左色条
ZH_BG = "#f0f6ff"       # 中文段落浅蓝底
ZH_BORDER = "#2563eb"   # 中文块左侧 4px 色条
CODE_BG = "#0f172a"     # 代码块深色底
CODE_INK = "#e2e8f0"    # 代码块浅色字
INK = "#1f2937"         # 正文墨色

# ---------------------------------------------------------------- CSS
CSS = f""":root{{
  --accent:{ACCENT}; --zh-bg:{ZH_BG}; --zh-border:{ZH_BORDER};
  --code-bg:{CODE_BG}; --code-ink:{CODE_INK}; --ink:{INK};
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:#faf6f1;color:var(--ink);
  font:18px/1.7 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
a{{color:var(--accent)}}

/* ---------- 左侧固定目录 ---------- */
nav#toc{{position:fixed;top:0;left:0;bottom:0;width:300px;overflow-y:auto;
  background:#fff;border-right:1px solid #e5e7eb;padding:20px 0;
  transform:translateX(0);transition:transform .25s ease;z-index:20}}
nav#toc.hidden{{transform:translateX(-300px)}}
nav#toc h1{{font-size:15px;padding:0 20px 8px;color:var(--accent);margin:0}}
nav#toc a{{display:block;padding:6px 20px;color:var(--ink);text-decoration:none;
  font-size:14px;line-height:1.5}}
nav#toc a:hover{{background:var(--zh-bg);color:var(--accent)}}
nav#toc a.l1{{font-weight:700}}
nav#toc a.l2{{font-weight:700}}
nav#toc a.l3{{padding-left:40px}}
#tocToggle{{position:fixed;top:12px;left:12px;z-index:30;width:40px;height:40px;
  border:1px solid #e5e7eb;background:#fff;border-radius:8px;font-size:18px;
  cursor:pointer;color:var(--accent);box-shadow:0 1px 4px rgba(0,0,0,.08)}}
#tocToggle:hover{{background:var(--zh-bg)}}

/* ---------- 主内容 ---------- */
main{{margin-left:300px;max-width:900px;padding:24px 40px 96px}}
.chapter-head{{border-bottom:2px solid var(--accent);padding-bottom:12px;margin-bottom:28px}}
.chapter-head .chap-label{{color:var(--accent);font-weight:700;font-size:15px;
  text-transform:uppercase;letter-spacing:.08em}}
.chapter-head h1{{margin:6px 0 4px;font-size:30px}}
.chapter-head .chap-sub{{color:#6b7280;margin:0;font-size:18px}}

/* ---------- 中英对照段落 ---------- */
p.en{{margin:14px 0;transition:background .15s}}
p.en:hover{{background:#eef4ff;border-radius:8px;cursor:pointer}}
p.zh{{display:none;background:var(--zh-bg);border-left:4px solid var(--zh-border);
  border-radius:0 8px 8px 0;padding:10px 16px;margin:6px 0 14px}}
p.zh.show{{display:block}}
/* 列表项中文与 p.zh 同规格（用户反馈后补上） */
li .zh{{display:none;background:var(--zh-bg);border-left:4px solid var(--zh-border);
  border-radius:0 8px 8px 0;padding:10px 16px;margin:6px 0 12px}}
li .zh.show{{display:block}}
/* 行内标题的中文对照（紧跟英文之后，灰色小字） */
.zh-inline{{color:#6b7280;font-weight:400;margin-left:8px}}

/* ---------- 代码块 ---------- */
pre{{background:var(--code-bg);color:var(--code-ink);border-radius:8px;
  padding:14px 16px;overflow-x:auto;font:13.5px/1.6 "SF Mono",Menlo,Consolas,monospace}}
code{{font-family:"SF Mono",Menlo,Consolas,monospace}}
p code,li code{{background:#fde9f3;color:#be185d;border-radius:4px;
  padding:1px 6px;font-size:.9em}}

/* ---------- 表格 ---------- */
table{{border-collapse:collapse;width:100%;margin:14px 0}}
th,td{{border:1px solid #d1d5db;padding:8px 12px;text-align:left;font-size:16px}}
th{{background:#f1f5f9}}

/* ---------- 图片 ---------- */
figure{{margin:20px 0}}
figure img{{max-width:100%;height:auto;border:1px solid #e5e7eb;border-radius:8px}}
figcaption{{color:#6b7280;font-size:15px;margin-top:8px}}

/* ---------- 页码标记 ---------- */
.page-mark{{margin:26px 0 6px;padding-top:8px;border-top:1px dashed #d1d5db;
  color:#9ca3af;font-size:13px;text-align:right}}

/* ---------- 分页按钮 ---------- */
nav.pager{{display:flex;margin-top:44px;border-top:1px solid #e5e7eb;padding-top:18px}}
nav.pager a{{flex:1;text-align:center;padding:12px 8px;text-decoration:none;
  color:var(--ink);border-radius:8px;font-size:16px}}
nav.pager a:hover{{background:var(--zh-bg);color:var(--accent)}}
nav.pager a.disabled{{opacity:.4;pointer-events:none}}
nav.pager a.center{{font-weight:700}}

/* ---------- 右下角模式切换按钮 ---------- */
#modeBtn{{position:fixed;right:20px;bottom:20px;z-index:30;width:52px;height:52px;
  border:none;border-radius:50%;background:var(--accent);color:#fff;font-size:22px;
  cursor:pointer;box-shadow:0 4px 14px rgba(37,99,235,.35)}}
#modeBtn:hover{{filter:brightness(1.08)}}
#modeTip{{position:fixed;right:20px;bottom:80px;z-index:30;background:#111827;
  color:#fff;font-size:13px;padding:6px 10px;border-radius:6px;display:none}}
#modeBtn:hover + #modeTip{{display:block}}

/* ---------- 显示模式（body[data-mode]） ---------- */
body[data-mode="en"] .zh{{display:none !important}}
body[data-mode="zh"] .en{{display:none !important}}
body[data-mode="zh"] .zh{{display:block !important}}

/* ---------- 锚点 / 窄屏 ---------- */
h2,h3{{scroll-margin-top:20px}}
@media (max-width:900px){{
  nav#toc{{transform:translateX(-300px)}}
  nav#toc.show{{transform:translateX(0)}}
  main{{margin-left:0;padding:64px 18px 96px}}
  body.toc-open{{overflow:hidden}}
}}
"""

# ---------------------------------------------------------------- JS
JS = """<script>
(function(){
  var KEY='bilingual-mode';
  var modes=['en','zh','both'];
  var labels={'en':'仅英文','zh':'仅中文','both':'中英对照'};
  var mode=localStorage.getItem(KEY)||'both';
  var toc=document.getElementById('toc');
  var modeBtn=document.getElementById('modeBtn');

  function applyMode(){
    document.body.dataset.mode=mode;
    modeBtn.textContent=mode==='en'?'🌐':(mode==='zh'?'🌐':'🌐');
    modeBtn.title='当前：'+labels[mode]+'，点击切换';
    // 点击展开的中文块在切走再切回时保留展开态（不强制清 .show）
  }
  // 点击英文段落：展开/收起其后紧跟的中文块（仅 both 模式下有意义）
  document.addEventListener('click',function(e){
    var en=e.target.closest('p.en');
    if(!en)return;
    var zh=en.nextElementSibling;
    if(zh&&zh.classList.contains('zh')){
      zh.classList.toggle('show');
    }else{
      // li 内的情形：.zh 在 li 内部
      var z=en.parentElement.querySelector(':scope > .zh');
      if(z)z.classList.toggle('show');
    }
  });
  // 🌐 模式循环
  modeBtn.addEventListener('click',function(){
    mode=modes[(modes.indexOf(mode)+1)%modes.length];
    localStorage.setItem(KEY,mode);
    applyMode();
  });
  // 目录折叠
  var btn=document.getElementById('tocToggle');
  btn.addEventListener('click',function(){
    if(window.matchMedia('(max-width:900px)').matches){
      toc.classList.toggle('show');
      document.body.classList.toggle('toc-open');
    }else{
      toc.classList.toggle('hidden');
    }
  });
  // 窄屏点击目录链接后自动收起抽屉
  toc.addEventListener('click',function(e){
    if(e.target.tagName==='A'&&window.matchMedia('(max-width:900px)').matches){
      toc.classList.remove('show');
      document.body.classList.remove('toc-open');
    }
  });
  applyMode();
})();
</script>"""


# ---------------------------------------------------------------- 内容函数
def P(en, zh):
    """中英对照段落。en 为英文原文，zh 为中文译文（默认隐藏，点击展开）。"""
    return (f'<p class="en" title="点击显示 / 隐藏中文">{en}</p>\n'
            f'<p class="zh">{zh}</p>\n')


def LI(en, zh):
    """中英对照列表项。"""
    return (f'<li><span class="en" title="点击显示 / 隐藏中文">{en}</span>'
            f'<div class="zh">{zh}</div></li>\n')


def CODE(code_text):
    """代码块：保持英文原文不翻译。"""
    return f'<pre><code>{code_text}</code></pre>\n'


def INLINE(code_text):
    """行内代码（粉色底）。"""
    return f'<code>{code_text}</code>'


def H(level, anchor, en, zh):
    """章节标题：英文标题 + 中文对照小字，anchor 供目录锚点跳转。"""
    tag = 'h%d' % level
    return (f'<{tag} id="{anchor}">{en}'
            f'<span class="zh-inline">{zh}</span></{tag}>\n')


def img_b64(data_file, caption_en, caption_zh):
    """图片：读取 assets/figN-M.txt 中的 base64，内嵌 data-URI；图注中英对照。

    data_file 为第 4 步 extract_assets.py 生成的 .txt 文件路径。
    """
    with open(data_file, encoding="utf-8") as f:
        b64 = f.read().strip()
    return (f'<figure><img src="data:image/jpeg;base64,{b64}" alt="{caption_en}">'
            f'<figcaption><span class="en">{caption_en}</span>'
            f'<span class="zh-inline">{caption_zh}</span></figcaption></figure>\n')


def page_mark(pdf_page):
    """页码标记：单独一行显示原 PDF 页码。每译完原书一页后调用一次。"""
    return f'<div class="page-mark">— p.{pdf_page} —</div>\n'


def page(filename, chapter_num_label, title_en, title_zh, entries, body,
         prev, next_):
    """组装完整 HTML 页面。

    filename: 输出文件名（小写连字符，如 chapter-01.html）
    chapter_num_label: 章节号标签，如 "Chapter 1"
    title_en / title_zh: 章标题中英文
    entries: 目录条目，[(level, en, zh, anchor), ...]，level 2 或 3
    body: 正文 HTML（由上方函数拼接）
    prev / next_: 上一章 / 下一章文件名；None 表示没有（按钮置灰）
    """
    toc_links = ['<h1>目录 / Contents</h1>',
                 '<a class="l1" href="index.html">返回总目录</a>']
    for level, en, zh, anchor in entries:
        cls = 'l2' if level == 2 else 'l3'
        toc_links.append(f'<a class="{cls}" href="#{anchor}">{en}'
                         f'<span class="zh-inline">{zh}</span></a>')
    toc_html = '\n'.join(toc_links)

    prev_html = (f'<a class="prev" href="{prev}">← 上一章</a>' if prev
                 else '<a class="prev disabled" aria-disabled="true">上一章</a>')
    next_html = (f'<a class="next" href="{next_}">下一章 →</a>' if next_
                 else '<a class="next disabled" aria-disabled="true">下一章</a>')
    pager = (f'<nav class="pager">{prev_html}'
             f'<a class="center" href="index.html">返回目录</a>'
             f'{next_html}</nav>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_en} — 双语阅读</title>
<style>{CSS}</style>
</head>
<body data-mode="both">
<nav id="toc">{toc_html}
</nav>
<button id="tocToggle" title="折叠 / 展开目录">☰</button>
<main>
<header class="chapter-head">
<span class="chap-label">{chapter_num_label}</span>
<h1>{title_en}</h1>
<p class="chap-sub">{title_zh}</p>
</header>
{body}
{pager}
</main>
<button id="modeBtn" title="切换显示模式">🌐</button>
<div id="modeTip">仅英文 / 仅中文 / 中英对照</div>
{JS}
</body>
</html>
"""


if __name__ == "__main__":
    # 自检：生成一个最小示例页面，验证模板可运行
    sample = (
        H(2, "sec-1", "Section 1", "第 1 节")
        + P("This is an English sentence.", "这是一句英文原文。")
        + "<ul>\n" + LI("First item.", "第一项。") + "</ul>\n"
        + CODE('{"hello": "world"}')
        + page_mark(7)
    )
    html = page("sample.html", "Chapter 0", "Sample Chapter", "示例章节",
                [(2, "Section 1", "第 1 节", "sec-1")], sample, None, "chapter-01.html")
    with open("/tmp/bilingual_sample.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("sample OK:", len(html.encode("utf-8")) // 1024, "KB -> /tmp/bilingual_sample.html")
