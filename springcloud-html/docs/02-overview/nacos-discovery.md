---
title: Nacos 服务发现
---

# 🌐 Nacos 服务发现

> Nacos = **Na**ming and **Co**nfiguration **S**ervice，阿里巴巴开源的**服务发现 + 配置中心**，生产环境的标配。

## 🎯 为什么选 Nacos？

| 维度 | Eureka | Nacos | Consul |
|---|---|---|---|
| 一致性 | AP | **AP/CP 可切换** | CP |
| 健康检查 | 心跳 | **心跳 + HTTP/TPC** | TCP/HTTP/gRPC |
| 集成 | Spring Cloud | **Spring Cloud Alibaba** | HashiCorp |
| 性能 | 一般 | **高（10万级实例）** | 高 |
| 易用性 | 一般 | **✅ 好** | 复杂 |

**Nacos 优势：**
- ✅ 一个组件 = 服务发现 + 配置中心
- ✅ 支持 AP/CP 切换
- ✅ 健康检查方式多
- ✅ 中文控制台

## 🚀 服务注册

### 1. 引入依赖

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

### 2. application.yml

```yaml
spring:
  application:
    name: order-service  # ⚠️ 服务名（注册到 Nacos 的唯一标识）
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848  # Nacos Server 地址
        namespace: public              # 命名空间
        group: DEFAULT_GROUP            # 分组
        # 元数据（其他服务可看到）
        metadata:
          version: 1.0.0
          zone: cn-east-1
          cluster: order-cluster
```

### 3. 启用服务发现

```java
@SpringBootApplication
@EnableDiscoveryClient  // 启用服务发现
public class OrderApplication { }
```

### 4. 启动效果

```
控制台输出：
INFO ... NacosRegistry: nacos registry, order-service 192.168.1.100:8081 REGISTERED
```

Nacos 控制台 → 服务列表 → 看到 `order-service`

## 📋 版本配置方式对比

> 服务发现不像配置中心有 bootstrap 强依赖，但**如果同时使用 Nacos Config + Discovery**，2021 版发现配置也需放 `bootstrap.yml`，否则 Config 加载期间 Discovery 还没初始化。

### 方式一：新版推荐（Spring Boot 3.x / 2023.x+）

```yaml
# application.yml — 服务发现与配置中心都写在这里
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: public
        group: DEFAULT_GROUP
        metadata:
          version: 1.0.0
          zone: cn-east-1
  config:
    import:
      - nacos:order-service.yaml?group=DEFAULT_GROUP&refreshEnabled=true
```

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<!-- 无需 spring-cloud-starter-bootstrap -->
```

### 方式二：2021 版（Spring Boot 2.x / 2021.x）

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bootstrap</artifactId>
</dependency>
```

```yaml
# bootstrap.yml — 服务发现 + 配置中心都放这里
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: public
        group: DEFAULT_GROUP
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        namespace: public
        refresh-enabled: true
```

```yaml
# application.yml（业务配置）
server:
  port: 8082
spring:
  profiles:
    active: dev
```

### 核心区别

| 维度 | 新版（2023.x+ / Spring Boot 3.x） | 2021 版（Spring Boot 2.x） |
|------|-----------------------------------|---------------------------|
| **配置文件** | `application.yml`（统一） | `bootstrap.yml` + `application.yml` |
| **额外依赖** | 不需要 | `spring-cloud-starter-bootstrap` |
| **加载顺序** | `spring.config.import` 控制 | bootstrap → application |
| **Config + Discovery 共存** | 都在 application.yml | 都放 bootstrap.yml（推荐） |
| **命令行覆盖** | `--spring.cloud.nacos.discovery.namespace=prod` | 相同 |

### 旧版迁移到新版

```yaml
# ❌ 2021 版写法（bootstrap.yml）
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848

# ✅ 新版写法（application.yml）
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
  config:
    import: nacos:order-service.yaml
```

## 📞 服务发现与调用

### 1. OpenFeign 声明式调用

```java
@FeignClient("user-service")  // ⚠️ 用服务名（不是 URL）
public interface UserClient {
    
    @GetMapping("/api/users/{id}")
    User getById(@PathVariable Long id);
    
    @PostMapping("/api/users")
    User create(@RequestBody UserDTO dto);
}
```

