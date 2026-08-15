---
title: 协议对比
---

# 协议对比

<div class="nt-badge nt-badge-interview">面试</div>
<div class="nt-badge nt-badge-basics">速记</div>

本章汇总常见协议的对比表，方便速记。

## 1. TCP vs UDP

| 维度 | TCP | UDP |
| --- | --- | --- |
| 连接 | 三次握手 | 无 |
| 可靠性 | ACK + 重传 | 无 |
| 顺序 | 保证 | 不保证 |
| 流量控制 | 滑动窗口 | 无 |
| 拥塞控制 | CUBIC / BBR | 无 |
| 头部 | 20~60B | 8B |
| 速度 | 慢 | 快 |
| 适用 | 可靠传输 | 实时 / 简单 |

## 2. HTTP/1.0 vs 1.1 vs 2.0 vs 3.0

| 维度 | 1.0 | 1.1 | 2.0 | 3.0 |
| --- | --- | --- | --- | --- |
| 连接 | 短 | 长 | 多路复用 | 多路复用 |
| 头部 | 文本 | 文本 | HPACK | QPACK |
| 队头阻塞 | 严重 | 严重 | TCP 层 | 无 |
| RTT | 多次 | 1-2 | 1-2 | 0-1 |
| 二进制 | ✗ | ✗ | ✓ | ✓ |
| 推送 | ✗ | ✗ | ✓（弃用） | ✗ |
| 传输 | TCP | TCP | TCP | QUIC |

## 3. IPv4 vs IPv6

| 维度 | IPv4 | IPv6 |
| --- | --- | --- |
| 位数 | 32 | 128 |
| 表示 | 点分十进制 | 冒号十六进制 |
| 头部 | 20~60B | 固定 40B |
| 分片 | 路由可分片 | 端到端 |
| 广播 | 有 | 无（用组播） |
| 配置 | 手动 / DHCP | SLAAC |
| 安全 | 需 IPsec | 原生支持 |
| 地址数 | 42 亿 | 3.4×10^38 |

## 4. TLS 1.2 vs 1.3

| 维度 | 1.2 | 1.3 |
| --- | --- | --- |
| 握手 RTT | 2 | 1 |
| 0-RTT | ✗ | ✓ |
| 套件 | 多 | 仅 AEAD |
| PFS | 可选 | 强制 |
| 重协商 | 有 | 无 |
| 可见算法 | 多 | 默认安全 |

## 5. RSA vs ECC vs EdDSA

| 维度 | RSA | ECC | EdDSA |
| --- | --- | --- | --- |
| 安全 | 2048+ | 256 | 256 |
| 签名长度 | 256B | 64B | 64B |
| 验证速度 | 中 | 快 | 极快 |
| 密钥长度 | 大 | 小 | 小 |
| 成熟度 | 极高 | 高 | 中 |
| 推荐 | ✓ | ✓ | **新选** |

## 6. 对称加密算法

| 算法 | 密钥 | 块 | 状态 |
| --- | --- | --- | --- |
| DES | 56 | 64 | 弃 |
| 3DES | 168 | 64 | 弃 |
| AES | 128/256 | 128 | **主流** |
| ChaCha20 | 256 | 流 | 移动 |
| SM4 | 128 | 128 | 国密 |

## 7. AES 模式

| 模式 | 认证 | 并行 | 用途 |
| --- | --- | --- | --- |
| ECB | ✗ | ✓ | 不推荐 |
| CBC | ✗ | ✗ | 旧 |
| CTR | ✗ | ✓ | 磁盘 |
| GCM | ✓ | ✓ | **TLS** |
| CCM | ✓ | ✗ | 嵌入式 |

## 8. 哈希算法

| 算法 | 输出 | 状态 |
| --- | --- | --- |
| MD5 | 128 | 破 |
| SHA-1 | 160 | 破 |
| SHA-256 | 256 | **主流** |
| SHA-3 | 256 | NIST |
| SM3 | 256 | 国密 |
| BLAKE2 | 256/512 | 高速 |

## 9. L4 vs L7 负载均衡

