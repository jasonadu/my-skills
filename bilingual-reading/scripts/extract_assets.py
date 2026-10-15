#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_assets.py — 从 PDF 页区间抽取图片、压缩、转 base64。

对应 SOP 第 ③④ 步。输出写为 assets/figN-M.txt（纯 base64 文本），
供 book_theme.img_b64() 内嵌进 HTML。

用法:
    python3 extract_assets.py <pdf_path> <start_page_1based> <end_page_1based> \
        [--out assets] [--max-width 800] [--quality 68]

要点:
- 按 xref 去重，同一图片跨页只导出一份
- jpx(JPEG2000)、RGBA、P 模式统一转 RGB 再存 JPEG（浏览器兼容）
- 宽度超 max_width 等比缩小（LANCZOS），单图压到几十 KB 量级
"""

import argparse
import base64
import io
import os

import fitz  # PyMuPDF
from PIL import Image


def extract_images(pdf_path, start, end, out_dir="assets",
                   max_width=800, quality=68):
    """从 pdf_path 的第 start~end 页（1-based，含两端）抽图。

    返回导出的图片数量。
    """
    doc = fitz.open(pdf_path)
    seen = set()
    count = 0
    os.makedirs(out_dir, exist_ok=True)

    for pno in range(start, end + 1):
        page = doc[pno - 1]  # PyMuPDF 0-based
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            pix = doc.extract_image(xref)
            im = Image.open(io.BytesIO(pix["image"]))

            # jpx / RGBA / P / CMYK → RGB
            if im.mode in ("RGBA", "P", "CMYK", "LA"):
                im = im.convert("RGB")

            # 宽超限等比缩小
            if im.width > max_width:
                h = round(im.height * max_width / im.width)
                im = im.resize((max_width, h), Image.LANCZOS)

            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=quality, optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")

            count += 1
            name = f"fig{pno:02d}-{count}.txt"
            with open(os.path.join(out_dir, name), "w", encoding="ascii") as f:
                f.write(b64)
            print(f"{name}\t{len(buf.getvalue()) // 1024} KB\t"
                  f"{im.width}x{im.height}")
    doc.close()
    print(f"done: {count} image(s) -> {out_dir}/")
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf_path")
    ap.add_argument("start_page", type=int)
    ap.add_argument("end_page", type=int)
    ap.add_argument("--out", default="assets")
    ap.add_argument("--max-width", type=int, default=800)
    ap.add_argument("--quality", type=int, default=68)
    args = ap.parse_args()
    extract_images(args.pdf_path, args.start_page, args.end_page,
                   args.out, args.max_width, args.quality)


if __name__ == "__main__":
    main()
