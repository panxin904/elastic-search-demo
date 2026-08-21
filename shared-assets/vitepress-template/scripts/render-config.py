#!/usr/bin/env python3
"""render-config.py - 从 config.mts.tpl 渲染指定子站（或所有子站）的 config.mts

C1 子站结构统一化工具：
  - 标准化 nav（顶部 7 项 + 跨站 dropdown 按 SITES 顺序去掉自己）
  - 标准化 head（加 viewport / og:site_name / twitter:card）
  - 保留各站 sidebar（依赖章节结构，不动）
  - 保留 socialLinks / footer.message（业务信息）

用法:
  python3 render-config.py <site-dir> [site-id]    # 单站
  python3 render-config.py --all                    # 28 站全跑
  python3 render-config.py --all --apply            # 全跑并自动覆盖（谨慎）

输出:
  <site-dir>/.vitepress/config.mts.rendered（默认不覆盖）
"""
import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "config.mts.tpl"
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent

# 从 sites.sh 提取 SITES 顺序
SITES_SH = PROJECT_ROOT / "sites-hub" / "scripts" / "sites.sh"
SITES_ORDER = []
PROJECT_DIR_MAP = {}  # site_id -> site_dir（特殊映射：cloud:springcloud-html;java:java-web-manual）
if SITES_SH.exists():
    sh_text = SITES_SH.read_text(encoding="utf-8")
    in_sites = False
    for line in sh_text.splitlines():
        if line.strip().startswith("SITES=("):
            in_sites = True
            continue
        if in_sites:
            if line.strip() == ")":
                break
            for w in line.split():
                if w and not w.startswith("#"):
                    SITES_ORDER.append(w)
    # 解析 PROJECT_DIR_MAP="cloud:springcloud-html;java:java-web-manual"
    m = re.search(r'PROJECT_DIR_MAP=["\']([^"\']+)["\']', sh_text)
    if m:
        for pair in m.group(1).split(";"):
            pair = pair.strip()
            if not pair or ":" not in pair:
                continue
            k, v = pair.split(":", 1)
            PROJECT_DIR_MAP[k.strip()] = v.strip()

# 默认 site_id -> site_dir 映射（特殊项被 PROJECT_DIR_MAP 覆盖）
_DEFAULT_DIR = {sid: f"{sid}-html" for sid in SITES_ORDER}
_DEFAULT_DIR.update(PROJECT_DIR_MAP)


def site_to_dir(site_id: str) -> str:
    """site_id -> site_dir（处理 cloud -> springcloud-html 映射）"""
    return _DEFAULT_DIR.get(site_id, f"{site_id}-html")

# 中文站名映射（dropdown 显示用）
SITE_NAMES = {
    'es': 'ElasticSearch', 'mysql': 'MySQL', 'redis': 'Redis',
    'cloud': '微服务 / Spring Cloud', 'python': 'Python', 'kafka': 'Kafka',
    'java': 'Java Web 开发', 'tools': '在线工具', 'frontend': '前端 & Node',
    'linux': 'Linux 服务器', 'cloud-native': '云原生 / Docker / K8s',
    'ai': 'AI 工具 / 大模型', 'bigdata': '大数据', 'network': '计算机网络',
    'video': '视频处理', 'filesystem': '文件系统与存储',
    'java-language': 'Java 语言', 'architecture': '企业级架构',
    'system-design': '系统设计', 'postgresql': 'PostgreSQL',
    'observability': '可观测性', 'security': '安全', 'devops': 'DevOps',
    'rust': 'Rust', 'go': 'Go', 'clickhouse': 'ClickHouse',
    'design-pattern': '设计模式', 'chaos': '混沌工程',
    'iot': '物联网',
    'android': '安卓',
}


def extract(text: str, pattern: str, default: str = "") -> str:
    m = re.search(pattern, text)
    return m.group(1) if m else default


def extract_block(text: str, key: str) -> str:
    """提取 sidebar: { ... } 整个块的内容"""
    m = re.search(rf"\b{key}:\s*\{{", text)
    if not m:
        return ""
    start = m.end() - 1
    depth = 0
    i = start
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i].rstrip(', \n')
        i += 1
    return ""


