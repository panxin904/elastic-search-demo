---
title: HTTP 协议
---

# HTTP 协议

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-basics">基础</div>

HTTP（HyperText Transfer Protocol）是浏览器与 Web 服务器之间的**请求-响应**协议，是互联网最核心的应用层协议。

## 1. HTTP 特性

| 特性 | 说明 |
| --- | --- |
| 请求-响应模型 | 客户端发起请求，服务器返回响应 |
| 无状态 | 每个请求独立，服务器不保留客户端信息 |
| 无连接（HTTP/1.0） | 每次请求建立新 TCP |
| 灵活 | 可传输任意类型数据（Content-Type） |
| 文本协议 | HTTP/1.x 可直接读懂（除二进制 chunk） |

## 2. URL 格式

```
scheme://user:pass@host:port/path?query#fragment
http://admin:1234@example.com:8080/api/v1/users?id=1#top
```

| 部分 | 说明 |
| --- | --- |
| scheme | 协议（http/https/ws/ftp） |
| user:pass | 认证信息（不推荐 URL 携带） |
| host | 主机名或 IP |
| port | 端口（默认 80 / 443） |
| path | 资源路径 |
| query | 查询参数 |
| fragment | 锚点，客户端使用 |

## 3. HTTP 请求报文

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Accept-Encoding: gzip
Connection: keep-alive
Cookie: sid=abc123

（请求体）
```

| 部分 | 说明 |
| --- | --- |
| 请求行 | 方法 + URI + HTTP 版本 |
| 请求头 | 键值对，元信息 |
| 空行 | 分隔头与体 |
| 请求体 | POST/PUT 的数据 |

## 4. HTTP 响应报文

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1234
Set-Cookie: sid=xyz; HttpOnly
Connection: keep-alive

<html>...</html>
```

| 部分 | 说明 |
| --- | --- |
| 状态行 | HTTP 版本 + 状态码 + 描述 |
| 响应头 | 同上 |
| 空行 | 分隔 |
| 响应体 | 资源内容 |

## 5. 常用方法

| 方法 | 幂等 | 安全 | 用途 |
| --- | --- | --- | --- |
| GET | ✓ | ✓ | 获取资源 |
| POST | ✗ | ✗ | 创建 / 提交 |
| PUT | ✓ | ✗ | 替换 / 全量更新 |
| PATCH | ✗ | ✗ | 部分更新 |
| DELETE | ✓ | ✗ | 删除 |
| HEAD | ✓ | ✓ | 仅响应头 |
| OPTIONS | ✓ | ✓ | 跨域 / 能力查询 |

> **幂等**：多次执行结果一致。**安全**：不修改服务器资源。

## 6. 状态码

| 类别 | 范围 | 含义 |
| --- | --- | --- |
| 1xx | 100-199 | 信息 |
| 2xx | 200-299 | 成功 |
| 3xx | 300-399 | 重定向 |
| 4xx | 400-499 | 客户端错误 |
| 5xx | 500-599 | 服务端错误 |

| 状态码 | 含义 |
| --- | --- |
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 301 | Moved Permanently |
| 302 | Found（临时） |
| 304 | Not Modified |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 409 | Conflict |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

## 7. 常用 Header

### 请求头

| Header | 作用 |
| --- | --- |
| Host | 虚拟主机 |
| User-Agent | 客户端标识 |
| Referer | 来源页 |
| Accept | 接受的内容类型 |
| Accept-Encoding | 接受的压缩（gzip, br） |
| Cookie | 携带 Cookie |
| Authorization | 认证（Bearer xxx） |
| If-None-Match | 缓存 ETag 验证 |

### 响应头

| Header | 作用 |
| --- | --- |
| Content-Type | MIME 类型 |
| Content-Length | 长度 |
| Content-Encoding | 压缩方式 |
| Set-Cookie | 写入 Cookie |
| Cache-Control | 缓存策略 |
| ETag | 资源标识 |
| Location | 重定向目标 |
| Access-Control-Allow-Origin | CORS |

## 8. 缓存策略

```
Cache-Control: max-age=3600           强缓存（秒）
Cache-Control: no-cache               需协商缓存
Cache-Control: no-store               不缓存
Cache-Control: public/private         公共 / 私有
ETag: "abc"                           资源指纹
If-None-Match: "abc"                  客户端缓存版本
Last-Modified / If-Modified-Since     时间协商
```

## 9. 长连接与管线化

- **HTTP/1.0**：每次请求开新 TCP
- **HTTP/1.1**：
  - 默认 `Connection: keep-alive`
  - 长连接（persistent connection）
  - **管线化**（pipelining）—— 客户端可连续发多个请求，但服务器仍按序响应（队头阻塞）

## 10. Cookie / Session / Token

| 机制 | 存储 | 鉴权 |
| --- | --- | --- |
| Cookie | 客户端 | SessionId |
| Session | 服务端 | SessionId → 用户 |
| JWT | 客户端 | 自包含 Token |

## 11. 抓包示例

```http
GET /api/users/1 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1...
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 85

{"id":1,"name":"Alice","email":"alice@example.com"}
```

## 12. 常见面试题

1. **HTTP 与 HTTPS 区别？** HTTPS = HTTP + TLS 加密。
2. **GET vs POST？** GET 参数在 URL，幂等；POST 在 body，可修改。
3. **常见状态码？** 200/301/302/304/400/401/403/404/500/502/503。
4. **HTTP 无状态怎么保持登录？** Cookie + Session / JWT。
5. **HTTP/1.1 队头阻塞？** 同一连接上一个响应延迟会阻塞后续。
6. **HTTP keep-alive 作用？** 复用 TCP 连接，减少握手开销。
