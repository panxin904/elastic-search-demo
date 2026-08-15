---
title: ARP 协议
---

# ARP 协议

<div class="nt-badge nt-badge-network">网络层</div>
<div class="nt-badge nt-badge-datalink">链路层</div>

ARP（Address Resolution Protocol）用于将 **IP 地址解析为 MAC 地址**，是 IPv4 网络中主机通信的第一步。

## 1. 为什么需要 ARP

```
应用层   HTTP
传输层   TCP
网络层   IP      ← 目标 IP 已知
链路层   Ethernet ← 需要目标 MAC
物理层
```

主机拿到目标 IP 后，需要知道对方的 MAC 才能在局域网发帧，ARP 完成这一映射。

## 2. ARP 工作过程

```
主机 A (192.168.1.1)  ──ARP Request──>  广播 (FF:FF:FF:FF:FF:FF)
                                            │
                       主机 B (192.168.1.2) │ 目标 IP 匹配
                                            ↓
主机 A  <──ARP Reply (含 B 的 MAC)──  单播回复
```

| 步骤 | 动作 |
| --- | --- |
| 1 | A 检查本机 ARP 缓存，无则广播 ARP Request |
| 2 | 全网段主机收到，只有目标 IP 匹配者回应 |
| 3 | B 单播 ARP Reply 给 A，含自己的 MAC |
| 4 | A 缓存映射到 ARP 表 |

## 3. ARP 报文格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Hardware Type (1=Ethernet)          |   Protocol Type |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  HLen  |  PLen |     Operation (1=req,2=rep)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Sender MAC Address (6 octets)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Sender IP Address (4 octets)                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Target MAC Address (6 octets)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Target IP Address (4 octets)                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- 硬件类型：1 = 以太网
- 协议类型：0x0800 = IPv4
- 操作：1 = Request，2 = Reply

## 4. ARP 缓存

| 字段 | 说明 |
| --- | --- |
| IP 地址 | 目标 IP |
| MAC 地址 | 解析出的 MAC |
| 类型 | 动态（学习）/ 静态（手动） |
| 生存期 | 默认 Linux 60s、Windows 15-45s |

```bash
# Linux
arp -n
ip neigh show

# Windows
arp -a
```

## 5. ARP 类型

| 类型 | 说明 |
| --- | --- |
| ARP | 标准 IP → MAC |
| RARP | MAC → IP（已被 BOOTP/DHCP 替代） |
| Proxy ARP | 路由器代答，帮不同子网主机解析 |
| Gratuitous ARP | 主动广播自己的 IP-MAC，用于宣告 / 冲突检测 |
| Inverse ARP | Frame Relay 中用 DLCI 找 IP |

## 6. 免费 ARP（Gratuitous ARP）

- 主机主动发送 ARP Request，**目标 IP = 自己 IP**
- 用途：
  1. IP 冲突检测
  2. 通告新 MAC（如更换网卡）
  3. 更新其他主机 ARP 缓存

## 7. ARP 攻击与防御

### 常见攻击

| 攻击 | 原理 | 危害 |
| --- | --- | --- |
| ARP 欺骗 | 伪造 IP-MAC 映射 | 中间人攻击、流量劫持 |
| ARP 泛洪 | 大量伪造 ARP | 交换机 MAC 表溢出 |
| 拒绝服务 | 让 ARP 表错乱 | 通信中断 |

### 防御措施

| 措施 | 原理 |
| --- | --- |
| 静态 ARP 绑定 | 手动写死关键主机映射 |
| 802.1X + DHCP Snooping | 限制非法 DHCP |
| DAI（Dynamic ARP Inspection） | 检查 ARP 报文合法性 |
| 端口安全 | 限制端口 MAC 数 |

## 8. IPv6 替代方案：NDP

IPv6 中用 **NDP**（Neighbor Discovery Protocol，基于 ICMPv6）替代 ARP：

| IPv4 ARP | IPv6 NDP |
| --- | --- |
| ARP Request/Reply | NS/NA |
| 广播 | 组播（ff02::1:ffxx:xxxx） |
| 单独协议 | ICMPv6 类型 135/136 |
| 无安全 | 可结合 SEND（CGAs） |

## 9. 抓包示例（Wireshark）

```
No.  Source            Dest              Protocol  Info
1    Huawei:xx:xx:xx  Broadcast         ARP       Who has 192.168.1.1? Tell 192.168.1.2
2    aa:bb:cc:dd:ee:ff Huawei:xx:xx:xx  ARP       192.168.1.1 is at aa:bb:cc:dd:ee:ff
```

## 10. 常见面试题

1. **ARP 跨越路由器吗？** 不，ARP 仅用于同一广播域（同一 LAN）。
2. **跨网段通信怎么做？** 主机把包发给网关，由网关再做 ARP 解析下一跳。
3. **ARP 缓存表老化时间？** Linux ~60s，Windows 15-45s，可调。
4. **免费 ARP 有什么用？** 检测 IP 冲突、通告 MAC 变更。
5. **如何防止 ARP 欺骗？** 静态绑定、DAI、端口安全。
