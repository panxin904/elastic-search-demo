---
title: requests HTTP
---

# 🌐 requests HTTP

> **requests** 是 Python **最流行的 HTTP 客户端库**。简单优雅的 API，强大的功能，几乎所有 Python 项目都用它。

## 🎯 为什么选 requests？

```
✅ 简单（API 直观）
✅ 功能强（Session、Cookie、文件上传）
✅ 稳定（生产环境久经验证）
✅ 生态丰富（requests-html、requests-toolbelt 等）

对比：
  - urllib：标准库，但 API 复杂
  - aiohttp：异步场景
  - httpx：现代异步/同步混合
  - requests：同步场景首选
```

## 🚀 快速开始

### 安装

```bash
pip install requests
```

### Hello World

```python
import requests

# GET 请求
r = requests.get("https://api.github.com")
print(r.status_code)  # 200
print(r.text)          # 响应内容（字符串）
print(r.content)       # 响应内容（字节）
print(r.json())        # JSON 响应（dict）
```

## 📡 各种 HTTP 方法

```python
import requests

# GET
r = requests.get("https://api.example.com/users")

# POST
r = requests.post("https://api.example.com/users", json={
    "name": "Alice",
    "age": 30
})

# PUT
r = requests.put("https://api.example.com/users/1", json={
    "name": "Alice Updated"
})

# PATCH
r = requests.patch("https://api.example.com/users/1", json={
    "age": 31
})

# DELETE
r = requests.delete("https://api.example.com/users/1")

# HEAD
r = requests.head("https://api.example.com/users")

# OPTIONS
r = requests.options("https://api.example.com/users")
```

## 📊 传参

### URL 参数（Query String）

```python
import requests

# 方式 1：params 参数
r = requests.get("https://api.example.com/search", params={
    "q": "python",
    "page": 1,
    "limit": 20
})
# URL: https://api.example.com/search?q=python&page=1&limit=20

# 方式 2：列表参数
r = requests.get("https://api.example.com/search", params=[
    ("q", "python"),
    ("tag", "tutorial"),
    ("tag", "advanced")
])
# q=python&tag=tutorial&tag=advanced

# 方式 3：字符串（手动编码）
r = requests.get("https://api.example.com/search?q=python&page=1")
```

### POST 数据

```python
import requests

# 1. JSON body（最常用）
r = requests.post(url, json={"name": "Alice", "age": 30})
# Content-Type: application/json

# 2. 表单数据（form-encoded）
r = requests.post(url, data={"name": "Alice", "age": 30})
# Content-Type: application/x-www-form-urlencoded

# 3. 多部分表单（multipart/form-data，文件上传）
files = {"file": open("report.pdf", "rb")}
r = requests.post(url, files=files, data={"user": "Alice"})

# 4. 原始数据
r = requests.post(url, data="raw data", headers={"Content-Type": "application/octet-stream"})

# 5. JSON 字符串
import json
r = requests.post(url, data=json.dumps({"name": "Alice"}), 
                 headers={"Content-Type": "application/json"})
```

## 📋 Headers

```python
import requests

# 1. 自定义 Headers
headers = {
    "User-Agent": "MyApp/1.0",
    "Authorization": "Bearer xxxxx",
    "X-Custom-Header": "value",
    "Content-Type": "application/json"
}
r = requests.get(url, headers=headers)

# 2. 查看响应 Headers
r = requests.get("https://api.github.com")
print(r.headers)
print(r.headers["content-type"])
print(r.headers.get("server"))
```

## 🍪 Cookie

```python
import requests

# 1. 自动管理 Cookie（Session 推荐）
session = requests.Session()
r = session.get("https://example.com/login")
r = session.post("https://example.com/login", data={"user": "x", "pass": "y"})
r = session.get("https://example.com/dashboard")  # 自动带 Cookie

# 2. 手动管理
cookies = {"session_id": "abc123"}
r = requests.get(url, cookies=cookies)

# 3. 提取 Cookie
print(r.cookies)
print(r.cookies.get_dict())
```

## 🔐 认证

```python
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

# 1. Basic Auth
r = requests.get(url, auth=HTTPBasicAuth("user", "pass"))

# 2. 简化
r = requests.get(url, auth=("user", "pass"))

# 3. Digest Auth
r = requests.get(url, auth=HTTPDigestAuth("user", "pass"))

# 4. Token
headers = {"Authorization": "Bearer xxxxx"}
r = requests.get(url, headers=headers)
```

## ⏱️ 超时和重试

### 超时

```python
import requests

# 单个超时（connect + read）
r = requests.get(url, timeout=5)

# 分别设置
r = requests.get(url, timeout=(3.05, 27))  # (connect, read)

# 不超时（不推荐）
r = requests.get(url, timeout=None)
```

### 重试

