#!/usr/bin/env python3
"""render-config.py - 从 config.mts.tpl 渲染指定子站的 config.mts

用法:
  python3 render-config.py <site-dir> [site-id]

输出: <site-dir>/.vitepress/config.mts.rendered（不自动覆盖）
迁移: mv .../.vitepress/config.mts.rendered .../.vitepress/config.mts
"""
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "config.mts.tpl"

if len(sys.argv) < 2:
    print("usage: render-config.py <site-dir> [site-id]", file=sys.stderr)
    sys.exit(1)

SITE_DIR = sys.argv[1]
SITE_ID = sys.argv[2] if len(sys.argv) > 2 else SITE_DIR.replace("-html", "")
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent

src_config = PROJECT_ROOT / SITE_DIR / ".vitepress" / "config.mts"
if not src_config.exists():
    print(f"ERROR: {src_config} not found", file=sys.stderr)
    sys.exit(1)

src_text = src_config.read_text(encoding="utf-8")

def extract(pattern, default=""):
    m = re.search(pattern, src_text)
    return m.group(1) if m else default

BASE = extract(r"base:\s*['\"]([^'\"]+)['\"]", "/")
TITLE = extract(r"siteTitle:\s*['\"]([^'\"]+)['\"]") or extract(r"title:\s*['\"]([^'\"]+)['\"]")
if not TITLE:
    print(f"WARN: no siteTitle/title found in {src_config}", file=sys.stderr)
    TITLE = SITE_ID
DESC = extract(r"description:\s*['\"]([^'\"]+)['\"]", "")
ACCENT = extract(r"theme-color.*content:\s*['\"]?(#[a-fA-F0-9]+)", "#8b5cf6")

tpl = TEMPLATE.read_text(encoding="utf-8")
out = tpl
out = out.replace("@SITE_ID", SITE_ID)
out = out.replace("@SITE_BASE", BASE)
out = out.replace("@SITE_TITLE", TITLE)
out = out.replace("@SITE_DESC", DESC)
out = out.replace("@SITE_ACCENT", ACCENT)
out = out.replace("@SITE_LANG", "zh-CN")
out = out.replace("@FOOTER_MESSAGE", f"{TITLE} · Scholar's Atlas 子站")
out = out.replace("@SOCIAL_GITHUB", '[{ icon: "github", link: "https://github.com" }]')
out = out.replace("@NAV_EXTRA@", "  ")
out = out.replace("@CROSS_SITES@", "  ")
out = out.replace("@SIDEBAR@", "  ")

out_path = PROJECT_ROOT / SITE_DIR / ".vitepress" / "config.mts.rendered"
out_path.write_text(out, encoding="utf-8")
print(f"OK: wrote {out_path}")
print(f"  site_id={SITE_ID}  base={BASE}  title={TITLE}")
print(f"  accent={ACCENT}")
print()
print("⚠  This is a preview only - NOT auto-applied.")
print(f"   Review then: mv {out_path} {src_config}")
