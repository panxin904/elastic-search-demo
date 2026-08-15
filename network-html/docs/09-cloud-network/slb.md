---
title: 负载均衡 SLB
---

# 负载均衡 SLB

<div class="nt-badge nt-badge-cloud">云网络</div>
<div class="nt-badge nt-badge-network">核心</div>

负载均衡（Server Load Balancer）将流量**均匀**分配到后端多台服务器，提升可用性与扩展性，是云上入口流量的关键组件。

## 1. 负载均衡分类

| 维度 | 类别 |
| --- | --- |
| 层级 | L4（传输层）/ L7（应用层） |
| 形态 | 硬件（F5）/ 软件（Nginx）/ 云服务（ALB） |
| 流量方向 | 入向 / 出向 |
| 算法 | 轮询 / 加权 / 最小连接 / 一致性哈希 |
| 协议 | TCP / UDP / HTTP / HTTPS / gRPC / QUIC |

## 2. L4 vs L7 负载均衡

| 维度 | L4 | L7 |
| --- | --- | --- |
| 工作层 | TCP/UDP | HTTP/HTTPS |
| 解析 | 4 元组 | URL / Header / Cookie |
| 性能 | 极高 | 中 |
| 路由粒度 | 端口 | 路径 / 主机 / Header |
| 终止 | 不终止 | 可终止 TLS |
| 缓存 | 无 | 可缓存 |
| 改造 | 透明 | 需 X-Forwarded-For |

## 3. 主流负载均衡器

| 类别 | 产品 |
| --- | --- |
| 硬件 | F5 BIG-IP、Citrix ADC |
| 软件 L4 | LVS、HAProxy（TCP 模式） |
| 软件 L7 | Nginx、HAProxy、Envoy、Traefik |
| 云厂商 | AWS ALB/NLB、阿里云 SLB、Azure LB、腾讯云 CLB |
| 服务网格 | Istio、Linkerd（Envoy） |
| API Gateway | Kong、APISIX、AWS API Gateway |

## 4. 负载均衡算法

| 算法 | 描述 | 适用 |
| --- | --- | --- |
| 轮询（Round Robin） | 顺序分配 | 后端等价 |
| 加权轮询 | 按权重 | 后端性能不同 |
| 最少连接 | 选连接数最少 | 长连接 |
| 加权最少连接 | 加权 + 少连接 | 后端异构 |
| 源 IP 哈希 | 同 IP 走同节点 | 会话保持 |
| URL 哈希 | 同 URL 走同节点 | 缓存亲和 |
| 一致性哈希 | 哈希环 | 分布式缓存 |
| P2C（Power of Two Choices） | 随机选 2 取优 | 长连接 |

## 5. 健康检查

| 类型 | 方式 |
| --- | --- |
| TCP 探活 | 三次握手 |
| HTTP GET | 检查 200/状态 |
| HTTPS | 同 HTTP |
| 自定义脚本 | 复杂检查 |

```nginx
# Nginx upstream
upstream backend {
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;

    health_check interval=5s uri=/health timeout=3s;
    keepalive 32;
}
```

## 6. 会话保持

| 方式 | 描述 |
| --- | --- |
| 源 IP | 简单，可能不均 |
| Cookie | 注入 cookie 路由 |
| Header | 按请求 header |

## 7. 高可用

- 多 AZ 部署
- 跨 AZ 备份
- DNS 轮询
- Anycast 入口
- 主备 / 多主

```
                   ┌─ ALB-1（AZ1）
Internet ──DNS─>  │
                   └─ ALB-2（AZ2）
                          │
                ┌─────────┴─────────┐
                │                   │
        Web-AZ1-1..N          Web-AZ2-1..N
```

## 8. TLS 终止

```
Client ──HTTPS──> ALB ──HTTP──> Backend
                  ↑
             TLS 终结
```

- ALB 配证书
- 后端用 HTTP（内网）
- 节省后端 CPU
- ALB 集中管理证书

## 9. 高级特性

| 特性 | 描述 |
| --- | --- |
| 自动扩缩 | 后端自动注册/注销 |
| 跨区域 | 全局负载均衡 |
| 灰度 | 按权重/规则分流 |
| WebSocket | 升级支持 |
| HTTP/2 / HTTP/3 | 多路复用 |
| 限流 | 防刷 |
| WAF 集成 | 防护 |
| 链路追踪 | 注入 X-Request-ID |

## 10. Envoy 进阶

现代服务网格数据面：

```yaml
static_resources:
  listeners:
  - name: listener_0
    address: { socket_address: { address: 0.0.0.0, port_value: 80 } }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        config:
          route_config:
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: backend }
          http_filters:
          - name: envoy.filters.http.router
  clusters:
  - name: backend
    type: EDS
    eds_cluster_config:
      service_name: backend
    health_checks:
    - timeout: 1s
      interval: 5s
      http: { path: /health }
```

## 11. 常见问题

| 问题 | 原因 |
| --- | --- |
| 502 Bad Gateway | 后端全挂 |
| 503 Service Unavailable | 容量超限 |
| 504 Gateway Timeout | 后端响应慢 |
| 负载不均 | 算法不当 / 长连接 |
| 健康检查误判 | 检查路径配置错误 |

## 12. 常见面试题

1. **L4 vs L7 区别？** 工作层、性能、路由粒度。
2. **负载均衡算法？** 轮询、加权、最少连接、哈希。
3. **健康检查作用？** 摘除异常节点。
4. **会话保持方式？** 源 IP、Cookie、Header。
5. **TLS 终止好处？** 后端简化为 HTTP，集中证书管理。
6. **ALB vs NLB？** L7 vs L4，ALB 路由细，NLB 性能高。
