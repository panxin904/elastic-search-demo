#!/usr/bin/env python3
"""
多静态网站一站式访问（Python 实现的反向代理）
用法: python3 start-hub.py
访问: http://localhost:8080/

子站列表由 sites-hub/scripts/sites.sh 驱动（**唯一真相源**）。
新增站点只改 sites.sh + 一张首页卡片 + 1 个项目目录。
本脚本通过 SITES_CSV 环境变量（start.sh 注入）获取子站清单。

路由:
  /X/        → <X>-html/dist  (或 scripts/sites.sh 中映射的目录)
  /          → 统一导航首页
  /healthz   → 健康检查（auth 前）
"""
import http.server
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

HUB_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = HUB_DIR.parent

# 从环境变量读 SITES（start.sh 注入），缺省回退到硬编码兜底
SITES_CSV = os.environ.get("SITES_CSV", "")
if SITES_CSV:
    SITES = [s.strip() for s in SITES_CSV.split(",") if s.strip()]
else:
    # 兜底：与 scripts/sites.sh 保持同步；如果改了一边也改这边
    SITES = [
        "es", "mysql", "redis", "cloud", "python", "kafka", "java", "tools",
        "frontend", "linux", "cloud-native", "ai", "bigdata", "network", "video",
        "filesystem", "java-language", "architecture", "system-design",
        "postgresql", "observability", "security", "devops", "rust", "go",
        "clickhouse", "design-pattern", "chaos",
    ]

# 与 sites.sh PROJECT_DIR 关联数组保持同步
PROJECT_DIR_OVERRIDES = {
    "cloud": "springcloud-html",
    "java": "java-web-manual",
}


def site_to_project(site: str) -> str:
    return PROJECT_DIR_OVERRIDES.get(site, f"{site}-html")


def project_to_site(project: str) -> str:
    for s in SITES:
        if site_to_project(s) == project:
            return s
    return project.removesuffix("-html")  # fallback


PROJECTS = {f"/{s}/": PROJECT_ROOT / site_to_project(s) / ".vitepress" / "dist"
            for s in SITES}

HUB_INDEX = HUB_DIR / "www" / "index.html"
PORT = int(os.environ.get("HUB_PORT", "8080"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        # 健康检查
        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        # 统一首页
        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HUB_INDEX, "rb") as f:
                self.wfile.write(f.read())
            return

        # 路由到对应项目
        for prefix, root in PROJECTS.items():
            if path.startswith(prefix):
                rel = path[len(prefix):].lstrip("/")
                file_path = root / rel
                if file_path.is_file():
                    self.send_file(file_path)
                    return
                if file_path.is_dir():
                    file_path = file_path / "index.html"
                    if file_path.is_file():
                        self.send_file(file_path)
                        return
                # SPA 兜底
                fallback = root / (rel + ".html") if rel else root / "index.html"
                if fallback.is_file():
                    self.send_file(fallback)
                    return
                fallback = root / "index.html"
                if fallback.is_file():
                    self.send_file(fallback)
                    return
                self.send_error(404, f"Not Found: {path}")
                return

        self.send_error(404, f"Not Found: {path}")

    def send_file(self, file_path):
        # 简单 MIME 推断（Python 自带 mimetypes 也可）
        import mimetypes
        ctype, _ = mimetypes.guess_type(str(file_path))
        if ctype is None:
            ctype = "application/octet-stream"
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except OSError as e:
            self.send_error(500, f"Read error: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # T6：VitePress 哈希资源可永久缓存
        if "/assets/" in str(file_path):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def main():
    print(f"Scholar's Atlas hub serving {len(SITES)} sites on port {PORT}:")
    for s in SITES:
        proj = site_to_project(s)
        print(f"  /{s}/  ->  ../{proj}/.vitepress/dist/")
    print(f"  /       ->  www/index.html (unified navigation)")
    print(f"  /healthz  ->  ok (auth-bypass)")
    socketserver = http.server.ThreadingHTTPServer if hasattr(http.server, "ThreadingHTTPServer") else None
    cls = socketserver or type(
        "S", (http.server.HTTPServer,),
        {}
    )
    # 简单 HTTPServer
    server = http.server.HTTPServer(("", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