| 维度 | L4 | L7 |
| --- | --- | --- |
| 工作层 | TCP/UDP | HTTP |
| 性能 | 极高 | 中 |
| 路由 | IP/Port | URL/Header |
| TLS 终止 | 否 | 是 |
| 缓存 | 无 | 有 |

## 10. 协议端口

| 协议 | 端口 |
| --- | --- |
| HTTP | 80 |
| HTTPS | 443 |
| DNS | 53 |
| SSH | 22 |
| FTP | 21 / 20 |
| SMTP | 25 |
| POP3 | 110 |
| IMAP | 143 |
| MySQL | 3306 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| MongoDB | 27017 |
| Kafka | 9092 |
| ZooKeeper | 2181 |
| gRPC | 443（HTTPS） |

## 11. 网络设备层级

| 层级 | 设备 |
| --- | --- |
| 接入 | 接入交换机 |
| 汇聚 | 汇聚交换机 |
| 核心 | 核心交换机 |
| 出口 | 路由器 + 防火墙 |
| 边界 | 边界路由器 |

## 12. 公有云对比

| 服务 | AWS | 阿里云 | 腾讯云 | Azure | GCP |
| --- | --- | --- | --- | --- | --- |
| 计算 | EC2 | ECS | CVM | VM | GCE |
| 网络 | VPC | VPC | VPC | VNet | VPC |
| LB | ALB/NLB | SLB | CLB | LB | GLB |
| DNS | Route 53 | 云解析 | DNSPod | DNS | Cloud DNS |
| CDN | CloudFront | CDN | CDN | Front Door | Cloud CDN |
| 专线 | Direct Connect | 高速通道 | 专线 | ExpressRoute | Dedicated Interconnect |

## 13. 消息协议

| 协议 | 传输 | 特点 |
| --- | --- | --- |
| MQTT | TCP | IoT 事实标准 |
| AMQP | TCP | 企业 |
| Kafka | TCP | 高吞吐 |
| CoAP | UDP | 受限设备 |
| STOMP | TCP | 简单 |

## 14. 序列化

| 格式 | 大小 | 速度 | 可读 | 跨语言 |
| --- | --- | --- | --- | --- |
| JSON | 大 | 慢 | 好 | ✓ |
| XML | 大 | 慢 | 好 | ✓ |
| Protobuf | 小 | 快 | ✗ | ✓ |
| Thrift | 小 | 快 | ✗ | ✓ |
| Avro | 小 | 快 | ✗ | ✓ |
| MessagePack | 小 | 快 | ✗ | ✓ |
| CBOR | 小 | 快 | ✗ | ✓ |

## 15. 数据库协议

| 类型 | 协议 |
| --- | --- |
| MySQL | MySQL Protocol（TCP） |
| PostgreSQL | PostgreSQL（TCP） |
| MongoDB | Wire Protocol（TCP） |
| Redis | RESP（TCP） |
| Cassandra | CQL（TCP） |
| Elasticsearch | HTTP / REST |

## 16. 网络安全协议

| 用途 | 协议 |
| --- | --- |
| 远程登录 | SSH |
| 文件传输 | SFTP / SCP |
| 邮件加密 | S/MIME / PGP |
| 虚拟专网 | IPsec / WireGuard / OpenVPN |
| 应用层 | TLS / HTTPS |
| 认证 | Kerberos / OAuth2 / SAML |
| 加密邮件 | STARTTLS |

## 17. 容器 / K8s 网络

| 概念 | 描述 |
| --- | --- |
| CNI | 容器网络接口 |
| Flannel | Overlay（VXLAN） |
| Calico | BGP / IPIP |
| Cilium | eBPF |
| Multus | 多网卡 |
| Service Mesh | Istio / Linkerd |

## 18. 速记口诀

| 主题 | 口诀 |
| --- | --- |
| OSI 七层 | 物数网传会表应 |
| TCP 标志 | URG/ACK/PSH/RST/SYN/FIN |
| TCP 三次 | SYN → SYN+ACK → ACK |
| TCP 四次 | FIN → ACK → FIN → ACK |
| HTTP 状态 | 1 信息 2 成功 3 重定向 4 客户端 5 服务端 |
| TLS 算法 | ECDHE + AES-GCM + SHA-256 |
