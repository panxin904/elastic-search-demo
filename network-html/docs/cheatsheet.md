---
title: 速记卡
---

# 速记卡

<div class="nt-badge nt-badge-interview">速记</div>
<div class="nt-badge nt-badge-cases">面试</div>

一页速记，覆盖**最常用**的协议、命令、面试题，便于快速回顾。

## 1. 端口速记

| 协议 | 端口 | 用途 |
| --- | --- | --- |
| HTTP | 80 | Web |
| HTTPS | 443 | TLS Web |
| DNS | 53 | 域名解析 |
| SSH | 22 | 远程登录 |
| FTP | 21 / 20 | 文件 |
| SMTP | 25 | 邮件发送 |
| POP3 | 110 | 邮件接收 |
| IMAP | 143 | 邮件 |
| MySQL | 3306 | 数据库 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| MongoDB | 27017 | 文档库 |
| Kafka | 9092 | 消息 |
| ZooKeeper | 2181 | 协调 |
| Elasticsearch | 9200 | 搜索 |

## 2. IP 段速记

| 类别 | 范围 | 用途 |
| --- | --- | --- |
| A | 1.0.0.0 ~ 126.255.255.255 | 大网 |
| B | 128.0.0.0 ~ 191.255.255.255 | 中网 |
| C | 192.0.0.0 ~ 223.255.255.255 | 小网 |
| D | 224.0.0.0 ~ 239.255.255.255 | 组播 |
| 私网 A | 10.0.0.0/8 | 大型 |
| 私网 B | 172.16.0.0/12 | 中型 |
| 私网 C | 192.168.0.0/16 | 小型 |
| 链路本地 | 169.254.0.0/16 | APIPA |
| 链路本地 IPv6 | fe80::/10 | IPv6 |
| 回环 | 127.0.0.0/8 | 本机 |

## 3. 协议号速记（IP）

| 协议 | 编号 |
| --- | --- |
| ICMP | 1 |
| TCP | 6 |
| UDP | 17 |
| IPv6 | 41 |
| GRE | 47 |
| IPsec ESP | 50 |
| IPsec AH | 51 |
| ICMPv6 | 58 |
| OSPF | 89 |

## 4. TCP 标志

| 标志 | 全称 | 含义 |
| --- | --- | --- |
| URG | Urgent | 紧急 |
| ACK | Ack | 确认 |
| PSH | Push | 上交 |
| RST | Reset | 重置 |
| SYN | Sync | 同步 |
| FIN | Finish | 关闭 |

## 5. HTTP 状态码

| 码 | 含义 |
| --- | --- |
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 301 | 永久重定向 |
| 302 | 临时重定向 |
| 304 | Not Modified |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Too Many Requests |
| 500 | Internal Error |
| 502 | Bad Gateway |
| 503 | Unavailable |
| 504 | Gateway Timeout |

## 6. 关键命令

```bash
# 网络排查
ping 8.8.8.8
traceroute baidu.com
mtr -r -c 30 baidu.com
ip addr show
ip route
ss -tan

# 抓包
tcpdump -i eth0 port 80 -w out.pcap
wireshark out.pcap

# HTTP
curl -v https://example.com
curl -I https://example.com

# DNS
dig example.com
dig @8.8.8.8 example.com

# 性能
iperf3 -c 192.168.1.1
speedtest-cli

# 防火墙
iptables -L -n
ufw status
```

## 7. 面试 8 问（速答）

| 问题 | 速答 |
| --- | --- |
| 三次握手目的 | 同步序列号 + 确认收发能力 |
| 四次挥手目的 | 全双工两端分别关闭 |
| TIME_WAIT 作用 | 1 可靠关闭 2 防旧报文 |
| HTTP 队头阻塞 | 同连接前响应慢阻塞后请求 |
| TLS 1.3 改进 | 1-RTT、强制 PFS、AEAD |
| CDN 原理 | 智能 DNS + 边缘节点 + 缓存 |
| TCP 可靠传输 | 序列号 + ACK + 重传 + 校验和 |
| HTTPS 慢在哪 | TLS 握手 + 非对称运算 + 证书 |

## 8. 必记数字

| 数字 | 含义 |
| --- | --- |
| 2^32 | IPv4 地址数 |
| 2^128 | IPv6 地址数 |
| 65535 | TCP 端口数 |
| 2 MSL | TIME_WAIT 时长（默认 60s×2） |
| 1460 | 常见 MSS |
| 1500 | 常见 MTU |
| 3 | 3 次重复 ACK 触发快速重传 |
| 1500-20-20=1460 | IP 头 + TCP 头 |

## 9. 加密算法速记

| 类别 | 推荐算法 |
| --- | --- |
| 对称加密 | AES-256-GCM、ChaCha20-Poly1305 |
| 非对称加密 | ECC P-256、Ed25519、RSA-2048 |
| 哈希 | SHA-256、SHA-3、BLAKE2 |
| 密钥交换 | ECDHE（X25519） |
| 密码哈希 | Argon2、bcrypt |

## 10. 性能调优速记

```bash
# TCP
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_tw_reuse = 1

# 缓冲区
net.ipv4.tcp_rmem = 4096 87380 6291456
net.ipv4.tcp_wmem = 4096 65536 4194304

# 端口
net.ipv4.ip_local_port_range = 10000 65000
```

## 11. 一图速记协议

```
Application:  HTTP / DNS / FTP / SSH
Transport:    TCP (可靠) / UDP (不可靠)
Network:      IP (寻址) / ICMP (错误) / ARP (IP→MAC)
Link:         Ethernet / WiFi / PPP
Physical:     光纤 / 双绞线 / 无线
```

## 12. 抓包常用过滤器

| 过滤器 | 含义 |
| --- | --- |
| `ip.addr == 1.2.3.4` | 特定 IP |
| `tcp.port == 443` | 特定端口 |
| `http.request` | HTTP 请求 |
| `tcp.flags.syn == 1` | SYN 包 |
| `tcp.analysis.retransmission` | 重传 |
| `dns.qry.name == "example.com"` | DNS 查询 |
| `tcp.stream eq 5` | 特定 TCP 流 |
| `not arp` | 排除 ARP |

## 13. 七层模型速记

| 层 | 名称 | 协议 | 设备 |
| --- | --- | --- | --- |
| 7 | 应用 | HTTP/DNS/SSH | — |
| 6 | 表示 | TLS/JPEG | — |
| 5 | 会话 | RPC | — |
| 4 | 传输 | TCP/UDP | 防火墙 |
| 3 | 网络 | IP/ICMP | 路由器 |
| 2 | 数据链路 | Ethernet/VLAN | 交换机 |
| 1 | 物理 | 光纤/铜线 | 网卡 |

## 14. 数据包结构速记

```
TCP segment:  [TCP Header 20B+] [Data]
IP packet:    [IP Header 20B] [TCP segment]
Frame:        [MAC Header 14B] [IP packet] [FCS 4B]
```

## 15. 关键 RFC

| RFC | 主题 |
| --- | --- |
| 791 | IPv4 |
| 793 | TCP |
| 768 | UDP |
| 826 | ARP |
| 792 | ICMP |
| 1122 | Host Requirements |
| 2581 | TCP Congestion Control |
| 5246 | TLS 1.2 |
| 8446 | TLS 1.3 |
| 7540 | HTTP/2 |
| 9000 | QUIC |
| 9110 | HTTP/3 |
