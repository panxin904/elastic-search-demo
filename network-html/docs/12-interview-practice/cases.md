---
title: 案例题
date: 2026-08-15  # date-auto-injected
---

# 案例题

<div class="nt-badge nt-badge-interview">面试</div>
<div class="nt-badge nt-badge-cases">综合</div>

本章汇总网络方向的案例题，给出思路与参考答案。

## 1. 设计题

### Q1: 设计一个支持千万 QPS 的网关

**思路**：

```
1. 多协议入口（HTTP/HTTPS/gRPC）
2. L4/L7 负载均衡（DNS + ALB）
3. 网关集群（多实例、无状态）
4. 限流熔断（Sentinel / Envoy）
5. 鉴权（OAuth2 / mTLS）
6. 灰度（按权重 / Header）
7. 缓存（Redis）
8. 异步（Kafka）
9. 可观测（Prometheus + Jaeger）
10. 容灾（多 AZ + 跨 Region）
```

**关键技术**：
- Envoy / Nginx 多 worker
- epoll / io_uring
- 连接池
- 长连接复用
- 零拷贝

### Q2: 设计一个全球电商的网络架构

```
1. Anycast DNS
2. 跨 Region 多活
3. 用户单元化（按 user_id % N）
4. CDN 全站加速
5. 全球加速（GA）
6. 数据就近读写
7. 异步同步
8. 限流降级
9. 监控告警
10. 灾备演练
```

### Q3: 设计一个视频直播网络

```
1. 推流 SDK → RTMP/HLS/SRT
2. 边缘接入 → 协议转换
3. 媒体处理集群（转码 + 截图）
4. CDN 分发（HLS/DASH）
5. 多码率自适应
6. 录制 + 截图存储
7. 实时监控（卡顿率、首屏）
8. 弱网优化（QUIC）
```

## 2. 故障题

### Q4: 用户反馈网站打不开，怎么排查？

```
1. 自己访问 → 确认问题
2. 询问范围（全部/部分/单用户）
3. 检查 DNS（dig）
4. ping / traceroute 路径
5. nc 端口
6. curl 看 HTTP 错误
7. 抓包分析
8. 服务端日志
9. LB / CDN 状态
10. 应急：切流量 / 回滚
```

### Q5: 服务大量 502，怎么处理？

```
1. 看 LB 日志（哪台后端）
2. 健康检查是否过
3. 后端进程是否在
4. 后端 CPU / 内存 / 网络
5. 数据库 / 下游是否慢
6. 连接池是否打满
7. 应急：摘除问题节点 / 扩缩
8. 复盘：监控 + 告警
```

### Q6: 跨地域数据传输慢

```
1. 测量两端带宽（iperf3）
2. mtr 路径质量
3. 是否加密开销大
4. 是否数据量可压缩
5. 是否能就近存储
6. 走专线 / SD-WAN
7. 数据分片并行
```

### Q7: 视频卡顿严重

```
1. 看卡顿率（首屏、缓冲、播速）
2. 推流端：带宽、丢包、编码
3. CDN 节点：命中率、回源
4. 播放端：网络类型、协议
5. 缓冲策略
6. 优化：QUIC、多码率、就近拉流
```

## 3. 优化题

### Q8: 首屏 3 秒降到 1 秒以内

```
1. CDN 全站加速
2. 关键资源 preload / preconnect
3. HTTP/2 / HTTP/3
4. 图片 WebP / AVIF
5. JS / CSS 压缩
6. 减少阻塞
7. SSR / 边缘渲染
8. 性能监控（Web Vitals）
```

### Q9: 数据库连接数暴涨

```
1. 慢 SQL 导致连接占用
2. 连接池配置
3. 是否有泄漏
4. 是否有大量重试
5. 服务拆分
6. 读写分离
7. 加缓存
```

### Q10: 上传大文件失败

```
1. 客户端分片
2. 断点续传
3. 服务端分片接收
4. 对象存储直传（OSS / S3 预签名）
5. 进度条
6. 后台异步处理
```

