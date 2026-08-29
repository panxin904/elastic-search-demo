---
title: BeautifulSoup
date: 2026-08-15  # date-auto-injected
---

# 🕷️ BeautifulSoup

> **BeautifulSoup** 是 Python **最流行的 HTML/XML 解析库**。配合 requests 是爬虫的经典组合。

## 🎯 为什么选 BeautifulSoup？

```
✅ 简单（API 直观）
✅ 容错性（能解析不规范的 HTML）
✅ 灵活（多种解析器）
✅ 生态丰富（与 requests、Scrapy 集成）

对比：
  - 正则：复杂 HTML 难处理
  - lxml：快但严格
  - pyquery：jQuery 风格
  - BeautifulSoup：推荐
```

## 🚀 快速开始

### 安装

```bash
pip install beautifulsoup4 lxml
```

### Hello World

```python
from bs4 import BeautifulSoup

html = """
<html>
<head><title>Hello</title></head>
<body>
    <h1 class="title">Welcome</h1>
    <p class="content">This is a paragraph.</p>
    <a href="https://example.com" id="link">Click</a>
</body>
</html>
"""

soup = BeautifulSoup(html, "lxml")
print(soup.title.text)        # 'Hello'
print(soup.h1.text)           # 'Welcome'
print(soup.p.text)             # 'This is a paragraph.'
print(soup.a["href"])          # 'https://example.com'
```

## 🔍 解析器选择

```python
from bs4 import BeautifulSoup

# html.parser：标准库（容错性差）
soup = BeautifulSoup(html, "html.parser")

# lxml：快（推荐，需 pip install lxml）
soup = BeautifulSoup(html, "lxml")

# html5lib：最宽松（需 pip install html5lib）
soup = BeautifulSoup(html, "html5lib")
```

| 解析器 | 速度 | 容错 | 依赖 |
|--------|------|------|------|
| html.parser | 中 | 中 | 标准库 |
| **lxml** | **快** | 好 | 需安装 |
| html5lib | 慢 | 极好 | 需安装 |

## 📝 基础操作

### 访问元素

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "lxml")

# 直接访问（首个匹配元素）
print(soup.title)         # <title>Hello</title>
print(soup.title.name)    # 'title'
print(soup.title.string)  # 'Hello'
print(soup.title.text)    # 'Hello'

# 获取属性
print(soup.a["href"])
print(soup.a.get("href"))
print(soup.a.get("id", "default"))  # 不存在时返回默认值
```

### 标签列表

```python
# 访问常见标签
soup.title
soup.body
soup.head
soup.h1
soup.p
soup.a
soup.div
```

### 标签属性

```python
tag = soup.a
print(tag.name)         # 'a'
print(tag.attrs)        # {'href': 'https://example.com', 'id': 'link'}
print(tag["href"])      # 'https://example.com'
print(tag["id"])        # 'link'

# 多值属性
print(tag.get("class", []))  # 类列表
```

## 🔎 查找元素

### find() - 找第一个

```python
# 基本
soup.find("a")  # 第一个 <a> 标签

# 按属性
soup.find("a", id="link")
soup.find("a", class_="external")  # 注意 class_（避免 Python 关键字）
soup.find("a", href="https://example.com")

# 按文本
soup.find("a", text="Click")
soup.find("a", string="Click")

# 按函数（自定义过滤）
soup.find("a", href=lambda x: x and x.startswith("https://"))
```

### find_all() - 找所有

```python
# 基本
links = soup.find_all("a")
print(len(links))  # 所有链接数量

# 多个标签
soup.find_all(["h1", "h2", "h3"])  # 找所有标题

# 按属性
soup.find_all("a", class_="external")
soup.find_all("div", {"data-id": True})  # 任意 data-id

# 按文本
soup.find_all(string="Python")  # 找所有文本为 "Python" 的标签

# 限制数量
soup.find_all("a", limit=5)

