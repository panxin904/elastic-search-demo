---
title: Scrapy 框架
---

# ⚡ Scrapy 框架

> **Scrapy** 是 Python **最专业的爬虫框架**，专为**大规模网络爬取**设计。提供**Spider、Pipeline、Item、Middleware** 等完整组件。

## 🎯 Scrapy 优势

```
✅ 工业级：成熟稳定，文档完善
✅ 异步：基于 Twisted（高性能）
✅ 完整生态：Spider + Pipeline + Middleware
✅ 可扩展：自定义组件丰富
✅ 内置：Item 提取、链接跟进、数据清洗

对比：
  - requests + BS4：简单爬虫
  - Scrapy：大规模爬虫（生产首选）
```

## 🚀 快速开始

### 安装

```bash
pip install scrapy
```

### 创建项目

```bash
# 创建 Scrapy 项目
scrapy startproject myproject

cd myproject
```

### 项目结构

```
myproject/
├── scrapy.cfg              # 项目配置
└── myproject/
    ├── __init__.py
    ├── items.py           # Item 定义
    ├── middlewares.py     # 中间件
    ├── pipelines.py       # 管道（数据处理）
    ├── settings.py        # 项目设置
    └── spiders/            # 爬虫
        ├── __init__.py
        └── quotes.py       # 示例爬虫
```

## 🕷️ 第一个爬虫

### 定义 Spider

```python
# myproject/spiders/quotes.py
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"  # 爬虫名
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    
    def parse(self, response):
        # 提取数据
        for quote in response.css(".quote"):
            yield {
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tag::text").getall()
            }
        
        # 翻页
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### 运行爬虫

```bash
# 运行爬虫
scrapy crawl quotes

# 保存结果到 JSON
scrapy crawl quotes -o quotes.json

# 保存为 CSV
scrapy crawl quotes -o quotes.csv

# 保存为 XML
scrapy crawl quotes -o quotes.xml
```

## 📦 Item 定义

```python
# items.py
import scrapy

class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
```

### 在 Spider 中使用

```python
from myproject.items import QuoteItem

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    
    def parse(self, response):
        for quote in response.css(".quote"):
            item = QuoteItem()
            item["text"] = quote.css(".text::text").get()
            item["author"] = quote.css(".author::text").get()
            item["tags"] = quote.css(".tag::text").getall()
            yield item
```

## 🔧 Selector（选择器）

### CSS 选择器

```python
# 基本
response.css("h1::text").get()              # 第一个 h1 的文本
response.css("a::attr(href)").getall()       # 所有链接的 href
response.css(".item").getall()              # 所有 .item 元素

# 组合
response.css("div.container > p.intro::text").get()
response.css("a[href*='example']::attr(href)").getall()

# 伪类
response.css("li:first-child::text").get()
response.css("li:nth-child(2)::text").get()
```

### XPath 选择器

```python
# 基本
response.xpath("//h1/text()").get()
response.xpath("//a/@href").getall()
response.xpath("//div[@class='item']")

# 组合
response.xpath("//div[@class='container']/p[@class='intro']/text()").get()
response.xpath("//a[contains(@href, 'example')]/@href").getall()

# 函数
response.xpath("//li[1]/text()").get()              # 第一个 li
response.xpath("//li[last()]/text()").get()          # 最后一个 li
response.xpath("//li[position()<3]/text()").getall() # 前两个
```

## 🛠️ Spider 进阶

### Spider 类

```python
import scrapy

class AdvancedSpider(scrapy.Spider):
    name = "advanced"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/page1"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 8
    }
    
    def start_requests(self):
        # 动态构造请求
        for page in range(1, 11):
            yield scrapy.Request(
                url=f"https://example.com/list?page={page}",
                callback=self.parse_list,
                meta={"page": page}  # 传递数据
            )
    
    def parse(self, response):
        # 入口解析
        for link in response.css("a.item::attr(href)").getall():
            yield response.follow(link, self.parse_item)
    
    def parse_list(self, response):
        # 列表页解析
        page = response.meta["page"]
        for item in response.css(".item"):
            yield {
                "page": page,
                "title": item.css(".title::text").get(),
                "price": item.css(".price::text").get()
            }
        
        # 递归到详情页
        for link in response.css(".item a::attr(href)").getall():
            yield response.follow(link, self.parse_item)
    
    def parse_item(self, response):
        # 详情页解析
        yield {
            "url": response.url,
            "title": response.css("h1::text").get(),
            "description": response.css(".description::text").get()
        }