## 4. 协议题

### Q11: 让你设计一个 RPC 协议

```
1. 二进制 + Protobuf
2. HTTP/2 多路复用
3. Header：traceID / spanID
4. Body：方法名 + 参数
5. 错误码 + 错误信息
6. 压缩（gzip）
7. 心跳
8. 双向流
9. 加密（mTLS）
```

### Q12: 让你设计一个消息协议

```
1. 长度前缀（避免粘包）
2. Magic Number
3. 协议版本
4. 命令字
5. 序列号
6. 消息体（Protobuf）
7. CRC / 校验
```

## 5. 安全题

### Q13: 让你设计登录系统

```
1. HTTPS 全站
2. 强密码 + 复杂度
3. 密码 hash（bcrypt / Argon2）
4. 限速（防爆破）
5. 验证码（异常时）
6. MFA（重要场景）
7. Session / JWT
8. SameSite Cookie
9. CSRF Token
10. 风控（IP / 设备 / 行为）
```

### Q14: 数据库被脱库

```
1. 立即隔离
2. 评估影响
3. 上报合规
4. 通知用户（按法律）
5. 修复漏洞（注入 / 弱口令）
6. 加固（加密、审计、最小权限）
7. 复盘
```

## 6. 高可用题

### Q15: 机房故障怎么办？

```
1. 摘除机房流量
2. 切换到备份机房
3. DNS 智能解析
4. 数据库切换（主从 / 主主）
5. 异步任务重试
6. 监控报警
7. 故障恢复后回切
```

### Q16: CDN 故障怎么办？

```
1. 多 CDN 备援
2. DNS 切换
3. 客户端降级
4. 源站抗压
5. 监控告警
```

## 7. 编码题

### Q17: 实现 HTTP 服务器

```python
import socket

def handle(c):
    req = c.recv(1024).decode()
    headers, body = req.split('\r\n\r\n', 1)
    lines = headers.split('\r\n')
    method, path, _ = lines[0].split()
    print(f"{method} {path}")
    response = f"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello"
    c.sendall(response.encode())
    c.close()

s = socket.socket()
s.bind(('0.0.0.0', 8080))
s.listen(128)
while True:
    c, _ = s.accept()
    handle(c)
```

### Q18: 实现 TCP Echo Server

```python
import socket, threading

def handle(c):
    while True:
        data = c.recv(1024)
        if not data:
            break
        c.sendall(data)
    c.close()

s = socket.socket()
s.bind(('0.0.0.0', 9999))
s.listen(128)
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,)).start()
```

## 8. 综合题

### Q19: TCP 三次握手时丢包怎么办？

```
1. 客户端发 SYN 丢
   → 超时重传（tcp_syn_retries）
2. 服务端 SYN+ACK 丢
   → 客户端重传 SYN
   → 服务端重传 SYN+ACK
3. 客户端 ACK 丢
   → 服务端超时重传 SYN+ACK
   → 客户端会回 RST
```

### Q20: 浏览器输入 URL 过程？

```
1. URL 解析
2. HSTS 检查
3. DNS 解析
4. TCP 握手
5. TLS 握手
6. HTTP 请求
7. 服务器处理
8. HTTP 响应
9. 浏览器渲染
10. 后续资源（CSS/JS/IMG）
```

## 9. 经验题

### Q21: HTTPS 改造经验

```
1. 选证书（DV/OV/EV）
2. 配 TLS（协议、套件）
3. 全站 301 跳转
4. 性能优化（TLS 1.3、Session Resumption、OCSP Stapling）
5. 监控（握手时间、错误率）
6. 自动化（Let's Encrypt）
```

### Q22: 双 11 大促网络保障

```
1. 容量评估（压测）
2. CDN 全站加速
3. 多机房多活
4. 限流熔断
5. 监控告警
6. 应急预案
7. 值班
```


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
