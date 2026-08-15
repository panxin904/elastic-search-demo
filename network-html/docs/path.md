---
title: 学习路径
---

# 学习路径

<div class="nt-badge nt-badge-basics">入门</div>
<div class="nt-badge nt-badge-interview">系统化</div>

按图索骥，从入门到精通。本章提供**5 条学习路径**，适配不同角色与目标。

## 1. 全栈网络工程师路径

```
阶段 1：基础（1~2 周）
  ├─ OSI 七层模型
  ├─ TCP/IP 四层模型
  ├─ 数据封装与解封装
  └─ 网络性能指标

阶段 2：物理 + 链路层（1 周）
  ├─ 信号与编码
  ├─ 传输介质
  ├─ MAC 地址
  ├─ 以太网 / 交换机
  ├─ VLAN
  └─ STP / RSTP

阶段 3：网络层（2~3 周）
  ├─ IP 地址 + 子网
  ├─ IPv6
  ├─ ARP
  ├─ ICMP
  ├─ IP 路由
  ├─ OSPF / BGP
  └─ NAT

阶段 4：传输层（2 周）
  ├─ UDP
  ├─ TCP 三次握手
  ├─ TCP 四次挥手
  ├─ TCP 可靠传输
  ├─ 流量控制
  ├─ 拥塞控制
  └─ Socket 编程

阶段 5：应用层（2~3 周）
  ├─ HTTP / 1.0 / 1.1
  ├─ HTTPS / TLS
  ├─ HTTP/2 / HTTP/3
  ├─ DNS
  ├─ CDN
  ├─ WebSocket
  ├─ RESTful
  └─ RPC（gRPC）

阶段 6：网络安全（1~2 周）
  ├─ 加密基础
  ├─ PKI / 数字签名
  ├─ TLS 实战
  ├─ 常见攻击
  ├─ 防火墙 / VPN
  ├─ 无线安全
  └─ SIEM / WAF

阶段 7：无线 + 云网络（1~2 周）
  ├─ WiFi 6/7
  ├─ 5G
  ├─ 蓝牙 / IoT
  ├─ VPC
  ├─ 负载均衡
  ├─ SDN
  └─ Service Mesh

阶段 8：工具与实战（1~2 周）
  ├─ Wireshark
  ├─ tcpdump / curl
  ├─ 性能测试
  ├─ 故障排查
  ├─ 监控
  ├─ CDN 案例
  ├─ 微服务网络
  └─ 跨地域组网
```

## 2. 后端工程师路径

```
重点：传输层 + 应用层 + 工具

第 1 周：
  ├─ TCP 三次握手、四次挥手
  ├─ TCP 可靠传输、流量控制、拥塞控制
  └─ Socket 编程

第 2 周：
  ├─ HTTP / 1.0 / 1.1
  ├─ HTTPS / TLS
  ├─ HTTP/2 / HTTP/3
  └─ WebSocket

第 3 周：
  ├─ DNS
  ├─ CDN
  ├─ RESTful / RPC
  └─ gRPC

第 4 周：
  ├─ Wireshark 抓包
  ├─ tcpdump / curl
  ├─ 性能测试
  └─ 故障排查
```

## 3. SRE / 运维工程师路径

```
重点：网络 + 监控 + 故障排查

第 1 周：
  ├─ IP / 子网 / 路由
  ├─ VLAN / STP
  └─ NAT

第 2 周：
  ├─ TCP 拥塞控制
  ├─ HTTP / HTTPS
  ├─ DNS / CDN
  └─ 负载均衡

第 3 周：
  ├─ VPC / VPN / 专线
  ├─ 跨地域组网
  ├─ Service Mesh
  └─ SD-WAN

第 4 周：
  ├─ 抓包分析
  ├─ 性能调优
  ├─ 故障排查
  └─ 监控告警
```

## 4. 安全工程师路径

```
重点：加密 + 协议 + 攻击防御

第 1 周：
  ├─ 对称 / 非对称加密
  ├─ 哈希 / 数字签名
  └─ PKI / CA

第 2 周：
  ├─ TLS 握手细节
  ├─ 证书链
  ├─ HTTPS 实战
  └─ OCSP Stapling

第 3 周：
  ├─ 常见网络攻击
  ├─ DDoS 防御
  ├─ 中间人攻击
  └─ ARP 欺骗 / DNS 劫持

第 4 周：
  ├─ 防火墙 / WAF
  ├─ VPN / IPsec
  ├─ 无线安全
  └─ SIEM
```

## 5. 面试突击路径

```
2 周突击：

Day 1-2：
  ├─ OSI / TCP/IP
  ├─ IP / 子网
  └─ 常见面试题

Day 3-4：
  ├─ TCP 三次握手、四次挥手
  ├─ 流量控制、拥塞控制
  └─ TIME_WAIT

Day 5-6：
  ├─ HTTP / HTTPS / TLS
  └─ HTTP/2 / HTTP/3

Day 7：
  ├─ DNS / CDN
  └─ 协议对比

Day 8-9：
  ├─ 加密 / 签名
  └─ PKI

Day 10：
  ├─ 抓包工具
  └─ 性能调优

Day 11-12：
  ├─ 案例题
  └─ 综合题

Day 13-14：
  ├─ 模拟面试
  └─ 查漏补缺
```

## 6. 推荐资源

| 资源 | 链接 | 说明 |
| --- | --- | --- |
| 书籍 | 《TCP/IP 详解 卷1》 | 经典 |
| 书籍 | 《计算机网络：自顶向下》 | 入门 |
| 书籍 | 《HTTPS 权威指南》 | 进阶 |
| 课程 | Kurose & Ross 公开课 | 入门 |
| RFC | datatracker.ietf.org | 标准 |
| 实验 | mininet / GNS3 | 实践 |
| 工具 | Wireshark / tcpdump | 抓包 |
| 在线 | ssldecker.com / ssllabs | 测试 |

## 7. 学习方法

| 方法 | 描述 |
| --- | --- |
| 抓包验证 | 每次学完协议都用 Wireshark 看一眼 |
| 写代码 | 写个 echo server、HTTP server |
| 画图 | 流程图、状态机、时序图 |
| 复述 | 教别人听 |
| 总结 | 自己的速记卡 |
