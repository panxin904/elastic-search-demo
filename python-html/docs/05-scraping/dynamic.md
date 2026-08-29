---
title: 动态渲染
date: 2026-08-15  # date-auto-injected
---

# 🌍 动态渲染

> 很多现代网站用 **JavaScript** 动态渲染内容（如 React、Vue）。requests 拿到的 HTML 是**空的骨架**，需要用**浏览器自动化工具**（Selenium / Playwright）渲染后再提取。

## 🎯 为什么需要动态渲染？

```
传统 requests 抓取：
  ❌ 拿到 HTML 骨架
  ❌ JavaScript 渲染的内容为空
  ❌ 数据通过 AJAX 异步加载

现代网站：
  ✅ React / Vue / Angular 单页应用
  ✅ 内容由 JavaScript 动态生成
  ✅ 关键数据由 API 异步获取
```

## 🛠️ Playwright（推荐）

### 安装

```bash
# 安装 Python SDK
pip install playwright

# 安装浏览器
playwright install chromium
playwright install firefox
playwright install webkit
```

### Hello World

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Title: {title}")
        
        await browser.close()

asyncio.run(main())
```

## 🎯 同步 API

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://example.com")
    print(page.title())
    page.screenshot(path="screenshot.png")
    
    browser.close()
```

## 📋 常用操作

### 导航

```python
# 打开页面
await page.goto("https://example.com")

# 等待加载
await page.wait_for_load_state("networkidle")  # 网络空闲
await page.wait_for_selector(".content")         # 等待元素
await page.wait_for_timeout(3000)                # 等待 3 秒

# 浏览器历史
await page.go_back()
await page.go_forward()
await page.reload()
```

### 元素操作

```python
# 定位元素
element = page.locator("css-selector")
element = page.locator("text=Hello")
element = page.locator("//xpath")  # XPath

# 查找
await page.locator("button").click()
await page.locator("input").fill("text")
await page.locator("select").select_option("value")

# 等待
await page.wait_for_selector("button.submit")
await page.locator("button").wait_for(state="visible")

# 获取文本/属性
text = await page.locator(".title").text_content()
href = await page.locator("a").get_attribute("href")

# 多个元素
items = await page.locator(".item").all()
for item in items:
    title = await item.locator(".title").text_content()
    print(title)
```

### 提取数据

```python
# 简单文本
title = await page.locator("h1").text_content()

# HTML 内容
html = await page.content()

# 属性
href = await page.locator("a").get_attribute("href")

# 截图
await page.screenshot(path="page.png", full_page=True)
```

## 🛠️ 实战：爬取动态网站

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_dynamic_site():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置 User-Agent
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36"
        })
        
        # 打开页面
        await page.goto("https://spa-example.com")
        
        # 等待内容加载
        await page.wait_for_selector(".product-list")
        
        # 滚动到底部（触发懒加载）
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
        
        # 提取数据
        products = []
        items = await page.locator(".product-item").all()
        for item in items:
            products.append({
                "name": await item.locator(".name").text_content(),
                "price": await item.locator(".price").text_content(),
                "url": await item.locator("a").get_attribute("href")
            })
        
        await browser.close()
        return products

products = asyncio.run(scrape_dynamic_site())
for p in products:
    print(p)
```

## 🛠️ Selenium（老牌选择）

### 安装

```bash
pip install selenium
# 下载浏览器驱动
# ChromeDriver（推荐与 Chrome 版本一致）
```

### 基本使用

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 创建浏览器
driver = webdriver.Chrome()
driver.get("https://example.com")

# 等待元素
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".content")))

# 提取
title = driver.find_element(By.CSS_SELECTOR, "h1").text
links = driver.find_elements(By.CSS_SELECTOR, "a")

# 关闭
driver.quit()
```

## 🛠️ Playwright vs Selenium

