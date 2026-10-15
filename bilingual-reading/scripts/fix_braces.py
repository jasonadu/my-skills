#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_braces.py — 修正 build_chN.py 中 f-string 内 P()/LI() 未求值问题。

对应 SOP 第 ⑦ 步：正文写在 f-string body 里时，P()/LI() 必须写成
{P(...)} / {LI(...)} 才会求值。本脚本自动补花括号：

- 匹配行首（可带缩进与 `+ ` 拼接符）后的 P( / LI( 调用，在函数名前补 '{'
- 单行调用：行尾直接补 '}'；跨行调用：向后找第一个以 ')' 结尾的行补 '}'
- 不处理 img_b64( / page( / CODE( 调用行，避免误把 '}' 加到末尾 page() 调用
- 幂等：已是 '{P(' / '+ {P(' 的行跳过，可重复运行

用法:
    python3 fix_braces.py build_chN.py
"""

import argparse
import re


def fix(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    out = []
    i = 0
    fixed = 0
    while i < len(lines):
        line = lines[i]
        # 行首（可含缩进与 + 拼接符）后紧跟 P( / LI( 调用
        m = re.match(r"^(\s*(?:\+\s*)?)(P|LI)\('", line)
        already_fixed = re.match(r"^\s*(?:\+\s*)?\{", line)
        if m and not already_fixed:
            prefix = m.group(1)
            out.append(line[:len(prefix)] + "{" + line[len(prefix):])
            fixed += 1
            i += 1
            if re.search(r"\)\s*$", line.rstrip()):
                # 单行调用：直接在行尾补 }
                out[-1] = out[-1].rstrip("\n") + "}\n"
            else:
                # 跨行调用：向后找第一个以 ')' 结尾的行作为结束行
                while i < len(lines) and not re.search(r"\)\s*$", lines[i].rstrip()):
                    out.append(lines[i])
                    i += 1
                if i < len(lines):
                    out.append(lines[i].rstrip("\n") + "}\n")
                    i += 1
        else:
            out.append(line)
            i += 1

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"fixed {fixed} call(s) in {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    args = ap.parse_args()
    fix(args.path)
