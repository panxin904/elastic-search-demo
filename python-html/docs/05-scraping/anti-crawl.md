---
title: 反爬对抗
---

# 🛡️ 反爬对抗

> 现代网站部署了**各种反爬虫机制**（User-Agent 检测、IP 限制、验证码等）。爬虫工程师需要掌握**绕过反爬的策略**。

## 🛡️ 常见反爬机制

```
1. User-Agent 检测
2. IP 限速 / 封禁
3. Referer 检测
4. Cookie / Session 校验
5. JavaScript 渲染
6. 验证码（CAPTCHA）
7. 登录验证
8. 蜜罐陷阱（honeypot）
9. CSRF Token
10. 行为分析（鼠标轨迹、点击模式）
```

## 🛠️ 对策 1：设置 User-Agent

```python
import requests

# 真实 User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get("https://example.com", headers=headers)
```

### 随机 User-Agent

```python
import random
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

headers = {"User-Agent": random.choice(USER_AGENTS)}
response = requests.get("https://example.com", headers=headers)
```

### 第三方库 fake-useragent

```bash
pip install fake-useragent
```

```python
from fake_useragent import UserAgent

ua = UserAgent()
headers = {"User-Agent": ua.random}
response = requests.get("https://example.com", headers=headers)
```

## 🛠️ 对策 2：限速（Throttling）

```python
import time
import random

def polite_request(url, min_delay=1, max_delay=3):
    response = requests.get(url)
    time.sleep(random.uniform(min_delay, max_delay))
    return response

# 慢速爬取
for url in urls:
    response = polite_request(url)
    # 处理
```

### 自定义限速

```python
import time

class RateLimiter:
    def __init__(self, rate=10, per=1.0):
        """rate 个请求 per 秒"""
        self.rate = rate
        self.per = per
        self.min_interval = per / rate
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

# 使用
limiter = RateLimiter(rate=2, per=1.0)  # 每秒 2 个请求
for url in urls:
    limiter.wait()
    response = requests.get(url)
```

## 🛠️ 对策 3：IP 代理池

```python
import random
import requests

PROXIES = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "socks5://user:pass@proxy3.example.com:1080",
]

proxy = random.choice(PROXIES)
response = requests.get("https://example.com", proxies={
    "http": proxy,
    "https": proxy
})
```

### 自建代理池

```python
import random

class ProxyPool:
    def __init__(self, proxies):
        self.proxies = proxies
        self.failed = set()
    
    def get(self):
        available = [p for p in self.proxies if p not in self.failed]
        if not available:
            # 重置失败列表
            self.failed.clear()
            available = self.proxies
        return random.choice(available)
    
    def mark_failed(self, proxy):
        self.failed.add(proxy)

# 使用
pool = ProxyPool(PROXIES)
proxy = pool.get()
try:
    response = requests.get("https://example.com", proxies={"http": proxy})
except:
    pool.mark_failed(proxy)
```

### 付费代理服务

```python
# 代理 API 示例（亮数据、快代理、蘑菇代理等）
def get_proxy():
    """从代理服务商获取代理 IP"""
    api_url = "https://api.proxy.com/get?num=1&type=http"
    response = requests.get(api_url)
    return response.json()["data"][0]["ip"]

# 使用
proxy = get_proxy()
response = requests.get("https://example.com", proxies={"http": proxy})
```

## 🛠️ 对策 4：Cookie / Session 处理

```python
import requests

session = requests.Session()

# 1. 先访问主页（获取初始 Cookie）
session.get("https://example.com")

# 2. 登录（带 Cookie）
session.post("https://example.com/login", data={
    "username": "myuser",
    "password": "mypass"
})

# 3. 访问受保护页面（自动带 Cookie）
response = session.get("https://example.com/data")
```

## 🛠️ 对策 5：Referer

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.google.com/",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
response = requests.get("https://example.com", headers=headers)
```

## 🛠️ 对策 6：处理验证码

### 方案 1：第三方打码平台

```python
# 打码平台示例（超级鹰、云打码等）
import requests

def recognize_captcha(image_bytes):
    # 上传到打码平台
    files = {"image": ("captcha.png", image_bytes, "image/png")}
    data = {
        "username": "myuser",
        "password": "mypass",
        "typeid": "1"  # 验证码类型
    }
    response = requests.post("http://api.chaojiying.com/upload", files=files, data=data)
    return response.json()["pic_str"]

# 使用
captcha_image = driver.find_element(...).screenshot_as_png
captcha_text = recognize_captcha(captcha_image)
driver.find_element(By.ID, "captcha").send_keys(captcha_text)
```

### 方案 2：机器学习识别

```python
import ddddocr

ocr = ddddocr.DdddOcr()

with open("captcha.png", "rb") as f:
    image_bytes = f.read()

result = ocr.classification(image_bytes)
print(f"识别结果: {result}")
```

### 方案 3：打码机器学习

```python
# 用 CNN 训练验证码识别模型
# TensorFlow / PyTorch
# 准确率可达 95%+
# 但需要训练数据
```

## 🛠️ 对策 7：蜜罐陷阱

```python
# 蜜罐：网站设置不可见链接，爬虫可能误入
# 解决：只爬取可见的链接

