"""
§8.77 新站 mermaid 章节结构图批量注入器

为 game / android / iot 三新站的每个章 README.md（21 个）末尾注入一张
mermaid 图，列出该章所有子页面为节点。

- 章路径：docs/01-foo/README.md（自动扫描）
- 子页：章目录下除 README.md 外的所有 .md
- mermaid 内容：基于子页 frontmatter title 自动生成节点标签
- marker：<!-- mermaid-injected:do-not-edit -->

用法：
  python3 sites-hub/scripts/inject-mermaid-chapters.py            # dry-run
  python3 sites-hub/scripts/inject-mermaid-chapters.py --apply     # 实际写入
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# §8.77 三新站
NEW_SITES = ['game', 'android', 'iot']

MARKER = '<!-- mermaid-injected:do-not-edit -->'
SECTION_HEADER = '## 🗺 章节目录图'


def extract_title(p: Path) -> str:
    """从 frontmatter 提取 title，否则用文件名"""
    text = p.read_text()
    m = re.search(r'^---\s*\ntitle:\s*([^\n]+)\s*\n---', text, re.M)
    if m:
        return m.group(1).strip().strip('"').strip("'")
    # fallback: 文件名
    return p.stem


def build_mermaid(chapter_dir: Path, chapter_name: str) -> str:
    """根据章目录生成 mermaid 图"""
    chapter_readme = chapter_dir / 'README.md'
    # 收集子页（除 README.md 外）
    children = sorted([p for p in chapter_dir.glob('*.md') if p.name != 'README.md'])

    if not children:
        return ''

    lines = ['```mermaid', 'graph LR']
    # 中心节点
    lines.append(f'  ROOT["{chapter_name}"]')

    # 子页节点 + 连接
    for child in children:
        title = extract_title(child)
        node_id = child.stem.replace('-', '_')
        lines.append(f'  {node_id}["{title}"]')
        lines.append(f'  ROOT --> {node_id}')
    lines.append('```')
    return '\n'.join(lines)


def main():
    apply = '--apply' in sys.argv
    if not apply:
        print('=== DRY-RUN（加 --apply 真正写入）===')

    stats = {'injected': 0, 'already_present': 0, 'no_children': 0}

    for site in NEW_SITES:
        site_dir = ROOT / f'{site}-html' / 'docs'
        if not site_dir.exists():
            print(f'WARN {site}: {site_dir} 不存在')
            continue
        # 站根 README + 所有章 README
        candidates = [site_dir / 'README.md']
        candidates += sorted(p / 'README.md' for p in site_dir.iterdir() if p.is_dir())

        for readme in candidates:
            if not readme.exists():
                continue
            text = readme.read_text()
            if MARKER in text:
                stats['already_present'] += 1
                continue

            # 站根 README.md 用站点名作为章名
            if readme.parent == site_dir:
                chapter_name = site
                chapter_dir = site_dir
            else:
                chapter_dir = readme.parent
                chapter_name = readme.parent.name

            children = [p for p in chapter_dir.glob('*.md') if p.name != 'README.md']
            if not children:
                stats['no_children'] += 1
                continue

            mermaid = build_mermaid(chapter_dir, chapter_name)
            if not mermaid:
                continue

            section = f"\n\n{SECTION_HEADER}\n\n{MARKER}\n\n{mermaid}\n"

            rel = readme.relative_to(ROOT)
            if apply:
                readme.write_text(text.rstrip() + section)
                stats['injected'] += 1
                print(f'✓ {rel} (+{len(children)} nodes)')
            else:
                print(f'  [DRY] {rel} (+{len(children)} nodes)')

    print('\n=== Summary ===')
    print(f'mode: {"APPLY" if apply else "DRY-RUN"}')
    print(f'injected:         {stats["injected"]}')
    print(f'already present:  {stats["already_present"]}')
    print(f'no children skip: {stats["no_children"]}')


if __name__ == '__main__':
    main()
