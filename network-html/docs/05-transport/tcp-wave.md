---
title: TCP 四次挥手
---

# TCP 四次挥手

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-interview">必考</div>

TCP 断开连接需要**四次挥手**（Four-Way Wavehand），因 TCP 是**全双工**，需要分别关闭两个方向的连接。

## 1. 挥手流程

```
       Client                          Server
         |                                |
         |  -------- FIN (seq=u) ----->   |  ① 客户端：没数据要发了
         |                                |
         |  <------- ACK (ack=u+1) ------ |  ② 服务端：知道了
         |                                |
         |       （服务端继续发送剩余数据）|
         |                                |
         |  <--- FIN (seq=v, ack=u+1) ----|  ③ 服务端：我也发完了
         |                                |
         |  -------- ACK (ack=v+1) -----> |  ④ 客户端：知道了
         |                                |
         |       （2MSL 等待）             |  →  CLOSED
```

## 2. 状态转换

| 阶段 | Client | Server |
| --- | --- | --- |
| 主动关 | FIN_WAIT_1 | CLOSE_WAIT |
| 收到 ACK | FIN_WAIT_2 | CLOSE_WAIT |
| 收到 FIN | TIME_WAIT | LAST_ACK |
| 发 ACK | TIME_WAIT | LAST_ACK → CLOSED |
| 2MSL 后 | CLOSED | — |

## 3. 为什么是四次而不是三次？

- **第二次**（ACK）只是确认收到了 FIN
- **第三次**（FIN）说明服务端也发完数据了
- 两次中间可能间隔时间较长（服务端还有数据），不能合并
- 但**TCP 延迟确认**或**同时关闭**时，可三次完成

## 4. TIME_WAIT 状态

### 4.1 什么是 TIME_WAIT

- 主动关闭方收到对端 FIN 的 ACK 后进入
- 持续 **2 MSL**（Maximum Segment Lifetime，默认 60s，共 120s）
- Linux 默认 `TIME_WAIT_TIMEOUT = 60s`

### 4.2 为什么要等 2MSL

| 目的 | 原因 |
| --- | --- |
| 可靠关闭 | 最后一个 ACK 丢失，对端会重传 FIN，本端能再次回 ACK |
| 防止旧报文 | 让本次连接的所有报文都从网络中消失，避免下一连接收到残留包 |

### 4.3 大量 TIME_WAIT 的影响

- 占用端口 / 文件描述符
- 高并发短连接服务（如 HTTP）易触达

### 4.4 优化

```bash
# 开启 TIME_WAIT 复用（仅对客户端发起的连接有效）
net.ipv4.tcp_tw_reuse = 1

# 缩短 2MSL（不推荐，可能丢报文）
net.ipv4.tcp_fin_timeout = 30

# 调大端口范围
net.ipv4.ip_local_port_range = 10000 65000
```

> **注意**：`tcp_tw_recycle` 已被 Linux 4.12 移除，会在 NAT 场景下误杀连接。

## 5. CLOSE_WAIT 大量堆积

- **被动关闭方**收到 FIN 后未调用 close()
- 通常是**应用 bug**（忘记释放资源、循环卡住、忘了 close）
- 排查：

```bash
ss -tan | grep CLOSE-WAIT | wc -l
netstat -tan | grep CLOSE-WAIT

# 找到卡死的进程 / 线程
lsof -i tcp
```

## 6. 异常关闭：RST

- **RST** 用于**异常**终止连接，无需 2MSL
- 触发场景：
  - 监听端口不存在
  - 收到不属于本连接的报文
  - 应用调用 `setsockopt(SO_LINGER, 0)`
  - 半连接收到数据

## 7. 同时关闭（Simultaneous Close）

双方都主动关闭时：

```
A ──FIN──> B
B ──FIN──> A
（两端都进入 FIN_WAIT_1）
A <─ACK── B  → A 进入 CLOSING
B <─ACK── A  → B 进入 CLOSING
收到 ACK 后两端 TIME_WAIT
```

## 8. 抓包示例

```
No.   Time     Source     Dest       Protocol  Info
1     0.000    10.0.0.1   10.0.0.2   TCP       49842 → 80 [FIN, ACK] seq=100
2     0.001    10.0.0.2   10.0.0.1   TCP       80 → 49842 [ACK] seq=200 ack=101
3     0.005    10.0.0.2   10.0.0.1   TCP       80 → 49842 [FIN, ACK] seq=200 ack=101
4     0.006    10.0.0.1   10.0.0.2   TCP       49842 → 80 [ACK] seq=101 ack=201
```

## 9. SO_LINGER 选项

| 设置 | 行为 |
| --- | --- |
| `l_onoff=0` | 默认，close 后立即返回，交给 TCP 处理 |
| `l_onoff=1, l_linger=0` | 发送 RST，丢弃未发数据 |
| `l_onoff=1, l_linger=N` | 等待 N 秒，确认对端收到所有数据才返回 |

## 10. 常见面试题

1. **为什么是四次挥手？** TCP 全双工，每个方向需要单独关闭。
2. **TIME_WAIT 作用？** 1) 可靠关闭；2) 防旧报文干扰下一连接。
3. **2MSL 是多久？** 默认 60s × 2 = 120s。
4. **CLOSE_WAIT 太多怎么办？** 检查应用是否忘记 close，修复代码。
5. **服务端大量 TIME_WAIT 正常吗？** 看是不是主动关闭方；正常情况下服务端应该是 CLOSE_WAIT。
6. **FIN 和 RST 区别？** FIN 优雅关闭，RST 异常终止。
