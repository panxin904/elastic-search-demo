---
title: RPC 远程调用
---

# RPC 远程调用

> 像调用本地方法一样调用远程服务。**性能、序列化、服务发现、超时重试**。

## 1. 什么是 RPC？

```
RPC（Remote Procedure Call）：
  - 进程间通信，看起来像本地调用
  - 隐藏网络细节
  - 微服务的基础

RPC vs HTTP：
  - HTTP：通用协议，文本（JSON/XML）
  - RPC：高性能，二进制，自定义协议

主流 RPC 框架：
  - gRPC（Google）
  - Thrift（Apache）
  - Dubbo（阿里）
  - Motan（微博）
```

## 2. RPC 流程

```
调用方：                       被调方：
                             
User → Stub → Client → Network → Server → Stub → UserImpl
                                    ↓
                                  返回结果
```

详细步骤：

```
1. 客户端调用本地 stub（代理对象）
2. stub 把方法名、参数序列化
3. 通过网络发送到服务端
4. 服务端 stub 反序列化
5. 调用实际方法
6. 返回值序列化
7. 客户端 stub 反序列化返回值
8. 客户端拿到结果

📌 stub = 代理对象，对用户透明
```

## 3. 核心组件

### 3.1 序列化

```
常见序列化协议：
  - JSON：可读，跨语言，慢
  - Protobuf：二进制，高效，跨语言，gRPC 默认
  - Thrift：二进制，Facebook 出品
  - Avro：二进制，Schema 演进好
  - Kryo / Hessian2：Java 生态快

选型：
  - 跨语言 → Protobuf
  - 性能极致 → Kryo
  - 易调试 → JSON
  - 演进友好 → Avro
```

### 3.2 网络通信

```
协议：
  - TCP：可靠，性能高（gRPC 用）
  - HTTP/1.1：通用，性能差
  - HTTP/2：多路复用，gRPC 用
  - QUIC：UDP 可靠，HTTP/3

IO 模型：
  - BIO：1 连接 1 线程，并发差
  - NIO：多路复用，Netty 实现
  - AIO：异步 IO，Linux 优化

📌 99% 框架用 Netty
```

### 3.3 服务发现

```
调用方需要知道被调方地址：
  - 静态配置：硬编码 IP（不可扩展）
  - DNS：域名解析（延迟高）
  - 注册中心：服务动态注册 + 发现

注册中心：
  - ZooKeeper：强一致
  - etcd：Raft，K8s 生态
  - Consul：多数据中心
  - Nacos：阿里，国产生态
  - Eureka：Netflix，AP 优先

流程：
  1. 服务启动 → 注册到注册中心
  2. 客户端订阅 → 拿到地址列表
  3. 负载均衡选一个调用
  4. 服务挂了 → 注册中心剔除
```

### 3.4 负载均衡

```
策略：
  - 随机：简单，不均衡
  - 轮询：均匀，不考虑机器性能
  - 加权轮询：按权重（机器性能）
  - 最少连接：把请求给连接数最少的
  - 一致性哈希：同 key 路由到同机器
  - P2C（Power of Two Choices）：随机选 2 个，挑负载低的

📌 Dubbo 默认 random + 权重
   gRPC 用 pick_first / round_robin
```

### 3.5 超时与重试

```
超时：
  - 连接超时：connect timeout（默认 1-3s）
  - 读超时：read timeout（默认 5-30s）
  - 总超时：全链路超时

重试：
  - 幂等服务：可重试
  - 非幂等：不能重试
  - 重试策略：最多 2-3 次，指数退避

📌 重试放大雪崩
   下游故障 + 重试 = 请求量翻倍
```

## 4. 主流框架对比

### 4.1 gRPC

```
特点：
  - HTTP/2 协议（多路复用 + 头部压缩）
  - Protobuf 序列化
  - 跨语言（11 种语言）
  - 流式 RPC（4 种模式）
  - 强类型（IDL 约束）

四种调用模式：
  - Unary：一元调用
  - Server Streaming：服务端流
  - Client Streaming：客户端流
  - Bidirectional Streaming：双向流

适用：
  - 微服务内部
  - 跨语言
  - 高性能场景
```

### 4.2 Dubbo

```
特点：
  - Java 生态
  - 自定义协议（Dubbo 协议）
  - 丰富治理：路由、限流、熔断、降级
  - SPI 扩展机制

架构：
  - Provider：服务提供方
  - Consumer：服务消费方
  - Registry：注册中心
  - Monitor：监控中心
  - Container：运行容器

📌 阿里系标配（HSF 演变而来）
   国内大厂首选
```

### 4.3 Thrift

```
特点：
  - Facebook 出品
  - 跨语言
  - 自带 IDL + codegen
  - 多种传输协议（Binary/Compact/JSON）
  - 多种 server 模型（单线程/多线程/非阻塞）

适用：
  - 大数据传输
  - 跨语言
  - 历史遗留系统
```

### 4.4 对比

| 框架 | 协议 | 序列化 | 跨语言 | 性能 | 生态 |
|---|---|---|---|---|---|
| gRPC | HTTP/2 | Protobuf | ✅ | 高 | 强 |
| Dubbo | 自定义 | Hessian2 | 有限 | 高 | Java 强 |
| Thrift | 自定义 | Thrift | ✅ | 极高 | 一般 |
| Spring Cloud | HTTP/1.1 | JSON | ✅ | 中 | 强 |

## 5. 工程实现

### 5.1 gRPC 示例

