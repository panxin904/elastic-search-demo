"""
§8.64 C5 增强：聚合 feed.xml 改为 git log 驱动
按 commit 时间倒序，每个 commit → 1 RSS item
- title：commit message（去 type 前缀）
- link：GitHub commit URL
- pubDate：commit 时间
- description：commit type + scope + 影响文件数

用法：
  python3 build-feed-from-git.py [--days 14] [--limit 50] [--output sites-hub/www/feed.xml]
"""
import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
# §8.64 独立输出，不覆盖 www/feed.xml（page-based）
DEFAULT_OUTPUT = ROOT / 'sites-hub' / 'www' / 'feeds' / 'git-log.xml'
GITHUB_REPO = 'https://github.com/panxin904/elastic-search-demo'

# Conventional Commits 类型 → emoji
TYPE_ICON = {
    'feat': '✨', 'fix': '🐛', 'refactor': '♻️', 'perf': '⚡',
    'docs': '📚', 'chore': '🔧', 'style': '💎', 'test': '🧪',
    'build': '📦', 'ci': '🤖',
}
# 跳过纯 CI/Chore 的 commit（不展示给最终用户）
SKIP_TYPES = {'ci', 'chore', 'build', 'style'}


def get_commits(days: int, limit: int) -> list[dict]:
    """git log --since=N.days"""
    since = f'{days}.days'
    result = subprocess.run(
        ['git', 'log', f'--since={since}', '--pretty=format:%H|%h|%ai|%s', f'--max-count={limit * 2}'],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        print(f'ERROR: git log failed: {result.stderr}', file=sys.stderr)
        return []

    commits = []
    for line in result.stdout.split('\n'):
        if not line.strip():
            continue
        parts = line.split('|', 3)
        if len(parts) != 4:
            continue
        sha, short_sha, date_str, subject = parts
        # 解析 Conventional Commits
        m = re.match(r'^(\w+)(?:\(([^)]+)\))?:\s*(.+)$', subject)
        if m:
            ctype, scope, desc = m.groups()
        else:
            ctype, scope, desc = 'other', '', subject
        commits.append({
            'sha': sha,
            'short_sha': short_sha,
            'date': date_str.strip(),
            'type': ctype,
            'scope': scope or '',
            'desc': desc.strip(),
        })
    return commits


def get_files_changed(sha: str) -> int:
    """git show --stat 看变更文件数"""
    result = subprocess.run(
        ['git', 'show', '--stat', '--format=', sha],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        return 0
    # 统计 | 后有数字的行
    return sum(1 for line in result.stdout.split('\n') if re.search(r'\|\s+\d+\s+', line))


def format_rfc822(date_str: str) -> str:
    """git log %ai 格式 → RFC 822 (RSS 2.0 必需)"""
    # '2026-08-25 10:30:45 +0800' → 'Mon, 25 Aug 2026 10:30:45 +0800'
    try:
        # git %ai 格式：2026-08-25 10:30:45 +0800
        dt = datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S %z')
        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    except Exception:
        return date_str


def build_rss(commits: list[dict], limit: int) -> str:
    items_xml = []
    for c in commits[:limit]:
        icon = TYPE_ICON.get(c['type'], '📦')
        scope_str = f" ({c['scope']})" if c['scope'] else ''
        # 标题 = emoji + type + 描述
        title = f"{icon} {c['type']}{scope_str}: {c['desc']}"
        # link → GitHub commit
        link = f"{GITHUB_REPO}/commit/{c['sha']}"
        # description 含 commit hash + 文件数
        n_files = get_files_changed(c['sha'])
        files_str = f' · {n_files} 文件' if n_files > 0 else ''
        desc = f"Commit <code>{c['short_sha']}</code>{files_str}\n\n{escape(c['desc'])}"
        items_xml.append(f"""    <item>
      <title>{escape(title)}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="true">{escape(link)}</guid>
      <description>{desc}</description>
      <pubDate>{format_rfc822(c['date'])}</pubDate>
    </item>""")

    # 过滤掉 SKIP_TYPES
    shown = [c for c in commits if c['type'] not in SKIP_TYPES][:limit]

    # 重新生成（按用户视角过滤后）
    items_xml = []
    for c in shown:
        icon = TYPE_ICON.get(c['type'], '📦')
        scope_str = f" ({c['scope']})" if c['scope'] else ''
        title = f"{icon} {c['type']}{scope_str}: {c['desc']}"
        link = f"{GITHUB_REPO}/commit/{c['sha']}"
        n_files = get_files_changed(c['sha'])
        files_str = f' · {n_files} 文件' if n_files > 0 else ''
        desc = f"Commit <code>{c['short_sha']}</code>{files_str}\n\n{escape(c['desc'])}"
        items_xml.append(f"""    <item>
      <title>{escape(title)}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="true">{escape(link)}</guid>
      <description>{desc}</description>
      <pubDate>{format_rfc822(c['date'])}</pubDate>
    </item>""")

    last_build = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Scholar's Atlas · 最近更新（git log 驱动）</title>
    <link>{GITHUB_REPO}/commits/main</link>
    <atom:link href="https://java-px.bot.cd/feed.xml" rel="self" type="application/rss+xml" />
    <description>按 commit 时间倒序 · 最近 {len(shown)} 条功能/修复/重构 · 跳过 ci/chore/build/style</description>
    <language>zh-cn</language>
    <lastBuildDate>{last_build}</lastBuildDate>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""


def main():
    ap = argparse.ArgumentParser(description='git log → RSS feed')
    ap.add_argument('--days', type=int, default=14, help='最近 N 天（默认 14）')
    ap.add_argument('--limit', type=int, default=50, help='最多 N 条（默认 50）')
    ap.add_argument('--output', type=Path, default=DEFAULT_OUTPUT, help='输出文件')
    ap.add_argument('--include-all', action='store_true', help='包含所有 commit（含 ci/chore）')
    args = ap.parse_args()

    commits = get_commits(args.days, args.limit)
    if not commits:
        print('WARNING: no commits found')
        sys.exit(0)

    if args.include_all:
        shown = commits[:args.limit]
    else:
        shown = [c for c in commits if c['type'] not in SKIP_TYPES][:args.limit]

    rss = build_rss(commits, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rss)
    print(f'✓ {args.output.relative_to(ROOT)}')
    print(f'  total commits: {len(commits)} (since {args.days} days)')
    print(f'  shown: {len(shown)} (skip ci/chore/build/style)')
    types = {}
    for c in shown:
        types[c['type']] = types.get(c['type'], 0) + 1
    for t, n in sorted(types.items(), key=lambda x: -x[1]):
        print(f'    {t}: {n}')


if __name__ == '__main__':
    main()
