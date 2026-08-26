---
title: requests + BeautifulSoup
---

# 🌐 requests + BeautifulSoup

> **requests + BeautifulSoup** 是 Python **静态页面爬取的经典组合**。简单、强大、稳定。

## 🚀 快速开始

### 安装

```bash
pip install requests beautifulsoup4 lxml
```

### Hello World

```python
import requests
from bs4 import BeautifulSoup

# 1. 发送请求
response = requests.get("https://quotes.toscrape.com/")

# 2. 解析 HTML
soup = BeautifulSoup(response.text, "lxml")

# 3. 提取数据
quotes = soup.select(".quote")
for quote in quotes:
    text = quote.select_one(".text").get_text(strip=True)
    author = quote.select_one(".author").get_text(strip=True)
    print(f"{author}: {text}")
```

## 📡 requests 基础

### 发送请求

```python
import requests

# GET
r = requests.get("https://api.example.com/users")

# POST（JSON）
r = requests.post("https://api.example.com/users", json={
    "name": "Alice"
})

# POST（表单）
r = requests.post("https://api.example.com/login", data={
    "username": "alice",
    "password": "secret"
})

# 带 Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0)",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
r = requests.get("https://example.com", headers=headers)

# 带参数
r = requests.get("https://example.com/search", params={
    "q": "python",
    "page": 1
})

# 带 Cookie
r = requests.get("https://example.com", cookies={"session": "abc"})

# 设置超时
r = requests.get("https://example.com", timeout=10)
```

### 处理响应

```python
r = requests.get("https://example.com")

print(r.status_code)    # 200
print(r.headers)         # 响应头
print(r.text)            # 响应内容（字符串）
print(r.content)         # 响应内容（字节）
print(r.json())          # JSON 响应
print(r.cookies)         # Cookies
print(r.elapsed)         # 响应时间
print(r.url)             # 最终 URL

# 状态码判断
if r.status_code == 200:
    print("OK")
elif r.status_code == 404:
    print("Not Found")

# 抛异常
r.raise_for_status()
```

### Session（保持 Cookie）

```python
session = requests.Session()

# 登录（设置 Cookie）
session.post("https://example.com/login", data={
    "username": "alice",
    "password": "secret"
})

# 后续请求自动带 Cookie
response = session.get("https://example.com/dashboard")
```

## 🕷️ BeautifulSoup 基础

### 解析器

```python
from bs4 import BeautifulSoup

# 推荐 lxml（速度 + 容错性平衡）
soup = BeautifulSoup(html, "lxml")

# 标准库（无依赖）
soup = BeautifulSoup(html, "html.parser")

# html5lib（最宽松）
soup = BeautifulSoup(html, "html5lib")
```

### 标签选择

```python
# 通过标签名
soup.title              # <title>...</title>
soup.body
soup.h1

# 获取文本
soup.title.text
soup.title.get_text()
soup.title.string

# 获取属性
soup.a["href"]
soup.a.get("href")
soup.a.get("href", "default")  # 不存在时返回默认值
```

### find / find_all

```python
# 找第一个
soup.find("a")
soup.find("a", id="link")
soup.find("a", class_="external")  # class 是 Python 关键字
soup.find("a", attrs={"data-id": "123"})

# 找所有
soup.find_all("a")
soup.find_all(["h1", "h2", "h3"])
soup.find_all("a", class_="link")
soup.find_all("div", {"class": "item"})
soup.find_all("a", limit=5)

# 按文本
soup.find_all(string="Python")
soup.find_all("p", string=lambda x: "Python" in x)

# 按函数（自定义过滤）
soup.find("a", href=lambda x: x and x.startswith("https://"))
```

### CSS 选择器

```python
# 标签
soup.select("a")
soup.select("div.content")
soup.select("div#main")
soup.select("a[href*=github]")
soup.select("div > p")
soup.select("ul li:first-child")
soup.select("ul li:nth-child(2)")
soup.select("input[type=text]")

# 多个选择器
soup.select("h1, h2, h3")

# 组合
soup.select("div.container > p.intro")
soup.select("a[href^='https://']")
soup.select("a[href$='.pdf']")
soup.select("a[href*='example']")
```

