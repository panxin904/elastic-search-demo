"""
C2 跨站内容关联注入脚本
读 sites-hub/data/xlink-terms.json，对每个站的 index.md 末尾追加"## 📚 相关阅读"段落
- 已存在则跳过（idempotent）
- 不存在则生成（2-3 行清单）
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TERMS_FILE = ROOT / 'sites-hub' / 'data' / 'xlink-terms.json'
SITES_DIRS = [
    'ai', 'android', 'architecture', 'bigdata', 'chaos', 'clickhouse',
    'cloud-native', 'design-pattern', 'devops', 'es', 'filesystem',
    'frontend', 'game', 'go', 'iot', 'java', 'java-language', 'kafka',
    'linux', 'mysql', 'network', 'observability', 'postgresql', 'python',
    'redis', 'rust', 'security', 'springcloud', 'system-design', 'tools', 'video'
]
SITE_SHORT_TO_DIR = {s.replace('-html', '').replace('java-language', 'java-language'): f"{s.replace('-html', '')}-html" for s in SITES_DIRS}
# 修正：直接 dir → short 映射
DIR_TO_SHORT = {
    'ai': 'ai',
    'android': 'android',
    'architecture': 'architecture',
    'bigdata': 'bigdata',
    'chaos': 'chaos',
    'clickhouse': 'clickhouse',
    'cloud-native': 'cloud-native',
    'design-pattern': 'design-pattern',
    'devops': 'devops',
    'es': 'es',
    'filesystem': 'filesystem',
    'frontend': 'frontend',
    'game': 'game',
    'go': 'go',
    'iot': 'iot',
    'java': 'java',
    # java 用 java-web-manual 目录
    '_java_dir_note': 'see java-web-manual',
    'java-language': 'java-language',
    'kafka': 'kafka',
    'linux': 'linux',
    'mysql': 'mysql',
    'network': 'network',
    'observability': 'observability',
    'postgresql': 'postgresql',
    'python': 'python',
    'redis': 'redis',
    'rust': 'rust',
    'security': 'security',
    'springcloud': 'cloud',  # 旧站已删，cloud 是现名'
    'system-design': 'system-design',
    'tools': 'tools',
    'video': 'video',
}

MARKER = '<!-- xlink-injected:do-not-edit -->'
SECTION_HEADER = '## 📚 相关阅读（跨站导航）'


def main():
    if not TERMS_FILE.exists():
        print(f'ERROR: {TERMS_FILE} not found')
        sys.exit(1)

    terms = json.loads(TERMS_FILE.read_text())
    terms.pop('_meta', None)

    stats = {'injected': [], 'already_present': [], 'missing_dir': [], 'no_terms': []}

    for short, dir_name in DIR_TO_SHORT.items():
        if short not in terms:
            stats['no_terms'].append(short)
            continue
        # 特殊：java 站用 java-web-manual
        if dir_name == 'java':
            index_path = ROOT / 'java-web-manual' / 'docs' / 'index.md'
        else:
            index_path = ROOT / f'{dir_name}-html' / 'docs' / 'index.md'
        if not index_path.exists():
            stats['missing_dir'].append(dir_name)
            continue

        text = index_path.read_text()
        if MARKER in text:
            stats['already_present'].append(short)
            continue

        # 生成"📚 相关阅读"段落
        target = terms[short]
        items = []
        for t in target:
            t_short = t['site']
            # 跳到 java 的链接用 java-web-manual
            link_short = 'java-web-manual' if t_short == 'java' else t_short
            items.append(f"- [{t_short}](https://java-px.bot.cd/{link_short}/)：{t['label']}")

        section = f"\n\n{SECTION_HEADER}\n\n{MARKER}\n\n按主题跨站推荐：\n\n" + "\n".join(items) + "\n"

        # 追加到文件末尾
        index_path.write_text(text.rstrip() + section)
        stats['injected'].append(short)
        print(f'✓ {short:20s} → +{len(items)} cross-site links')

    print('\n=== Summary ===')
    print(f'injected:       {len(stats["injected"])}')
    print(f'already present:{len(stats["already_present"])}')
    print(f'missing dir:    {len(stats["missing_dir"])}')
    print(f'no terms:       {len(stats["no_terms"])}')
    if stats['already_present']:
        print(f'  already: {", ".join(stats["already_present"])}')
    if stats['missing_dir']:
        print(f'  missing: {", ".join(stats["missing_dir"])}')
    if stats['no_terms']:
        print(f'  no terms: {", ".join(stats["no_terms"])}')


if __name__ == '__main__':
    main()
