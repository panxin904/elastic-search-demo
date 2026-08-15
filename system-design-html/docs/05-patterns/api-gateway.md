---
title: API 网关
---

# API 网关

> 微服务的"门面"——所有外部请求的统一入口。

## 1. 为什么需要 API 网关？

```
没有网关：
  Client → 直接调 Service A
  Client → 直接调 Service B
  Client → 直接调 Service C
  ...
  Client 端要：
    - 知道所有服务的地址
    - 处理鉴权
    - 处理协议转换
    - 处理限流
    - 重复实现 N 次

有网关：
  Client → Gateway → 转发到合适的 Service
  Client 端只需：
    - 知道 Gateway 地址
    - 一次鉴权
    - 一个协议
```

## 2. 网关的核心职责

```
1. 路由转发：
   - URL 路径 → 后端服务
   - 例：/api/order/* → OrderService
         /api/user/*  → UserService

2. 鉴权认证：
   - JWT 验证
   - API Key 校验
   - OAuth 2.0

3. 限流熔断：
   - 入口限流
   - 后端服务熔断

4. 协议转换：
   - HTTP → gRPC
   - REST → GraphQL
   - WebSocket 适配

5. 聚合编排：
   - 一个客户端请求 → 聚合多个服务
   - 减少客户端轮询

6. 监控日志：
   - 请求统计
   - 错误率
   - 响应时间
```

## 3. 网关架构

### 3.1 单层网关

```
┌────────┐      ┌────────────┐      ┌──────────┐
│ Client │ ───► │ API Gateway │ ───► │ Services │
└────────┘      └────────────┘      └──────────┘
                       │
                       ├─→ Auth
                       ├─→ Rate Limit
                       ├─→ Logging
                       └─→ Routing
```

### 3.2 多层网关

```
外部网关（BFF / 边缘网关）：
  - 对外的统一入口
  - HTTPS 终止
  - 全局限流

内部网关：
  - 微服务之间的调用入口
  - 服务间鉴权
  - 内部限流

例：
  Client → CDN → SLB → 外部网关 → 内部网关 → Microservices
```

### 3.3 BFF（Backend for Frontend）

```
为不同前端定制的网关：
  - Mobile BFF：返回移动端所需字段
  - Web BFF：返回 Web 端所需字段
  - Open API BFF：返回第三方接口所需字段

📌 不同前端要的数据不同
   单一网关难以兼顾
```

## 4. 路由策略

### 4.1 静态路由

```
基于 URL 前缀：
  /api/order/* → OrderService
  /api/user/*  → UserService
  /api/pay/*   → PayService

简单但不够灵活
```

### 4.2 动态路由

```
基于服务注册中心：
  - 网关订阅 Registry
  - 服务实例变化时自动更新路由表
  - 支持权重 / 版本路由

例：
  /api/order → OrderService 的 v2 实例（灰度）
```

### 4.3 高级路由

```
基于 Header / Cookie：
  - 灰度发布：Header X-Version=2
  - A/B 测试：Cookie bucket=A
  - 租户隔离：Header X-Tenant=acme

基于 IP：
  - 地域路由：华东用户 → 华东机房
  - 黑白名单

基于权重：
  - 95% 流量 → 老版本
  - 5% 流量 → 新版本
```

## 5. 限流（在网关层）

```
为什么网关限流？
  - 在入口挡住异常流量
  - 保护后端所有服务
  - 比每个服务各自限流更高效

限流算法（详见 rate-limiter.md）：
  - 令牌桶
  - 漏桶
  - 滑动窗口

📌 网关层是"粗粒度限流"（保护后端）
   服务层是"细粒度限流"（保护业务）
```

## 6. 鉴权

```
流程：
  1. Client 登录 → 服务颁发 Token（JWT）
  2. Client 请求带 Token
  3. Gateway 验证 Token 有效性
  4. 验证通过 → 转发请求（带 UserID）
  5. 验证失败 → 返回 401

📌 Gateway 做"统一鉴权"，业务服务做"业务级权限校验"
   - 鉴权 = 你是谁
   - 授权 = 你能做什么
   - Gateway 只管前者
```

## 7. 灰度发布

