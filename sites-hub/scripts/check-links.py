#!/usr/bin/env python3
"""check-links.py - 死链扫描器（BFS）

扫描范围:
  1) 28 个子站根 URL (/es/、/mysql/...)
  2) 首页 / 所有内部 href（仅 base 同源），BFS 至 --depth

输出:
  - text 模式：状态分布 + dead link 列表
  - json 模式：完整 results JSON

用法:
  # 起本地服务
  python3 sites-hub/scripts/start-hub.py        # 或 start-all.sh
  # 跑扫描
  python3 sites-hub/scripts/check-links.py [--base URL] [--depth N]
"""
from __future__ import annotations
import argparse, json, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_BASE = "http://localhost:8081"
TIMEOUT = 8
WORKERS = 2   # 默认低并发 + 1s 延迟，避开 nginx limit_req (T3 防爆破 10r/m burst=20)

SITES_SH = Path(__file__).resolve().parent / "sites.sh"


def load_sites() -> list[str]:
    text = SITES_SH.read_text()
    m = re.search(r"SITES=\((.*?)\)", text, re.S)
    if not m:
        raise RuntimeError("SITES=(...) not found in sites.sh")
    return re.findall(r"\b(\w[\w-]*)\b", m.group(1))


class LinkExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.hrefs.append(d["href"])


def extract_links(html: str) -> list[str]:
    p = LinkExtract()
    p.feed(html)
    out = []
    for h in p.hrefs:
        if h.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        out.append(h)
    return out


def fetch(url: str, timeout: float, delay: float = 0.0) -> tuple[bytes | None, str, dict]:
    if delay > 0:
        time.sleep(delay)
    req = urllib.request.Request(url, headers={"User-Agent": "sites-hub-linkcheck/1.0"})
    t = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            ms = (time.monotonic() - t) * 1000
            return body, "", {"url": url, "status": r.status, "ms": round(ms, 1),
                              "size": len(body), "ctype": r.headers.get("Content-Type", "")}
    except urllib.error.HTTPError as e:
        ms = (time.monotonic() - t) * 1000
        return None, "", {"url": url, "status": e.code, "ms": round(ms, 1), "error": e.reason}
    except Exception as e:
        ms = (time.monotonic() - t) * 1000
        return None, "", {"url": url, "status": 0, "ms": round(ms, 1),
                          "error": type(e).__name__ + ": " + str(e)[:60]}


def normalize(base: str, href: str) -> str | None:
    """只保留同源 / 开头的相对链接；剥离 fragment。"""
    if href.startswith(("javascript:", "mailto:", "tel:")):
        return None
    full = urllib.parse.urljoin(base + "/", href)
    parsed = urllib.parse.urlparse(full)
    if parsed.scheme not in ("http", "https"):
        return None
    base_parsed = urllib.parse.urlparse(base)
    if parsed.netloc != base_parsed.netloc:
        return None
    # 去掉 fragment
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--depth", type=int, default=2, help="BFS depth; 1=roots only")
    ap.add_argument("--timeout", type=float, default=TIMEOUT)
    ap.add_argument("--concurrency", type=int, default=WORKERS)
    ap.add_argument("--delay-ms", type=float, default=1.0, help="请求间隔秒数, 避开 nginx limit_req (10r/m -> 每个 >=6s)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    sites = load_sites()

    # seed
    queue: list[tuple[str, int]] = [(base + "/", 0)]
    for s in sites:
        queue.append((f"{base}/{s}/", 0))

    visited: set[str] = set()
    results: dict[str, dict] = {}
    bodies: dict[str, bytes] = {}

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        for depth in range(args.depth + 1):
            # 当前层未访问的 URL
            cur = [(u, d) for u, d in queue if u not in visited]
            if not cur:
                break
            # 并发抓
            futs = {pool.submit(fetch, u, args.timeout, args.delay_ms): u for u, _ in cur}
            for fut in as_completed(futs):
                body, _, info = fut.result()
                url = futs[fut]
                visited.add(url)
                results[url] = info
                if body is not None and "text/html" in info.get("ctype", ""):
                    bodies[url] = body
            # 下一层
            next_q: list[tuple[str, int]] = []
            if depth < args.depth:
                for url in bodies:
                    html = bodies[url].decode("utf-8", errors="replace")
                    for href in extract_links(html):
                        norm = normalize(base, href)
                        if norm and norm not in visited and norm not in {u for u, _ in next_q}:
                            next_q.append((norm, depth + 1))
            queue = next_q

    by_status: dict[int, int] = {}
    for r in results.values():
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    dead = [r for r in results.values() if r["status"] >= 400 or r["status"] == 0]

    if args.json:
        print(json.dumps({
            "base": base,
            "checked": len(results),
            "by_status": by_status,
            "dead": sorted(dead, key=lambda x: x["url"]),
        }, indent=2))
    else:
        print(f"\n=== check-links: {len(results)} URLs checked (depth={args.depth}) ===")
        for s in sorted(by_status):
            print(f"  HTTP {s}: {by_status[s]}")
        if dead:
            print(f"\nDEAD LINKS ({len(dead)}):")
            for r in sorted(dead, key=lambda x: x["url"])[:50]:
                err = r.get("error", "")
                print(f"  [{r['status']}] {r['url']}  {err}")
            if len(dead) > 50:
                print(f"  ... and {len(dead) - 50} more")
        else:
            print("\nAll links OK")

    sys.exit(1 if dead else 0)


if __name__ == "__main__":
    main()