### 遍历文档树

```python
# 子节点
soup.body.contents      # 直接子节点列表
soup.body.children      # 迭代器
soup.body.descendants   # 所有后代

# 父节点
soup.title.parent        # 父节点
soup.title.parents       # 所有祖先

# 兄弟节点
soup.p.previous_sibling
soup.p.next_sibling
soup.p.previous_siblings
soup.p.next_siblings
```

## 🛠️ 实战：爬取豆瓣电影 Top 250

```python
import requests
from bs4 import BeautifulSoup
import time
import json

def scrape_douban_top250():
    base_url = "https://movie.douban.com/top250"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    movies = []
    for page in range(0, 250, 25):  # 10 页
        url = f"{base_url}?start={page}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        
        for item in soup.select(".item"):
            title = item.select_one(".title").get_text(strip=True)
            rating = item.select_one(".rating_num").get_text(strip=True)
            quote = item.select_one(".quote .inq")
            quote_text = quote.get_text(strip=True) if quote else ""
            
            movies.append({
                "title": title,
                "rating": float(rating),
                "quote": quote_text
            })
        
        time.sleep(1)  # 礼貌爬取
    
    return movies

# 运行
movies = scrape_douban_top250()
print(f"共 {len(movies)} 部电影")

# 保存
with open("douban_top250.json", "w", encoding="utf-8") as f:
    json.dump(movies, f, ensure_ascii=False, indent=2)
```

## 🛠️ 实战：登录 + 爬取

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# 1. 登录
login_url = "https://example.com/login"
response = session.post(login_url, data={
    "username": "myuser",
    "password": "mypass"
})

# 检查登录是否成功
if "Welcome" in response.text:
    print("登录成功")
else:
    print("登录失败")
    return

# 2. 访问需要登录的页面
profile_url = "https://example.com/profile"
response = session.get(profile_url)
soup = BeautifulSoup(response.text, "lxml")

# 3. 提取数据
username = soup.select_one(".username").get_text(strip=True)
email = soup.select_one(".email").get_text(strip=True)
print(f"用户名: {username}, 邮箱: {email}")
```

## 🛠️ 实战：爬取表格

```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://example.com/data")
soup = BeautifulSoup(response.text, "lxml")

# 提取表格
table = soup.find("table")
rows = []

# 提取表头
headers = [th.get_text(strip=True) for th in table.select("thead th")]

# 提取数据行
for tr in table.select("tbody tr"):
    cols = [td.get_text(strip=True) for td in tr.select("td")]
    row = dict(zip(headers, cols))
    rows.append(row)

print(f"列: {headers}")
print(f"行数: {len(rows)}")
print(f"第一行: {rows[0]}")
```

## 🛠️ 实战：异步批量爬取

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time

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

# 同步 vs 异步
urls = [f"https://example.com/page/{i}" for i in range(20)]

start = time.time()
sync_results = [parse(requests.get(u).text) for u in urls]
print(f"同步: {time.time() - start:.2f}s")

start = time.time()
async_results = asyncio.run(scrape_all(urls))
print(f"异步: {time.time() - start:.2f}s")
# 异步快 5-10 倍
```

## 📊 错误处理

```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

def safe_scrape(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Timeout:
            print(f"Timeout, retry {attempt + 1}")
        except ConnectionError:
            print(f"Connection error, retry {attempt + 1}")
        except RequestException as e:
            print(f"Error: {e}")
            return None
    return None
```

## 🎯 总结

**requests + BeautifulSoup 核心要点**：
- ✅ requests：最流行的 HTTP 库
- ✅ BeautifulSoup：最简单的 HTML 解析
- ✅ 组合：静态页面爬取的标准方案
- ✅ Session：保持 Cookie
- ✅ CSS 选择器：灵活提取
- ✅ 异步 aiohttp：高性能爬虫
- ⚠️ 设置 User-Agent 和限速
- ⚠️ 异常处理和重试
- ⚠️ 遵守 robots.txt

**下一步：** [⚡ Scrapy 框架](/05-scraping/scrapy) — 工业级爬虫


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