```
通过网关实现灰度：

1. 部署 v2 版本
2. 网关配置：/api/order 的 5% 流量路由到 v2
3. 观察 v2 错误率 / 延迟
4. 没问题 → 逐步调高比例（5% → 25% → 50% → 100%）
5. 下线 v1 实例

📌 网关层灰度 vs K8s 灰度：
   - 网关层：路由灵活（按用户 / 地区 / Header）
   - K8s 层：按实例比例
   - 实际常组合使用
```

## 8. 主流网关对比

| 方案 | 性能 | 语言 | 特点 |
|---|---|---|---|
| **Nginx** | ★★★★★ | C | 高性能，需配置 Lua |
| **Kong** | ★★★★ | OpenResty | Nginx + Lua，生态完善 |
| **APISIX** | ★★★★ | OpenResty | 国产，云原生 |
| **Spring Cloud Gateway** | ★★★ | Java | Spring 生态，WebFlux |
| **Zuul** | ★★ | Java | Netflix，IO 模型老 |
| **Envoy** | ★★★★★ | C++ | 服务网格 / Sidecar |
| **Traefik** | ★★★★ | Go | K8s 友好，自动发现 |
| **Istio Gateway** | ★★★★★ | C++ | 服务网格 |

## 9. Kong 详解（参考实现）

### 9.1 架构

```
基于 OpenResty（Nginx + Lua）：
  - 高性能（基于 Nginx）
  - Lua 插件灵活扩展
  - PostgreSQL 存储配置
  - 插件生态丰富

插件：
  - key-auth
  - jwt
  - rate-limiting
  - cors
  - logging
```

### 9.2 配置示例

```yaml
# 添加服务
services:
  - name: order-service
    url: http://order-service:8080

# 添加路由
routes:
  - service: order-service
    paths:
      - /api/order

# 添加插件
plugins:
  - name: jwt
  - name: rate-limiting
    config:
      minute: 100
      policy: local
```

## 10. 自研网关

### 10.1 为什么自研？

```
现成网关不够用时：
  - 特殊协议（MQTT / gRPC-Web）
  - 特殊业务（复杂编排）
  - 性能极致要求
  - 成本控制
```

### 10.2 自研网关的核心

```
1. 高性能：
   - 异步 I/O（Netty / Tokio）
   - 连接复用
   - 零拷贝

2. 路由引擎：
   - Trie 树匹配 URL 前缀
   - 支持动态配置

3. 插件机制：
   - 类似 Kong 的插件架构
   - 业务可扩展

4. 可观测性：
   - 请求 trace
   - 错误率
   - 延迟分布

📌 现代网关实现：Go / Rust + 异步 I/O
```

## 11. API 网关的误区

### 11.1 网关不是万能

```
不能把业务逻辑放在网关：
  - 网关应该是无状态的
  - 业务逻辑应该放在 BFF 或独立服务
  - 否则网关成了"巨石"

不能把数据库访问放网关：
  - 网关是入口，不是数据层
```

### 11.2 网关不是 ESB

```
传统 ESB（企业服务总线）：
  - 重量级
  - 包含业务逻辑
  - 中心化

现代 API 网关：
  - 轻量级
  - 只做转发 / 鉴权 / 限流
  - 无状态

📌 把网关当 ESB 用 = 性能 + 维护双重灾难
```

### 11.3 网关不是必须的

```
小规模微服务：
  - 3-5 个服务
  - 直接调也行
  - 加网关反而复杂

中大规模：
  - 10+ 个服务
  - 多个客户端
  - 网关价值显著
```

## 12. 一句话总结

```
📌 API 网关是微服务的"门面"，统一入口 + 路由 + 鉴权 + 限流
📌 核心职责：路由 / 鉴权 / 限流 / 协议转换 / 聚合 / 监控
📌 多层网关：外部网关（BFF）+ 内部网关
📌 灰度发布是网关的核心价值（按比例 / 用户 / Header）
📌 选型：Kong/APISIX（高性能）、Spring Cloud Gateway（Spring 生态）、Envoy（服务网格）
📌 不要把业务逻辑放进网关（保持网关轻量）
📌 小规模项目可能不需要网关，避免过度设计
```

## 13. 参考资料

- Kong: https://github.com/Kong/kong
- APISIX: https://apisix.apache.org/
- Spring Cloud Gateway: 官方文档
- Envoy: https://www.envoyproxy.io/
- Microservices Patterns (Chris Richardson, 2018) —— 第 7 章
- Building Microservices (Sam Newman, 2015)