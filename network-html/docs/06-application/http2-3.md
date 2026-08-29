---
title: HTTP/2 与 HTTP/3
date: 2026-08-15  # date-auto-injected
---

# HTTP/2 与 HTTP/3

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-cloud">性能</div>

HTTP/2 与 HTTP/3 是为解决 HTTP/1.1 **队头阻塞、连接数受限、协议冗余**等问题而设计的演进协议。

## 1. HTTP/1.1 的痛点

| 问题 | 现象 |
| --- | --- |
| 队头阻塞 | 一个响应延迟阻塞后续 |
| 明文协议 | 体积大、解析慢 |
| 头部重复 | Cookie、UA 等重复传输 |
| 并发受限 | 浏览器同域 6 个 TCP 连接 |
| 无优先级 | 无法表达资源重要程度 |

## 2. HTTP/2 核心特性

| 特性 | 作用 |
| --- | --- |
| 二进制分帧 | 协议解析更快 |
| 多路复用 | 1 连接并行多个 stream |
| 头部压缩（HPACK） | 减少重复 header |
| 服务器推送（已弃用） | 主动推资源 |
| 流量优先级 | 关键资源优先 |
| 首部表 | 客户端/服务端共享历史 header |

## 3. HTTP/2 帧与流

### 3.1 帧（Frame）

最小通信单位，9 字节头部 + 负载：

```
+-----------------------------------------------+
|  Length (24) |  Type (8) | Flags (8) |  R (1) |
+-----------------------------------------------+
|              Stream Identifier (31)           |
+-----------------------------------------------+
|  Frame Payload (Length)                        |
+-----------------------------------------------+
```

类型：DATA、HEADERS、PRIORITY、RST_STREAM、SETTINGS、PING、GOAWAY、WINDOW_UPDATE、CONTINUATION、PUSH_PROMISE。

### 3.2 流（Stream）

- 虚拟的"双向字节流"
- 同一连接上可有多个 stream
- 每个 stream 有唯一 ID
- 客户端发起的 stream 奇数，服务器偶数

### 3.3 多路复用

```
TCP Connection
   ├── Stream 1 (HTML)
   ├── Stream 3 (CSS)
   ├── Stream 5 (JS)
   └── Stream 7 (IMG)
```

解决队头阻塞，连接数不再受限。

## 4. 头部压缩 HPACK

- 静态表：61 个常用 header（:method, :path...）
- 动态表：连接期间累积
- 哈夫曼编码
- 减少 header 体积 50%+

## 5. 服务器推送（Server Push，HTTP/2 已弃用）

- 服务器主动推资源（HTML 解析前就推 CSS/JS）
- 实战效果不及预期，HTTP/3 移除

## 6. HTTP/2 仍存在的问题

- **TCP 层队头阻塞**：单个丢包阻塞所有 stream
- TCP 握手 + TLS 握手延迟
- 拥塞控制不可定制

## 7. HTTP/3 与 QUIC

HTTP/3 基于 **QUIC** 协议，QUIC 基于 **UDP**。

### 7.1 QUIC 核心特性

| 特性 | 优势 |
| --- | --- |
| 0-RTT / 1-RTT | 首次 1-RTT，再次 0-RTT |
| 多路复用无队头阻塞 | 单包丢失只影响该 stream |
| 内置 TLS 1.3 | 默认加密 |
| 连接迁移 | IP / 端口变化保持连接 |
| 应用层拥塞控制 | 不依赖内核 |

### 7.2 QUIC 连接

```
QUIC Connection
   ├── Stream 1
   ├── Stream 2
   ├── Stream 3
   ...

每 stream 独立拥塞窗口 / 独立确认
```

## 8. HTTP/3 帧

- 帧类型：HEADERS、DATA、GOAWAY、SETTINGS...
- 头部压缩：**QPACK**（HTTP/2 是 HPACK）
- 多路复用基于 QUIC 流

## 9. 协议对比

| 维度 | HTTP/1.1 | HTTP/2 | HTTP/3 |
| --- | --- | --- | --- |
| 传输 | TCP | TCP | UDP + QUIC |
| 多路复用 | 串行 / 有限连接 | ✓ | ✓（更强） |
| 队头阻塞 | 应用层 | TCP 层 | 无 |
| 头部压缩 | 无 | HPACK | QPACK |
| 握手 | 1-3 RTT | 2-3 RTT | 0-1 RTT |
| 加密 | 可选 TLS | 通常 TLS | 强制 TLS 1.3 |
| 部署难度 | 易 | 中 | 难（UDP） |

## 10. 实战配置

### Nginx 启用 HTTP/2

```nginx
listen 443 ssl http2;
ssl_protocols TLSv1.2 TLSv1.3;
```

### 启用 HTTP/3（Nginx 1.25+）

```nginx
listen 443 quic reuseport;
listen 443 ssl;
add_header Alt-Svc 'h3=":443"; ma=86400';
http3 on;
```

### 客户端检测

```bash
curl -I --http2 https://example.com   # HTTP/2
curl -I --http3 https://example.com   # HTTP/3
```

## 11. 性能对比案例

| 场景 | HTTP/1.1 | HTTP/2 | HTTP/3 |
| --- | --- | --- | --- |
| 100 张图片页 | 6 连接并发，3.2s | 1 连接多路复用，1.1s | 0.9s |
| 弱网 5% 丢包 | 4.5s | 2.8s | 1.4s |
| 移动切换 WiFi | 重新握手 | 重新握手 | 连接迁移不中断 |

## 12. 常见面试题

1. **HTTP/2 怎么解决队头阻塞？** 二进制分帧 + 多路复用。
2. **HTTP/2 还有什么问题？** TCP 层丢包仍阻塞所有 stream。
3. **HTTP/3 为什么用 UDP？** 避开 TCP 内核限制，QUIC 在用户态实现。
4. **HPACK 与 QPACK 区别？** HPACK 用 HPACK 字典，QPACK 改用非阻塞更新。
5. **0-RTT 风险？** 重放攻击，需业务层防重放。
6. **HTTP/2 服务器推送为什么被废弃？** 实际效果有限且增加复杂度。
