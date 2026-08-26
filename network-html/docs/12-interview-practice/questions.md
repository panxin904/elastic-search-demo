---
title: 高频面试题
---

# 高频面试题

<div class="nt-badge nt-badge-interview">面试</div>
<div class="nt-badge nt-badge-basics">高频</div>

本章汇总计算机网络方向的高频面试题，按主题分类。

## 1. 网络分层

### Q1: OSI 七层模型与 TCP/IP 四层模型？

| OSI 七层 | TCP/IP 四层 |
| --- | --- |
| 应用层 | 应用层 |
| 表示层 | 应用层 |
| 会话层 | 应用层 |
| 传输层 | 传输层 |
| 网络层 | 网络层（Internet） |
| 数据链路层 | 链路层（Network Access） |
| 物理层 | 链路层 |

### Q2: 各层代表协议？

| 层 | 协议 |
| --- | --- |
| 应用 | HTTP / DNS / FTP / SMTP / SSH |
| 传输 | TCP / UDP |
| 网络 | IP / ICMP / ARP / OSPF / BGP |
| 链路 | Ethernet / PPP / VLAN / STP |

## 2. IP / 子网

### Q3: IPv4 地址分类？

A/B/C/D/E，看首字节。

### Q4: 私有 IP 段？

10.0.0.0/8、172.16.0.0/12、192.168.0.0/16

### Q5: 192.168.1.1/24 主机数？

254 台（2^8 - 2）

### Q6: 子网掩码作用？

区分网络位与主机位。

### Q7: CIDR 与 VLSM？

CIDR 是聚合，VLSM 是子网细分。本质都是子网划分。

## 3. TCP / UDP

### Q8: TCP 三次握手？

SYN → SYN+ACK → ACK

### Q9: 为什么三次？

防服务端单方面分配资源导致半开连接浪费。

### Q10: 四次挥手？

FIN → ACK → FIN → ACK + 2MSL

### Q11: TIME_WAIT 作用？

可靠关闭 + 防旧报文干扰。

### Q12: TCP 可靠传输？

序列号 + ACK + 超时重传 + 校验和。

### Q13: 滑动窗口？

接收方告知窗口，发送方按窗口发，ACK 后右移。

### Q14: 拥塞控制算法？

慢启动 → 拥塞避免 → 快速重传 → 快速恢复。

### Q15: CUBIC vs BBR？

CUBIC 基于丢包，BBR 基于带宽 × RTT。

### Q16: UDP vs TCP？

UDP 无连接、不可靠、快；TCP 相反。

## 4. HTTP

### Q17: HTTP 与 HTTPS 区别？

HTTPS = HTTP + TLS。

### Q18: 常见状态码？

200/201/204/301/302/304/400/401/403/404/500/502/503。

### Q19: HTTP 1.0 vs 1.1 vs 2.0 vs 3.0？

| 版本 | 特点 |
| --- | --- |
| 1.0 | 短连接 |
| 1.1 | 长连接 + 管线化 + chunk |
| 2.0 | 二进制 + 多路复用 + HPACK |
| 3.0 | QUIC + 0-RTT + 解决队头阻塞 |

### Q20: GET vs POST？

GET 参数在 URL，幂等；POST 在 body，可修改。

### Q21: 队头阻塞？

HTTP/1.1 同一连接上一个响应延迟阻塞后续。

## 5. HTTPS

### Q22: TLS 握手流程？

参考 `06-application/https.md`。

### Q23: 对称 vs 非对称加密？

对称同密钥快；非对称公私钥慢但安全分发。HTTPS 用混合。

### Q24: 数字签名原理？

私钥加密 hash，公钥解密对比。

### Q25: CA 干什么？

第三方签发证书，建立信任链。

### Q26: 证书链？

Root CA → Intermediate → Server，客户端验证根 CA。

### Q27: TLS 1.3 优势？

1-RTT 握手、强制 PFS、移除不安全算法。

## 6. DNS

### Q28: DNS 端口？

53（UDP/TCP）。

### Q29: 递归 vs 迭代？

递归：客户端问一次；迭代：客户端多次问。

### Q30: DNS 缓存多久？

由 TTL 决定。

### Q31: CNAME 与 A 区别？

CNAME 是别名（再查一次），A 直接给 IP。

## 7. 安全

### Q32: XSS 怎么防？

输出编码 + CSP + HttpOnly。

### Q33: CSRF 怎么防？

SameSite + Token + Referer。

### Q34: SQL 注入怎么防？

参数化查询。

### Q35: DDoS 怎么防？

流量清洗 + Anycast + 限速 + 验证码。

### Q36: 中间人攻击怎么防？

CA 证书 + HSTS + DoH/DoT。

## 8. 工具

### Q37: Wireshark 怎么抓 HTTPS 明文？

导出 SSLKEYLOGFILE，Wireshark 加载。

### Q38: ping 不通但服务能访问？

ICMP 被禁。

### Q39: TCP 慢怎么排查？

mtr + ss + 抓包 + 内核参数。

### Q40: 怎么定位丢包？

mtr 看哪跳 + ethtool 硬件 + 流量监控。

## 9. 进阶

### Q41: TCP 连接数上限？

文件描述符 + 内存（每个连接 ~ 几 KB）。

### Q42: 长连接 vs 短连接？

长连接省握手、占资源；短连接相反。

### Q43: CDN 怎么工作？

智能 DNS + 边缘节点 + 回源。

### Q44: CDN 命中怎么看？

X-Cache 头 / CloudFront 监控。

### Q45: Service Mesh 价值？

业务无感升级，零信任 + 流量管理 + 可观测。

## 10. 行为面试

### Q46: 一次网络故障如何排查？

1. 影响范围
2. 自下而上
3. 缩小范围
4. 抓包
5. 应急
6. 复盘

### Q47: HTTPS 改造过程？

1. 选证书
2. 配置 TLS
3. 性能优化
4. 全站改造
5. 监控
6. 文档

### Q48: 跨地域架构怎么设计？

1. 业务评估
2. 选方案（专线 / SD-WAN）
3. 数据同步
4. 流量调度
5. 多活设计
6. 演练


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
