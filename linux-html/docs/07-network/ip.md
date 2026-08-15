---
title: ip / ifconfig
---

# ip / ifconfig

> `ifconfig` 老、deprecated；`ip` 是现代替代。

## 🆚 ifconfig vs ip

| | ifconfig (net-tools) | ip (iproute2) |
|--|----------------------|----------------|
| 包 | 已 deprecated | 现代默认 |
| 功能 | 看 + 简单配置 | 看 + 配置 + 路由 + 策略 + 命名空间 |
| 语法 | 老式 | 统一 `ip OBJECT COMMAND` |

```bash
# ifconfig 还可能装（保留兼容）
sudo apt install net-tools
ifconfig                       # 老风格
```

## 🔍 ip a - 地址

```bash
ip a                            # 同 ip addr
ip a show dev eth0              # 只看某网卡
ip -4 a                         # 只 IPv4
ip -6 a                         # 只 IPv6
ip -br a                        # 简短输出（脚本友好）
```

输出：

```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.10/24 brd 192.168.1.255
    inet6 fe80::a00:27ff:fe4e:1234/64
```

## 🛣 ip r - 路由表

```bash
ip r                            # 默认路由表
ip r show table main             # main 表
ip route get 8.8.8.8            # 看某 IP 的路由路径
ip r add 10.0.0.0/8 via 192.168.1.1 dev eth0
ip r del 10.0.0.0/8 via 192.168.1.1 dev eth0
ip r add default via 192.168.1.1 dev eth0   # 默认路由
```

## 🔗 ip link - 网卡状态

```bash
ip link                         # 所有网卡
ip link show eth0                # 单个网卡
ip link set eth0 up              # 启用
ip link set eth0 down            # 停用
ip link set eth0 mtu 1500        # 改 MTU
ip link set eth0 name newname    # 改名（限 down 时）

# 看 VLAN
ip link show type vlan
```

## 🅰 ip addr - 配置地址

```bash
# 加 IP
sudo ip addr add 192.168.1.20/24 dev eth0
sudo ip addr add 192.168.1.21/24 dev eth0

# 删 IP
sudo ip addr del 192.168.1.20/24 dev eth0

# 临时生效（重启失效）
sudo ip link set eth0 up
sudo ip addr add 192.168.1.20/24 dev eth0

# 永久生效
sudo nmcli con mod eth0 ipv4.addresses 192.168.1.20/24
# 或改 /etc/network/interfaces
# 或 systemd-networkd
```

## 🌐 ip route - 路由 / 策略

```bash
# 策略路由（基于源 IP）
ip rule add from 192.168.1.0/24 table 100
ip rule list

# 多路由表
echo '100 custom' >> /etc/iproute2/rt_tables
ip route add default via 192.168.1.1 dev eth0 table custom

# 看邻居表（ARP）
ip neigh
ip neigh show dev eth0
ip neigh add 192.168.1.50 lladdr aa:bb:cc:dd:ee:ff dev eth0
```

## 🛜 ip maddr / ip tunnel / ip rule

```bash
ip maddr show                   # 多播地址
ip tunnel show                 # 隧道（IPIP / GRE）
ip rule show                   # 策略路由规则
```

## 🛠 实战

### 配置静态 IP

```bash
# 临时
sudo ip addr add 192.168.1.20/24 dev eth0
sudo ip route add default via 192.168.1.1

# 永久（NetworkManager）
sudo nmcli con mod "Wired connection 1" \
  ipv4.addresses 192.168.1.20/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8 1.1.1.1" \
  ipv4.method manual
sudo nmcli con up "Wired connection 1"

# 永久（Debian /etc/network/interfaces）
auto eth0
iface eth0 inet static
  address 192.168.1.20/24
  gateway 192.168.1.1
  dns-nameservers 8.8.8.8 1.1.1.1
```

### 多 IP 同网卡

```bash
# 加 secondary IP
sudo ip addr add 10.0.0.100/24 dev eth0

# 网卡别名（老式）
# ifconfig eth0:1 10.0.0.100/24  ← 已 deprecated
```

### 看某 IP 走的哪张网卡

```bash
ip route get 8.8.8.8
# 8.8.8.8 via 192.168.1.1 dev eth0 src 192.168.1.10 uid 0
```

## ❓ 常见问题

```bash
# "网断了"
ip link show eth0                # 看状态
ip -s link show eth0             # 看收发包计数 / 错误

# "能 ping 网关但 ping 不通外网"
ip r                            # 看路由 / 默认网关
cat /etc/resolv.conf            # DNS

# "改 IP 不生效，重启后丢失"
# 用 NetworkManager 或 systemd-networkd 持久化
```

## 🔗 下一步

- [ping / traceroute](/07-network/ping)
- [curl / wget](/07-network/curl)
- [ss / netstat](/07-network/ss)