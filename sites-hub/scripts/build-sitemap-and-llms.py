#!/usr/bin/env python3
"""
build-sitemap-and-llms.py — C12 站点地图 + AI 索引文件生成器

输入：28 个子站 docs/**/*.md
输出：
  1. sitemap.xml（28 子站各一份 + 主门户聚合版）
  2. llms.txt（28 子站各一份 + 主门户聚合版，列出 URL + 标题 + 摘要）
  3. llms-full.txt（主门户聚合版，含完整正文）

URL base: https://java-px.bot.cd/

运行：
  python3 sites-hub/scripts/build-sitemap-and-llms.py
  # 输出到 www/（主门户）+ sites-hub/dist/<site>/（子站）
"""
from __future__ import annotations
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent.parent
SITES_SH = ROOT / 'sites-hub' / 'scripts' / 'sites.sh'
WWW_DIR = ROOT / 'www'
DIST_DIR = ROOT / 'sites-hub' / 'dist'
BASE_URL = 'https://java-px.bot.cd'

def load_sites() -> list[str]:
    """从 sites.sh 读 SITES 数组"""
    out = subprocess.run(
        ['bash', '-c', f'source {SITES_SH} && printf "%s\\n" "${{SITES[@]}}"'],
        capture_output=True, text=True, check=True,
    )
    return [s.strip() for s in out.stdout.split('\n') if s.strip()]

def site_to_project(site: str) -> str:
    """从 sites.sh 读 site→project_dir 映射"""
    out = subprocess.run(
        ['bash', '-c', f'source {SITES_SH} && site_to_project {site}'],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """简单 frontmatter parser"""
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for ln in m.group(1).split('\n'):
        if ':' in ln and not ln.startswith(' '):
            k, _, v = ln.partition(':')
            fm[k.strip()] = v.strip().strip('"\'')
    return fm, m.group(2)

def get_title(text: str, fm: dict) -> str:
    """从 frontmatter title 或正文首个 h1"""
    if 'title' in fm:
        return fm['title']
    m = re.search(r'^#\s+(.+?)$', text, re.MULTILINE)
    return m.group(1).strip() if m else 'Untitled'

def get_summary(text: str, max_chars: int = 200) -> str:
    """正文前 max_chars 字符作为摘要（跳过代码块）"""
    in_code = False
    out = []
    for ln in text.split('\n'):
        s = ln.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code or not s or s.startswith('#'):
            continue
        out.append(s)
        if sum(len(x) for x in out) > max_chars:
            break
    summary = ' '.join(out)[:max_chars].strip()
    return summary or '(暂无摘要)'

def scan_site(site: str) -> list[dict]:
    """扫描一个子站所有 .md，返回页面元数据列表"""
    project = site_to_project(site)
    docs_dir = ROOT / project / 'docs'
    if not docs_dir.exists():
        return []
    
    pages = []
    for md_path in sorted(docs_dir.rglob('*.md')):
        rel = md_path.relative_to(docs_dir)
        url_path = '/' + str(rel.with_suffix(''))
        # 读 frontmatter + 提取元数据
        try:
            text = md_path.read_text(errors='replace')
        except Exception:
            continue
        fm, body = parse_frontmatter(text)
        pages.append({
            'site': site,
            'path': url_path,
            'title': get_title(body, fm),
            'summary': get_summary(body),
            'description': fm.get('description', ''),
            'date': fm.get('date', ''),
            'mtime': datetime.fromtimestamp(md_path.stat().st_mtime).isoformat(),
            'rel_path': str(rel),
            'words': len(body),
            'full_text': body,  # 仅用于 llms-full.txt
        })
    return pages

def build_sitemap_xml(pages: list[dict], site: str | None = None) -> str:
    """生成 sitemap.xml"""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        url = f"{BASE_URL}/{p['site']}{p['path']}" if site is None else f"{BASE_URL}/{site}{p['path']}"
        # 首页特殊路径：'/'
        if p['path'] == '/index' or p['path'] == '/':
            url = f"{BASE_URL}/{p['site']}/" if site is None else f"{BASE_URL}/{site}/"
        lines.append('  <url>')
        lines.append(f'    <loc>{escape(url)}</loc>')
        if p.get('date'):
            lines.append(f'    <lastmod>{p["date"]}</lastmod>')
        elif p.get('mtime'):
            lines.append(f'    <lastmod>{p["mtime"][:10]}</lastmod>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'

def build_llms_txt(pages: list[dict], site: str | None = None, full: bool = False) -> str:
    """生成 llms.txt (或 llms-full.txt)"""
    title_site = f'{site} 子站' if site else 'Scholar\'s Atlas 跨站知识图谱'
    out = [f'# {title_site}', '']
    out.append(f'> 自动生成 by sites-hub/scripts/build-sitemap-and-llms.py（C12）')
    out.append(f'> {len(pages)} 个文档页 · {sum(p["words"] for p in pages):,} 字')
    out.append(f'> 生成时间：{datetime.now().isoformat()[:19]}')
    out.append('')
    
    for p in pages:
        url = f"{BASE_URL}/{p['site']}{p['path']}" if site is None else f"{BASE_URL}/{site}{p['path']}"
        out.append(f'## [{p["title"]}]({url})')
        if p['description']:
            out.append(f'> {p["description"]}')
        elif p['summary']:
            out.append(f'> {p["summary"]}')
        out.append('')
        if full:
            # 包含完整正文（去掉 frontmatter，保留 markdown）
            out.append(p['full_text'].strip())
            out.append('')
            out.append('---')
            out.append('')
    return '\n'.join(out)

def main():
    sites = load_sites()
    print(f'扫描 {len(sites)} 个子站...')
    
    WWW_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    all_pages = []
    site_pages = {}
    
    for site in sites:
        pages = scan_site(site)
        site_pages[site] = pages
        all_pages.extend(pages)
        print(f'  {site:<22} {len(pages)} 页')
    
    # 1. 每个子站 sitemap.xml + llms.txt
    for site, pages in site_pages.items():
        site_dist = DIST_DIR / site
        site_dist.mkdir(parents=True, exist_ok=True)
        (site_dist / 'sitemap.xml').write_text(build_sitemap_xml(pages, site))
        (site_dist / 'llms.txt').write_text(build_llms_txt(pages, site, full=False))
        # llms-full.txt 仅主门户，避免巨型文件
    print(f'\n✓ 28 站 sitemap.xml + llms.txt 写入 {DIST_DIR}/<site>/')
    
    # 2. 主门户聚合 sitemap.xml + llms.txt + llms-full.txt
    (WWW_DIR / 'sitemap.xml').write_text(build_sitemap_xml(all_pages))
    (WWW_DIR / 'llms.txt').write_text(build_llms_txt(all_pages, full=False))
    (WWW_DIR / 'llms-full.txt').write_text(build_llms_txt(all_pages, full=True))
    
    total_words = sum(p['words'] for p in all_pages)
    print(f'✓ 主门户 sitemap.xml ({len(all_pages)} URL)')
    print(f'✓ 主门户 llms.txt ({len(all_pages)} 摘要)')
    print(f'✓ 主门户 llms-full.txt ({len(all_pages)} 全文 / {total_words:,} 字 / {len((WWW_DIR / "llms-full.txt").read_text()):,} 字节)')

if __name__ == '__main__':
    main()
