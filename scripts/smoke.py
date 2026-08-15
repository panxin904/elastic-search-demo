#!/usr/bin/env python3
"""28-station smoke test for sites-hub on VPS java-px.bot.cd.

Password resolution priority:
  1. SITES_HUB_PASSWORD environment variable
  2. First command-line argument
  3. Default: "admin"

Usage:
  python3 smoke.py                 # uses default password
  python3 smoke.py mysecret        # uses "mysecret"
  SITES_HUB_PASSWORD=mysecret python3 smoke.py
"""
import os
import subprocess
import sys

PASSWORD = (
    os.environ.get("SITES_HUB_PASSWORD")
    or (sys.argv[1] if len(sys.argv) > 1 else "admin")
)
CURL = "/usr/bin/curl"
STATIONS = [
    "es", "mysql", "redis", "cloud", "python", "kafka", "java", "tools",
    "frontend", "linux", "cloud-native", "ai", "java-language", "bigdata",
    "architecture", "network", "video", "filesystem", "system-design",
    "postgresql", "observability", "security", "devops", "rust", "go",
    "clickhouse", "design-pattern", "chaos",
]


def fetch(path):
    r = subprocess.run(
        [CURL, "-sL", "-u", f"admin:{PASSWORD}", f"https://java-px.bot.cd/{path}"],
        capture_output=True, text=True, timeout=30,
    )
    return r.stdout


def head_check(path):
    """Returns final HTTP code after following redirects (-L).
    Use bare path (e.g. 'chaos' or 'chaos/01-foundations/overview').
    For homepage (path='') the URL is just '/'.
    """
    if path == "":
        url = "https://java-px.bot.cd/"
    else:
        # Stations add / for redirect → 200; subpages stay without /
        url = f"https://java-px.bot.cd/{path}/" if "/" not in path else f"https://java-px.bot.cd/{path}"
    r = subprocess.run(
        [CURL, "-sL", "-o", "/dev/null", "-w", "%{http_code}",
         "-u", f"admin:{PASSWORD}", url],
        capture_output=True, text=True, timeout=30,
    )
    return r.stdout.strip()


def deep_check(path, must_contain):
    """path is like 'chaos/01-foundations/overview' (no trailing slash)."""
    body = fetch(path)
    return {
        "200": head_check(path) == "200",
        "VPLink": "VPLink" in body,  # subpages have VPLink nav
        "🏠 门户": body.count("🏠 门户") >= 2,
        "门户首页": body.count("门户首页") >= 1,
        "must_contain": must_contain in body if must_contain else True,
    }


total_ok = 0
print(f"=== 28 站冒烟测试（sites-hub @ java-px.bot.cd） ===")
print(f"{'站点':<15}{'HTTP':<6}{'nav':<5}{'foot':<5}{'hero':<5}{'result'}")
print("-" * 60)
for path in STATIONS:
    body = fetch(f"{path}/")
    code = head_check(path)
    nav = body.count("🏠 门户")
    foot = body.count("门户首页")
    hero = body.count("VPHero") + body.count("VPHome")
    ok = code == "200" and nav >= 2 and foot >= 1 and hero >= 1
    if ok:
        total_ok += 1
    status = "✓" if ok else "✗"
    print(f"{path:<15}{code:<6}{nav:<5}{foot:<5}{hero:<5}{status}")

print(f"\n=== 结果: {total_ok}/{len(STATIONS)} 通过 ===")
if total_ok != len(STATIONS):
    sys.exit(1)

# Deep check on latest station (chaos)
print("\nDeep check on /chaos/01-foundations/overview ...")
checks = deep_check("chaos/01-foundations/overview", "稳态假设")
for k, v in checks.items():
    print(f"  {'✓' if v else '✗'} {k}")

# Portal homepage
print("\nPortal homepage / ...")
home = fetch("")
print(f"  station hrefs: {len(set(__import__('re').findall(r'href=\"/([a-z-]+)/\"', home)))}")
print(f"  data-count='28': {chr(34)+'28'+chr(34) in home or '28 个' in home}")