# 1. CSS selector 过滤
response.css("a:visible")  # CSS 选择器筛选

# 2. 颜色过滤（蜜罐常用特殊颜色）
from parsel import Selector

sel = Selector(text=html)
# 过滤 display: none 的元素
visible_links = [a for a in sel.css("a") if "display: none" not in (a.attrib.get("style", ""))]

# 3. 行为检测（蜜罐用 JS 检测爬虫）
# 真实用户会触发 JavaScript 事件
# 爬虫通常只发送 HTTP 请求
# 用 Playwright 模拟真实用户行为
```

## 🛠️ 对策 8：行为分析

```python
# 网站可能检测：
# - 鼠标轨迹
# - 点击模式
# - 浏览速度
# - 停留时间

# 用 Playwright 模拟真实用户
import asyncio
from playwright.async_api import async_playwright

async def human_like_browse():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        
        # 模拟用户滚动（随机速度）
        for _ in range(5):
            scroll_amount = random.randint(100, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # 模拟鼠标移动
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await asyncio.sleep(0.5)
        
        # 点击
        await page.locator("button").click()
        await asyncio.sleep(2)
        
        await browser.close()
```

## 🛠️ 对策 9：CSRF Token

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# 1. 访问登录页（获取 CSRF Token）
response = session.get("https://example.com/login")
soup = BeautifulSoup(response.text, "lxml")
csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

# 2. 带 CSRF Token 登录
response = session.post("https://example.com/login", data={
    "username": "myuser",
    "password": "mypass",
    "csrf_token": csrf_token
})
```

## 🛠️ 对策 10：请求签名

```python
# 一些网站对请求参数进行签名（防止伪造）
# 需要逆向 JavaScript 找到签名算法

# 1. 用 Playwright 拦截 JavaScript 执行
async def get_signing_algorithm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 拦截 JavaScript 函数
        await page.add_init_script("""
            window._originalSign = window.sign;
            window.sign = function(data) {
                window._capturedSign = { data, result: window._originalSign(data) };
                return window._capturedSign.result;
            };
        """)
        
        await page.goto("https://example.com")
        # 触发 sign 函数
        await page.click("button")
        
        # 提取签名结果
        result = await page.evaluate("window._capturedSign")
        return result
```

## 🛠️ 综合爬虫架构

```python
import asyncio
import random
import requests
from playwright.async_api import async_playwright

class AdvancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = self.load_user_agents()
        self.proxies = self.load_proxies()
    
    def load_user_agents(self):
        return [
            "Mozilla/5.0 (Windows NT 10.0) ...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) ..."
        ]
    
    def load_proxies(self):
        # 从代理池 API 加载
        return []
    
    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.google.com/"
        }
    
    def get_proxy(self):
        if self.proxies:
            return random.choice(self.proxies)
        return None
    
    async def scrape(self, url):
        # 1. 简单页面：requests
        if self.is_simple_page(url):
            response = self.session.get(
                url,
                headers=self.get_headers(),
                proxies={"http": self.get_proxy()} if self.get_proxy() else None,
                timeout=10
            )
            return self.parse_html(response.text)
        
        # 2. 复杂页面：Playwright
        else:
            return await self.scrape_dynamic(url)
    
    def is_simple_page(self, url):
        return "/static/" in url
    
    def parse_html(self, html):
        # 解析
        return []
    
    async def scrape_dynamic(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 模拟真实用户
            await page.set_extra_http_headers(self.get_headers())
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            
            content = await page.content()
            
            await browser.close()
            return self.parse_html(content)
    
    async def batch_scrape(self, urls):
        tasks = [self.scrape(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# 使用
scraper = AdvancedScraper()
results = asyncio.run(scraper.batch_scrape(urls))
```

## 🛡️ 反爬的道德与法律

```
⚠️ 爬虫注意事项：
  1. 遵守 robots.txt
  2. 不要对服务器造成过大压力
  3. 不要爬取用户隐私数据
  4. 不要用于商业牟利（看网站条款）
  5. 公开数据 vs 私有数据（注意区分）
  6. 反爬绕过可能违反法律（部分司法管辖区）
```

## 🎯 总结

**反爬对抗核心要点**：
- ✅ 设置 User-Agent（最基础）
- ✅ 控制请求频率（限速）
- ✅ 使用代理池（IP 轮换）
- ✅ 处理 Cookie / Session
- ✅ 验证码识别（打码平台 / ML）
- ✅ 行为分析对抗（模拟真实用户）
- ✅ 蜜罐陷阱（过滤隐藏链接）
- ✅ Playwright 解决动态渲染
- ⚠️ 遵守 robots.txt 和网站条款
- ⚠️ 谨慎使用高强度反爬技术

**下一步：** [🤖 AI 应用概览](/06-ai-ml/overview) — Python AI/ML 生态


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