```protobuf
// 1. IDL 定义
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);  // 服务端流
}

message GetUserRequest {
  int64 user_id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

```java
// 2. 服务端
public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {
    @Override
    public void getUser(GetUserRequest req, StreamObserver<User> responseObserver) {
        User user = userDao.findById(req.getUserId());
        responseObserver.onNext(user);
        responseObserver.onCompleted();
    }
}

// 3. 客户端
ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 9090)
    .usePlaintext()
    .build();
UserServiceGrpc.UserServiceBlockingStub stub = UserServiceGrpc.newBlockingStub(channel);
User user = stub.getUser(GetUserRequest.newBuilder().setUserId(1001L).build());
```

### 5.2 Dubbo 示例

```java
// 1. 定义接口
public interface UserService {
    User getUser(Long userId);
}

// 2. Provider
@Service
public class UserServiceImpl implements UserService {
    public User getUser(Long userId) {
        return userDao.findById(userId);
    }
}

// 3. Consumer
@Reference
private UserService userService;

public void process() {
    User user = userService.getUser(1001L);
}
```

## 6. 关键问题

### 6.1 透明化（Stub）

```
问题：
  - 用户调用 stub 就像本地
  - 但 stub 要做大量工作（序列化、网络、异常映射）

实现：
  - 静态代理（gRPC 编译生成）
  - 动态代理（JDK Proxy / ByteBuddy / Javassist）
  - AOP 织入

📌 stub 是 RPC 框架的"魔法"
   99% 用动态代理
```

### 6.2 异常处理

```
网络异常：
  - 连接超时 → 重试
  - 读超时 → 重试
  - 服务端 500 → 业务异常
  - 服务端 404 → 方法不存在
  - 序列化失败 → 立即失败

异常透传：
  - 服务端异常 → 序列化 → 客户端反序列化
  - 跨语言异常难处理
  - 通常用错误码 + 错误消息代替
```

### 6.3 调用链追踪

```
分布式调用：
  - A → B → C → D
  - 每个节点都有日志
  - 怎么串起来？

方案：
  1. TraceId + SpanId（OpenTelemetry）
  2. gRPC 自带 metadata（headers）
  3. Dubbo 自带 attachment

传递方式：
  - 隐式：拦截器自动加
  - 显式：业务代码加
```

### 6.4 异步调用

```
同步调用：
  - 调用方阻塞等返回
  - 资源浪费

异步：
  - Future / CompletableFuture
  - Callback
  - RxJava / Reactor
  - gRPC async stub
```

## 7. 高级话题

### 7.1 连接复用

```
HTTP/1.1：
  - 一个连接一次请求
  - 短连接或 keep-alive

HTTP/2：
  - 多路复用，一个连接多请求
  - 显著减少连接数

gRPC：
  - 默认 HTTP/2
  - 长连接 + 多路复用
  - 推荐 1 个 stub 1 个 channel
```

### 7.2 服务降级

```
场景：
  - 下游服务挂了
  - 调用方不能也跟着挂

降级策略：
  - 返回默认值
  - 返回缓存
  - 抛默认异常
  - 走 mock 实现

实现：
  - 框架支持（Dubbo mock）
  - Sentinel 规则
  - 客户端拦截器
```

### 7.3 限流

```
RPC 层限流：
  - 全局限流（按服务名）
  - 用户级限流（按 userId）
  - IP 限流

Sentinel：
  - QPS 限流
  - 线程数限流
  - 慢调用比例
```

### 7.4 优雅停机

```
问题：
  - 服务重启时，调用方还在发请求
  - 失败率上升

解决：
  1. preStop hook：摘除注册（停止接新请求）
  2. 等待 30s 让 in-flight 请求完成
  3. 关闭连接
  4. kill 进程

📌 Kubernetes 配合 readiness probe
   deregister + sleep 30 + stop
```

## 8. RPC vs HTTP API

```
选 RPC：
  - 微服务内部（高频调用）
  - 性能要求高
  - 类型安全
  - 团队统一技术栈

选 HTTP：
  - 对外 API（REST 风格）
  - 浏览器调用
  - 跨平台（异构客户端）
  - 调试简单

📌 业界主流：
   内部：RPC（gRPC/Dubbo）
   外部：HTTP（REST/GraphQL）
```

## 9. 一句话总结

```
📌 RPC = stub 代理 + 序列化 + 网络 + 注册中心 + 治理
📌 框架：gRPC（跨语言首选） / Dubbo（Java 生态） / Thrift（高性能）
📌 序列化：Protobuf（首选） / Thrift / Avro
📌 网络：Netty + HTTP/2，主流方案
📌 治理：服务发现 + 负载均衡 + 超时重试 + 限流降级
📌 关键设计：调用链追踪（TraceId）+ 优雅停机 + 异常透传
📌 选型：内部 RPC（高性能），外部 HTTP（通用性）
📌 未来趋势：gRPC + Protobuf 主导
```

## 10. 参考资料

- gRPC 官方文档
- Apache Dubbo 官方文档
- Apache Thrift 设计文档
- "RPC: Remote Procedure Call" 经典论文
- Protobuf Encoding 规范
- OpenTelemetry 分布式追踪标准


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):企业架构
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [kafka](https://java-px.bot.cd/kafka/):消息

<!-- svg-injected:do-not-edit -->

## 图示：gRPC 调用链路（HTTP/2 + Protobuf）

![gRPC 调用链路（HTTP/2 + Protobuf）](/grpc-flow.svg)
