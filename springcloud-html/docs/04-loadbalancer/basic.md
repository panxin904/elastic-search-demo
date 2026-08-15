---
title: Spring Cloud LoadBalancer
---

# 🔄 Spring Cloud LoadBalancer

> Spring Cloud LoadBalancer 是 Spring Cloud **官方**的客户端负载均衡器，替代了 Netflix Ribbon。

## 🎯 LoadBalancer vs Ribbon

| 维度 | Ribbon | LoadBalancer |
|---|---|---|
| 维护方 | Netflix（已停止维护） | **Spring 官方** |
| 架构 | 阻塞 | **响应式（Reactor）** |
| 性能 | 一般 | **更好** |
| 集成 | 复杂 | **自动（Spring Cloud）** |
| 状态 | **维护模式** | **推荐使用** |

**Spring Cloud 2020+ 默认用 LoadBalancer 替代 Ribbon**

## 🚀 快速开始

### 1. 添加依赖

```xml
<!-- OpenFeign 已自动引入 LoadBalancer -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>

<!-- 或单独引入 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>
```

### 2. 启用（默认开启）

```yaml
# application.yml
spring:
  application:
    name: order-service  # 服务名
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
```

```java
// 启动类
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class Application { }
```

### 3. 使用

```java
// 方式 1：OpenFeign（推荐）
@FeignClient("user-service")  // ⚠️ 用服务名调用
public interface UserClient {
    @GetMapping("/api/users/{id}")
    User getById(@PathVariable Long id);
}

// 方式 2：RestTemplate
@Bean
@LoadBalanced  // ⚠️ 关键
public RestTemplate restTemplate() {
    return new RestTemplate();
}

restTemplate.getForObject("http://user-service/api/users/1", User.class);

// 方式 3：WebClient
@Bean
@LoadBalanced
public WebClient.Builder webClientBuilder() {
    return WebClient.builder();
}

webClientBuilder.build()
    .get()
    .uri("http://user-service/api/users/{id}", 1)
    .retrieve()
    .bodyToMono(User.class);
```

## 🎯 内置负载均衡策略

```yaml
spring:
  cloud:
    loadbalancer:
      # 全局策略
      configs:
        default:
          # 策略：轮询 / 随机 / 一致性 Hash / 响应时间
          # 默认：轮询（RoundRobin）
```

| 策略 | 说明 |
|---|---|
| `RoundRobin`（默认） | 依次轮询每个实例 |
| `Random` | 随机选择实例 |
| `WeightedResponseTime` | 根据响应时间加权（快实例多分配） |

## 🔧 配置负载均衡策略

### 全局配置

```yaml
spring:
  cloud:
    loadbalancer:
      configs:
        default:
          # 随机策略
          type: Random
```

### 特定服务配置

```java
@Bean
public ReactorLoadBalancer<ServiceInstance> randomLoadBalancer(
    Environment environment, LoadBalancerClientFactory factory
) {
    String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
    return new RandomLoadBalancer(
        factory.getLazyProvider(name),
        factory.getName(environment)
    );
}
```

## 🎯 自定义负载均衡策略

### 场景：按版本号路由

```java
public class VersionLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    private final ObjectProvider<ServiceInstanceListSupplier> supplier;
    private final String serviceId;
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        // 1. 从请求头获取期望版本
        String expectedVersion = request.getContext()
            .getClientRequest().getHeaders().getFirst("X-Version");
        
        // 2. 获取所有实例
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                if (expectedVersion == null) {
                    return new DefaultResponse(instances.get(0));
                }
                // 3. 按版本过滤
                ServiceInstance match = instances.stream()
                    .filter(i -> expectedVersion.equals(
                        i.getMetadata().get("version")))
                    .findFirst()
                    .orElse(instances.get(0));
                return new DefaultResponse(match);
            });
    }
}
```

```java
// Java SPI 加载
public class VersionLoadBalancerConfiguration {
    
    @Bean
    public ReactorLoadBalancer<ServiceInstance> versionLoadBalancer(
        Environment environment, 
        LoadBalancerClientFactory factory
    ) {
        String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
        return new VersionLoadBalancer(
            factory.getLazyProvider(name),
            name
        );
    }
}
```

```
META-INF/spring.factories:
com.example.config.VersionLoadBalancerConfiguration
```

### 场景：按权重路由

```yaml
# Nacos 中配置实例权重
spring:
  cloud:
    nacos:
      discovery:
        metadata:
          weight: 100  # 权重
```

```java
public class WeightedLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 按权重加权随机
                int totalWeight = instances.stream()
                    .mapToInt(i -> Integer.parseInt(
                        i.getMetadata().getOrDefault("weight", "100")))
                    .sum();
                int random = ThreadLocalRandom.current().nextInt(totalWeight);
                int sum = 0;
                for (ServiceInstance instance : instances) {
                    sum += Integer.parseInt(
                        instance.getMetadata().getOrDefault("weight", "100"));
                    if (random < sum) {
                        return new DefaultResponse(instance);
                    }
                }
                return new DefaultResponse(instances.get(0));
            });
    }
}
```

## 🔗 同一服务多实例

```
Nacos 上注册：
- user-service: 192.168.1.10:8081
- user-service: 192.168.1.11:8081
- user-service: 192.168.1.12:8081

调用 user-service 时：
→ LoadBalancer 自动从这 3 个实例中选择
```

## 🛡️ 实战：服务降级

```java
@FeignClient(name = "user-service", fallbackFactory = UserClientFallback.class)
public interface UserClient {
    @GetMapping("/api/users/{id}")
    User getById(@PathVariable Long id);
}

@Component
public class UserClientFallback implements FallbackFactory<UserClient> {
    
    @Override
    public UserClient create(Throwable cause) {
        return new UserClient() {
            @Override
            public User getById(Long id) {
                return User.empty();  // 降级返回空对象
            }
        };
    }
}
```

## 🎯 总结

**LoadBalancer 核心：**
- ✅ 替代 Ribbon（Spring Cloud 官方）
- ✅ 响应式架构（性能更好）
- ✅ 自动与 OpenFeign 集成
- ✅ 支持自定义策略

**内置策略：**
- ✅ RoundRobin（默认，轮询）
- ✅ Random（随机）
- ✅ WeightedResponseTime（响应时间加权）

**自定义策略场景：**
- ✅ 按版本号路由
- ✅ 按权重路由
- ✅ 按机房/地域路由
- ✅ 一致性 Hash（相同请求到同一实例）

**下一步：** [🎯 负载均衡策略](/04-loadbalancer/strategy) — 深入各种策略与场景