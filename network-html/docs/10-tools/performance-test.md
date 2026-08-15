---
title: 网络性能测试
---

# 网络性能测试

<div class="nt-badge nt-badge-tools">性能</div>
<div class="nt-badge nt-badge-cases">实战</div>

网络性能测试包括**带宽、时延、抖动、丢包、并发**等维度。本章梳理主流工具与调优思路。

## 1. 性能指标

| 指标 | 含义 | 单位 |
| --- | --- | --- |
| 带宽（Bandwidth） | 最大传输速率 | bps / Bps |
| 时延（Latency） | 单向 / 往返时间 | ms |
| RTT | Round-Trip Time | ms |
| 抖动（Jitter） | 时延变化 | ms |
| 丢包率（Loss） | 丢包百分比 | % |
| 并发（Concurrency） | 同时连接数 | — |
| QPS / TPS | 每秒查询 / 事务 | — |
| P99 延迟 | 99% 请求延迟 | ms |

## 2. iperf3 带宽测试

```bash
# 服务端
iperf3 -s

# 客户端
iperf3 -c 192.168.1.1
iperf3 -c 192.168.1.1 -t 30 -P 4   # 4 并发
iperf3 -c 192.168.1.1 -u -b 100M   # UDP
iperf3 -c 192.168.1.1 -R           # 反向
iperf3 -c 192.168.1.1 -p 5201      # 端口
```

输出：
```
[ ID] Interval       Transfer     Bandwidth
[  5] 0.00-10.00 sec  1.10 GBytes  945 Mbits/sec
```

## 3. ping / mtr 时延

```bash
# 简单
ping -c 10 8.8.8.8

# mtr（结合 ping + traceroute）
mtr -r -c 30 8.8.8.8

# 详细
ping -c 100 -i 0.2 -s 1000 8.8.8.8
```

## 4. Web 压测

### 4.1 ab（Apache Bench）

```bash
ab -n 10000 -c 100 https://example.com/
```

### 4.2 wrk

```bash
wrk -c100 -t10 -d30s https://example.com/
wrk -c100 -t10 -d30s -s script.lua https://example.com/
```

### 4.3 hey

```bash
hey -n 10000 -c 100 https://example.com/
hey -n 10000 -c 100 -m POST -d '{"x":1}' https://api.example.com/
```

### 4.4 vegeta

```bash
echo "GET https://example.com/" | vegeta attack -duration=30s -rate=1000 | vegeta report
```

### 4.5 k6

```js
import http from 'k6/http';

export default function () {
  http.get('https://example.com');
}
```

## 5. 抓包辅助

```bash
# 压测时同步抓包
tcpdump -i eth0 -w test.pcap 'tcp port 80'

# 查看重传
tshark -r test.pcap -Y "tcp.analysis.retransmission"
```

## 6. 网络质量测试

| 工具 | 用途 |
| --- | --- |
| speedtest-cli | 带宽 + 时延 |
| netperf | TCP/UDP 吞吐 |
| iperf3 | 带宽 / 抖动 / 丢包 |
| flent | 综合（缓冲膨胀测试） |
| nuttcp | 替代 iperf |
| mtr | 路径诊断 |
| smokeping | 长期监测 |

```bash
# speedtest
pip install speedtest-cli
speedtest-cli

# netperf
netperf -H 192.168.1.1
```

## 7. 指标观察

### 7.1 TCP 重传统计

```bash
ss -ti
# 看 "retrans" 字段

nstat -az
# TcpRetransSegs
```

### 7.2 延迟分解

```
DNS 解析：time_namelookup
TCP 握手：time_connect
TLS 握手：time_appconnect
首字节：time_starttransfer
总耗时：time_total
```

### 7.3 慢请求分析

```bash
# 系统调用
strace -p PID -e trace=network

# 网络栈
ss -p -o state established
```

## 8. 调优清单

| 维度 | 调优 |
| --- | --- |
| TCP 窗口 | `tcp_window_scaling` |
| 缓冲区 | `tcp_rmem` / `tcp_wmem` |
| 拥塞控制 | `tcp_congestion_control = bbr` |
| 队列 | `fq_codel` |
| 并发 fd | `ulimit -n` |
| TIME_WAIT | `tcp_tw_reuse` |
| 中断 | RSS / RPS 软中断分核 |
| 零拷贝 | sendfile / splice |
| 多核 | SO_REUSEPORT |

## 9. 调优案例

### 案例 1：高并发短连接

```bash
# 端口范围
net.ipv4.ip_local_port_range = 10000 65000
# TIME_WAIT 复用
net.ipv4.tcp_tw_reuse = 1
```

### 案例 2：大文件传输

```bash
# 窗口缩放
net.ipv4.tcp_window_scaling = 1
# 缓冲区
net.ipv4.tcp_rmem = 4096 87380 16777216
# sendfile 零拷贝
```

### 案例 3：高带宽长肥网络

```bash
# 增大初始 cwnd
ip route change default via x.x.x.x dev eth0 initcwnd 50
# BBR
net.ipv4.tcp_congestion_control = bbr
```

## 10. 常见面试题

1. **带宽 vs 吞吐？** 带宽是理论上限，吞吐是实际。
2. **时延 vs 抖动？** 时延是绝对值，抖动是变化量。
3. **怎么测最大带宽？** iperf3 TCP 多并发。
4. **wrk 优势？** 多线程 + Lua 脚本扩展。
5. **P99 延迟为何重要？** 比平均值更反映尾部用户体验。
6. **怎么定位网络瓶颈？** mtr 路径 + ss 状态 + iperf 分段。