```java
@Service
public class OrderService {
    @Autowired
    private UserClient userClient;  // ⚠️ 像调用本地方法一样
    
    public Order createOrder(OrderDTO dto) {
        // 自动负载均衡到 user-service 的某个实例
        User user = userClient.getById(dto.getUserId());
        // ...
    }
}
```

### 2. RestTemplate + LoadBalancer

```java
@Configuration
public class RestTemplateConfig {
    
    @Bean
    @LoadBalanced  // ⚠️ 启用负载均衡
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

```java
@Service
public class OrderService {
    @Autowired
    private RestTemplate restTemplate;
    
    public User getUser(Long id) {
        // 用服务名调用，自动负载均衡
        return restTemplate.getForObject(
            "http://user-service/api/users/" + id, 
            User.class
        );
    }
}
```

### 3. WebClient（响应式）

```java
@Bean
@LoadBalanced
public WebClient.Builder webClientBuilder() {
    return WebClient.builder();
}
```

```java
@Service
public class OrderService {
    @Autowired
    private WebClient.Builder builder;
    
    public Mono<User> getUser(Long id) {
        return builder.build()
            .get()
            .uri("http://user-service/api/users/{id}", id)
            .retrieve()
            .bodyToMono(User.class);
    }
}
```

## 🏷️ 元数据（Metadata）

```yaml
spring:
  cloud:
    nacos:
      discovery:
        metadata:
          version: 2.0.0
          zone: cn-east-1           # 可用于就近路由
          cluster: order-cluster   # 可用于集群隔离
          weight: 100              # 可用于自定义负载均衡
```

```java
// 其他服务可获取元数据
@FeignClient("order-service")
public interface OrderClient {
    
    @GetMapping("/api/orders/{id}")
    Order getById(@PathVariable Long id,
                  // 通过 Feign RequestInterceptor 传递
                  @RequestHeader("X-Version") String version);
}
```

## 🏥 健康检查

```yaml
spring:
  cloud:
    nacos:
      discovery:
        # 心跳间隔（默认 5s）
        heart-beat-interval: 5000
        # 心跳超时（默认 15s）
        heart-beat-timeout: 15000
```

**健康检查失败处理：**
- 超过 15 秒没收到心跳 → 标记为不健康
- 从服务列表中剔除
- Gateway / LoadBalancer 自动跳过

## 🌐 Nacos Server 集群部署

### 单机模式（开发）

```bash
./startup.sh -m standalone
```

### 集群模式（生产推荐）

```
3 台服务器：
- 192.168.1.10
- 192.168.1.11
- 192.168.1.12
```

```bash
# 每台机器上启动
./startup.sh -m cluster
```

**集群配置文件：** `conf/cluster.conf`
```properties
192.168.1.10:8848
192.168.1.11:8848
192.168.1.12:8848
```

## 🏷️ Namespace 命名空间

```
命名空间 = 环境隔离
- public（默认）：所有环境共享
- dev：开发环境
- test：测试环境
- prod：生产环境
```

### 概念图解

```
┌─────────────────────────────────────────────────┐
│               Nacos Server                       │
│                                                  │
│  ┌───── Namespace: dev ──────────────────┐      │
│  │  服务列表:                              │      │
│  │    - order-service (192.168.1.1:8081) │      │
│  │    - user-service  (192.168.1.2:8082) │      │
│  │    - gateway        (192.168.1.3:8080)│      │
│  └────────────────────────────────────────┘      │
│                                                  │
│  ┌───── Namespace: prod ─────────────────┐      │
│  │  服务列表:                              │      │
│  │    - order-service (10.0.1.1:8081)     │      │
│  │    - user-service  (10.0.1.2:8082)     │      │
│  │    - gateway        (10.0.1.3:8080)    │      │
│  └────────────────────────────────────────┘      │
└──────────────────────────────────────────────────┘

关键：不同 Namespace 的服务不可见
  dev 的 order-service 调用不到 prod 的 user-service ✓ 天然隔离
```

### 新版配置（Spring Boot 3.x / 2023.x+）

```yaml
# application-dev.yml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: dev    # ⚠️ Nacos 控制台的 Namespace ID（UUID）
        group: DEFAULT_GROUP
