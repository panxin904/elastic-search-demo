---
title: Socket 编程
---

# Socket 编程

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-tools">实战</div>

Socket 是应用层与传输层之间的**编程接口**，是网络通信的端点。本章梳理 TCP/UDP 客户端、服务端、IO 模型与常见调优。

## 1. Socket 类型

| 类型 | 协议 | 特点 |
| --- | --- | --- |
| SOCK_STREAM | TCP | 面向连接、可靠、字节流 |
| SOCK_DGRAM | UDP | 无连接、不可靠、数据报 |
| SOCK_RAW | 直接 IP | 自定义协议 / 抓包 |
| SOCK_SEQPACKET | SCTP | 面向消息的可靠连接 |

地址族：
- `AF_INET`：IPv4
- `AF_INET6`：IPv6
- `AF_UNIX`：本机进程间通信

## 2. TCP 客户端 / 服务端流程

### 2.1 服务端

```
socket()  → 创建 socket
bind()    → 绑定地址端口
listen()  → 监听（设置 backlog）
accept()  → 阻塞等待连接
recv()    → 接收数据
send()    → 发送数据
close()   → 关闭
```

### 2.2 客户端

```
socket()  → 创建 socket
connect() → 发起三次握手
send()    → 发送数据
recv()    → 接收数据
close()   → 关闭（四次挥手）
```

## 3. Python 示例

### TCP Echo Server

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 9999))
server.listen(128)

while True:
    conn, addr = server.accept()
    with conn:
        print(f"connected: {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)   # echo
```

### TCP Client

```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))
client.sendall(b'hello')
data = client.recv(1024)
print(data)
client.close()
```

### UDP 示例

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 9999))
while True:
    data, addr = server.recvfrom(1024)
    print(f"recv from {addr}: {data}")
    server.sendto(b'pong', addr)
```

## 4. Java 示例

```java
// Server
ServerSocket server = new ServerSocket(9999);
while (true) {
    Socket conn = server.accept();
    new Thread(() -> {
        try (InputStream in = conn.getInputStream();
             OutputStream out = conn.getOutputStream()) {
            byte[] buf = new byte[1024];
            int n;
            while ((n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
            }
        } catch (IOException e) { e.printStackTrace(); }
    }).start();
}

// Client
Socket client = new Socket("127.0.0.1", 9999);
client.getOutputStream().write("hello".getBytes());
byte[] buf = new byte[1024];
int n = client.getInputStream().read(buf);
System.out.println(new String(buf, 0, n));
client.close();
```

## 5. 关键 Socket 选项

| 选项 | 作用 |
| --- | --- |
| SO_REUSEADDR | 重启服务时复用 TIME_WAIT 端口 |
| SO_KEEPALIVE | 启用 TCP 保活 |
| TCP_NODELAY | 关闭 Nagle（小包立即发） |
| TCP_QUICKACK | 立即回 ACK |
| SO_SNDBUF / SO_RCVBUF | 发送 / 接收缓冲 |
| SO_LINGER | 控制 close 行为 |
| TCP_FASTOPEN | 启用 TFO |

## 6. IO 模型

| 模型 | 特点 | 典型 |
| --- | --- | --- |
| Blocking IO | 阻塞 | 早期 Java |
| Non-Blocking IO | 非阻塞 + 轮询 | NIO Selector |
| IO Multiplexing | 多路复用 | epoll / kqueue / select |
| Signal-Driven | 信号驱动 | SIGIO |
| Async IO | 全异步 | io_uring / IOCP |

### epoll 示例（Python selectors）

```python
import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    print(f"accept: {addr}")
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1024)
    if data:
        print(f"recv: {data}")
        conn.sendall(data)
    else:
        sel.unregister(conn)
        conn.close()

server = socket.socket()
server.bind(('0.0.0.0', 9999))
server.listen(100)
server.setblocking(False)
sel.register(server, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
```

## 7. 高并发框架

| 框架 | IO | 线程模型 | 性能 |
| --- | --- | --- | --- |
| Netty | NIO | Reactor | 极高 |
| gRPC | NIO | 异步 | 极高 |
| Nginx | epoll | 多进程 | 极高 |
| Node.js | libuv | 单线程事件循环 | 高 |
| Go net | goroutine | M:N | 极高 |

## 8. 常用工具

```bash
# 查看连接
ss -tan
netstat -tan

# 看某个进程的 socket
lsof -p PID
ls /proc/PID/fd

# 模拟客户端
nc 127.0.0.1 9999
curl -v telnet://127.0.0.1:9999

# 压测
wrk -c100 -t10 http://localhost:8080
ab -n 10000 -c 100 http://localhost:8080/
```

## 9. 常见问题

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| bind: address already in use | 端口被占 / TIME_WAIT | SO_REUSEADDR |
| Too many open files | fd 耗尽 | ulimit / 限制连接 |
| Connection reset | RST | 检查对端、SO_LINGER |
| Broken pipe | 已关连接发数据 | 忽略 SIGPIPE |
| Connection timeout | 网络不可达 / SYN 丢 | 检查路由、防火墙 |

## 10. 常见面试题

1. **socket() 返回什么？** 整数文件描述符。
2. **listen() 中 backlog 含义？** 已连接未 accept 的最大队列。
3. **accept() 阻塞条件？** 无新连接时阻塞。
4. **TCP_NODELAY 作用？** 关闭 Nagle，小包立即发。
5. **epoll vs select？** epoll O(1)，select O(n) 且 fd 数受限。
6. **Reactor vs Proactor？** Reactor 同步 IO + 复用，Proactor 全异步。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
