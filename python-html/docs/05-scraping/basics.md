---
title: 爬虫基础
---

# 🎯 爬虫基础

> **网络爬虫**是**自动获取网页数据**的程序。Python 因其丰富的爬虫库（requests、BeautifulSoup、Scrapy、Playwright）成为爬虫的首选语言。

## 🎯 爬虫基础概念

```
爬虫 = 模拟浏览器请求 + 解析 HTML + 提取数据 + 存储

主要流程：
  1. 构造请求（URL、Headers、Cookies）
  2. 发送请求（requests / aiohttp）
  3. 接收响应（HTML / JSON）
  4. 解析数据（BeautifulSoup / lxml）
  5. 提取数据（CSS 选择器 / XPath / 正则）
  6. 存储数据（文件 / 数据库）
  7. 翻页或递归爬取
```

## 🛠️ robots.txt 协议

```
robots.txt 是网站声明爬虫规则的协议：
  - /robots.txt 放在网站根目录
  - 告诉爬虫哪些路径可以爬
  - 哪些不可以爬

示例（github.com/robots.txt）：

User-agent: *
Allow: /
Disallow: /search
Disallow: /api/
```

### 使用 robotparser

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

# 检查 URL 是否允许爬取
print(rp.can_fetch("*", "https://example.com/page"))  # True/False
print(rp.can_fetch("Googlebot", "https://example.com/admin"))  # False

# 检查爬取延迟
print(rp.crawl_delay("*"))  # 1.0（秒）
```

## 📋 HTTP 基础

### 请求方法

```
GET     - 获取资源（最常用）
POST    - 提交数据（登录、搜索）
PUT     - 更新资源
DELETE  - 删除资源
HEAD    - 只获取响应头
OPTIONS - 查询支持的方法
```

### 常用 Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com"
}
```

### Cookie 和 Session

```python
import requests

# 1. 自动管理 Cookie
session = requests.Session()
session.get("https://example.com")  # 设置 Cookie
session.get("https://example.com/dashboard")  # 自动带 Cookie

# 2. 手动管理
cookies = {"session_id": "abc123"}
r = requests.get(url, cookies=cookies)
```

## 🛠️ 第一个爬虫

```python
import requests
from bs4 import BeautifulSoup

def scrape_quotes():
    url = "https://quotes.toscrape.com"
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })
    
    if response.status_code != 200:
        print(f"Failed: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "lxml")
    quotes = []
    
    for quote in soup.select(".quote"):
        text = quote.select_one(".text").get_text(strip=True)
        author = quote.select_one(".author").get_text(strip=True)
        quotes.append({"text": text, "author": author})
    
    return quotes

# 运行
quotes = scrape_quotes()
for q in quotes:
    print(f"{q['author']}: {q['text']}")
```

## 📊 爬虫分类

### 1. 通用爬虫 vs 聚焦爬虫

```
通用爬虫：抓取整个网站（如 Google 爬虫）
聚焦爬虫：抓取特定数据（如商品信息、价格）
```

### 2. 同步 vs 异步爬虫

```
同步：requests + BeautifulSoup（简单）
异步：aiohttp + asyncio（高性能）
```

### 3. 静态 vs 动态爬虫

```
静态：HTML 中包含数据（requests + BS4）
动态：JavaScript 渲染（Selenium / Playwright）
```

## 🛠️ 爬虫流程

### 单页爬取

```python
import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "lxml")
    return soup

# 提取数据
soup = scrape_page("https://example.com")
title = soup.title.text
links = [a["href"] for a in soup.select("a[href]")]
```

### 多页爬取（分页）

```python
import requests
from bs4 import BeautifulSoup

def scrape_paginated(base_url, max_pages=10):
    results = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "lxml")
        
        items = soup.select(".item")
        if not items:
            break  # 没有更多数据
        
        for item in items:
            results.append(extract_item(item))
    
    return results

def extract_item(item):
    return {
        "title": item.select_one(".title").get_text(strip=True),
        "url": item.select_one("a")["href"]
    }
```

### 递归爬取（爬取整个网站）

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def crawl(url, visited=None, max_pages=100):
    if visited is None:
        visited = set()
    
    if len(visited) >= max_pages:
        return []
    if url in visited:
        return []
    
    visited.add(url)
    
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "lxml")
    
    # 提取本页数据
    data = soup.select(".data")
    
    # 提取所有链接
    base_domain = urlparse(url).netloc
    for link in soup.select("a[href]"):
        href = link.get("href")
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        full_url = urljoin(url, href)
        if urlparse(full_url).netloc == base_domain:
            # 递归爬取
            data.extend(crawl(full_url, visited, max_pages))
    
    return data
```

## 🛠️ 数据存储

### 保存为 JSON

```python
import json

data = [{"title": "A", "url": "https://..."}, {"title": "B", "url": "https://..."}]

# 保存
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 追加
with open("data.jsonl", "a", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
```

### 保存为 CSV

```python
import csv

with open("data.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "url"])
    writer.writeheader()
    for item in data:
        writer.writerow(item)
```

### 保存到数据库

```python
import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        title TEXT,
        url TEXT
    )
""")

for item in data:
    cursor.execute(
        "INSERT INTO items (title, url) VALUES (?, ?)",
        (item["title"], item["url"])
    )

conn.commit()
conn.close()
```

## 🛠️ 异步爬虫

```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def scrape_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        htmls = await asyncio.gather(*tasks)
        return [parse(html) for html in htmls]

def parse(html):
    soup = BeautifulSoup(html, "lxml")
    return [a["href"] for a in soup.select("a[href]")]

# 使用
urls = [f"https://example.com/page/{i}" for i in range(100)]
results = asyncio.run(scrape_all(urls))
```

## 📊 爬虫最佳实践

### 1. 设置 User-Agent

```python
headers = {
    "User-Agent": "MyBot/1.0 (+https://example.com/bot)"
}
```

### 2. 限制请求频率

```python
import time

for url in urls:
    response = requests.get(url)
    # 处理
    time.sleep(1)  # 每秒 1 次
```

### 3. 设置超时

```python
response = requests.get(url, timeout=10)
```

### 4. 异常处理

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except RequestException as e:
    print(f"Error: {e}")
```

### 5. 遵守 robots.txt

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

if not rp.can_fetch("*", url):
    print("Disallowed by robots.txt")
    return
```

## 🎯 总结

**爬虫基础核心要点**：
- ✅ HTTP 基础（请求方法、Headers、Cookie）
- ✅ robots.txt 协议
- ✅ requests + BeautifulSoup 基础爬虫
- ✅ 静态 vs 动态爬虫
- ✅ 同步 vs 异步爬虫
- ✅ 数据存储（JSON / CSV / 数据库）
- ✅ 异常处理和重试
- ⚠️ 遵守 robots.txt 和网站条款
- ⚠️ 设置 User-Agent 和限速
- ⚠️ 注意反爬虫机制

**下一步：** [🌐 requests + BeautifulSoup](/05-scraping/requests-bs4) — 静态页面爬取实战