```

```yaml
# application-prod.yml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 192.168.1.10:8848
        namespace: prod   # ⚠️ 不同 Namespace，服务注册表完全隔离
        group: DEFAULT_GROUP
```

### 2021 版配置（Spring Boot 2.x）

```yaml
# bootstrap-dev.yml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: dev      # Namespace ID
        group: DEFAULT_GROUP
```

### 命令行覆盖 Namespace

```bash
# 开发环境（默认）
java -jar order-service.jar

# 指定 dev 环境
java -jar order-service.jar \
  --spring.cloud.nacos.discovery.namespace=dev

# 指定 prod 环境
java -jar order-service.jar \
  --spring.cloud.nacos.discovery.namespace=prod

# 新版 Spring Boot 3.x 也可
SPRING_CLOUD_NACOS_DISCOVERY_NAMESPACE=prod \
  java -jar order-service.jar
```

### 跨 Namespace 调用方案

```yaml
# ⚠️ 不同 Namespace 的服务默认不可互相发现
# 解决方案：用同一个 Namespace 内的 Gateway 做路由转发
#
# 场景：
#   - order-service（dev 命名空间）
#   - user-service（dev 命名空间）  ← 同一 namespace，可发现
#   - payment-service（prod 命名空间） ← 不同 namespace，不可见
#
# 方案 1：统一放到同一 Namespace
# 方案 2：通过 Gateway 跨 Namespace 转发（Gateway 注册到两个 namespace）
# 方案 3：使用同一个 Nacos Cluster 但不同 Namespace，服务间通过 Feign URL 直连
```

### Namespace + Group 组合

```yaml
spring:
  cloud:
    nacos:
      discovery:
        namespace: dev
        group: ORDER_GROUP    # ⚠️ 进一步分组

# 调用方也必须指定相同 group 才能发现
spring:
  cloud:
    nacos:
      discovery:
        namespace: dev
        group: ORDER_GROUP    # 一致才能发现
```

```yaml
# 不指定 group = 使用 DEFAULT_GROUP
# 不同 group 的服务互相不可见
# 适用于同一环境内按业务线隔离
```

## 🔒 安全配置

```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
```

## 🎯 实战：完整的微服务调用

### 场景

```
用户服务：user-service（端口 8081）
订单服务：order-service（端口 8082）
```

### user-service（服务提供方）

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        return userService.findById(id);
    }
}
```

### order-service（服务消费方）

```java
@FeignClient("user-service")
public interface UserClient {
    @GetMapping("/api/users/{id}")
    User getById(@PathVariable Long id);
}

@Service
public class OrderService {
    @Autowired
    private UserClient userClient;
    
    public Order createOrder(OrderDTO dto) {
        // 通过服务名调用（自动负载均衡）
        User user = userClient.getById(dto.getUserId());
        // 业务逻辑
        return order;
    }
}
```

## 🐛 常见问题

### 问题 1：服务注册不上

```bash
# 检查 Nacos Server 是否启动
curl http://127.0.0.1:8848/nacos/

# 检查网络
ping 127.0.0.1

# 检查配置
spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
spring.application.name=your-service-name
```

### 问题 2：找不到服务

```bash
# 检查服务名是否一致
# 服务提供方：
spring.application.name=user-service

# 服务消费方：
@FeignClient("user-service")  # ⚠️ 必须完全一致
```

### 问题 3：调用超时

```java
// OpenFeign 默认超时 1s
@FeignClient(name = "user-service", url = "...")
public interface UserClient {
    // ...
}

// 配置超时
feign:
  client:
    config:
      default:
        connect-timeout: 5000
        read-timeout: 5000
```

## 🎯 总结

**Nacos 服务发现核心：**
- ✅ 服务自动注册（启动时）
- ✅ 服务自动发现（其他服务调用时）
- ✅ 健康检查 + 故障自动剔除
- ✅ 元数据支持（版本/机房/集群）

**调用方式：**
- ✅ OpenFeign（推荐，声明式）
- ✅ RestTemplate + @LoadBalanced
- ✅ WebClient（响应式）

**生产部署：**
- ✅ Nacos 集群（3 节点）
- ✅ Namespace 隔离环境
- ✅ 安全认证

**下一步：** [⚙️ Nacos 配置中心](/02-overview/nacos-config) — 动态配置 + Namespace 隔离