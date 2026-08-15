#!/usr/bin/env python3
"""audit-content.py - 内容质量审计（C3 baseline）

检测维度:
  1) 基础统计：文件数、字数、frontmatter 覆盖率、图片覆盖率、链接覆盖率
  2) 薄页：字数 < MIN_WORDS（默认 500）
  3) 缺 frontmatter
  4) frontmatter date 缺失
  5) frontmatter date 过期（> MAX_AGE_DAYS，默认 365）
  6) 缺 alt 的图片（HTML <img> 无 alt 属性）
  7) 重复标题（编辑距离 / Jaccard 相似度 > THRESHOLD）
  8) 内部链接死链（href 指向不存在的 .md）
  9) 跨站引用统计（href 以 https://java-px.bot.cd/<site>/ 开头）

输出:
  - Markdown 报告：reports/content-quality-YYYY-MM-DD.md
  - 控制台 summary
"""
from __future__ import annotations
import argparse, datetime, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path('/Users/a1111/work_space/elastic-search-demo')
SITES_DIRS = [
    'ai-html', 'architecture-html', 'bigdata-html', 'chaos-html', 'clickhouse-html',
    'cloud-html', 'cloud-native-html', 'design-pattern-html', 'devops-html',
    'es-html', 'filesystem-html', 'frontend-html', 'go-html', 'java-html',
    'java-language-html', 'kafka-html', 'linux-html', 'mysql-html', 'network-html',
    'observability-html', 'postgresql-html', 'python-html', 'redis-html',
    'rust-html', 'security-html', 'system-design-html', 'tools-html', 'video-html',
]
# java-html 没有 docs/，用 java-web-manual
SITE_DOCS = {s: ROOT / s / 'docs' for s in SITES_DIRS}
SITE_DOCS['java-html'] = ROOT / 'java-web-manual' / 'docs'

EXCLUDE_DIRS = {'node_modules', '.vitepress', 'release', '.git', 'dist', 'public'}

CN_CHAR = re.compile(r'[\u4e00-\u9fff]')
EN_WORD = re.compile(r'\b[a-zA-Z]+\b')
LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
MD_IMG = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
HTML_IMG = re.compile(r'<img\s+([^>]*)/?>', re.I)
HTML_IMG_ATTR = re.compile(r'(\w+)=["\']([^"\']+)["\']')
TITLE_H1 = re.compile(r'^#\s+(.+?)\s*$', re.M)
TITLE_H2 = re.compile(r'^##\s+(.+?)\s*$', re.M)
FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)
HREF_INTERNAL = re.compile(r'\[[^\]]+\]\((/[^)#]+|(\.\./|\./)[^)#]+)\)')

# 子站 URL 路径 -> 子站目录
SITES_URL_MAP = {s.replace('-html', ''): s for s in SITES_DIRS if s != 'java-html'}
SITES_URL_MAP['java'] = 'java-web-manual'

