---
title: 服务治理
date: 2026-08-15  # date-auto-injected
---

# 微服务治理

**服务治理 = 让多个服务稳定运行**：限流 / 熔断 / 降级 / 链路追踪 / 配置中心 / 服务发现。

## 一句话总结

> **服务治理 = 高可用 + 可观测 + 可配置 + 可扩展**。**核心：限流 + 熔断 + 链路追踪 + 配置中心**。

---

## 一、服务治理全景

```
┌─────────────────────────────────────────────┐
│ 服务治理                                       │
├──────────────┬──────────────┬────────────────┤
│  服务稳定性   │  可观测性     │  服务协作        │
│  限流        │  链路追踪     │  服务发现        │
│  熔断        │  日志        │  配置中心        │
│  降级        │  指标        │  消息队列        │
│  超时        │  健康检查     │  分布式锁        │
│  重试        │  告警        │  全链路灰度      │
└──────────────┴──────────────┴────────────────┘
```

## 二、限流

**目的**：防止流量过载，保护后端。

### 算法

| 算法 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| 固定窗口 | 1s 计数 | 简单 | 边界突刺 |
| 滑动窗口 | 多个窗口 | 平滑 | 内存大 |
| 漏桶 | 固定速率出水 | 恒定 | 突发浪费 |
| 令牌桶 | 攒令牌 | 允许突发 | 略复杂 |

### Go 实现

```go
import "golang.org/x/time/rate"

// 令牌桶：每秒 100 个，桶容量 200
limiter := rate.NewLimiter(rate.Limit(100), 200)

if !limiter.Allow() {
    http.Error(w, "Too Many Requests", 429)
    return
}
```

### 分布式限流

**Redis + Lua 原子计数**：

```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local cur = redis.call("INCR", key)
if cur > limit then
    return 0
end
redis.call("EXPIRE", key, 1)
return 1
```

**Sentinel / Sentinel-Go**（阿里开源）：

```go
import "github.com/alibaba/sentinel-golang/core/flow"

flow.LoadRules([]*flow.Rule{
    {Resource: "order", TokenCalculateStrategy: flow.WarmUp, WarmUpColdFactor: 3, Threshold: 100},
})

entry, _ := flow.LoadGlobalTrace(context.Background(), "order")
if entry != nil { defer entry.Exit() }
```

## 三、熔断

**目的**：下游服务故障时快速失败，避免雪崩。

### 状态机

```
Closed ──故障率超阈值──> Open ──(sleep window)──> Half-Open
   ▲                                                  │
   └────────────────成功──────────────────────────────┘
                          └──失败──> Open
```

### Go 实现（gobreaker）

```go
import "github.com/sony/gobreaker"

cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
    Name:        "user-service",
    MaxRequests: 3,
    Interval:    1 * time.Minute,    // 统计周期
    Timeout:     30 * time.Second,   // Open 持续时间
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        return counts.ConsecutiveFailures > 5
    },
})

result, err := cb.Execute(func() (interface{}, error) {
    return httpClient.Get("http://user-service/api/users")
})
```

**sentinel-golang**：

```go
import "github.com/alibaba/sentinel-golang/core/circuitbreaker"

circuitbreaker.LoadRules([]*circuitbreaker.Rule{
    {Resource: "user-service", Strategy: circuitbreaker.SlowRequestRatio,
        Threshold: 0.5, StatIntervalMs: 10000, MinRequestAmount: 10,
        SlowRatioThreshold: 0.6, MaxAllowedRtMs: 100},
})
```

## 四、超时与重试

```go
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

// 一层调用：3s 超时
resp, err := client.GetUser(ctx, req)

// 多层传递：每层 1s
ctx, cancel = context.WithTimeout(parentCtx, 1*time.Second)
```

**重试**：

```go
import "github.com/avast/retry-go"

err := retry.Do(
    func() error {
        return doRequest()
    },
    retry.Attempts(3),
    retry.Delay(100*time.Millisecond),
    retry.DelayType(retry.BackOffDelay),
    retry.MaxDelay(2*time.Second),
    retry.OnRetry(func(n uint, err error) {
        log.Printf("retry %d: %v", n, err)
    }),
)
```

**重试策略**：
- 指数退避：`100ms → 200ms → 400ms → ...`
- 抖动：避免雷鸣群
- 仅 idempotent 操作可重试

## 五、服务发现

**目标**：客户端无需硬编码服务地址。

### 模式

| 模式 | 特点 | 代表 |
|---|---|---|
| 客户端发现 | 客户端查注册中心 + LB | Eureka / Consul |
| 服务端发现 | LB 查询注册中心 | K8s Service / AWS ALB |

### Go 客户端发现

