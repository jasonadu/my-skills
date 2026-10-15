# my-skills

个人 Skill 仓库，每个目录是一个可独立安装的标准 Skill（含 `SKILL.md` 及配套
`scripts/`、`references/` 资源）。

## Skills 列表

| Skill | 说明 |
|---|---|
| [bilingual-reading](./bilingual-reading/) | 将英文 PDF（技术书、教程、手册等）转换为逐段中英对照、图片 base64 内嵌、带左侧可折叠目录导航的离线多文件 HTML 阅读版。 |

## 目录结构

```
my-skills/
├── README.md
└── bilingual-reading/
    ├── SKILL.md                    # Skill 入口（YAML frontmatter + 工作流说明）
    ├── scripts/
    │   ├── book_theme.py           # 共享页面主题模块（CSS/JS/骨架 + P/LI/CODE/H 等函数）
    │   ├── extract_assets.py       # 从 PDF 抽图、压缩、转 base64
    │   └── fix_braces.py           # 批量修正构建脚本 f-string 花括号
    └── references/
        ├── style-guide.md          # 页面样式与交互规范
        └── troubleshooting.md      # 问题排查与可复用经验
```

## 安装

将需要的 Skill 目录复制到 Agent 的用户 Skill 目录（路径以 `workspace/.user_skills`
结尾）下即可：

```bash
cd ~/.doubao/agent_mode/workspace/.user_skills   # 路径随环境而异
git clone https://github.com/jasonadu/my-skills.git /tmp/my-skills
cp -r /tmp/my-skills/bilingual-reading ./
```

也可以只克隆单个目录后整体放入。Skill 被加载后，Agent 会根据 `SKILL.md`
frontmatter 中的 `name` 与 `description` 自动判断触发场景。

## 依赖

- Python 3.8+
- `bilingual-reading` 需要：PyMuPDF（`fitz`）、Pillow

```bash
pip install PyMuPDF Pillow
```

## 开发与校验

新增或修改 Skill 后，可用校验脚本检查 frontmatter 与命名规范：

```bash
python3 /path/to/skill-creator-for-work/scripts/quick_validate.py bilingual-reading
```

规范要点：

- 每个 Skill 一个目录，目录名小写连字符（hyphen-case），与 frontmatter 的 `name` 一致；
- `SKILL.md` 必须包含 YAML frontmatter，且仅含 `name`、`description` 等允许字段；
- 可执行脚本放 `scripts/`，按需加载的文档放 `references/`，输出用素材放 `assets/`；
- Skill 目录内不添加 README、CHANGELOG 等额外说明文件。
