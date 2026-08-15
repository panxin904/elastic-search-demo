---
layout: home
title: 计算机网络知识库
hero:
  name: 计算机网络
  text: 知识图谱 · 学习路径 · 实战案例
  tagline: 系统掌握 TCP/IP / HTTP / 网络安全 / 云网络，构建完整网络工程师能力栈
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /graph
    - theme: alt
      text: 思维导图
      link: /mindmap
    - theme: alt
      text: 速记卡
      link: /cheatsheet
features:
  - icon: 🧠
    title: 知识图谱
    details: 50+ 核心概念关系图，全局理解网络技术栈
    link: /graph
    linkText: 查看图谱
  - icon: 🗺️
    title: 学习路径
    details: 从 OSI 七层到云网络，按图索骥系统学习
    link: /path
    linkText: 开始学习
  - icon: 🧭
    title: 思维导图
    details: 11 大模块结构化梳理，定位薄弱点
    link: /mindmap
    linkText: 展开导图
  - icon: ⚡
    title: 速记卡
    details: 协议对比、面试题、案例精讲
    link: /cheatsheet
    linkText: 速记
  - icon: 🛠️
    title: 工具实战
    details: Wireshark、tcpdump、curl、抓包排查、性能测试
    link: /10-tools/wireshark
    linkText: 工具篇
  - icon: 🔒
    title: 网络安全
    details: 加密、TLS、PKI、攻击防御、零信任
    link: /07-security/encryption
    linkText: 安全篇
  - icon: ☁️
    title: 云网络
    details: VPC、负载均衡、SDN、Service Mesh
    link: /09-cloud-network/vpc
    linkText: 云网络
  - icon: 📡
    title: 无线网络
    details: WiFi 6/7、5G、蓝牙、IoT
    link: /08-wireless/wifi
    linkText: 无线篇
---

<ClientOnly>
  <WhyThisGraph
    :pain-points="[
      "TCP/IP 协议栈（IP / TCP / UDP / HTTP）讲不清？",
      "三次握手 / 四次挥手 / TIME_WAIT 太多怎么排查？",
      "HTTPS / TLS 1.3 / HTTP/2 / HTTP/3 关系？",
      "DNS 解析过程、CDN 调度、负载均衡策略？",
      "网络排查工具（tcpdump / wireshark / ss / netstat）不会用？"
    ]"
    :goals="[
      "理论体系（OSI 7 层 / TCP/IP 4 层 / 协议族）",
      "HTTP 全家桶（HTTP/1.1 / HTTP/2 / HTTP/3 / HTTPS）",
      "TCP 深度（握手 / 挥手 / 重传 / 拥塞控制）",
      "DNS / CDN / 负载均衡",
      "网络安全（TLS / WAF / ACL）",
      "排查工具（tcpdump / wireshark / ss / iperf）"
    ]"
    :related-sites="[
      { site: "linux", path: "/13-net/iptables", label: "iptables 防火墙" },
      { site: "security", path: "/02-network/tls", label: "TLS 协议" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "CAP 定理" },
      { site: "devops", path: "/01-pipeline/overview", label: "CI/CD 流水线" },
      { site: "observability", path: "/05-sre/network-debug", label: "网络排查" }
    ]"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


## 关于本站

**计算机网络** 知识库面向后端工程师、SRE、网络工程师、面试候选人，提供**理论 + 实战**的完整知识体系。

### 模块结构

| 章节 | 内容 | 关键文档 |
| --- | --- | --- |
| [网络基础](/01-basics/osi) | OSI / TCP/IP / 封装 | OSI 七层、TCP/IP 四层 |
| [物理层](/02-physical/signal) | 信号、介质、复用 | 信号编码、传输介质 |
| [数据链路层](/03-data-link/mac) | MAC、交换、VLAN、STP | 以太网、VLAN、STP |
| [网络层](/04-network/ip-address) | IP、子网、路由、NAT | IPv4/IPv6、OSPF/BGP |
| [传输层](/05-transport/udp) | UDP、TCP 三大表 | 三次握手、四次挥手 |
| [应用层](/06-application/http) | HTTP/HTTPS/DNS/CDN | HTTP/2/3、WebSocket |
| [网络安全](/07-security/encryption) | 加密、PKI、TLS、攻击 | 对称/非对称、签名 |
| [无线网络](/08-wireless/wifi) | WiFi、5G、蓝牙、IoT | WiFi 6/7、5G、LoRa |
| [云网络](/09-cloud-network/vpc) | VPC、LB、SDN、Mesh | Transit Gateway、Istio |
| [工具实战](/10-tools/wireshark) | 抓包、性能、监控 | Wireshark、tcpdump |
| [企业案例](/11-cases/cdn-case) | CDN、微服务、跨域 | 全球加速、多活 |
| [面试/实战](/12-interview-practice/questions) | 高频题、案例、对比 | 48 道高频题 |

### 学习建议

- **入门** → [网络基础](/01-basics/osi) → [物理层](/02-physical/signal) → [数据链路层](/03-data-link/mac) → [网络层](/04-network/ip-address) → [传输层](/05-transport/udp) → [应用层](/06-application/http)
- **后端 / SRE** → [传输层 TCP](/05-transport/tcp-handshake) → [HTTP/HTTPS](/06-application/https) → [性能测试](/10-tools/performance-test) → [故障排查](/10-tools/troubleshooting)
- **安全** → [加密基础](/07-security/encryption) → [PKI/TLS](/07-security/pki-tls) → [网络攻击](/07-security/network-attack) → [防火墙/VPN](/07-security/firewall-vpn)
- **面试** → [高频题](/12-interview-practice/questions) → [案例题](/12-interview-practice/cases) → [协议对比](/12-interview-practice/comparison)