| 维度 | Playwright | Selenium |
|------|-------------|-----------|
| 速度 | 快（异步） | 较慢 |
| API | 现代（async/await） | 传统（同步） |
| 自动等待 | ✅ 内置 | 需手动 |
| 浏览器支持 | Chromium/Firefox/WebKit | 多浏览器 |
| 维护 | 活跃 | 活跃 |
| 调试工具 | ✅ 内置 | 需额外 |
| 上手难度 | 中等 | 中等 |

## 📊 实战：登录 + 爬取

```python
import asyncio
from playwright.async_api import async_playwright

async def login_and_scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. 登录
        await page.goto("https://example.com/login")
        await page.locator("input[name='username']").fill("myuser")
        await page.locator("input[name='password']").fill("mypass")
        await page.locator("button[type='submit']").click()
        
        # 等待登录完成
        await page.wait_for_url("**/dashboard")
        
        # 2. 爬取
        await page.goto("https://example.com/data")
        await page.wait_for_selector(".data-row")
        
        data = []
        rows = await page.locator(".data-row").all()
        for row in rows:
            data.append({
                "title": await row.locator(".title").text_content(),
                "value": await row.locator(".value").text_content()
            })
        
        # 3. 保存 Cookie（下次免登录）
        cookies = await context.cookies()
        
        await browser.close()
        return data

data = asyncio.run(login_and_scrape())
```

## 📊 实战：爬取无限滚动页面

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_infinite_scroll():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com/feed")
        
        # 自动滚动加载
        previous_count = 0
        while True:
            # 滚动到底
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)  # 等待加载
            
            # 检查新增数量
            current_count = await page.locator(".item").count()
            print(f"Items: {current_count}")
            
            # 没有新增则停止
            if current_count == previous_count:
                break
            previous_count = current_count
        
        # 提取所有
        items = []
        elements = await page.locator(".item").all()
        for el in elements:
            items.append({
                "title": await el.locator(".title").text_content(),
                "url": await el.locator("a").get_attribute("href")
            })
        
        await browser.close()
        return items

items = asyncio.run(scrape_infinite_scroll())
```

## 📊 实战：拦截 AJAX 请求

```python
import asyncio
from playwright.async_api import async_playwright

async def intercept_ajax():
    api_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 监听网络请求
        async def handle_response(response):
            if "/api/" in response.url:
                try:
                    data = await response.json()
                    api_data.append({"url": response.url, "data": data})
                except:
                    pass
        
        page.on("response", handle_response)
        
        # 打开页面（触发 AJAX）
        await page.goto("https://spa-example.com")
        await page.wait_for_timeout(5000)
        
        await browser.close()
        return api_data

# 直接获取 API 响应（更快）
data = asyncio.run(intercept_ajax())
```

## 🛠️ 性能优化

```python
# 1. 关闭图片加载（节省带宽）
await page.route("**/*.{png,jpg,jpeg,gif,webp}", lambda route: route.abort())

# 2. 禁用 JavaScript（如不需要）
browser = await p.chromium.launch(java_script_enabled=False)

# 3. 复用浏览器
browser = await p.chromium.launch()
context = await browser.new_context()
# 多个页面共享 context
page1 = await context.new_page()
page2 = await context.new_page()

# 4. 拦截广告和追踪脚本
await page.route("**/ads/**", lambda route: route.abort())
await page.route("**/analytics/**", lambda route: route.abort())
```

## 🎯 总结

**动态渲染核心要点**：
- ✅ Playwright（推荐）：现代、快、API 优雅
- ✅ Selenium：老牌、广泛使用
- ✅ 等待元素加载（wait_for_selector）
- ✅ 自动等待（Playwright 内置）
- ✅ 拦截 AJAX 请求（获取 API 数据）
- ✅ 无限滚动、登录、表单提交都支持
- ⚠️ 性能比 requests 慢（启动浏览器开销）
- ⚠️ 需要安装浏览器驱动

**下一步：** [🛡️ 反爬对抗](/05-scraping/anti-crawl) — 应对反爬虫机制

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
