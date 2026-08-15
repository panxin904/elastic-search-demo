---
title: Wireshark 抓包
---

# Wireshark 抓包

<div class="nt-badge nt-badge-tools">抓包排查</div>
<div class="nt-badge nt-badge-interview">必备</div>

Wireshark 是业界最流行的**网络协议分析器**，能抓取并解析几乎所有常见协议，是网络工程师与开发者的必备工具。

## 1. 抓包原理

- **网卡混杂模式**：抓取所有经过网卡的帧
- **本地抓包**：loopback 在 Windows 上可抓；Linux 上需用 `tcpdump -i lo` 或 Npcap
- **远程抓包**：SSH 端口镜像 / ERSPAN / RPCAP

## 2. 安装

| 平台 | 安装 |
| --- | --- |
| Windows | 官方安装包（带 Npcap） |
| macOS | `brew install wireshark` |
| Linux | `apt install wireshark` / `yum install wireshark` |

> Linux 上 dumpcap 需要 root 或加入 wireshark 组。

## 3. 抓包基础

### 3.1 选择网卡

- 主界面列出所有接口
- 双击接口开始抓包
- 红色 = 有流量，黑色 = 无

### 3.2 实时 vs 离线

- 实时抓取：直接点接口
- 离线分析：File → Open → .pcap

### 3.3 过滤器

#### 显示过滤器（Display Filter）

```
ip.addr == 192.168.1.1
ip.src == 10.0.0.0/24
tcp.port == 443
tcp.flags.syn == 1
http.request.uri contains "login"
dns.qry.name == "example.com"
tcp.stream eq 5
```

#### 捕获过滤器（Capture Filter）—— BPF 语法

```
host 1.2.3.4
port 80
src 192.168.1.0/24 and dst port 443
not arp
tcp[tcpflags] & (tcp-syn) != 0
```

> 捕获过滤器在抓包时就丢，性能高；显示过滤器只影响显示。

## 4. 三栏窗口

| 窗格 | 内容 |
| --- | --- |
| Packet List | 包列表 |
| Packet Details | 协议树 |
| Packet Bytes | 原始字节 |

## 5. 常用协议过滤

| 协议 | 过滤器 |
| --- | --- |
| TCP | `tcp` |
| UDP | `udp` |
| HTTP | `http` |
| HTTPS | `tls` |
| DNS | `dns` |
| ICMP | `icmp` |
| ARP | `arp` |
| SSH | `ssh` |
| FTP | `ftp` |
| SMTP | `smtp` |

## 6. 跟随流（Follow Stream）

- 右键 → Follow → TCP Stream
- 重组完整会话（ASCII / EBCDIC / Hex / C Arrays）

```
右键包 → Follow → TCP Stream
```

## 7. 统计功能

| 菜单 | 用途 |
| --- | --- |
| Conversations | 会话列表（TCP/UDP/IP） |
| Endpoints | 端点统计 |
| Protocol Hierarchy | 协议分布 |
| IO Graphs | 时序图 |
| Flow Graph | 流程图 |
| Expert Information | 警告 |
| TCP Stream Graph | RTT、窗口变化 |
| Statistics → DNS | DNS 详情 |

## 8. 抓包文件格式

| 格式 | 说明 |
| --- | --- |
| .pcap | libpcap 格式 |
| .pcapng | 新版（推荐） |
| .cap | 同 pcap |
| .snoop | Solaris |
| .5vw | NetXRay |

## 9. 抓 HTTPS

Wireshark 默认只能看到 TLS 加密数据。要看明文：

### 9.1 用浏览器日志

```
SSLKEYLOGFILE=/tmp/key.log chrome
Wireshark → Edit → Preferences → TLS → (Pre)-Master-Secret log filename
```

### 9.2 用代理抓

mitmproxy / Charles / Fiddler 替代见 `10-tools/curl.md`。

## 10. 抓包命令行（替代）

```bash
# tcpdump
tcpdump -i eth0 -w out.pcap
tcpdump -i eth0 port 80 -X
tcpdump -i eth0 host 1.2.3.4

# tshark
tshark -i eth0 -Y "http.request"
tshark -r out.pcap -Y "ip.addr==1.2.3.4"
```

## 11. 实战案例

### 案例 1：HTTP 请求分析

```
过滤: http.request
右键 → Follow → HTTP Stream
```

### 案例 2：TCP 重传

```
过滤: tcp.analysis.retransmission
```

### 案例 3：DNS 解析慢

```
过滤: dns
排序 by Time
看 time / response time
```

### 案例 4：RST 排查

```
过滤: tcp.flags.reset == 1
```

### 案例 5：抓取 VoIP

```
Telephony → RTP → Show All Streams
Telephony → RTP → Player
```

## 12. 性能调优

- 限制抓包大小：`-c 10000`
- 切割文件：Capture → Options → Multiple files
- 环形缓冲：保持固定数量
- 关闭实时显示：抓完再看

## 13. 常见面试题

1. **捕获过滤 vs 显示过滤？** 前者抓包时丢包，性能高；后者只过滤显示。
2. **怎么抓 HTTPS 明文？** 浏览器导出 SSLKEYLOGFILE，Wireshark 加载。
3. **怎么找 TCP 重传？** `tcp.analysis.retransmission`。
4. **Follow Stream 干什么？** 重组 TCP 会话。
5. **pcap 和 pcapng 区别？** pcapng 是新版，支持注释、metadata。
6. **怎么只看某个 IP？** `ip.addr == 1.2.3.4`。
