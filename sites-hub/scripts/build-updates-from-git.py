#!/usr/bin/env python3
"""
sites-hub/scripts/build-updates-from-git.py

从 git log 自动生成「最近更新」section 的 HTML 片段，
注入到 sites-hub/www/index.html 的 <div id="updates-list"> 容器。

数据流：
  git log --since=N.days --pretty=format:'%h|%ai|%s'
    ↓ 按 prefix 过滤（feat/fix/refactor）
    ↓ Conventional Commits 解析
    ↓ 生成 update-item HTML
    ↓ 替换 index.html 里 <div id="updates-list">...</div>

支持 dry-run（只打印不写文件）。

用法：
  python3 build-updates-from-git.py              # 默认 14 天
  python3 build-updates-from-git.py --days 7     # 7 天
  python3 build-updates-from-git.py --dry-run    # 只打印不写
  python3 build-updates-from-git.py --limit 10   # 限制条数（默认 12）
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_HTML = REPO_ROOT / "sites-hub" / "www" / "index.html"

# 显示的 commit 类型前缀（Conventional Commits）
SHOW_PREFIXES = ("feat", "fix", "refactor")
# commit 类型 → 图标（emoji）
TYPE_ICON = {
    "feat": "✨",
    "fix": "🐛",
    "refactor": "♻️",
}

# 站点 ID → 图标（按站点分类 chip 颜色）
SITE_ICONS = {
    "es": "📚", "redis": "🔧", "kafka": "📨", "mysql": "🐬",
    "postgresql": "🐘", "clickhouse": "🟡", "bigdata": "📊",
    "java": "☕", "java-language": "☕", "springcloud": "☁️",
    "go": "🐹", "rust": "🦀", "python": "🐍", "frontend": "🎨",
    "design-pattern": "🟣", "system-design": "🧠", "architecture": "🏛️",
    "filesystem": "🗄️", "linux": "🐧", "network": "🌐",
    "security": "🛡️", "devops": "⚙️", "chaos": "🔥",
    "observability": "📈", "ai": "🤖", "video": "🎬",
    "tools": "🔨", "cloud": "☁️", "cloud-native": "⛅",
}


def parse_commit(line: str):
    """解析 'hash|date|subject' → dict"""
    parts = line.split("|", 2)
    if len(parts) != 3:
        return None
    h, date_full, subject = parts
    date = date_full.split(" ")[0]  # 2026-08-16 09:14:07 +0800 → 2026-08-16
    return {"hash": h, "date": date, "subject": subject}


def extract_type_scope(subject: str):
    """解析 'feat(c4): title' → (type, scope, title)"""
    m = re.match(r"^(\w+)(?:\(([^)]+)\))?: (.+)$", subject)
    if not m:
        return None, None, subject
    return m.group(1), m.group(2), m.group(3)


def detect_site(scope: str) -> str:
    """从 scope 推测站点 ID：c4/c2 → None（任务），es-html → es"""
    if not scope:
        return None
    s = scope.lower()
    # 匹配 -html 后缀
    if s.endswith("-html"):
        return s[:-5]
    # C 任务 (c1-c12 / c7+1 等) → portal 级
    if re.match(r"^c\d+(\+.+)?$", s):
        return None
    # 已知站点
    if s in SITE_ICONS:
        return s
    return None



def categorize(site: str) -> str:
    """站点 → 首页 chip category"""
    cat_map = {
        "es": "data", "redis": "data", "kafka": "data",
        "mysql": "data", "postgresql": "data", "clickhouse": "data",
        "bigdata": "data",
        "java": "backend", "java-language": "backend",
        "go": "backend", "rust": "backend", "python": "backend",
        "design-pattern": "backend", "system-design": "backend", "chaos": "backend",
        "filesystem": "infra", "linux": "infra", "network": "infra", "cloud": "infra",
        "cloud-native": "infra", "devops": "infra", "iot": "infra",
        "security": "security",
        "architecture": "arch",
        "observability": "ops",
        "ai": "ai", "video": "ai",
        "frontend": "frontend", "tools": "frontend", "android": "frontend", "game": "frontend",
    }
    return cat_map.get(site, "arch")  # portal 级 → arch 类目


def get_commits(days: int, limit: int) -> list[dict]:
    """git log → 过滤后的 commits 列表"""
    cmd = [
        "git", "log",
        f"--since={days} days ago",
        "--no-merges",
        "--pretty=format:%h|%ai|%s",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"[build-updates] git log failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        c = parse_commit(line)
        if not c:
            continue
        ctype, scope, title = extract_type_scope(c["subject"])
        if ctype not in SHOW_PREFIXES:
            continue
        c["type"] = ctype
        c["scope"] = scope
        c["title"] = title
        c["site"] = detect_site(scope)
        c["category"] = categorize(c["site"])
        c["icon"] = TYPE_ICON.get(ctype, "•")
        commits.append(c)

    return commits[:limit]


def render_item(c: dict) -> str:
    """单条 commit → update-item HTML"""
    site = c["site"] or "portal"
    href = f"/{site}/" if site != "portal" else "/"
    return (
        f'        <a class="update-item" href="{href}" data-cat="{c["category"]}">\n'
        f'          <div class="update-date">{c["date"]}</div>\n'
        f'          <div class="update-icon">{c["icon"]}</div>\n'
        f'          <div class="update-body">\n'
        f'            <div class="update-title">{c["title"]}</div>\n'
        f'            <div class="update-desc">'
        f'<code>{c["hash"]}</code> · scope: <code>{c["scope"] or "—"}</code>'
        f'</div>\n'
        f'          </div>\n'
        f'        </a>'
    )


def render_updates(commits: list[dict]) -> str:
    """commit 列表 → updates-grid 内容"""
    return "\n".join(render_item(c) for c in commits)


def inject_into_html(updates_html: str, days: int) -> str:
    """替换 index.html 里 <div id="updates-list">...</div>"""
    html = INDEX_HTML.read_text()
    # 容器标记（成对出现，替换中间内容）
    pattern = re.compile(
        r'(<div id="updates-list">)(.*?)(</div>)',
        re.DOTALL,
    )
    if not pattern.search(html):
        print("[build-updates] WARN: <div id=\"updates-list\"> not found", file=sys.stderr)
        sys.exit(1)
    new_html, n = pattern.subn(
        lambda m: f'{m.group(1)}\n{updates_html}\n      {m.group(3)}',
        html,
    )
    print(f"[build-updates] replaced {n} container(s), {len(updates_html.splitlines())} lines injected")
    return new_html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14, help="时间窗口（天）")
    ap.add_argument("--limit", type=int, default=12, help="最多条数")
    ap.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    args = ap.parse_args()

    commits = get_commits(args.days, args.limit)
    print(f"[build-updates] {len(commits)} commits in {args.days} days (limit {args.limit})")
    for c in commits:
        print(f"  {c['date']} {c['icon']} {c['subject']}")

    updates_html = render_updates(commits)

    if args.dry_run:
        print("\n--- HTML output ---")
        print(updates_html)
        return

    new_html = inject_into_html(updates_html, args.days)
    INDEX_HTML.write_text(new_html)
    print(f"[build-updates] wrote {INDEX_HTML}")


if __name__ == "__main__":
    main()
