"""
§8.80 B-1: frontmatter 缺 date 自动补全（基于 git log 首次提交日期）

对所有 *-html/docs/**/*.md 文件：
- 若 frontmatter 缺 date / lastUpdated / updated 字段
- 用 git log --follow --diff-filter=A --format=%cI 取该文件首次提交日期
- 在 title 行后插入 `date: YYYY-MM-DD` + marker（idempotent）

用法：
  python3 sites-hub/scripts/add-frontmatter-dates.py           # dry-run
  python3 sites-hub/scripts/add-frontmatter-dates.py --apply   # 写入
"""
import datetime
from typing import Optional
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SITES_ROOT = ROOT
MARKER = '# date-auto-injected'


def has_date(fm: str) -> bool:
    return any(re.search(rf'^{k}\s*:', fm, re.M) for k in ('date', 'lastUpdated', 'updated'))


def get_git_first_date(path: Path):
    try:
        r = subprocess.run(
            ['git', 'log', '--follow', '--diff-filter=A', '--format=%cI', '--', str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        iso = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else None
        if iso:
            return iso.split('T')[0]
    except Exception:
        pass
    try:
        mtime = path.stat().st_mtime
        return datetime.datetime.fromtimestamp(mtime).date().isoformat()
    except Exception:
        return None


def add_date(path: Path, date: str) -> bool:
    text = path.read_text(encoding='utf-8')
    if MARKER in text:
        return False
    m = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', text, re.S)
    if not m:
        return False
    pre, fm, post = m.group(1), m.group(2), m.group(3)
    if has_date(fm):
        return False
    lines = fm.split('\n')
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and re.match(r'^title\s*:', line):
            new_lines.append(f'date: {date}  {MARKER}')
            inserted = True
    if not inserted:
        new_lines.insert(0, f'date: {date}  {MARKER}')
    new_fm = '\n'.join(new_lines)
    new_text = pre + new_fm + post + text[m.end():]
    path.write_text(new_text, encoding='utf-8')
    return True


def main():
    apply = '--apply' in sys.argv
    sites = sorted([d for d in SITES_ROOT.iterdir()
                    if d.is_dir() and (d / 'docs').exists() and d.name not in ('sites-hub', 'node_modules')])
    stats = []
    for site in sites:
        s_files = s_updated = 0
        for md in (site / 'docs').rglob('*.md'):
            s_files += 1
            try:
                t = md.read_text(encoding='utf-8', errors='ignore')[:500]
            except Exception:
                continue
            fm_m = re.match(r'^---\s*\n(.*?)\n---', t, re.S)
            if not fm_m:
                continue
            if has_date(fm_m.group(1)):
                continue
            if MARKER in md.read_text(encoding='utf-8', errors='ignore'):
                continue
            date = get_git_first_date(md)
            if not date:
                continue
            if apply:
                if add_date(md, date):
                    s_updated += 1
            else:
                s_updated += 1
        short = site.name.replace('-html', '')
        stats.append((short, s_files, s_updated))

    mode = 'APPLY' if apply else 'DRY-RUN'
    print(f'=== §8.80 B-1 frontmatter date 自动补全 ({mode}) ===')
    print(f"{'site':<18} {'files':>6} {'updated':>8}")
    print('-' * 36)
    total_f = total_u = 0
    for s, f, u in stats:
        if u > 0:
            print(f'{s:<18} {f:>6} {u:>8}')
        total_f += f
        total_u += u
    print('-' * 36)
    print(f"{'TOTAL':<18} {total_f:>6} {total_u:>8}")


if __name__ == '__main__':
    main()