```go
import "github.com/hashicorp/consul/api"

client, _ := api.NewClient(api.DefaultConfig())
services, _, _ := client.Catalog().Service("user-service", "", nil)
for _, s := range services {
    fmt.Println(s.ServiceAddress, s.ServicePort)
}

// resolver 自动
conn, _ := grpc.Dial("consul:///user-service",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`))
```

### K8s 模式（服务端发现）

```go
// K8s Service 自带负载均衡
conn, _ := grpc.Dial("user-service.default.svc.cluster.local:50051")
// K8s DNS + Service VIP → kube-proxy → pod
```

## 六、配置中心

**Apollo**（携程开源）：

```go
import "github.com/apolloconfig/agollo/v4"

client, _ := agollo.StartWithConfig(func() (*config.AppConfig, error) {
    return &config.AppConfig{
        AppID:          "myapp",
        Cluster:        "default",
        IP:             "http://apollo.config:8080",
        NamespaceName:  "application",
    }, nil
})

timeout := client.GetStringValue("request.timeout", "3s")
```

**Nacos**（阿里开源）：

```go
import "github.com/nacos-group/nacos-sdk-go/clients"

client, _ := clients.NewConfigClient(vo.NacosClientParam{
    ServerConfigs: []vo.ServerConfig{{IpAddr: "127.0.0.1", Port: 8848}},
})
dataId, _ := client.GetConfig(vo.ConfigParam{DataId: "user-service.yaml", Group: "DEFAULT_GROUP"})
```

**Viper + K8s ConfigMap**：

```go
viper.SetConfigFile("/etc/config/user-service.yaml")
viper.WatchConfig()
viper.OnConfigChange(func(e fsnotify.Event) {
    reloadConfig()
})
```

## 七、链路追踪

**OpenTelemetry（推荐）**：

```go
import "go.opentelemetry.io/otel"

func main() {
    tp := otelinit.NewTracerProvider()  // 初始化
    otel.SetTracerProvider(tp)
    
    r := gin.Default()
    r.Use(otelgin.Middleware("user-service"))
    
    r.GET("/users/:id", func(c *gin.Context) {
        ctx := c.Request.Context()
        tracer := otel.Tracer("user-service")
        ctx, span := tracer.Start(ctx, "GetUser")
        defer span.End()
        
        // 业务代码
        u, _ := userService.GetUser(ctx, c.Param("id"))
        c.JSON(200, u)
    })
}
```

**Jaeger / Tempo / Zipkin**：trace 后端。

## 八、健康检查

```go
import "github.com/heptiolabs/healthcheck"

health := healthcheck.NewHandler()
health.AddLivenessCheck("goroutine-threshold", healthcheck.GoroutineCountCheck(100))
health.AddReadinessCheck("mysql", healthcheck.DatabasePingCheck(db, 1*time.Second))
health.AddReadinessCheck("redis", healthcheck.RedisPingCheck(redisClient, "localhost:6379", 1*time.Second))

http.Handle("/live", health)
http.Handle("/ready", health)
```

**K8s 集成**：
- Liveness probe：`/live` 失败 → 重启 pod
- Readiness probe：`/ready` 失败 → 不接流量

## 九、降级

```go
// Hystrix 风格
type DegradeFunc func(ctx context.Context) (interface{}, error)

func WithFallback(primary, fallback func(ctx context.Context) (interface{}, error)) func(ctx context.Context) (interface{}, error) {
    return func(ctx context.Context) (interface{}, error) {
        result, err := primary(ctx)
        if err != nil {
            log.Printf("primary failed: %v, fallback", err)
            return fallback(ctx)
        }
        return result, nil
    }
}

// 用
getProduct := WithFallback(
    func(ctx context.Context) (interface{}, error) { return productService.Get(ctx, id) },
    func(ctx context.Context) (interface{}, error) { return defaultProduct, nil },  // 降级
)
```

## 十、灰度发布

**K8s + Istio**：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service
spec:
  http:
  - match:
    - headers:
        x-user-group:
          exact: beta
    route:
    - destination:
        host: user-service
        subset: v2
  - route:
    - destination:
        host: user-service
        subset: v1
```

**按比例**：

```yaml
spec:
  http:
  - route:
    - destination:
        host: user-service
        subset: v2
      weight: 10
    - destination:
        host: user-service
        subset: v1
      weight: 90
```

## 关联章节

- **05-microservices/grpc**：RPC
- **05-microservices/kratos**：框架
- **05-microservices/case-study**：真实案例
- **04-cloud-native/kubernetes-internals**：K8s

## 一句话总结

> **服务治理 = 限流 + 熔断 + 追踪 + 配置 + 发现**。**K8s 简化部分，框架简化全部**。


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

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
