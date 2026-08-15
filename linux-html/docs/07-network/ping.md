---
title: ping / traceroute
---

# ping / traceroute / mtr

> 网络排错三件套。

## 📡 ping - 基础连通性

```bash
ping host                       # 默认一直 ping
ping -c 4 host                  # 4 次后停
ping -i 0.2 host                # 0.2 秒间隔（默认 1s）
ping -s 1000 host               # 包大小 1000 字节
ping -W 2 host                  # 超时 2 秒

# 看 TTL 推测系统
ping host | head -1            # TTL=64 一般 Linux，128 Windows
```

### ping 输出解读

```
64 bytes from 8.8.8.8: icmp_seq=1 ttl=119 time=12.3 ms
│                  │                  │       │
│                  │                  │       └─ 延迟
│                  │                  └─ 跳数（每次过路由减 1）
│                  └─ 序列号
└─ 响应大小（IP 默认 + 8 字节 ICMP）
```

### ping 返回的"问题"

| 输出 | 含义 |
|------|------|
| `time=` | 正常 |
| `time=` 忽大忽小 | 网络拥塞 / 不稳定 |
| `Request timeout` | 对方没响应（防火墙或下线） |
| `Destination host unreachable` | 本地路由不到目标 |
| `Network is unreachable` | 本地路由配置错 |
| `TTL exceeded in transit` | 路由环路（真网络问题） |
| `From host x.x.x.x: ...` | 中间路由才返回 |

## 🛰 traceroute - 路径追踪

```bash
# 默认
traceroute host

# 不解析主机名（更快）
traceroute -n host

# 用 ICMP 而非 UDP（更准）
traceroute -I host

# 看 TCP 路径
traceroute -T host

# 指定起点 TTL
traceroute -m 30 host           # 最多 30 跳
traceroute -q 1 host            # 每跳只发 1 包（快）

# 看 AS 号
traceroute -A host
```

### traceroute 输出解读

```
traceroute to google.com (142.250.x.x), 30 hops max
 1  192.168.1.1      1.2 ms   ← 本地网关
 2  10.0.0.1         5.4 ms   ← ISP
 3  203.0.113.5      8.7 ms   ← ISP 骨干
 4  72.14.215.x     12.1 ms   ← Google 边缘
 5  142.250.x.x     11.9 ms   ← 目标
 ...
12  142.250.x.x     13.5 ms   ← 到达

# " * * *" 表示该跳不响应 ICMP（可能是防火墙）
# 但仍可能往下一跳转发
```

## 📊 mtr - 实时 traceroute

`mtr` 把 ping + traceroute 合并，且能看丢包率。

```bash
sudo apt install mtr
mtr host                        # 实时
mtr -n host                     # 不解析
mtr -r -c 100 host              # 报告模式（非交互）
mtr -j host                     # JSON 输出

# 输出示例
# Host                 Loss%  Snt   Last  Avg  Best  Wrst
# 1. 192.168.1.1       0.0%   100    1.2  1.5  0.8   3.2
# 2. 10.0.0.1          0.0%   100    5.4  5.8  4.9   9.1
# 3. 203.0.113.5       0.0%   100    8.7  9.0  7.5  15.0
# 4. ???               100.0%  100    0.0  0.0  0.0   0.0   ← 丢 100%（可能丢包或屏蔽）
# 5. 142.250.x.x       5.0%   100   12.1 13.2 11.5  25.0   ← 这一跳开始丢 5%
```

### 关键：丢包在哪一跳

```
# 在第 1 / 2 跳丢：本地 / ISP
# 在某跳开始丢但后续丢：那一跳链路或设备问题
# 接近目标才丢：目标侧限速
# * * * 但继续走：那一跳屏蔽 ICMP（不代表丢包）
```

## 🪛 实战

### 我访问不了某个网站

```bash
ping -c 4 host                  # 通不通
ping -c 4 8.8.8.8              # DNS 是不是好的
ping -c 4 your-dns-ip          # DNS 通不通

traceroute host                 # 哪里断了
mtr -r -c 50 host              # 持续看哪跳丢

curl -I https://host           # TCP 80/443 通不通
nslookup host                  # DNS 解析正常吗
```

### DNS 间歇不通

```bash
mtr 8.8.8.8                    # 看路径
# 如果路径某跳丢包率突变，可能是运营商问题

# 改 DNS 临时对比
sudo systemd-resolve --set-dns 8.8.8.8
```

### 跨大洲延迟高

```bash
mtr japan-host
# 1. 192.168.1.1     1ms
# 2. 10.0.0.1        5ms
# 3. ... 国际海缆 ...    250ms  ← 跳数大即物理距离
```

## ❓ 常见问题

```bash
# "ping localhost 不通"
# IPv6 vs IPv4 问题
ping ::1                        # IPv6
ping 127.0.0.1                  # IPv4

# "ping 通但 curl 不通"
# 端口被防火墙拦了
# 80 端口能 ping 但 443 不通？firewall / SELinux

# "mtr 一直 * * *"
# 那一跳屏蔽 ICMP，不一定坏
# 看后续跳的延迟是否合理
```

## 🔗 下一步

- [ip / ifconfig](/07-network/ip)
- [curl / wget](/07-network/curl)
- [DNS 解析](/07-network/dns)