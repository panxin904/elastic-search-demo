---
title: WebSocket
---

# WebSocket

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-cloud">实时</div>

WebSocket 是 HTML5 引入的**全双工通信协议**，在一个 TCP 连接上实现客户端与服务器**双向实时**通信，是 HTTP 的升级。

## 1. 为什么需要 WebSocket

| HTTP 痛点 | WebSocket 解决 |
| --- | --- |
| 单向请求-响应 | 全双工 |
| 实时性差（轮询） | 推送式实时 |
| 每次请求都带 header | 长连接 + 帧开销小 |
| 多请求才能更新 | 一次握手长期通信 |

## 2. 握手升级

WebSocket 基于 HTTP 升级机制（HTTP Upgrade）：

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://example.com
```

服务端响应：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

之后切换为 WebSocket 协议。

## 3. 帧格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

| 字段 | 说明 |
| --- | --- |
| FIN | 1=最后一帧 |
| RSV1~3 | 扩展（压缩等） |
| opcode | 帧类型（0x1=文本、0x2=二进制、0x8=关闭、0x9=ping、0xA=pong） |
| MASK | 客户端发必须置 1 |
| Payload len | 7 bit / 16 bit / 64 bit |
| Masking-key | 客户端帧的 4 字节掩码 |
| Payload | 应用数据 |

## 4. 数据帧类型

| Opcode | 含义 |
| --- | --- |
| 0x0 | 续帧（分片） |
| 0x1 | 文本 |
| 0x2 | 二进制 |
| 0x3-0x7 | 保留 |
| 0x8 | 关闭 |
| 0x9 | Ping |
| 0xA | Pong |
| 0xB-0xF | 保留控制帧 |

## 5. 心跳与连接保活

- 客户端 / 服务端可发 **Ping**（0x9）
- 对端必须回 **Pong**（0xA）
- 浏览器/网关可基于 Ping/Pong 维护连接
- 应用层也可定时业务心跳

## 6. 关闭连接

```
客户端: 发送 opcode=0x8 + close code
服务端: 回 pong + close frame
TCP 四次挥手
```

| 关闭码 | 含义 |
| --- | --- |
| 1000 | 正常 |
| 1001 | 端点离开 |
| 1002 | 协议错误 |
| 1003 | 数据类型错误 |
| 1008 | 策略违规 |
| 1011 | 服务器异常 |

## 7. 性能与限制

- 默认单帧最大 1MB（部分实现 64KB）
- 大数据可分片（opcode 0x0 续帧）
- 头部用 per-message-deflate 压缩
- 同源策略：默认 ws:// 只允许同源，可配 Origin

## 8. 实战：Echo Server（Python）

```python
import asyncio
import websockets

async def echo(ws, path):
    async for msg in ws:
        print(f"recv: {msg}")
        await ws.send(f"echo: {msg}")

start_server = websockets.serve(echo, "0.0.0.0", 9999)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## 9. 实战：浏览器客户端

```js
const ws = new WebSocket('wss://example.com/socket');

ws.onopen = () => {
    ws.send('hello');
};

ws.onmessage = (event) => {
    console.log('recv:', event.data);
};

ws.onclose = (event) => {
    console.log('closed:', event.code);
};

ws.onerror = (err) => {
    console.error(err);
};
```

## 10. Secure WebSocket（WSS）

- 协议：`wss://`
- 端口：443（默认）
- 基于 TLS，等价 HTTPS + WebSocket

## 11. WebSocket 与 HTTP/2 推送

| 维度 | WebSocket | HTTP/2 Push |
| --- | --- | --- |
| 方向 | 全双工 | 服务端单向 |
| 标准 | RFC 6455 | RFC 7540 |
| 浏览器支持 | 全 | 已被多数浏览器弃用 |
| 实际使用 | 广泛 | 极少 |

## 12. 高可用设计

| 维度 | 方案 |
| --- | --- |
| 长连接保持 | 业务心跳 + ping/pong |
| 断线重连 | 客户端指数退避重连 |
| 消息可靠 | 应用层 ACK + 序号 |
| 水平扩展 | Redis Pub/Sub / Kafka / Socket.IO Adapter |
| 反向代理 | Nginx `proxy_set_header Upgrade` |
| 鉴权 | 握手时携带 Token / Cookie |

### Nginx 反向代理

```nginx
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

## 13. 常见面试题

1. **WebSocket vs HTTP？** 全双工 vs 单向请求-响应。
2. **怎么升级协议？** HTTP Upgrade + 101 Switching Protocols。
3. **WebSocket 端口？** ws=80/8080，wss=443/8443。
4. **心跳机制？** ping/pong 帧 + 应用层心跳。
5. **断线重连策略？** 指数退避 + 抖动。
6. **WebSocket 与 Socket.IO？** Socket.IO 是 WebSocket 之上的库，有降级（轮询）和重连机制。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