```

### CrawlSpider（自动跟进链接）

```python
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class BookSpider(CrawlSpider):
    name = "books"
    start_urls = ["https://books.example.com/"]
    
    rules = (
        # 列表页：跟进到详情页
        Rule(LinkExtractor(restrict_css=".book-link"), callback="parse_item"),
        # 翻页：跟进但不分页解析
        Rule(LinkExtractor(restrict_css=".next-page")),
    )
    
    def parse_item(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "author": response.css(".author::text").get(),
            "price": response.css(".price::text").get()
        }
```

## 🛠️ Pipeline（数据管道）

```python
# pipelines.py
import json
import pymongo
from itemadapter import ItemAdapter

class JsonWriterPipeline:
    """保存为 JSON"""
    def open_spider(self, spider):
        self.file = open("items.json", "w", encoding="utf-8")
    
    def close_spider(self, spider):
        self.file.close()
    
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

class MongoDBPipeline:
    """保存到 MongoDB"""
    def open_spider(self, spider):
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["scrapy_db"]
        self.collection = self.db["items"]
    
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        self.collection.insert_one(ItemAdapter(item).asdict())
        return item

class FilterPipeline:
    """过滤无效数据"""
    def process_item(self, item, spider):
        if not item.get("title"):
            raise scrapy.exceptions.DropItem("Missing title")
        if item.get("price", 0) <= 0:
            raise scrapy.exceptions.DropItem("Invalid price")
        return item
```

### 启用 Pipeline

```python
# settings.py
ITEM_PIPELINES = {
    "myproject.pipelines.FilterPipeline": 100,
    "myproject.pipelines.JsonWriterPipeline": 200,
    "myproject.pipelines.MongoDBPipeline": 300
}
```

## 🛠️ Middleware（中间件）

```python
# middlewares.py
import random

class RotateUserAgentMiddleware:
    """随机 User-Agent"""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ]
    
    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(self.USER_AGENTS)
        return None

class RandomDelayMiddleware:
    """随机延迟"""
    def process_request(self, request, spider):
        delay = random.uniform(0.5, 2.0)
        request.meta["download_delay"] = delay
        return None

class ProxyMiddleware:
    """使用代理"""
    def process_request(self, request, spider):
        request.meta["proxy"] = "http://proxy.example.com:8080"
        return None
```

## 🛠️ 配置

```python
# settings.py

# 并发
CONCURRENT_REQUESTS = 16              # 全局并发数
CONCURRENT_REQUESTS_PER_DOMAIN = 8   # 单域名并发数

# 下载延迟
DOWNLOAD_DELAY = 1                   # 下载延迟（秒）
RANDOMIZE_DOWNLOAD_DELAY = True      # 随机化

# 缓存
HTTPCACHE_ENABLED = True              # 启用 HTTP 缓存
HTTPCACHE_EXPIRATION_SECS = 3600      # 缓存过期
HTTPCACHE_DIR = "httpcache"           # 缓存目录

# 限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
DOWNLOAD_TIMEOUT = 30                # 下载超时

# Robots
ROBOTSTXT_OBEY = True                # 遵守 robots.txt
```

## 🛠️ 实战：豆瓣电影爬虫

```python
# spiders/douban.py
import scrapy

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/top250"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0)",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
    }
    
    def parse(self, response):
        for movie in response.css(".item"):
            yield {
                "title": movie.css(".title::text").get().strip(),
                "rating": movie.css(".rating_num::text").get(),
                "quote": movie.css(".inq::text").get(),
            }
        
        # 翻页
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

```bash
# 运行
scrapy crawl douban -o douban.json
```

## 🎯 总结

**Scrapy 核心要点**：
- ✅ 工业级爬虫框架
- ✅ 异步（基于 Twisted）
- ✅ 完整组件：Spider + Item + Pipeline + Middleware
- ✅ CSS / XPath 选择器
- ✅ 内置：Item 提取、链接跟进、去重
- ✅ Pipeline 处理数据（清洗、存储）
- ✅ Middleware 扩展（UA、代理、限速）
- ⚠️ 学习曲线较陡
- ⚠️ 反爬虫需配合 Playwright / Selenium

**下一步：** [🌍 动态渲染](/05-scraping/dynamic) — Selenium / Playwright


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [data](https://java-px.bot.cd/data/):数据处理
