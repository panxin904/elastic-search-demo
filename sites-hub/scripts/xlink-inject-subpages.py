"""
§8.76 v2 跨站引用密度补强 · 子页面批量注入器

对 7 个低密度站（cloud/python/system-design/redis/design-pattern/filesystem/network）的
每个站 top-N 子页面（按字节排序，排除 4 个 shell 页），末尾追加"## 🔗 相关阅读"段。

- 复用 xlink-terms.json 中每站的推荐目标站列表
- 每页注入 3 条精简链接（避免长尾占用过多正文）
- marker 标记 idempotent，重跑不重复

用法：
  python3 sites-hub/scripts/xlink-inject-subpages.py           # 默认 dry-run
  python3 sites-hub/scripts/xlink-inject-subpages.py --apply    # 实际写入
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TERMS_FILE = ROOT / 'sites-hub' / 'data' / 'xlink-terms.json'

# §8.76 v2：低密度站清单（每千字 < 0.20 的 7 站），dir → short
LOW_DENSITY_SITES = {
    'springcloud-html': 'cloud',
    'python-html': 'python',
    'system-design-html': 'system-design',
    'redis-html': 'redis',
    'design-pattern-html': 'design-pattern',
    'filesystem-html': 'filesystem',
    'network-html': 'network',
}

# 跳过的 shell 页（已有跨站段或不该注入的页面）
SKIP_FILES = {'index.md', 'mindmap.md', 'cheatsheet.md', 'path.md', 'questions.md', 'comparison.md'}

MARKER = '<!-- xlink-subpage-injected:do-not-edit -->'
SECTION_HEADER = '## 🔗 相关阅读（跨站导航）'
TOP_N_PER_SITE = 6  # 每站挑几个子页面
LINKS_PER_PAGE = 3   # 每页注入几条跨站链接


def pick_target_pages(docs_dir: Path, n: int) -> list[Path]:
    """挑该站 top-n 子页面（按字节排序，跳过 shell 页与已注入页）"""
    candidates = []
    for p in docs_dir.rglob('*.md'):
        if p.name in SKIP_FILES:
            continue
        try:
            t = p.read_text()
        except Exception:
            continue
        if MARKER in t:
            continue
        candidates.append((p.stat().st_size, p))
    candidates.sort(reverse=True)
    return [p for _, p in candidates[:n]]


def main():
    apply = '--apply' in sys.argv
    if not TERMS_FILE.exists():
        print(f'ERROR: {TERMS_FILE} not found')
        sys.exit(1)

    terms = json.loads(TERMS_FILE.read_text())
    terms.pop('_meta', None)

    if not apply:
        print('=== DRY-RUN（加 --apply 真正写入）===')

    total_injected = 0
    per_site_stats = []

    for dir_name, short in LOW_DENSITY_SITES.items():
        docs_dir = ROOT / dir_name / 'docs'
        if not docs_dir.exists():
            print(f'WARN {short}: {docs_dir} 不存在')
            continue
        if short not in terms:
            print(f'WARN {short}: xlink-terms.json 中无配置')
            continue

        targets = terms[short]
        link_items = targets[:LINKS_PER_PAGE]

        pages = pick_target_pages(docs_dir, TOP_N_PER_SITE)
        site_injected = 0
        for page in pages:
            rel = page.relative_to(ROOT)
            if apply:
                text = page.read_text()
                lines = []
                for t in link_items:
                    t_short = t['site']
                    link_short = 'java-web-manual' if t_short == 'java' else t_short
                    lines.append(f"- [{t_short}](https://java-px.bot.cd/{link_short}/):{t['label']}")
                section = f"\n\n{SECTION_HEADER}\n\n{MARKER}\n\n本页相关主题的跨站入口:\n\n" + "\n".join(lines) + "\n"
                page.write_text(text.rstrip() + section)
                site_injected += 1
            else:
                print(f'  [DRY] {short:15s} -> {rel}')

        per_site_stats.append((short, len(pages), site_injected, len(link_items)))
        total_injected += site_injected

    print('\n=== Summary ===')
    print(f'mode: {"APPLY" if apply else "DRY-RUN"}')
    print(f'sites: {len(LOW_DENSITY_SITES)}  pages picked: {sum(s[1] for s in per_site_stats)}  links injected: {total_injected}')
    print()
    print(f'{"站":15s} {"子页数":>6s} {"注入":>6s} {"每页链接":>8s}')
    for short, picked, inj, lp in per_site_stats:
        print(f'{short:15s} {picked:>6d} {inj:>6d} {lp:>8d}')


if __name__ == '__main__':
    main()
