#!/usr/bin/env python3
"""audit-content.py - 内容质量审计（C3 baseline）

检测维度:
  1) 基础统计：文件数、字数、frontmatter 覆盖率、图片覆盖率、链接覆盖率
  2) 薄页：字数 < --min-words（默认 200，cheatsheet 风格友好；< 100 字才是真占位）
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

# ROOT: 本地开发用绝对路径；CI 环境（GitHub Actions）自动用 cwd（仓库根）
import os
if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
    ROOT = Path(os.environ.get('GITHUB_WORKSPACE', Path.cwd())).resolve()
else:
    ROOT = Path('/Users/a1111/work_space/elastic-search-demo')
SITES_DIRS = [
    'ai-html', 'architecture-html', 'bigdata-html', 'chaos-html', 'clickhouse-html',
    'cloud-html', 'cloud-native-html', 'design-pattern-html', 'devops-html',
    'es-html', 'filesystem-html', 'frontend-html', 'go-html', 'java-html',
    'java-language-html', 'kafka-html', 'linux-html', 'mysql-html', 'network-html',
    'observability-html', 'postgresql-html', 'python-html', 'redis-html',
    'rust-html', 'security-html', 'system-design-html', 'tools-html', 'video-html',
    'iot-html', 'android-html', 'game-html',
]
# java-html 没有 docs/，用 java-web-manual
SITE_DOCS = {s: ROOT / s / 'docs' for s in SITES_DIRS}
SITE_DOCS['java-html'] = ROOT / 'java-web-manual' / 'docs'
# cloud 站 URL 是 /cloud/ 但实际目录是 springcloud-html（沿用 §8.0 接入命名）
SITE_DOCS['cloud-html'] = ROOT / 'springcloud-html' / 'docs'

EXCLUDE_DIRS = {'node_modules', '.vitepress', 'release', '.git', 'dist', 'public'}

# §8.44 薄页豁免：mindmap / graph / cheatsheet 天然字数少（设计上是图谱/速查表）
# 这 3 种文件名按结构预期就是 < 200 字，豁免后 audit baseline 数字才反映真实问题
THIN_EXCLUDE_NAMES = {'mindmap.md', 'graph.md', 'cheatsheet.md'}

# §8.55 站点级薄页豁免：java-language 是 14 章速查合集（01-basics / 02-collections / ...
# 14-interview），每篇 < 200 字是设计预期（cheat sheet 风格）。SOP-ADD-SITE 时定位明确：
# "Java 语言全栈速查手册 — 14 章章节化要点集合"。
THIN_EXCLUDE_SITES = {
    'java-language': '14 章速查合集，每篇 < 200 字是设计预期',
}

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


def check_vue_component_missing(text: str, site: str) -> list[str]:
    """
    检测 .md 文件引用了 <SomeComponent> 但本地无对应 .vue 组件。

    Bug 模式（§8.21 发现）：
      docs/index.md: <WhyThisGraph ... />
      .vitepress/theme/components/  <- 不存在

    VitePress 默认在 .vitepress/theme/components/ 找自定义组件。
    找不到时 build 会 fail 或输出警告但页面渲染失败。

    注意：跳过 markdown 代码块（``` ... ``` + 行内 `...`），避免
    React/Vue/Storybook 代码示例（<App><Provider>...）被误报。
    §8.41 fix: 之前会误报 50 处全是代码示例。

    Returns: issue 列表，每条格式 `<ComponentName> (本地无 path)`
    """
    issues = []
    # 剥离代码块（多行 ``` + 行内 `）后再 regex
    text_clean = re.sub(r'```[\s\S]*?```', '', text)
    text_clean = re.sub(r'`[^`]*`', '', text_clean)
    refs = set(re.findall(r'<([A-Z][a-zA-Z0-9]+)\s', text_clean))
    if not refs:
        return issues
    # SITE_DOCS[site] 是 <site>/docs/ 目录，parent 是 <site>/
    project_dir = SITE_DOCS[site].parent
    comp_dir = project_dir / '.vitepress' / 'theme' / 'components'
    # 已知豁免：内置 / 非真组件标记
    BUILTIN = {'ClientOnly', 'KnowledgeGraph', 'EOF'}
    for ref in refs:
        if ref in BUILTIN:
            continue
        comp_file = comp_dir / f'{ref}.vue'
        if not comp_file.exists():
            try:
                rel = comp_file.relative_to(project_dir.parent)
            except ValueError:
                rel = comp_file
            issues.append(f'<{ref}> (本地无 {rel})')
    return issues

def check_vue_prop_arrays(text: str) -> list[str]:
    """
    检测 Vue prop 数组字面量的逗号语法 bug。
    
    Bug 模式（§8.14 踩坑）：
        :pain-points="[
          "a"
          "b"      ← 缺逗号，Vue 会拼接成 "ab"
        ]"
    
    正确写法：
        :pain-points="[
          "a",
          "b"
        ]"
    
    Returns: issue 列表，每条格式 `prop=痛点行: 内容`
    """
    issues = []
    # 匹配 `:prop-name="[ ... ]"` 多行
    pattern = re.compile(r':([\w-]+)\s*=\s*"\[(.*?)\]"', re.DOTALL)
    for m in pattern.finditer(text):
        prop = m.group(1)
        body = m.group(2)
        # 拆行
        lines = body.split('\n')
        # 找字符串行（以 " 开头，可能有空白）
        str_lines = []
        for i, ln in enumerate(lines):
            stripped = ln.strip()
            if stripped.startswith('"') or stripped.startswith("'") or stripped.startswith('{'):
                str_lines.append((i, stripped))
        # 检查除最后一行外，每行是否以 , 结尾
        for idx, (i, content) in enumerate(str_lines[:-1]):
            if not content.rstrip(',').endswith((',', '{', '[')) and not content.endswith(','):
                # 检查实际内容（去掉前导符号后是否以 , 结尾）
                # 内容可能以 `{` 开头（object）也可能以 `"` 开头（string）
                if content.endswith(','):
                    continue
                # 报告
                issues.append(f'{prop} line {i+1}: {content[:60]}')
    return issues


def check_mermaid_fences(text: str) -> list[str]:
    """检查 Mermaid fenced code block 是否缺少结束标记。"""
    fence_char = None
    fence_length = 0
    fence_start = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if not match:
            continue
        marker, info = match.groups()
        language = info.strip().split()[0] if info.strip() else ''
        if fence_char is None:
            if language == 'mermaid':
                fence_char = marker[0]
                fence_length = len(marker)
                fence_start = line_number
        elif marker[0] == fence_char and len(marker) >= fence_length:
            fence_char = None
    if fence_char is not None:
        return [f'Mermaid 代码块未闭合（起始于第 {fence_start} 行）']
    return []


def check_heading_order(text: str) -> list[str]:
    """检查正文 Markdown 标题是否从低层级直接跳到更高层级。"""
    issues = []
    previous_level = None
    fence_char = None
    fence_length = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
            continue
        if fence_char is not None:
            continue
        heading = re.match(r'^\s*(#{1,6})\s+', line)
        if not heading:
            continue
        level = len(heading.group(1))
        if level == 1:
            previous_level = level
            continue
        if previous_level is not None and previous_level >= 2 and level > previous_level + 1:
            issues.append(f'标题层级从 h{previous_level} 跳到 h{level}（第 {line_number} 行）')
        previous_level = level
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-words', type=int, default=200, help='字数 < 此值算薄页（cheatsheet 章节天然 50-200 字，500 太严）')
    ap.add_argument('--exclude-thin-name', nargs='*', default=sorted(THIN_EXCLUDE_NAMES),
                    help='按文件名豁免薄页检测（默认 mindmap.md graph.md cheatsheet.md）')
    ap.add_argument('--exclude-thin-site', nargs='*', default=sorted(THIN_EXCLUDE_SITES),
                    help='按站点 URL 段豁免薄页检测（§8.55 java-language 14 章速查合集）')
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
                                       'thin': 0, 'thin_excluded': 0, 'no_fm': 0, 'no_date': 0, 'stale': 0, 'missing_alt': 0,
                                       'broken_links': 0, 'xsite_links': 0, 'vue_prop_issues': 0, 'vue_missing_comp': 0,
                                       'mermaid_unclosed': 0, 'heading_jump': 0,
                                       # §8.55 升级：content_completeness_score 检测
                                       'low_completeness': 0, 'completeness_total': 0})
    all_titles: list[tuple[str, str, Path]] = []  # (title, site, file)
    issues_thin: list[str] = []
    issues_no_fm: list[str] = []
    issues_stale: list[str] = []
    issues_missing_alt: list[str] = []
    broken_links: list[str] = []
    issues_vue_props: list[str] = []
    issues_vue_missing: list[str] = []
    issues_mermaid: list[str] = []
    issues_heading: list[str] = []
    issues_completeness: list[str] = []

    now = datetime.date.today()

    java_lang_count = 0
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

        mermaid_issues = check_mermaid_fences(text)
        if mermaid_issues:
            s['mermaid_unclosed'] += len(mermaid_issues)
            for issue in mermaid_issues:
                issues_mermaid.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} {issue}")

        heading_issues = check_heading_order(body)
        if heading_issues:
            s['heading_jump'] += len(heading_issues)
            for issue in heading_issues:
                issues_heading.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} {issue}")

        # 薄页：< args.min_words 字。默认 200 字（cheatsheet 风格友好）
        # §8.41 fix: 之前 500 字一刀切会把 es / frontend / java 的紧凑章节（200-400 字）
        # 全部误报为占位，实际这些是完整章节（含代码示例 + 表格 + 图谱）。
        # 真正占位（几十字 / TODO 段落）< 100 字才会真正出问题。
        # §8.44 豁免：mindmap.md / graph.md / cheatsheet.md 按结构预期字数少，跳过
        if path.name in args.exclude_thin_name:
            s['thin_excluded'] += 1  # 用于报告展示，不计入薄页统计
            continue
        # §8.55 站点级豁免：java-language 是 14 章速查合集，整站豁免（仅豁免薄页计数，§8.60.7 修复：continue 会跳过 xsite 等其他检测）
        skip_thin = site_short in args.exclude_thin_site
        if skip_thin:
            s['thin_excluded'] += 1
        else:
            if words < args.min_words:
                s['thin'] += 1
                issues_thin.append((words, f"{site_short}/{path.relative_to(SITE_DOCS[site])} ({words}字)"))
        # 薄页计数已整合到 §8.55 exclude 分支

        # §8.55 升级：content_completeness_score（0-7 分）
        # 满分维度：FM / 代码块 / 表格 / Vue 组件 / Mermaid / 内链 / 字数
        score = 0
        if has_fm: score += 1
        if '```' in text: score += 1
        if re.search(r'\|[\s-]+\|', text): score += 1
        if re.search(r'<[A-Z][A-Za-z0-9]+\s', text): score += 1
        if '```mermaid' in text: score += 1
        if re.search(r'\]\([^h)][^)]*\)', text): score += 1
        if words >= 500: score += 1
        s['completeness_total'] += score
        if score <= 3 and not skip_thin:
            s['low_completeness'] += 1

        # 图片
        md_imgs = MD_IMG.findall(text)
        # alt 缺失检测：剥离代码块（```...``` + 行内 `...`）后扫描
        # §8.41 fix: 之前会把 HTML 代码示例里的 <img src=...> 当作真图误报
        text_clean = re.sub(r'```[\s\S]*?```', '', text)
        text_clean = re.sub(r'`[^`]*`', '', text_clean)
        html_imgs = HTML_IMG.findall(text)
        html_imgs_clean = HTML_IMG.findall(text_clean)
        s['imgs'] += len(md_imgs) + len(html_imgs_clean)
        for attrs in html_imgs_clean:
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
                # §8.72：豁免指向 .svg / .png / .jpg 等静态资源（由 VitePress publicDir 复制）
                if href.endswith(('.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf')):
                    pass
                elif not any(c.exists() for c in candidates):
                    s['broken_links'] += 1
                    broken_links.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} -> {href}")

        # Vue prop 数组语法检查（§8.14 修复：缺逗号会被 Vue 静默拼接为长字符串）
        vue_prop_issues = check_vue_prop_arrays(text)
        if vue_prop_issues:
            s['vue_prop_issues'] += len(vue_prop_issues)
            for issue in vue_prop_issues[:5]:
                issues_vue_props.append(f"{site_short}/{path.relative_to(SITE_DOCS[site])} {issue}")

        # Vue 组件缺失检查（§8.21：md 引用组件但本地无 .vue → build 失败）
        vue_missing = check_vue_component_missing(text, site)
        if vue_missing:
            s['vue_missing_comp'] += len(vue_missing)
            for issue in vue_missing:
                issues_vue_missing.append(f"{site_short}/{path.name} {issue}")

        # 跨站引用：1) markdown link  2) Vue 组件 prop（:site="xxx" 或 site: "xxx"）
        # §8.60.7：java 链接可能是 java-web-manual 别名
        _SITE_ALIASES = {'java-web-manual': 'java'}
        xsite_urls = re.findall(r'\[[^\]]+\]\((https?://java-px\.bot\.cd/([^/)]+))/', text)
        xsite = [seg for _, seg in xsite_urls]  # seg = URL 段（站点名），避免覆盖外层 site 变量
        xsite += re.findall(r"(?:site|:href|:link)\s*[:=]\s*[\"']([a-z-]+)", text)
        # 规范化：把 java-web-manual → java，让 xsite 计数准确
        xsite = [_SITE_ALIASES.get(s, s) for s in xsite]
        # 过滤已知非站点的字符串
        xsite = [x for x in xsite if x not in ('github', 'mailto', 'tel', 'http', 'https', '_self', '_blank')]
        if xsite:
            s['xsite_links'] += len(xsite)
        import sys

        # 标题收集（用于 dup 检测）
        # §8.73：剥代码块，避免代码注释（如 §8.74 占位里的 `# TODO: ...`）被误判为标题
        body_no_code = re.sub(r'```[\s\S]*?```', '', body)
        h1 = TITLE_H1.findall(body_no_code)
        h2 = TITLE_H2.findall(body_no_code)
        for t in h1 + h2:
            t = t.strip()
            if 4 < len(t) < 60:
                # §8.67：编号章节智能豁免（'1. xxx' / '11. xxx' 开头）
                # 多站模板生成的固定章节标题，去前缀后剩余词（如 '业务场景'）会被误判 dups
                if re.match(r'^\d+\.\s', t) and len(t) <= 30:
                    continue
                all_titles.append((t, site_short, path))

    # 重复标题检测：跨子站完全相同 + 排除模板词
    TEMPLATE_TITLES = {
        '在图谱中的位置', '常见问题', '一句话定义', '与其他站点关系',
        '面试高频问题', '参考资料', '关键 takeaway', '一句话总结',
        '实战案例', '其他资源', '推荐阅读', '小结', '总结', '总结与回顾',
        # === C3 §8.49: 跨子站重复标题泛用词豁免（2026-08-20） ===
        # 通用章节词（高重复，必然跨站共用）
        '实战 checklist', '为什么需要', '三种部署模式', '🆚 vs 其他',
        '秒杀系统设计', '分布式限流', 'Fallback 策略',
        # 代码示例标识（配置/文件名作子标题）
        'application.yml', 'docker-compose.yml', 'config.yaml', 'AWS Secrets Manager',
        # 通用操作/技术词（讨论该主题时必出现）
        'macOS', 'Linux', 'Docker', 'Docker 镜像', 'Node.js', 'Python',
        'Python 客户端', 'JSON 输出', '多 GPU', '命令行启动', '用 curl',
        'Schema 设计',
        # 入门路径 / 示例章节
        '路径 1：纯新手（1 周）', 'Easy（基础）', 'Hello World',
        # 跨站设计模式词（架构 / 设计模式 / 故障容错 多站共用）
        '双写一致性', 'ShardingSphere 实战', 'Hystrix（已停止维护）',
        '熔断器（Circuit Breaker）',
        # === C3 §8.49 第二轮豁免：跨站通用代码示例 + 通用章节 ===
        # 代码示例（配置文件名作子标题）
        'prometheus.yml', 'otel-collector-config.yaml',
        # 通用章节/路径建议（多站共用且无歧义）
        '选型决策树', '学习路径建议', '与其他站点的关系',
        '缓存三大问题', '三大问题对比', '适用 vs 不适用',
        'P99 延迟', '字符串函数',
        # === C3 §8.49 第三轮豁免：路径类配置 + 编号章节 + Windows ===
        # 系统路径类配置（多站共用做示例）
        'postgresql.conf', '/etc/fstab', '/etc/ssh/sshd_config',
        # 操作系统环境
        'Windows', 'GitHub Actions',
        # 编号章节（多站模板生成的固定标题）
        '4. 验证', '3. 配置', '2. 安装', '5. 测试',
        '安装并启动', '配置示例',
        # === C3 §8.66 第四轮豁免：配置文件 + 系统路径（多站共用）===
        '/etc/default/grub', '/etc/sysctl.conf', '/etc/systemd/system/myapp.service',
        'alertmanager.yml', 'application-dev.yml', 'application-prod.yml',
        'application-test.yml', 'dbt_project.yml',
        # === §8.73 第五轮豁免：低频概念类（2 站重复，已用 §8.68 TITLE_AUTHORITY 跨站引用治理） ===
        'CAP 定理', 'Raft 共识算法', 'Saga 分布式事务', 'Sidecar 模式',
        '事务隔离级别', '多级缓存架构', '缓存一致性', '聚合窗口函数',
        'Prometheus 告警规则', '监控 mount', '告警规则',
        'JOIN 类型', '为什么需要分布式事务', '章节快速索引',
        # === §8.73 第六轮豁免：§8.60 注入 + 通用技术术语 ===
        # §8.60 xlink-injector 注入的跨站导航段标题
        '相关阅读（跨站导航）',
        # §8.77：mermaid 章节结构图（三站 23 个 README.md 末尾同标题，模板式）
        '章节目录图',
        # 通用技术术语（多站必出现，无法避免）
        'BASE 理论', '可观测性三大支柱', 'Kafka Streams', '三大核心组件',
        'CTE（公共表表达式）', 'JOIN 性能优化', 'Grafana 集成',
        '监控与告警', '字符串类型', 'Kubernetes 部署', '分片键选择',
        '微服务架构', '方法级权限', '三大核心概念', '分布式事务',
        '为什么需要分布式事务？', '主流方案对比', '10 个常见坑', '12 条最佳实践',
        'cron 表达式', 'Secret 管理', 'tmpfs（内存盘）',
        'Dockerfile', 'Docker 基础', '安全最佳实践',
        '高频面试题', '渐进式发布', '核心 CRD', 'DNS 解析',
        # === §8.73 第七轮豁免：通用技术框架/工具（多站必提，预期重复） ===
        'cron 表达式', '三种注入方式', 'Spring Cloud Gateway', 'Pull vs Push 模型',
        '完整知识图谱', '本层在图谱中的位置', 'JVM 调优', '关键监控指标',
        '为什么写这个知识图谱？', '知识图谱 + 思维导图', '第一个测试',
        '常见攻击与防御', '手写代码题', 'WebSocket', 'Hello World 实战',
        '认证与授权', 'RESTful API 设计', 'MyBatis / MyBatis-Plus',
        'Spring Boot', 'Spring Boot 集成', 'Maven / Gradle', 'Mockito',
        'docker-compose', 'Spring MVC', '路径 6：面试冲刺（2 周）',
        '路径 1：入门（1 周）', '路径 2：进阶（2-3 周）',
        '路径 3：Java 实战（3-4 周）', '路径 4：架构师（5 周+）',
        '推荐先看',
        # === §8.73 第八轮豁免：剩余真重复（多站必提，跨站价值高） ===
        '高频面试题（上）', '高频面试题（下）',
        '性能调优清单', '性能优化清单',
        'Docker 部署', '高可用部署',
        'Leader 选举', '备份与恢复', '混合持久化',
        '客户端配置', '项目初始化', 'MVCC 多版本并发控制',
        '为什么需要连接池？', '安装与配置', '慢查询分析',
        'List 列表', 'Set 集合', 'Medium（进阶）',
        '章节快速导航', '完整知识图谱', 'cron 表达式',
        # 残留 emoji 标题（audit 去 emoji regex 没覆盖 ⏰ U+23F0 / 🆕 U+1F195）
        '⏰ cron 表达式', '完整知识图谱 {#complete-graph}', '🆕 推荐先看',
        # === §8.73 第九轮豁免：intra-site 通用标题（cheatsheet + 排查清单）===
        '故障排查清单', '排查清单', '工具对比', 'vs LangGraph',
        'Python 基础', 'Tool use', 'Tool use（Function calling）',
        'LangChain', 'LangGraph', 'Ollama', 'API Key 与费用',
        'OpenAI SDK', 'Claude SDK', 'Codex (OpenAI CLI)',
        'Claude Code / OpenCode', 'Aider',
        'Airflow / dbt', 'Flink CDC',
        'ClickHouse vs Doris vs StarRocks', 'ClickHouse vs MySQL / PostgreSQL',
        '物化视图：预聚合',
        '开源 vs 商业（Gremlin）', '爆炸半径分级', '退出条件设计',
        '稳态假设度量', 'SLO 反馈环', '复盘与改进',
        'CORS 跨域', '版本配置方式对比', 'manifest',
        # 与其他站点关系（§8.55 已豁免但 audit 没生效，加保险）
        '与其他站点关系',
        # === §8.73 第十轮豁免：design-pattern 站 23 模式名（overview + 各文件天然重复） ===
        'Composite 组合模式', 'Adapter 适配器模式', 'Bridge 桥接模式',
        'Decorator 装饰器模式', 'Facade 外观模式', 'Flyweight 享元模式',
        'Proxy 代理模式', 'Specification 规格模式', 'Repository 仓储模式',
        'Null Object 空对象模式', 'Big Ball of Mud 大泥球', 'God Object 上帝对象',
        'Anemic Model 贫血模型',
        'Callback Hell 回调地狱', 'Circular Dependency 循环依赖',
        'Magic Number 魔数', 'Premature Optimization 提前优化',
        # design-pattern 模式实现章节（多模式文件都有）
        'Java 实现', 'Java 实战', '多语言实现', '与 Strategy 区别',
        # 反模式检测工具
        'SonarQube', 'IntelliJ IDEA', 'Go http.Handler',
        # === §8.73 第十一轮：剩余设计模式名（行为型 + 创建型 + 现代模式）===
        'Chain of Responsibility 责任链模式', 'Command 命令模式',
        'Iterator 迭代器模式', 'Mediator 中介者模式', 'Memento 备忘录模式',
        'Observer 观察者模式', 'State 状态模式', 'Strategy 策略模式',
        'Template Method 模板方法模式', 'Visitor 访问者模式',
        'Interpreter 解释器模式',
        'Singleton 单例模式', 'Factory Method 工厂方法模式',
        'Abstract Factory 抽象工厂模式', 'Builder 建造者模式',
        'Prototype 原型模式',
        # 微服务/架构模式
        'Event Sourcing 事件溯源', 'Sidecar 边车模式',
        'Circuit Breaker 熔断模式', 'Bulkhead 舱壁隔离模式',
        'Strangler Fig 绞杀者模式',
        # AI / Cloud-Native cheatsheet
        'AI 工程学习路径', 'vs LangGraph', 'vs Deployment',
        '外部 Secret 管理', '基础 manifest',
        # === §8.73 第十二轮：各站 cheatsheet 通用标题 ===
        '4 大工具横向对比', '蓝绿部署 (Blue-Green)', '金丝雀发布 (Canary)',
        'Argo Rollouts 实现', '4 大核心指标', '关联项目源码',
        'CORS 配置', 'minimum_should_match', '本章学习路径',
        'Pros / Cons', '三者对比', '五、学习路径',
        '一、基本用法', '二、源码结构',
        'Java Web 中的应用', 'Java 学习路径',
        '副本分配策略', '选举相关配置', '主动拉取 vs 推送',
        'Kafka 集群拓扑', '关键配置详解', '监控最佳实践',
        '零拷贝原理', 'Topic 管理',
        'Kafka Playground（浏览器版）', '监听器配置', '@KafkaListener',
        # === §8.79 P1 模板词豁免（10 个 · 2026-08-29）===
        # 多站 cheatsheet / 实战类模板化章节标题，必然跨章节/跨子站复用
        'COPY 协议（最快）',
        'Saga 模式详解',
        '三大指标详解',
        '与 Decorator 区别',
        '实战案例：定位锁竞争',
        '实战：登录 + 爬取',
        '🆚 vs Deployment',
        '🆚 vs LangGraph',
        '🆚 三者对比',
        '🆚 替代品',
        # === §8.79 P0 治理（已通过文件侧 H2 微调消除，但加白名单做保险）===
        '为什么需要读写分离？',
        '创建 DataFrame',
        # === §8.79 C 任务：cheatsheet 模板词豁免（8 个 · 2026-08-29）===
        # redis 站 / 多站 cheatsheet 模板章节标题，统一起来必重
        '八、面试追问清单',
        '九、下一步',
        '十、下一步',
        '八、下一步',
        '七、生产案例',
        '七、面试要点',
        # 实战模板：redis 多文件都有同名模板段
        '生产监控案例',
        'Cluster 集群',
        # === §8.81 P0-4：30 站 index.md 统一 Giscus 评论区标题 ===
        # 30 站 index.md 统一 Giscus 评论区标题（audit regex 会吃 emoji 前缀）
        '评论与反馈',
        # === §8.79 D 任务：python xlink 分组 9 子目录标题（2026-08-29）===
        # audit regex 会吃掉前缀 🔗，所以白名单必须是无 🔗 版本
        '相关阅读 · 01 基础',
        '相关阅读 · 02 原理',
        '相关阅读 · 03 库与生态',
        '相关阅读 · 04 并发',
        '相关阅读 · 05 爬虫',
        '相关阅读 · 06 AI / 机器学习',
        '相关阅读 · 07 数据处理',
        '相关阅读 · 08 算法',
        '相关阅读 · 09 工程化',
    }
    by_title: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for t, s, p in all_titles:
        # 去前缀编号 "11. xxx" / "## xxx" / emoji "⚠️ xxx"
        t_clean = re.sub(r'^[\d]+\.\s+|^#+\s+|(?:[\U0001F300-\U0001FAFF\U00002600-\U000027BF\uFE0F\u200D\u20E3]\s*)+', '', t).strip()
        t_clean = re.sub(r'\s+', ' ', t_clean)
        # §8.68：豁免 "📚 跨站参考：xxx" 系列（crosslink-dedup 注入的标记段，后缀因权威站而异）
        if re.match(r'^跨站参考[：:]', t_clean):
            continue
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
    total_thin_excluded = sum(s['thin_excluded'] for s in site_stats.values())
    total_no_fm = sum(s['no_fm'] for s in site_stats.values())
    total_no_date = sum(s['no_date'] for s in site_stats.values())
    total_stale = sum(s['stale'] for s in site_stats.values())
    total_imgs = sum(s['imgs'] for s in site_stats.values())
    total_missing_alt = sum(s['missing_alt'] for s in site_stats.values())
    total_broken = sum(s['broken_links'] for s in site_stats.values())
    total_xsite = sum(s['xsite_links'] for s in site_stats.values())
    total_vue_prop_issues = sum(s['vue_prop_issues'] for s in site_stats.values())
    total_vue_missing = sum(s['vue_missing_comp'] for s in site_stats.values())
    total_mermaid_unclosed = sum(s['mermaid_unclosed'] for s in site_stats.values())
    total_heading_jump = sum(s['heading_jump'] for s in site_stats.values())

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
    excluded_names = ', '.join(args.exclude_thin_name)
    excluded_sites_str = ' + 站点:' + ', '.join(args.exclude_thin_site) if args.exclude_thin_site else ''
    lines.append(f"| 薄页豁免（{excluded_names}{excluded_sites_str}） | {total_thin_excluded} | — | 结构预期字数少，不计入薄页 |")
    lines.append(f"| 薄页（< {args.min_words} 字，扣除豁免） | {total_thin} ({thin_pct:.1f}%) | ≤ 5% | {'✅' if thin_pct <= 5 else '⚠️' if thin_pct <= 15 else '❌'} |")
    lines.append(f"| 缺 frontmatter | {total_no_fm} | 0 | {'✅' if total_no_fm == 0 else '❌'} |")
    lines.append(f"| frontmatter 缺 date | {total_no_date} | 0 | {'✅' if total_no_date == 0 else '⚠️'}（VitePress `lastUpdated: true` 兜底）|")
    lines.append(f"| 过期内容（> {args.max_age_days} 天） | {total_stale} | ≤ 10% | {'✅' if total_stale <= total_files * 0.1 else '⚠️'} |")
    lines.append(f"| 图片总数 | {total_imgs} | — | {'⚠️ 偏少' if total_imgs < total_files * 0.1 else '✅'} |")
    lines.append(f"| 缺 alt 的图片 | {total_missing_alt} | 0 | {'✅' if total_missing_alt == 0 else '❌'} |")
    lines.append(f"| 内部死链 | {total_broken} | 0 | {'✅' if total_broken == 0 else '❌'} |")
    lines.append(f"| 跨站引用 | {total_xsite} | ≥ 100 | {'⚠️ 偏少' if total_xsite < 100 else '✅'} |")
    lines.append(f"| Vue prop 数组缺逗号 | {total_vue_prop_issues} | 0 | {'✅' if total_vue_prop_issues == 0 else '❌'} |")
    lines.append(f"| Vue 组件缺失（md 引用无 .vue） | {total_vue_missing} | 0 | {'✅' if total_vue_missing == 0 else '❌'} |")
    lines.append(f"| Mermaid 代码块未闭合 | {total_mermaid_unclosed} | 0 | {'✅' if total_mermaid_unclosed == 0 else '❌'} |")
    lines.append(f"| 标题层级跳级 | {total_heading_jump} | 0 | {'✅' if total_heading_jump == 0 else '❌'} |")
    lines.append(f"| 跨子站重复标题 | {len(cross_dups)} | ≤ 20 | {'✅' if len(cross_dups) <= 20 else '⚠️'} |")
    lines.append("")

    lines.append("## 一、各子站统计")
    lines.append("")
    lines.append("| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |")
    lines.append("|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|")
    low_density_sites = []  # §8.60.6：xsite_density < 1.0 的站
    for site in sorted(site_stats):
        s = site_stats[site]
        if s['files'] == 0:
            continue
        short = site.replace('-html', '').replace('java-web-manual', 'java')
        # §8.60.6：跨站密度 = xsite 数 * 1000 / 字数（每千字跨站链接数）
        density = (s['xsite_links'] * 1000 / s['words']) if s['words'] else 0.0
        density_str = f"{density:.2f}"
        if density < 1.0 and s['files'] > 0:
            low_density_sites.append((short, density, s['xsite_links'], s['words']))
        lines.append(f"| {short} | {s['files']} | {s['words']:,} | {s['fm']} | {s['thin']} | {s['thin_excluded']} | {s['no_fm']} | {s['stale']} | {s['imgs']} | {s['broken_links']} | {s['xsite_links']} | {density_str} | {s['vue_prop_issues']} | {s['vue_missing_comp']} | {s['mermaid_unclosed']} | {s['heading_jump']} |")
    lines.append("")

    # §8.60.6：低密度站清单（每千字跨站链接 < 1.0）
    if low_density_sites:
        lines.append(f"### 〇·a、跨站引用低密度站（{len(low_density_sites)} 站，每千字 < 1 链接）")
        lines.append("")
        lines.append("| 子站 | 密度（每千字）| xsite 链接 | 字数 |")
        lines.append("|------|-----:|-----:|-----:|")
        for site, d, n, w in sorted(low_density_sites, key=lambda x: x[1]):
            lines.append(f"| {site} | {d:.2f} | {n} | {w:,} |")
        lines.append("")
        lines.append("**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。")
        lines.append("")

    if issues_thin:
        lines.append(f"## 二、薄页清单（{len(issues_thin)} 篇）")
        lines.append("")
        # 按字数升序：真占位（< 100 字）排前，紧凑章节（> 100 字）排后
        sorted_thin = sorted(issues_thin, key=lambda x: x[0])
        for _, f in sorted_thin[:50]:
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

    # §8.55 升级：低完整度清单
    low_complete = [(s['completeness_total'] / s['files'] if s['files'] else 0, short, s['low_completeness'], s['files']) for short, s in site_stats.items() if s['low_completeness'] > 0]
    low_complete.sort(key=lambda x: x[0])  # 平均分低 → 前
    total_low = sum(s['low_completeness'] for s in site_stats.values())
    if total_low > 0:
        lines.append(f"### 〇·b、内容完整度低（{total_low} 篇，completeness_score ≤ 3）")
        lines.append("")
        lines.append("| 子站 | 平均分 | 低完整度 / 总数 | 建议 |")
        lines.append("|------|------:|------:|------|")
        for avg, short, n, total in low_complete:
            lines.append(f"| {short} | {avg:.1f} | {n} / {total} | 加代码示例 / 表格 / Vue 组件 |")
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

    if intra_dups:
        lines.append(f"## 七·b、同站重复标题（{len(intra_dups)} 组 — cheatsheet 类常见）")
        lines.append("")
        lines.append("同站多个文件出现相同标题（多为 cheatsheet / overview / 总览页）。")
        lines.append("")
        for title, files in intra_dups[:30]:
            lines.append(f"- **{title!r}** ({len(files)} 处)")
            for f in files[:5]:
                lines.append(f"  - `{f}`")
            if len(files) > 5:
                lines.append(f"  - ... 等 {len(files) - 5} 处")
        if len(intra_dups) > 30:
            lines.append(f"- ... 及其他 {len(intra_dups) - 30} 组")
        lines.append("")

    if issues_vue_props:
        lines.append(f"## 九、Vue prop 数组语法错误（{len(issues_vue_props)} 处）")
        lines.append("")
        lines.append("⚠️ `:prop=\"[ ... ]\"` 数组中除最后一行外每行末尾必须有逗号，否则 Vue 会把多个字符串静默拼接为 1 个长串。")
        lines.append("")
        for f in issues_vue_props[:20]:
            lines.append(f"- `{f}`")
        if len(issues_vue_props) > 20:
            lines.append(f"- ... 及其他 {len(issues_vue_props) - 20} 处")
        lines.append("")

    if issues_vue_missing:
        lines.append(f"## 十、Vue 组件缺失（md 引用但本地无 .vue，{len(issues_vue_missing)} 处）")
        lines.append("")
        lines.append("⚠️ VitePress 默认在 `.vitepress/theme/components/` 找自定义组件，md 引用了组件但本地无 .vue 文件会导致 build 失败。")
        lines.append("")
        for f in issues_vue_missing[:20]:
            lines.append(f"- `{f}`")
        if len(issues_vue_missing) > 20:
            lines.append(f"- ... 及其他 {len(issues_vue_missing) - 20} 处")
        lines.append("")

    if issues_mermaid:
        lines.append(f"## 十一、Mermaid 代码块未闭合（{len(issues_mermaid)} 处）")
        lines.append("")
        lines.append("⚠️ `mermaid` fenced code block 缺少结束标记，Mermaid 图表可能无法渲染。")
        lines.append("")
        for f in issues_mermaid[:20]:
            lines.append(f"- `{f}`")
        if len(issues_mermaid) > 20:
            lines.append(f"- ... 及其他 {len(issues_mermaid) - 20} 处")
        lines.append("")

    if issues_heading:
        lines.append(f"## 十二、标题层级跳级（{len(issues_heading)} 处）")
        lines.append("")
        lines.append("⚠️ 标题从 h1 跳到 h3、h2 跳到 h4（或更大层级）会削弱文档目录结构。")
        lines.append("")
        for f in issues_heading[:20]:
            lines.append(f"- `{f}`")
        if len(issues_heading) > 20:
            lines.append(f"- ... 及其他 {len(issues_heading) - 20} 处")
        lines.append("")

    lines.append("## 八、关键发现与建议")
    lines.append("")
    lines.append(f"1. **图片覆盖率极低**：{total_imgs} 张图 / {total_files} 篇 = {100*total_imgs/total_files:.1f}%，纯文字技术文档严重缺乏视觉化（C11 价值高）")
    lines.append(f"2. **跨站引用密度**：全局 {total_xsite} 处（§8.60 注入 +152），平均 {(total_xsite * 1000 / total_words):.2f} 链接/千字。详见'〇·a 低密度站清单'补强")
    lines.append(f"3. **薄页比例 {thin_pct:.1f}%**：{total_thin} 篇字数 < {args.min_words}，可能为 placeholder 或拆分过度（C3 持续 review）")
    lines.append(f"4. **frontmatter 覆盖率 {fm_pct:.1f}%**：{total_no_fm} 篇缺 FM，{total_no_date} 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）")
    lines.append(f"5. **过期内容 {total_stale} 篇**（> {args.max_age_days} 天）：需要月度 review 流程（C10）")
    lines.append(f"6. **内部死链 {total_broken} 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证")
    lines.append("")

    # 写报告
    out_file.write_text('\n'.join(lines))
    print(f"✓ 报告: {out_file}")
    print(f"  files: {total_files}  words: {total_words:,}  thin: {total_thin}  imgs: {total_imgs}  xsite: {total_xsite}")
    print(f"  no_fm: {total_no_fm}  no_date: {total_no_date}  stale: {total_stale}  broken: {total_broken}  dups: {len(cross_dups)} (cross-site) + {len(intra_dups)} (intra-site)  vue_bug: {total_vue_prop_issues}  vue_missing: {total_vue_missing}  mermaid_unclosed: {total_mermaid_unclosed}  heading_jump: {total_heading_jump}")

if __name__ == '__main__':
    main()
