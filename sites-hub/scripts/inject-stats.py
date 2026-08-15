#!/usr/bin/env python3
"""
sites-hub/scripts/inject-stats.py

Read release/sites-hub/www/data.json and patch the corresponding numbers
in release/sites-hub/www/index.html, so the portal's hard-coded stats
(SITES / PAGES / NODES / WIDGETS) come from a single source of truth.

Substitutions:
  - <span class="stat-num" data-count="N">  (4 occurrences: sites/pages/nodes/widgets)
  - <span class="brand-sub">学习网站 · 28 站</span>
  - <span class="section-count" id="visibleCount">28 项</span>
  - footer: "28 sites · 1429+ pages"
  - about block: "包含 26 个 VitePress 子站点"
  - hero-lede: "收录 28 个垂直领域"
  - <meta property="og:title" content="Scholar's Atlas · 28 个学习站点门户">
  - <meta property="og:description" content="...28 个 VitePress 子站...">
  - <span class="section-count" id="visibleCount">28 项</span>
  - <span class="chip-count" id="cnt-all">28</span>  (initially 0, JS will overwrite)

If data.json is missing or any field is missing, the script is a no-op
(exits 0, prints WARN). This keeps the build robust.
"""
import json
import re
import sys
from pathlib import Path

RELEASE = Path(__file__).resolve().parent.parent.parent / "release" / "sites-hub"
DATA_JSON = RELEASE / "www" / "data.json"
INDEX_HTML = RELEASE / "www" / "index.html"

REQUIRED_KEYS = ("sites", "pages", "nodes", "widgets")


def fail(msg: str, code: int = 1) -> None:
    print(f"[inject-stats] {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    if not DATA_JSON.exists():
        fail(f"data.json not found at {DATA_JSON}; build-release.sh must generate it first")
    if not INDEX_HTML.exists():
        fail(f"index.html not found at {INDEX_HTML}")

    try:
        with DATA_JSON.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"data.json invalid JSON: {e}")

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        fail(f"data.json missing keys: {missing}; got keys {list(data.keys())}")

    sites = int(data["sites"])
    pages = int(data["pages"])
    nodes = int(data["nodes"])
    widgets = int(data["widgets"])
    built = int(data.get("built", sites))

    print(f"[inject-stats] SITES={sites} PAGES={pages} NODES={nodes} WIDGETS={widgets} BUILT={built}")

    html = INDEX_HTML.read_text()
    original = html

    # 1. stat-num data-count: 4 个，按出现顺序填入 sites/pages/nodes/widgets
    stat_pat = re.compile(r'(<span class="stat-num" data-count=")([0-9]+)(">)')
    stat_targets = (sites, pages, nodes, widgets)
    stat_index = {"i": 0}

    def stat_repl(m: re.Match) -> str:
        i = stat_index["i"]
        if i >= len(stat_targets):
            return m.group(0)
        stat_index["i"] += 1
        return f"{m.group(1)}{stat_targets[i]}{m.group(3)}"

    html, stat_count = stat_pat.subn(stat_repl, html)
    if stat_count != 4:
        fail(f"expected 4 stat-num data-count matches, replaced {stat_count}")
    print(f"[inject-stats] stat-num: replaced {stat_count} occurrences")

    # 2. brand-sub: 学习网站 · 28 站
    html, n = re.subn(
        r'(<span class="brand-sub" data-stat="sites" data-format="brand">学习网站 · <span data-stat="sites-num">)[0-9]+(</span> 站</span>)',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"brand-sub: expected 1 match, got {n}")
    print(f"[inject-stats] brand-sub: replaced {n}")

    # 3. section-count: "28 项"
    html, n = re.subn(
        r'(<span class="section-count" id="visibleCount" data-stat="sites" data-format="items"><span data-stat="sites-num">)[0-9]+(</span> 项</span>)',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"visibleCount: expected 1 match, got {n}")
    print(f"[inject-stats] visibleCount: replaced {n}")

    # 4. footer: "28 sites · 1429+ pages"
    html, n = re.subn(
        "(Scholar's Atlas · <span data-stat=\"sites-num\">)[0-9]+(</span> sites · <span data-stat=\"pages-num\">)[0-9]+\\+(</span> pages)",
        rf'\g<1>{sites}\g<2>{pages}+\g<3>', html)
    if n != 1:
        fail(f"footer: expected 1 match, got {n}")
    print(f"[inject-stats] footer: replaced {n}")

    # 5. about block: "包含 26 个 VitePress 子站点"
    html, n = re.subn(
        r'(包含 <span data-stat="sites-num">)[0-9]+(</span> 个 VitePress 子站点)',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"about block: expected 1 match, got {n}")
    print(f"[inject-stats] about block: replaced {n}")

    # 6. hero-lede: "收录 28 个垂直领域"
    html, n = re.subn(
        r'(收录 <span data-stat="sites-num">)[0-9]+(</span> 个垂直领域)',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"hero-lede: expected 1 match, got {n}")
    print(f"[inject-stats] hero-lede: replaced {n}")

    # 7. og:title: "Scholar's Atlas · 28 个学习站点门户"
    html, n = re.subn(
        r"(og:title\" content=\"Scholar's Atlas · )[0-9]+( 个学习站点门户\")",
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"og:title: expected 1 match, got {n}")
    print(f"[inject-stats] og:title: replaced {n}")

    # 8. og:description: "面向后端 / 前端 / AI / SRE 的系统化技术知识门户，28 个 VitePress 子站统一部署。"
    html, n = re.subn(
        r'(og:description\" content=\"面向后端 / 前端 / AI / SRE 的系统化技术知识门户，)[0-9]+( 个 VitePress 子站统一部署。\")',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"og:description: expected 1 match, got {n}")
    print(f"[inject-stats] og:description: replaced {n}")

    # 9. meta name=description: 与 og:description 内容一致
    html, n = re.subn(
        r'(name=\"description\" content=\"Scholar.s Atlas：[0-9]+ 个 VitePress 子站统一部署，)[0-9]+(\+ 内容页)',
        rf'\g<1>{pages}\g<2>', html)
    if n != 1:
        fail(f"description: expected 1 match, got {n}")
    print(f"[inject-stats] description: replaced {n}")

    # 10. twitter:title (含 28)
    html, n = re.subn(
        r'(twitter:title\" content=\"Scholar.s Atlas · )[0-9]+( 个学习站点门户\")',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"twitter:title: expected 1 match, got {n}")
    print(f"[inject-stats] twitter:title: replaced {n}")

    # 11. twitter:description (含 28)
    html, n = re.subn(
        r'(twitter:description\" content=\"面向后端 / 前端 / AI / SRE 的系统化技术知识门户，)[0-9]+( 个 VitePress 子站统一部署。\")',
        rf'\g<1>{sites}\g<2>', html)
    if n != 1:
        fail(f"twitter:description: expected 1 match, got {n}")
    print(f"[inject-stats] twitter:description: replaced {n}")

    if html == original:
        fail("no substitutions made (html unchanged) — check patterns")

    INDEX_HTML.write_text(html)
    print(f"[inject-stats] done: {INDEX_HTML}")


if __name__ == "__main__":
    main()