```python
# requests 默认不重试
# 用 urllib3.util.retry.Retry 实现
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,                    # 最多重试 3 次
    backoff_factor=0.5,         # 退避因子
    status_forcelist=[500, 502, 503, 504],  # 哪些状态码重试
    method_whitelist=["GET", "POST"]          # 哪些方法重试
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

r = session.get(url)  # 自动重试
```

### tenacity（推荐）

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), 
       wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch(url):
    return requests.get(url)

r = fetch(url)  # 自动重试
```

## 🔄 Session（连接池）

```python
import requests

# 1. Session 复用连接
session = requests.Session()

# 跨请求保持 Cookie、Headers
session.headers.update({"User-Agent": "MyApp/1.0"})
r1 = session.get(url1)
r2 = session.post(url2, json={...})

# 2. 性能优势：连接复用（HTTP Keep-Alive）

# 3. Session 配置
session.verify = False  # 禁用 SSL 验证
session.mount("https://", HTTPAdapter(pool_connections=10, pool_maxsize=20))
```

## 📁 文件上传 / 下载

### 上传

```python
import requests

# 单文件
files = {"file": open("report.pdf", "rb")}
r = requests.post("https://api.example.com/upload", files=files)

# 多文件
files = [
    ("files", ("report1.pdf", open("report1.pdf", "rb"), "application/pdf")),
    ("files", ("report2.pdf", open("report2.pdf", "rb"), "application/pdf"))
]
r = requests.post(url, files=files)

# 表单数据 + 文件
data = {"user": "Alice", "description": "Profile photo"}
files = {"photo": open("photo.jpg", "rb")}
r = requests.post(url, data=data, files=files)
```

### 下载

```python
import requests

# 下载文件（小文件）
r = requests.get("https://example.com/file.pdf")
with open("local.pdf", "wb") as f:
    f.write(r.content)

# 流式下载（大文件）
r = requests.get("https://example.com/large.zip", stream=True)
r.raise_for_status()
with open("large.zip", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
```

## 🔍 响应处理

```python
import requests

r = requests.get(url)

# 状态码
print(r.status_code)
print(r.ok)               # 2xx: True
print(r.headers)
print(r.encoding)        # 'utf-8'
print(r.content)         # bytes
print(r.text)            # str
print(r.json())          # dict (JSON)
print(r.cookies)
print(r.elapsed)         # 响应时间
print(r.url)              # 最终 URL
print(r.history)         # 重定向历史
print(r.headers.get("Content-Type"))
print(r.cookies.get_dict())

# 状态码检查
if r.status_code == 200:
    print("Success")
elif r.status_code == 404:
    print("Not Found")

# 抛出异常
r.raise_for_status()  # 4xx/5xx 时抛 HTTPError
```

## 🛡️ SSL / HTTPS

```python
import requests

# 默认验证 SSL 证书
r = requests.get("https://api.example.com")

# 禁用验证（不推荐）
r = requests.get("https://api.example.com", verify=False)

# 指定 CA 证书
r = requests.get("https://api.example.com", verify="/path/to/ca-bundle.crt")

# 指定客户端证书
r = requests.get(url, cert=("/path/client.cert", "/path/client.key"))
```

## 🔌 代理

```python
import requests

# HTTP 代理
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
}
r = requests.get(url, proxies=proxies)

# SOCKS 代理（需要 pysocks）
# pip install pysocks
proxies = {
    "http": "socks5://user:pass@proxy.example.com:1080",
    "https": "socks5://user:pass@proxy.example.com:1080"
}
r = requests.get(url, proxies=proxies)
```

## 📊 实战：HTTP 客户端封装

```python
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(self, base_url, token=None, timeout=10):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = timeout
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["User-Agent"] = "MyApp/1.0"
    
    def request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        try:
            r = self.session.request(method, url, **kwargs)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            logger.error("HTTP %s %s failed: %s", method, url, e)
            raise
    
    def get(self, path, params=None, **kwargs):
        return self.request("GET", path, params=params, **kwargs).json()
    
    def post(self, path, json=None, data=None, **kwargs):
        return self.request("POST", path, json=json, data=data, **kwargs).json()
    
    def put(self, path, json=None, **kwargs):
        return self.request("PUT", path, json=json, **kwargs).json()
    
    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

# 使用
client = HttpClient("https://api.github.com")
user = client.get("/users/octocat")
print(user["login"])
```

## 🎯 总结

**requests 核心要点**：
- ✅ 最流行的 Python HTTP 库
- ✅ 简单优雅的 API
- ✅ Session 复用连接（性能提升）
- ✅ 支持文件上传/下载、流式响应
- ✅ 自动处理 Cookie、重定向、SSL
- ✅ tenacity 库实现自动重试
- ⚠️ 大文件下载用 stream=True
- ⚠️ 生产环境用 Session 而非 requests.get
- ⚠️ 异常处理用 raise_for_status()

**下一步：** [🕷️ BeautifulSoup](/03-libraries/beautifulsoup) — HTML 解析