def render_one(site_dir: str, site_id: str = "") -> Path:
    site_dir_path = PROJECT_ROOT / site_dir
    if not (site_dir_path / ".vitepress" / "config.mts").exists():
        print(f"ERROR: {site_dir_path}/.vitepress/config.mts not found", file=sys.stderr)
        sys.exit(1)
    if not site_id:
        # 从 site_dir 推导 site_id（处理 springcloud-html → cloud 映射）
        for k, v in PROJECT_DIR_MAP.items():
            if v == site_dir:
                site_id = k
                break
        if not site_id:
            site_id = site_dir.replace("-html", "")

    src = (site_dir_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")

    # 提取关键字段
    base = extract(src, r"base:\s*['\"]([^'\"]+)['\"]", "/")
    title = extract(src, r"siteTitle:\s*['\"]([^'\"]+)['\"]") or extract(src, r"title:\s*['\"]([^'\"]+)['\"]", site_id)
    desc = extract(src, r"description:\s*['\"]([^'\"]+)['\"]", "")
    accent = extract(src, r"theme-color.*content:\s*['\"]?(#[a-fA-F0-9]+)", "#8b5cf6")
    # footer.message 可能含 } (HTML 标签) 或 \\' （转义引号）
    # 用 (?:\\.|(?!\1).)*? 跳过转义字符 + 非 \1 引号
    footer_message = ""
    fm = re.search(r"footer:\s*\{[^}]*?message:\s*(['\"])((?:\\.|(?!\1).)*?)\1", src, re.S)
    if fm:
        footer_message = fm.group(2).strip()
    if not footer_message:
        footer_message = f"{title} · Scholar's Atlas 子站"
    social_match = re.search(r"socialLinks:\s*(\[[^\]]*\])", src, re.S)
    social_links = social_match.group(1) if social_match else "[]"
    sidebar = extract_block(src, "sidebar")

    # sidebar 缩进处理：每行加 4 空格 + 移除原首尾多余空白
    if sidebar:
        # 每行前面加 4 空格缩进
        sidebar = "\n".join(("    " + line if line.strip() else line) for line in sidebar.split("\n"))
    # 跨站 dropdown：按 SITES 顺序，跳过自己
    cross_sites_lines = []
    for s in SITES_ORDER:
        if s == site_id:
            continue
        name = SITE_NAMES.get(s, s)
        cross_sites_lines.append(f'        {{ text: "{name}", link: "https://java-px.bot.cd/{s}/" }},')
    cross_sites = "\n".join(cross_sites_lines)

    # 读模板 + 替换
    tpl = TEMPLATE.read_text(encoding="utf-8")
    out = (tpl
        .replace("@SITE_ID", site_id)
        .replace("@SITE_BASE", base)
        .replace("@SITE_TITLE", title)
        .replace("@SITE_DESC", desc)
        .replace("@SITE_ACCENT", accent)
        .replace("@SITE_LANG", "zh-CN")
        .replace("@FOOTER_MESSAGE", footer_message)
        .replace("@SOCIAL_GITHUB", social_links)
        .replace("@CROSS_SITES", cross_sites)
        .replace("@SIDEBAR", "    " + sidebar.replace("\n", "\n    ") if sidebar else "    // (no sidebar)"))

    out_path = site_dir_path / ".vitepress" / "config.mts.rendered"
    out_path.write_text(out, encoding="utf-8")
    print(f"OK: {out_path.relative_to(PROJECT_ROOT)}")
    print(f"    site_id={site_id}  base={base}  title={title}")
    print(f"    sidebar preserved: {len(sidebar)} chars  socialLinks: {len(social_links)} chars")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site_dir", nargs="?", help="子站目录 (e.g. es-html)")
    ap.add_argument("site_id", nargs="?", help="子站 ID (e.g. es)")
    ap.add_argument("--all", action="store_true", help="渲染所有 28 站")
    ap.add_argument("--apply", action="store_true", help="直接覆盖 config.mts（默认 .rendered 预览）")
    args = ap.parse_args()

    if args.all:
        for site_id in SITES_ORDER:
            site_dir = site_to_dir(site_id)
            if not (PROJECT_ROOT / site_dir / ".vitepress" / "config.mts").exists():
                print(f"SKIP: {site_dir} no config.mts", file=sys.stderr)
                continue
            out = render_one(site_dir, site_id)
            if args.apply:
                target = out.parent / "config.mts"
                target.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
                out.unlink()
                print(f"    APPLIED -> {target.relative_to(PROJECT_ROOT)}")
    else:
        if not args.site_dir:
            ap.print_help()
            sys.exit(1)
        out = render_one(args.site_dir, args.site_id or "")
        if args.apply:
            target = out.parent / "config.mts"
            target.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
            out.unlink()
            print(f"APPLIED -> {target.relative_to(PROJECT_ROOT)}")
        else:
            print()
            print("⚠  Preview only. Review then re-run with --apply or:")
            print(f"   mv {out} {out.parent / 'config.mts'}")


if __name__ == "__main__":
    main()
