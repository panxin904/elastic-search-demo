---
title: IPv6 协议
date: 2026-08-15  # date-auto-injected
---

# IPv6 协议

<div class="nt-badge nt-badge-network">网络层</div>
<div class="nt-badge nt-badge-cloud">未来</div>

IPv6（Internet Protocol version 6）使用 128 bit 地址，从根本上解决 IPv4 地址枯竭问题，并简化了报文头、增强安全与 QoS。

## 1. 为什么要 IPv6

| 问题 | IPv6 解决方案 |
| --- | --- |
| 地址枯竭 | 128 bit，3.4×10^38 个地址 |
| 路由表膨胀 | 层次化聚合 |
| 报文头复杂 | 固定 40 字节，便于硬件转发 |
| 安全缺失 | 原生集成 IPsec |
| 配置繁琐 | SLAAC 无状态自动配置 |
| NAT 滥用 | 充足地址，无需 NAT |

## 2. IPv6 地址表示

```
完整形式：2001:0db8:85a3:0000:0000:8a2e:0370:7334
压缩形式：2001:db8:85a3::8a2e:370:7334
回环：    ::1   （等价 127.0.0.1）
未指定：  ::    （等价 0.0.0.0）
```

压缩规则：
1. 每组前导 0 可省略（至少保留 1 位）
2. 连续全 0 组用 `::` 替代（**只能出现一次**）

## 3. IPv6 地址类型

| 类型 | 前缀 | 用途 |
| --- | --- | --- |
| 全球单播 | 2000::/3 | 公网 |
| 链路本地 | fe80::/10 | 同链路通信（自动生成） |
| 唯一本地 | fc00::/7 | 内网（替代 IPv4 私网） |
| 组播 | ff00::/8 | 一对多 |
| 任播 | 任意单播 | 一对最近 |

> IPv6 **没有广播**，用组播替代。

## 4. IPv6 报文头

```
+-------+---------+-------------+---------------+
| Ver=6 |  Traffic Class |    Flow Label   |
+-------+---------+-------------+---------------+
|  Payload Length    | Next Header | Hop Limit |
+-------------------+--------------+-----------+
|              Source Address (128 bit)        |
+----------------------------------------------+
|            Destination Address (128 bit)     |
+----------------------------------------------+
```

对比 IPv4 头：
- 字段数 12 → 8
- 长度 20~60B → **固定 40B**
- 无校验和（链路层 / 传输层已校验）
- 无分片字段（改为路径 MTU 发现）

## 5. 邻居发现协议 NDP

替代 IPv4 的 ARP，基于 ICMPv6：

| 报文 | 替代 | 作用 |
| --- | --- | --- |
| RS (Router Solicitation) | — | 主机请求路由器 |
| RA (Router Advertisement) | — | 路由器通告前缀 |
| NS (Neighbor Solicitation) | ARP Request | 询问邻居 MAC |
| NA (Neighbor Advertisement) | ARP Reply | 回应 MAC |
| Redirect | ICMP Redirect | 路由优化 |

## 6. SLAAC 无状态自动配置

```
1. 主机生成链路本地地址：fe80:: + EUI-64（MAC 转换）
2. 发送 RS，请求前缀
3. 路由器 RA 回送前缀 + 生存期
4. 主机拼出：前缀 + 接口ID
5. DAD（重复地址检测）无冲突后启用
```

无需 DHCP 即可上网。

## 7. IPv4 ↔ IPv6 过渡技术

| 技术 | 说明 |
| --- | --- |
| 双栈 | 设备同时跑 IPv4/IPv6（推荐） |
| 隧道 | 6in4、6to4、Teredo，将 IPv6 包封装在 IPv4 中 |
| NAT64/DNS64 | 纯 IPv6 客户端访问 IPv4 服务器 |
| 464XLAT | 运营商级翻译方案 |

## 8. 实战命令

```bash
# Linux
ip -6 addr show
ip -6 route
ping6 2001:4860:4860::8888    # Google DNS IPv6

# 查看 NDP 表（替代 ARP）
ip -6 neigh show

# 禁用 IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
```

## 9. 常见面试题

1. **IPv6 地址位数与表示？** 128 bit，冒号十六进制。
2. **IPv6 没有广播用什么？** 组播（multicast）。
3. **链路本地地址前缀？** fe80::/10。
4. **IPv6 报文头固定多少字节？** 40 字节。
5. **EUI-64 怎么生成？** MAC 中间插入 ff:fe，置 U/L 位（取反第 7 位）。
6. **IPv4/IPv6 双栈可以同时用吗？** 是，按 DNS 解析结果优先选择。

## 10. 一图速记

```
128 bit = 充足地址
无广播 = 全部用组播
NDP  = 替代 ARP
SLAAC = 免 DHCP
双栈 = 平滑过渡
```


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
