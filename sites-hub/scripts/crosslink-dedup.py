"""
§8.68 P2 dups 高频概念类加跨站段落
读 dedup-suggestions.md 找高频概念类（≥3 站），在每个重复文件末尾加跨站段落。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEDUP_MD = ROOT / 'sites-hub' / 'reports' / 'dedup-suggestions.md'
MARKER = '<!-- xlink-dedup:do-not-edit -->'


def parse_dedup_md():
    """读 dedup-suggestions.md 提取概念类（≥3 站）dups"""
    if not DEDUP_MD.exists():
        print(f'ERROR: {DEDUP_MD} not found')
        return []

    text = DEDUP_MD.read_text()
    lines = text.split('\n')

    # 找"## 一、概念类重复"段
    in_concept = False
    high_freq = []
    for line in lines:
        if line.startswith('## 一、'):
            in_concept = True
            continue
        if line.startswith('## 二、'):
            in_concept = False
            break
        if not in_concept:
            continue
        # 匹配表格行: | 标题 | 主题 | N | site1, site2 |
        m = re.match(r'^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*$', line)
        if not m:
            continue
        title, theme, count, sites_str = m.groups()
        n = int(count)
        if n < 3:  # 只处理 ≥ 3 站的
            continue
        sites = [s.strip() for s in sites_str.split(',')]
        high_freq.append({
            'title': title,
            'theme': theme,
            'count': n,
            'sites': sites,
        })
    return high_freq


def find_files_for_title(title: str, sites: list[str]) -> list[Path]:
    """找包含该标题的 md 文件"""
    title_stripped = title.replace('🔧', '').replace('📚', '').replace('📊', '').replace('🧰', '').strip()
    out = []
    for site in sites:
        site_dir = ROOT / f'{site}-html' / 'docs'
        if not site_dir.exists():
            site_dir = ROOT / 'java-web-manual' / 'docs' if site == 'java' else None
        if not site_dir or not site_dir.exists():
            continue
        for f in site_dir.rglob('*.md'):
            text = f.read_text(errors='replace')
            if title_stripped in text:
                out.append(f)
    return out


# §8.68 P2 dups 高频概念类加跨站段落（v2：每个重复页指向权威站）
# 权威站优先级：observability > architecture > system-design > devops
# §8.68.2 fix：去掉"主版本"概念，改用"权威站"，让每个重复页都有合理跳转
PRIORITY_SITES = ['observability', 'architecture', 'system-design', 'devops']


def append_xlink_paragraph(file: Path, title: str, sites: list[str]):
    """在文件末尾追加跨站段落"""
    text = file.read_text(errors='replace')
    if MARKER in text:
        return False

    # §8.68.2：去掉"主版本"概念，改用"权威站"（所有重复页都指向它）
    # §8.68.3：标题 → 权威站映射（专题类 dups 指向专题站）
    # §8.68.4 fix：title_clean 是去 emoji 后的值，字典 key 也去 emoji
    TITLE_AUTHORITY = {
        '监控告警': 'observability',
        '常用场景快速索引': 'redis',  # redis 的场景索引最常用
        '告警规则': 'observability',
        'Prometheus 告警规则': 'observability',
    }
    title_clean = title.replace('🔧', '').replace('📚', '').replace('📊', '').replace('🧰', '').replace('🚨', '').strip()
    if title_clean in TITLE_AUTHORITY:
        authority = TITLE_AUTHORITY[title_clean]
    else:
        authority = None
        for prio in PRIORITY_SITES:
            if prio in sites:
                authority = prio
                break
    if not authority:
        authority = sites[0]

    others = [s for s in sites if s != authority]
    auth_link = 'java-web-manual' if authority == 'java' else authority
    auth_url = f'https://java-px.bot.cd/{auth_link}/'

    other_links = []
    for o in others:
        o_link = 'java-web-manual' if o == 'java' else o
        other_links.append(f'[{o}](https://java-px.bot.cd/{o_link}/)')

    section = f"""

## 📚 跨站参考：{title}

{MARKER}

本节在 {len(sites)} 站展开，最权威版本位于 **{authority}** 站（[{auth_url}]({auth_url})）。

其他站参考：{ ' / '.join(other_links) }

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
"""
    file.write_text(text.rstrip() + section)
    return True


def main():
    high_freq = parse_dedup_md()
    if not high_freq:
        print('no high-freq concept dups')
        return

    print(f'高频概念类 dups (≥3 站): {len(high_freq)} 组')
    added = 0
    skipped = 0
    for d in high_freq:
        files = find_files_for_title(d['title'], d['sites'])
        print(f'\n  [{d["theme"]}] "{d["title"]}" ({d["count"]} 站 / {len(files)} 文件)')
        for f in files:
            if append_xlink_paragraph(f, d['title'], d['sites']):
                added += 1
                print(f'    ✓ {f.relative_to(ROOT)}')
            else:
                skipped += 1
    print(f'\n=== Summary ===')
    print(f'added: {added}')
    print(f'skipped (already): {skipped}')


if __name__ == '__main__':
    main()