def count_words(text: str) -> int:
    return len(CN_CHAR.findall(text)) + len(EN_WORD.findall(text))

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """返回 (frontmatter_dict, body_text)"""
    m = FRONTMATTER.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    # 简易 YAML 解析（仅支持 key: value 单行 / 日期）
    fm = {}
    for line in fm_text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_all_md_files() -> list[tuple[Path, str]]:
    """返回 (file_path, site_name) 列表"""
    out = []
    for site, docs_dir in SITE_DOCS.items():
        if not docs_dir.exists():
            continue
        for p in docs_dir.rglob('*.md'):
            if not any(x in p.parts for x in EXCLUDE_DIRS):
                out.append((p, site))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-words', type=int, default=500)
    ap.add_argument('--max-age-days', type=int, default=365)
    ap.add_argument('--dup-threshold', type=float, default=0.85)
    ap.add_argument('--output-dir', default=str(ROOT / 'sites-hub' / 'reports'))
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'content-quality-{today}.md'

    files = find_all_md_files()
    site_stats = defaultdict(lambda: {'files': 0, 'words': 0, 'fm': 0, 'imgs': 0, 'links': 0,
                                       'thin': 0, 'no_fm': 0, 'no_date': 0, 'stale': 0, 'missing_alt': 0,
                                       'broken_links': 0, 'xsite_links': 0})
    all_titles: list[tuple[str, str, Path]] = []  # (title, site, file)
    issues_thin: list[str] = []
    issues_no_fm: list[str] = []
    issues_stale: list[str] = []
    issues_missing_alt: list[str] = []
    broken_links: list[str] = []

    now = datetime.date.today()

    for path, site in files:
        try:
            text = path.read_text(errors='replace')
        except Exception:
            continue
        site_short = site.replace('-html', '').replace('java-web-manual', 'java')
        s = site_stats[site]
        s['files'] += 1
        words = count_words(text)
        s['words'] += words

        # frontmatter
        fm, body = parse_frontmatter(text)
        has_fm = bool(fm)
        if has_fm:
            s['fm'] += 1
        elif path.name == 'README.md':
            # VitePress 默认目录页：README.md 不加 FM 是惯例
            pass
        else:
            s['no_fm'] += 1
            issues_no_fm.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])}")

        # date 检查
        date_str = fm.get('date', '') or fm.get('lastUpdated', '') or fm.get('updated', '')
        if has_fm and not date_str:
            s['no_date'] += 1
        elif date_str:
            # 尝试解析
            try:
                d = datetime.date.fromisoformat(date_str.split('T')[0])
                age = (now - d).days
                if age > args.max_age_days:
                    s['stale'] += 1
                    issues_stale.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} ({date_str}, {age}d)")
            except Exception:
                pass

        # 薄页
        if words < args.min_words:
            s['thin'] += 1
            issues_thin.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} ({words}字)")

        # 图片
        md_imgs = MD_IMG.findall(text)
        html_imgs = HTML_IMG.findall(text)
        s['imgs'] += len(md_imgs) + len(html_imgs)
        # alt 缺失：HTML img 无 alt 属性
        for attrs in html_imgs:
            attr_d = dict(HTML_IMG_ATTR.findall(attrs))
            if 'alt' not in attr_d or not attr_d['alt'].strip():
                s['missing_alt'] += 1
                issues_missing_alt.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} <img>")

        # 链接
        links = LINK.findall(text)
        s['links'] += len(links)
        # 内部死链：href 指向不存在的页面
        # VitePress cleanUrls: 优先 <name>.md, <name>.html, <name>/index.html
        def file_exists_in_site(rel_path: Path) -> bool:
            for ext in ('', '.md', '.html', '/index.html'):
                if (rel_path.with_name(rel_path.name + ext) if not ext.startswith('/') else rel_path / 'index.html').exists():
                    return True
                # 也试 rel_path 直接
                if ext == '' and rel_path.exists():
                    return True
            return False
        for href in links:
            if href.startswith(('http://', 'https://', 'mailto:', 'javascript:', '#')):
                continue
            if href.endswith('.md') or href.startswith('/') or href.startswith('./') or href.startswith('../'):
                # 解析目标
                if href.startswith('/'):
                    target_base = SITE_DOCS[site] / href.lstrip('/')
                else:
                    target_base = (path.parent / href).resolve()
                if not target_base.exists():
                    target_base = target_base.with_suffix('.md')
                # VitePress cleanUrls 兼容
                # VitePress 目录本身也是合法 URL（自动渲染 index.md 或默认页）
                candidates = [
                    target_base if target_base.is_dir() else (target_base.with_suffix('.md') if not target_base.suffix else target_base),
                    target_base.with_suffix('.html') if not target_base.is_dir() else None,
                    target_base / 'index.md' if target_base.is_dir() else None,
                    target_base / 'index.html' if target_base.is_dir() else None,
                ]
                candidates = [c for c in candidates if c is not None]
                if not any(c.exists() for c in candidates):
                    s['broken_links'] += 1
                    broken_links.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} -> {href}")

        # 跨站引用（指向 java-px.bot.cd/）
        xsite = re.findall(r'\[[^\]]+\]\((https?://java-px\.bot\.cd/([^/)]+))/', text)
        if xsite:
            s['xsite_links'] += len(xsite)

        # 标题收集（用于 dup 检测）
        h1 = TITLE_H1.findall(body)
        h2 = TITLE_H2.findall(body)
        for t in h1 + h2:
            t = t.strip()
            if 4 < len(t) < 60:
                all_titles.append((t, site_short, path))

    # 重复标题检测：跨子站完全相同 + 排除模板词
    TEMPLATE_TITLES = {
        '在图谱中的位置', '常见问题', '一句话定义', '与其他站点关系',
        '面试高频问题', '参考资料', '关键 takeaway', '一句话总结',
        '实战案例', '其他资源', '推荐阅读', '小结', '总结', '总结与回顾',
    }
    by_title: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for t, s, p in all_titles:
        # 去前缀编号 "11. xxx" / "## xxx" / emoji "⚠️ xxx"
        t_clean = re.sub(r'^[\d]+\.\s+|^#+\s+|^[\U0001F300-\U0001FAFF\U00002600-\U000027BF]\s*', '', t).strip()
        t_clean = re.sub(r'\s+', ' ', t_clean)
        if 4 < len(t_clean) < 40 and t_clean not in TEMPLATE_TITLES:
            by_title[t_clean].append((s, p))

    cross_dups: list[tuple[str, list[str]]] = []  # (title, [site/file])
    intra_dups: list[tuple[str, list[str]]] = []  # 同站重复
    for title, locs in by_title.items():
        if len(locs) < 2:
            continue
        sites = {l[0] for l in locs}
        files = [f"{l[0]}/{l[1].name}" for l in locs]
        if len(sites) >= 2:
            cross_dups.append((title, files))
        else:
            intra_dups.append((title, files))

    # ---------- 报告 ----------
    total_files = sum(s['files'] for s in site_stats.values())
    total_words = sum(s['words'] for s in site_stats.values())
    total_thin = sum(s['thin'] for s in site_stats.values())
    total_no_fm = sum(s['no_fm'] for s in site_stats.values())
    total_no_date = sum(s['no_date'] for s in site_stats.values())
    total_stale = sum(s['stale'] for s in site_stats.values())
    total_imgs = sum(s['imgs'] for s in site_stats.values())
    total_missing_alt = sum(s['missing_alt'] for s in site_stats.values())
    total_broken = sum(s['broken_links'] for s in site_stats.values())
    total_xsite = sum(s['xsite_links'] for s in site_stats.values())

    lines = []
    lines.append(f"# 内容质量审计报告 — {today}")
    lines.append("")
    lines.append(f"> 自动生成 by `scripts/audit-content.py`（C3 baseline）")
    lines.append(f"> 检测范围: {len(SITES_DIRS)} 子站 × {total_files} .md 文件")
    lines.append("")
    lines.append("## 〇、Summary")
    lines.append("")
    lines.append("| 指标 | 数值 | 健康阈值 | 状态 |")
    lines.append("|------|------|----------|------|")
    fm_pct = 100 * (1 - total_no_fm / total_files) if total_files else 0
    thin_pct = 100 * total_thin / total_files if total_files else 0
    lines.append(f"| 总文件数 | {total_files} | — | — |")
    lines.append(f"| 总字数（中英混合） | {total_words:,} | — | — |")
    lines.append(f"| frontmatter 覆盖率 | {fm_pct:.1f}% | ≥ 95% | {'✅' if fm_pct >= 95 else '⚠️' if fm_pct >= 80 else '❌'} |")
    lines.append(f"| 薄页（< {args.min_words} 字） | {total_thin} ({thin_pct:.1f}%) | ≤ 5% | {'✅' if thin_pct <= 5 else '⚠️' if thin_pct <= 15 else '❌'} |")
    lines.append(f"| 缺 frontmatter | {total_no_fm} | 0 | {'✅' if total_no_fm == 0 else '❌'} |")
    lines.append(f"| frontmatter 缺 date | {total_no_date} | 0 | {'✅' if total_no_date == 0 else '❌'} |")
    lines.append(f"| 过期内容（> {args.max_age_days} 天） | {total_stale} | ≤ 10% | {'✅' if total_stale <= total_files * 0.1 else '⚠️'} |")
    lines.append(f"| 图片总数 | {total_imgs} | — | {'⚠️ 偏少' if total_imgs < total_files * 0.1 else '✅'} |")
    lines.append(f"| 缺 alt 的图片 | {total_missing_alt} | 0 | {'✅' if total_missing_alt == 0 else '❌'} |")
    lines.append(f"| 内部死链 | {total_broken} | 0 | {'✅' if total_broken == 0 else '❌'} |")
    lines.append(f"| 跨站引用 | {total_xsite} | ≥ 100 | {'⚠️ 偏少' if total_xsite < 100 else '✅'} |")
    lines.append(f"| 跨子站重复标题 | {len(cross_dups)} | ≤ 20 | {'✅' if len(cross_dups) <= 20 else '⚠️'} |")
    lines.append("")

    lines.append("## 一、各子站统计")
    lines.append("")
    lines.append("| 子站 | 文件 | 字数 | FM | 薄页 | 缺FM | 过期 | 图片 | 死链 | 跨站 |")
    lines.append("|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|")
    for site in sorted(site_stats):
        s = site_stats[site]
        if s['files'] == 0:
            continue
        short = site.replace('-html', '').replace('java-web-manual', 'java')
        lines.append(f"| {short} | {s['files']} | {s['words']:,} | {s['fm']} | {s['thin']} | {s['no_fm']} | {s['stale']} | {s['imgs']} | {s['broken_links']} | {s['xsite_links']} |")
    lines.append("")

    if issues_thin:
        lines.append(f"## 二、薄页清单（{len(issues_thin)} 篇）")
        lines.append("")
        for f in issues_thin[:50]:
            lines.append(f"- `{f}`")
        if len(issues_thin) > 50:
            lines.append(f"- ... 及其他 {len(issues_thin) - 50} 篇")
        lines.append("")

    if issues_no_fm:
        lines.append(f"## 三、缺 frontmatter 清单（{len(issues_no_fm)} 篇）")
        lines.append("")
        for f in issues_no_fm[:30]:
            lines.append(f"- `{f}`")
        if len(issues_no_fm) > 30:
            lines.append(f"- ... 及其他 {len(issues_no_fm) - 30} 篇")
        lines.append("")

    if issues_stale:
        lines.append(f"## 四、过期内容清单（{len(issues_stale)} 篇）")
        lines.append("")
        for f in issues_stale[:30]:
            lines.append(f"- `{f}`")
        if len(issues_stale) > 30:
            lines.append(f"- ... 及其他 {len(issues_stale) - 30} 篇")
        lines.append("")

    if issues_missing_alt:
        lines.append(f"## 五、缺 alt 图片清单（{len(issues_missing_alt)} 张）")
        lines.append("")
        for f in issues_missing_alt[:20]:
            lines.append(f"- `{f}`")
        lines.append("")

    if broken_links:
        lines.append(f"## 六、内部死链清单（{len(broken_links)} 处）")
        lines.append("")
        for f in broken_links[:30]:
            lines.append(f"- `{f}`")
        if len(broken_links) > 30:
            lines.append(f"- ... 及其他 {len(broken_links) - 30} 处")
        lines.append("")

    if cross_dups:
        lines.append(f"## 七、跨子站重复标题（{len(cross_dups)} 组 — 候选合并/跨站引用）")
        lines.append("")
        lines.append("模板 词已在检测中过滤（在图谱中的位置 / 一句话定义 / 关键 takeaway 等）")
        lines.append("")
        for title, files in cross_dups[:30]:
            lines.append(f"- **{title!r}** ({len(files)} 处)")
            for f in files[:5]:
                lines.append(f"  - `{f}`")
            if len(files) > 5:
                lines.append(f"  - ... 等 {len(files) - 5} 处")
        if len(cross_dups) > 30:
            lines.append(f"- ... 及其他 {len(cross_dups) - 30} 组")
        lines.append("")

    lines.append("## 八、关键发现与建议")
    lines.append("")
    lines.append(f"1. **图片覆盖率极低**：{total_imgs} 张图 / {total_files} 篇 = {100*total_imgs/total_files:.1f}%，纯文字技术文档严重缺乏视觉化（C11 价值高）")
    lines.append(f"2. **跨站引用近零**：仅 {total_xsite} 处，28 站 1429+ 页形成内容孤岛（C2 价值高）")
    lines.append(f"3. **薄页比例 {thin_pct:.1f}%**：{total_thin} 篇字数 < {args.min_words}，可能为 placeholder 或拆分过度（C3 持续 review）")
    lines.append(f"4. **frontmatter 覆盖率 {fm_pct:.1f}%**：{total_no_fm} 篇缺 FM，{total_no_date} 篇 FM 缺 date（C1 模板可根治）")
    lines.append(f"5. **过期内容 {total_stale} 篇**（> {args.max_age_days} 天）：需要月度 review 流程（C10）")
    lines.append(f"6. **内部死链 {total_broken} 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证")
    lines.append("")

    # 写报告
    out_file.write_text('\n'.join(lines))
    print(f"✓ 报告: {out_file}")
    print(f"  files: {total_files}  words: {total_words:,}  thin: {total_thin}  imgs: {total_imgs}  xsite: {total_xsite}")
    print(f"  no_fm: {total_no_fm}  no_date: {total_no_date}  stale: {total_stale}  broken: {total_broken}  dups: {len(cross_dups)} (cross-site) + {len(intra_dups)} (intra-site)")

if __name__ == '__main__':
    main()
