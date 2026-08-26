---
title: RPC 远程过程调用
---

# RPC 远程过程调用

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-cloud">微服务</div>

RPC（Remote Procedure Call）让程序像调用本地方法一样调用远程服务，隐藏了网络通信细节。

## 1. RPC vs REST

| 维度 | RPC | REST |
| --- | --- | --- |
| 风格 | 面向动作 / 函数 | 面向资源 |
| 协议 | 自有（HTTP/2, TCP） | HTTP |
| 数据格式 | Protobuf / Thrift | JSON / XML |
| 性能 | 高 | 中 |
| 浏览器友好 | 弱 | 强 |
| 适用 | 内部微服务 | 开放 API |

## 2. RPC 调用流程

```
Client                         Server
  |                              |
  |  1. stub.encode(req)         |
  |  2. transport.send(msg)      |
  |  =====================>      |  3. 接收消息
  |                              |  4. stub.decode(req)
  |                              |  5. 业务方法执行
  |                              |  6. stub.encode(resp)
  |  <=====================      |  7. transport.send(resp)
  |  8. stub.decode(resp)        |
  |  9. 返回结果给调用方          |
```

## 3. RPC 核心组件

| 组件 | 作用 |
| --- | --- |
| Client Stub | 代理对象，把方法调用转成网络消息 |
| Server Stub | 接收消息，反序列化为方法调用 |
| 序列化 | 对象 ↔ 字节流 |
| 传输层 | TCP / HTTP/2 / QUIC |
| 服务发现 | 找到目标服务地址 |
| 负载均衡 | 多实例间分配请求 |
| 容错 | 重试、超时、熔断 |

## 4. 主流 RPC 框架

| 框架 | 协议 | 序列化 | 厂商 |
| --- | --- | --- | --- |
| gRPC | HTTP/2 | Protobuf | Google |
| Thrift | TFramed / TBinary | Thrift | Apache |
| Dubbo | TCP / HTTP/2 | Hessian2 / JSON | 阿里 |
| Spring Cloud OpenFeign | HTTP | JSON | Spring |
| Tars | TCP | Tars | 腾讯 |
| bRPC | HTTP/2 | Protobuf | 百度 |
| Motan | TCP | JSON / Hessian | 微博 |

## 5. gRPC 详解

### 5.1 Proto 定义

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser(UserRequest) returns (UserResponse);
  rpc ListUsers(ListRequest) returns (stream UserResponse);
  rpc Upload(stream UploadRequest) returns (UploadResponse);
  rpc Chat(stream Message) returns (stream Message);
}

message UserRequest {
  int64 id = 1;
}

message UserResponse {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

四种调用方式：
- **Unary**：客户端发 1 个，服务端回 1 个
- **Server streaming**：客户端发 1 个，服务端回 N 个
- **Client streaming**：客户端发 N 个，服务端回 1 个
- **Bidirectional streaming**：双向流

### 5.2 优势

- 基于 HTTP/2：多路复用、低延迟
- Protobuf：高效二进制、强 schema
- 跨语言：自动生成 10+ 语言 stub
- 双向流 + 取消

### 5.3 局限

- 浏览器不友好（需 grpc-web / JSON transcoding）
- 强 schema，调试不如 JSON 直观
- 默认无加密（需配 TLS）

## 6. Protobuf vs JSON

| 维度 | Protobuf | JSON |
| --- | --- | --- |
| 体积 | 小（2~5x） | 大 |
| 速度 | 快（5~10x） | 慢 |
| 可读 | 差 | 好 |
| 强 schema | 强（.proto） | 弱（注释） |
| 跨语言 | 自动生成 | 手写 |

## 7. 服务注册与发现

```
┌─────────┐     注册     ┌──────────┐
│ Service │ ──────────> │ Registry │
└─────────┘             └──────────┘
                              ▲
                              │ 发现
                              │
                        ┌─────────┐
                        │ Client  │
                        └─────────┘
```

| 方案 | 特点 |
| --- | --- |
| Consul | 服务注册 + 健康检查 + KV |
| Etcd | KV，强一致 |
| ZooKeeper | CP 强一致 |
| Nacos | 阿里，配置 + 注册 |
| Eureka | Netflix AP 高可用 |
| K8s DNS | K8s 原生 |

## 8. 负载均衡策略

| 策略 | 描述 |
| --- | --- |
| 随机 | 简单 |
| 轮询 | 均匀 |
| 加权轮询 | 按权重 |
| 最少连接 | 动态 |
| 一致性哈希 | 同 key 走同节点 |
| P2C（Power of Two Choices） | 随机选 2 个，挑负载低 |

## 9. 容错机制

| 机制 | 作用 |
| --- | --- |
| 超时（Timeout） | 防长时间阻塞 |
| 重试（Retry） | 幂等接口有限重试 |
| 熔断（Circuit Breaker） | 错误率超阈值熔断 |
| 限流（Rate Limit） | 保护下游 |
| 降级（Fallback） | 返回兜底结果 |
| 隔离（Bulkhead） | 线程池 / 信号量隔离 |

## 10. gRPC 拦截器

```go
func clientInterceptor(ctx context.Context, method string, req, reply interface{},
    cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
    start := time.Now()
    err := invoker(ctx, method, req, reply, cc, opts...)
    log.Printf("rpc=%s cost=%v err=%v", method, time.Since(start), err)
    return err
}
```

可实现：链路追踪、日志、监控、认证、限流。

## 11. RPC 实战注意

| 问题 | 建议 |
| --- | --- |
| 接口版本 | URL / Header / IDL 版本字段 |
| 大包 | 启用压缩（gzip） |
| 慢调用 | 客户端超时 < 服务端超时 |
| 数据传输 | 用 stream 处理大文件 |
| 跨机房 | 就近路由 + 多协议 |
| 安全 | mTLS / 鉴权 / 限流 |

## 12. RPC vs HTTP API 选择

```
内部服务调用、高性能 → RPC（gRPC、Dubbo）
对外开放、跨组织   → REST + JSON
浏览器端调用      → REST（Fetch / AJAX）
移动 APP          → gRPC + JSON gateway
实时消息          → WebSocket / gRPC stream
```

## 13. 常见面试题

1. **RPC 核心？** 客户端 stub + 序列化 + 网络传输 + 服务端 stub。
2. **gRPC 用什么协议？** HTTP/2。
3. **Protobuf 优势？** 体积小、速度快、强 schema、跨语言。
4. **什么是流式 RPC？** 客户端或服务端可持续发送多个消息。
5. **服务发现怎么做？** Consul / Nacos / Etcd / K8s DNS。
6. **RPC 和 REST 怎么选？** 内部高性能用 RPC，对外通用接口用 REST。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
