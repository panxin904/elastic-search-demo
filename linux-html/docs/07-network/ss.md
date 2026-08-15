---
title: ss / netstat
---

# ss / netstat - 看端口 / 连接

> `netstat` 老、deprecated；`ss` 是现代替代（socket statistics）。

## 🆚 ss vs netstat

| | ss | netstat |
|--|-----|---------|
| 包 | iproute2（默认装） | net-tools（要装） |
| 速度 | 快 | 慢（遍历 /proc） |
| 功能 | 看 socket + 路由表 | 仅 socket |

```bash
# 装 net-tools（兼容）
sudo apt install net-tools
```

## 🔍 ss 基础

```bash
ss                              # 默认 TCP established
ss -a                            # 所有（listen / established / 等）
ss -t                            # 仅 TCP
ss -u                            # 仅 UDP
ss -x                            # Unix socket
ss -l                            # 仅 listen
ss -p                            # 看进程（需 root）
ss -n                            # 不解析（更快）
ss -tunlp                        # 组合：TCP+UDP+数字+listen+进程

# 经典 3 选 1
ss -tlnp                         # 监听中的 TCP 端口
ss -tnp                          # 所有 TCP 连接
ss -tln                          # 仅数字 + listen
```

## 📜 输出字段

```
State    Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process
LISTEN   0       128    0.0.0.0:22            0.0.0.0:*          users:(("sshd",pid=1234))
ESTAB    0       0      192.168.1.10:22       192.168.1.5:54321  users:(("sshd",pid=5678))
```

| 状态 | 含义 |
|------|------|
| LISTEN | 监听 |
| ESTAB | established 连接 |
| TIME-WAIT | 主动关闭方 |
| CLOSE-WAIT | 被动关闭方（应用未 close） |
| FIN-WAIT-1/2 | 关闭中 |
| SYN-SENT / SYN-RECV | 三次握手 |

## 🎯 过滤

```bash
# 按端口
ss -tlnp 'sport = :80'
ss -tlnp 'sport = :22 or sport = :80'

# 按状态
ss -t state established
ss -t state time-wait | head

# 按进程
ss -tlnp 'users match "nginx"'

# 按 IP
ss -t dst 192.168.1.5
```

## 📊 实战

### 看哪些进程监听端口

```bash
ss -tlnp
# State  Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
# LISTEN 0       128     0.0.0.0:80          0.0.0.0:*         users:(("nginx",pid=1234,fd=5))
# LISTEN 0       128     0.0.0.0:22          0.0.0.0:*         users:(("sshd",pid=567,fd=4))

# 谁占用 8080
ss -tlnp 'sport = :8080'
# 没结果就是没人监听（端口未开）
```

### TCP 连接统计

```bash
ss -s
# TCP:   50 (estab 30, closed 10, orphaned 0, timewait 5)
# ...
```

### 看 TIME_WAIT 数量

```bash
ss -tan state time-wait | wc -l
# 太多 → 调 /etc/sysctl.conf
# net.ipv4.tcp_max_tw_buckets = 131072
# net.ipv4.tcp_tw_reuse = 1
```

### 看 socket 缓冲

```bash
ss -t -i                        # 显示内部 TCP 信息（cwnd / rtt / etc）
```

## 🔧 与 lsof 对比

```bash
lsof -i :80                     # 看谁占用 80 端口（不区分 TCP/UDP）
lsof -p <pid>                   # 该进程的所有文件 / socket
lsof -u alice                   # alice 的所有 socket
```

## 🪛 netstat（兼容老习惯）

```bash
netstat -tlnp                   # 等价 ss -tlnp
netstat -an | grep ESTAB       # 看 established
netstat -s                      # 协议统计
```

## 🩺 实战排查

### "服务起不来，端口被占"

```bash
ss -tlnp 'sport = :3306'
# mysql 8084,fd=20  ← 看到 PID

# 或
lsof -i :3306
# COMMAND  PID  USER   FD   TYPE  DEVICE  SIZE/OFF  NODE  NAME
# mysqld  8084  mysql  20u  IPv4  ...     TCP    *:3306 (LISTEN)
```

### "TIME_WAIT 太多"

```bash
ss -tan state time-wait | wc -l

# 调内核参数
sudo sysctl -w net.ipv4.tcp_max_tw_buckets=131072
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
```

### "外网 TCP 连不上但本地能"

```bash
ss -tln                          # 看 nginx / app 是否真监听了 0.0.0.0
# LISTEN 0.0.0.0:80    ← OK
# LISTEN 127.0.0.1:80  ← 只监听本地（防火墙后不可达）

# 然后看防火墙
sudo iptables -L -n
sudo ufw status
```

### "看每个连接的速率"

```bash
# 实时
watch -n 1 "ss -tlnp"
```

## 🆚 替代品

| 工具 | 何时 |
|------|------|
| `ss` | 默认首选 |
| `netstat` | 老脚本兼容 |
| `lsof -i` | 想看具体 socket 文件描述符 |
| `tcpdump` | 看具体包 |

## 🔗 下一步

- [ip / ifconfig](/07-network/ip)
- [curl / wget](/07-network/curl)
- [防火墙 / iptables](/08-firewall-ssh/iptables)