# 按函数
soup.find_all("a", href=lambda x: x and ".pdf" in x)
```

### CSS 选择器

```python
# 标签选择器
soup.select("a")                    # 所有 <a>
soup.select("div.content")         # class="content" 的 div
soup.select("div#main")            # id="main" 的 div
soup.select("a[href*=github]")     # href 包含 github 的 a
soup.select("div > p")              # div 的直接子 p
soup.select("ul li:first-child")   # 第一个 li
soup.select("ul li:nth-child(2)")   # 第二个 li
soup.select("input[type=text]")     # type="text" 的 input
```

## 📊 遍历文档树

```python
# 子节点
soup.body.contents       # 直接子节点列表
soup.body.children       # 迭代器
soup.body.descendants    # 所有后代

# 父节点
soup.title.parent        # 父节点（head）
soup.title.parents       # 所有祖先

# 兄弟节点
soup.p.previous_sibling  # 前一个兄弟
soup.p.next_sibling      # 后一个兄弟
soup.p.previous_siblings  # 所有前兄弟
soup.p.next_siblings      # 所有后兄弟
```

## 📋 数据提取

### 提取文本

```python
# 提取所有文本
text = soup.get_text()
text = soup.get_text(separator="\n")        # 用换行分隔
text = soup.get_text(separator=" | ", strip=True)  # 去除空白

# 提取特定元素的文本
print(soup.title.get_text())
print(soup.h1.get_text())
```

### 提取属性

```python
# 单个属性
href = soup.a["href"]
href = soup.a.get("href", "")

# 多个属性
attrs = soup.a.attrs
print(attrs["href"], attrs.get("id"))

# 提取所有链接
links = [a["href"] for a in soup.find_all("a", href=True)]
```

### 提取表格

```python
table = soup.find("table")
rows = table.find_all("tr")

for row in rows:
    cols = row.find_all(["td", "th"])
    data = [col.get_text(strip=True) for col in cols]
    print(data)
```

## 🛠️ 实战：爬取商品信息

```python
import requests
from bs4 import BeautifulSoup

def scrape_products(url):
    r = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })
    soup = BeautifulSoup(r.text, "lxml")
    
    products = []
    for item in soup.select(".product-item"):
        product = {
            "title": item.select_one(".title").get_text(strip=True),
            "price": item.select_one(".price").get_text(strip=True),
            "rating": item.select_one(".rating").get_text(strip=True),
            "link": item.select_one("a")["href"]
        }
        products.append(product)
    
    return products

products = scrape_products("https://example.com/products")
for p in products:
    print(p)
```

## 🔧 修改文档树

```python
# 修改标签内容
tag = soup.h1
tag.string = "New Title"

# 修改属性
tag["class"] = "highlight"

# 添加新标签
new_tag = soup.new_tag("div", class_="new")
soup.body.append(new_tag)

# 插入到指定位置
soup.body.insert(0, new_tag)

# 删除标签
tag.decompose()  # 彻底删除
tag.extract()    # 移除但保留引用
```

## 🛠️ 与 requests 集成

```python
import requests
from bs4 import BeautifulSoup

class SimpleSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0"
    
    def get_soup(self, url, **kwargs):
        r = self.session.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    
    def parse_listing(self, url):
        soup = self.get_soup(url)
        items = []
        for card in soup.select(".card"):
            items.append({
                "title": card.select_one("h2").text,
                "url": card.select_one("a")["href"]
            })
        return items

spider = SimpleSpider()
items = spider.parse_listing("https://example.com/list")
```

## 🎯 总结

**BeautifulSoup 核心要点**：
- ✅ 最简单的 HTML 解析库
- ✅ 4 个核心方法：find/find_all/select/get_text
- ✅ 支持 CSS 选择器
- ✅ 多种解析器（推荐 lxml）
- ✅ 容错性好（处理不规范 HTML）
- ✅ 适合静态页面解析
- ⚠️ 动态页面需要 Selenium / Playwright
- ⚠️ 大量数据考虑 lxml（更快）

**下一步：** [🗄️ SQLAlchemy ORM](/03-libraries/sqlalchemy) — Python ORM
