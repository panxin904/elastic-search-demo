---
title: tcpdump 与 curl
---

# tcpdump 与 curl

<div class="nt-badge nt-badge-tools">调试工具</div>
<div class="nt-badge nt-badge-basics">基础</div>

`tcpdump` 是 Linux 命令行抓包工具，`curl` 是 HTTP 调试瑞士军刀。两者结合足以解决大部分网络调试问题。

## 1. tcpdump 基础

```bash
# 抓取所有
tcpdump -i eth0

# 限制数量
tcpdump -i eth0 -c 100

# 保存到文件
tcpdump -i eth0 -w out.pcap

# 读取文件
tcpdump -r out.pcap

# 详细输出
tcpdump -i eth0 -v
tcpdump -i eth0 -vvv

# 数字（不解析）
tcpdump -i eth0 -n

# ASCII
tcpdump -i eth0 -A

# 十六进制
tcpdump -i eth0 -X
```

## 2. BPF 过滤器

| 表达式 | 含义 |
| --- | --- |
| host 1.2.3.4 | IP 过滤 |
| src 1.2.3.4 | 源 IP |
| dst 1.2.3.4 | 目标 IP |
| net 192.168.0.0/24 | 网段 |
| port 80 | 端口 |
| src port 80 | 源端口 |
| tcp | 协议 |
| udp | 协议 |
| icmp | 协议 |
| arp | 协议 |
| not arp | 排除 |
| and / or | 逻辑 |
| `tcp[0:4] = 0xDEADBEEF` | 字节比较 |

```bash
# 组合
tcpdump -i eth0 host 1.2.3.4 and port 80
tcpdump -i eth0 src net 10.0.0.0/8 and dst port 443
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0'   # SYN 包
tcpdump -i eth0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'  # HTTP 数据
```

## 3. 高级用法

```bash
# 按时间戳
tcpdump -tttt -i eth0

# 抓包大小
tcpdump -i eth0 -s 0          # 完整包
tcpdump -i eth0 -s 64         # 前 64 字节

# 文件大小
tcpdump -i eth0 -w out.pcap -C 100 -W 5   # 5 个 100MB 文件循环

# 抓包轮转
tcpdump -i eth0 -G 60 -w 'out-%Y%m%d-%H%M%S.pcap' -w out.pcap
```

## 4. 抓取 HTTP 请求

```bash
# 输出包内容
tcpdump -i eth0 -A -s 0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
```

输出示例：
```
GET /api HTTP/1.1
Host: example.com
User-Agent: curl/7.79.1
```

## 5. 抓取 MySQL

```bash
tcpdump -i eth0 -A -s 0 'tcp port 3306' | head -100
```

## 6. curl 基础

```bash
# 简单 GET
curl https://example.com

# 保存文件
curl -O https://example.com/file.zip
curl -o file.zip https://example.com/file.zip

# 详细
curl -v https://example.com

# 跟随重定向
curl -L https://example.com

# 显示头部
curl -I https://example.com

# 自定义 UA
curl -A "Custom" https://example.com
```

## 7. POST 请求

```bash
# 表单
curl -X POST -d "user=alice&pass=secret" https://api.example.com/login

# JSON
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"alice","age":30}' https://api.example.com/users

# 文件
curl -X POST -F "file=@/path/to/file" https://api.example.com/upload
```

## 8. Header 与认证

```bash
# 自定义 Header
curl -H "Authorization: Bearer xxx" -H "X-Request-ID: abc" URL

# Cookie
curl -b "sid=xxx" URL
curl -c cookies.txt URL

# Basic Auth
curl -u user:pass URL

# 客户端证书
curl --cert client.crt --key client.key URL
```

## 9. HTTPS / TLS

```bash
# 跳过证书验证
curl -k https://self-signed.example.com

# 指定 CA
curl --cacert ca.crt https://example.com

# 协议版本
curl --tlsv1.2 https://example.com
curl --tlsv1.3 https://example.com

# 详细 TLS
curl -v --tls-max 1.3 https://example.com 2>&1 | grep -i TLS

# 导出 SSLKEYLOG
SSLKEYLOGFILE=/tmp/key.log curl -v https://example.com
```

## 10. 性能测试

```bash
# 限速
curl --limit-rate 100k https://example.com/file

# 时间
curl -w "@format.txt" -o /dev/null -s https://example.com
# format.txt:
#   time_namelookup: %{time_namelookup}\n
#   time_connect:    %{time_connect}\n
#   time_appconnect: %{time_appconnect}\n
#   time_pretransfer:%{time_pretransfer}\n
#   time_redirect:   %{time_redirect}\n
#   time_starttransfer:%{time_starttransfer}\n
#   time_total:      %{time_total}\n
```

## 11. 调试 HTTP/2 / HTTP/3

```bash
# HTTP/2
curl --http2 -I https://example.com

# HTTP/3（需 curl 编译 QUIC）
curl --http3 -I https://example.com
```

## 12. WebSocket

```bash
# websocat
websocat wss://echo.websocket.events
```

## 13. 常用组合

```bash
# 测试 API 端到端
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxx" \
  -d '{"q":"hello"}' \
  -w "\nHTTP %{http_code} | %{time_total}s\n" \
  https://api.example.com/search

# 抓包 + 重放
tcpdump -i eth0 -w out.pcap 'tcp port 80' &
curl -X POST -d @body.json URL
```

## 14. 其他工具

| 工具 | 用途 |
| --- | --- |
| ab / wrk | 压测 |
| hey | Go 压测 |
| vegeta | 压测 |
| mitmproxy | HTTPS 抓包改包 |
| Charles | GUI 抓包 |
| Postman | API 调试 |
| httpie | 人性化 curl |
| h2c | HTTP/2 调试 |

## 15. 常见面试题

1. **tcpdump 抓 HTTPS 是什么？** 加密后字节流，要看明文需 SSLKEYLOG。
2. **curl 怎么测时间？** `-w` + 自定义格式。
3. **curl 如何发 JSON？** `-H "Content-Type: application/json" -d '{}'`。
4. **tcpdump 怎么写文件？** `-w out.pcap`。
5. **BPF 是什么？** Berkeley Packet Filter，抓包过滤语法。
6. **curl 怎么跟随重定向？** `-L`。


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
