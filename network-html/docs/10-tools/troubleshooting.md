---
title: 故障排查方法
---

# 故障排查方法

<div class="nt-badge nt-badge-tools">故障排查</div>
<div class="nt-badge nt-badge-cases">实战</div>

网络故障排查需要**分层**思维（OSI 各层）+ **系统化**思路（先易后难，先外后内）。本章给出常用排查方法与命令清单。

## 1. 排查方法论

### 1.1 OSI 分层

```
L7 应用层    curl、HTTP
L6 表示层    加密 / 解密
L5 会话层    TLS 握手
L4 传输层    TCP / UDP
L3 网络层    IP / ICMP / 路由
L2 数据链路   ARP / VLAN
L1 物理层    网线 / 光模块
```

**原则**：从下往上排查。L1 通了再考虑 L2...L7。

### 1.2 双向验证

- 客户端 → 服务端
- 服务端 → 客户端
- 中间路径

### 1.3 缩小范围

- 是否影响所有用户 / 部分 / 单个？
- 是否所有接口 / 单个？
- 是否所有协议 / 单个？

## 2. 工具清单

| 工具 | 层级 | 用途 |
| --- | --- | --- |
| ping | L3 | 连通性 |
| traceroute | L3 | 路径 |
| mtr | L3 | 路径 + 统计 |
| ip / ifconfig | L2/L3 | 接口 / 地址 |
| ss / netstat | L4 | 连接 |
| tcpdump / Wireshark | L2-L7 | 抓包 |
| curl | L7 | HTTP |
| nslookup / dig | L7 | DNS |
| iperf3 | L4 | 带宽 |
| ethtool | L1/L2 | 网卡 |
| arp | L2 | ARP 表 |
| strace | L7 | 系统调用 |

## 3. 排查流程模板

### 3.1 远程服务不通

```
1. 本地 ping 自身网卡 IP           → 检查 L1
2. ping 网关                      → 检查同子网
3. ping 远端公网 IP（如 8.8.8.8）   → 检查出口
4. ping 域名                      → 检查 DNS
5. telnet / nc 远端端口             → 检查 L4
6. curl 远端 URL                   → 检查 L7
7. traceroute                      → 路径问题
8. mtr                             → 哪跳丢包
9. 抓包                           → 应用层分析
```

### 3.2 服务慢

```
1. curl -w 看各段时间
2. 看服务端响应是否慢（直接打到后端）
3. mtr 看路径丢包 / 时延
4. ss -ti 看连接状态 / 重传
5. 抓包看 TCP 行为
6. 排查拥塞控制 / 缓冲区
```

### 3.3 间歇性断连

```
1. mtr 长期观察（1 小时）
2. 看是否与时间相关（定时任务）
3. 看是否与流量相关（带宽耗尽）
4. 看是否与硬件相关（光模块、网线）
5. 抓长期 pcap
```

## 4. 常见故障案例

### 案例 1：网站打不开

```
1. ping example.com
   - 失败：DNS 问题
2. ping IP
   - 失败：网络问题
3. nc 80
   - 失败：服务未起 / 防火墙
4. curl -v
   - 看 SSL / HTTP 错误
```

### 案例 2：TCP 连接慢

```
1. mtr 路径
2. ss -ti dst（看 SYN_SENT）
3. 抓包看 SYN 是否丢
4. 看防火墙 / iptables 是否拦截
5. 内核参数 net.ipv4.tcp_syn_retries
```

### 案例 3：带宽异常

```
1. iftop / nethogs 看哪个进程在用
2. iperf3 测试真实带宽
3. ss -s 看连接状态分布
4. ifconfig 看网卡 errors / dropped
5. ethtool -S 看硬件统计
```

### 案例 4：DNS 解析慢

```
1. dig +trace example.com
2. dig @8.8.8.8 与本地对比
3. 看 /etc/resolv.conf
4. 看 systemd-resolved
5. 看是否启用 DNSSEC
```

### 案例 5：HTTP 502

```
1. ALB / Nginx 日志
2. 后端是否在
3. 健康检查是否通过
4. 后端响应时间
5. keep-alive 是否被断开
```

## 5. 性能瓶颈定位

### 5.1 P99 延迟

```bash
# 用 brendan gregg USE 方法
utilization - 资源使用率
saturation   - 队列长度
errors       - 错误率
```

### 5.2 软中断

```bash
# 看 CPU 软中断分布
mpstat -P ALL 1
# 软中断集中在一核 → 改 RPS / RFS
```

### 5.3 缓存命中率

```bash
# CPU 缓存
perf stat -e cache-misses,cache-references
# DNS 缓存
nscd -g
# 路由缓存
ip route show cache
```

## 6. 内核参数排查

```bash
# 连接状态
ss -s

# SYN 队列
ss -lnt 'sport = :80' | head

# 重传
netstat -s | grep -i retrans

# 丢包
ip -s link show eth0
```

## 7. 网络接口错误

```bash
ifconfig eth0 | grep -E "errors|dropped|overruns"
ethtool -S eth0 | grep err
```

| 字段 | 含义 |
| --- | --- |
| errors | 接收错误 |
| dropped | 丢包 |
| overruns | 接收 FIFO 溢出 |
| frame | 帧错误 |
| carrier | 载波错误 |

## 8. 时间同步问题

```bash
# 检查 NTP
chronyc sources
ntpq -p
# 偏差
ntpdate -q ntp.server
```

NTP 偏差 > 500ms 时 TLS 证书校验可能失败。

## 9. 应急 SOP

```
1. 影响范围评估
2. 启动应急群
3. 回滚最近变更
4. 切换流量（DNS / LB）
5. 抓现场数据
6. 止血
7. 复盘
```

## 10. 常见面试题

1. **ping 不通但服务能访问？** 可能 ICMP 被禁。
2. **TCP 连接慢怎么查？** mtr + ss + 抓包。
3. **502 排查？** LB 与后端连接 + 后端健康 + keep-alive。
4. **大量 TIME_WAIT 怎么办？** tcp_tw_reuse + 端口范围 + 减少短连接。
5. **丢包怎么定位？** mtr 看哪跳 + ethtool 看硬件 + 流量监控。
6. **网络排查的层次？** 自下而上（OSI）。


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
