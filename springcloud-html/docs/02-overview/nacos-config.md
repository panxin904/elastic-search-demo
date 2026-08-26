---
title: Nacos 配置中心
---

# ⚙️ Nacos 配置中心

> Nacos 不只是服务发现，还是**配置中心**。配置变更可**实时推送**给应用，无需重启。

## 🎯 为什么用配置中心？

```
传统方式：
- 配置写在 application.yml
- 改配置要重新打包 + 部署
- 多环境配置分散在多处

配置中心：
- ✅ 集中管理（Web 控制台）
- ✅ 实时推送（@RefreshScope）
- ✅ 环境隔离（Namespace）
- ✅ 版本管理（历史版本）
- ✅ 灰度发布（部分实例生效）
```

## 🚀 快速开始

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

### 2. 配置 Nacos 地址

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml          # 配置格式（properties / yaml / json）
        refresh-enabled: true         # 开启自动刷新
        # 命名空间（隔离环境）
        namespace: public
        # 分组
        group: DEFAULT_GROUP
```

### 3. 在 Nacos 控制台添加配置

```
Data ID: order-service.yaml
Group: DEFAULT_GROUP
配置格式: YAML
配置内容:
  server:
    port: 8082
  myapp:
    timeout: 30
```

### 4. 注入配置

```java
@RestController
public class DemoController {
    
    // 简单值
    @Value("${myapp.timeout:10}")  // 默认值 10
    private int timeout;
    
    // 对象配置
    @Autowired
    private MyAppProperties properties;
}
```

## 📋 版本配置方式对比

> ⚠️ **重要**：Spring Boot 3.x / Spring Cloud Alibaba 2023.x **不再默认使用 bootstrap.yml**，改为 `spring.config.import`。如果仍在用 Spring Boot 2.x / 2021 版本，则需使用 bootstrap.yml。

### 方式一：新版推荐（Spring Boot 3.x / 2023.x+）

```yaml
# application.yml（无需 bootstrap.yml）
spring:
  application:
    name: order-service
  config:
    import:
      - nacos:order-service.yaml?group=DEFAULT_GROUP&refreshEnabled=true
      - nacos:common.yaml?group=COMMON_GROUP&refreshEnabled=true
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        namespace: public
```

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
<!-- 新版不需要 spring-cloud-starter-bootstrap -->
```

### 方式二：2021 版（Spring Boot 2.x / 2021.x）

需额外引入 `spring-cloud-starter-bootstrap` 并创建 `bootstrap.yml`：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bootstrap</artifactId>
</dependency>
```

```yaml
# bootstrap.yml（⚠️ 配置中心的地址必须写在这里）
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        namespace: public
        group: DEFAULT_GROUP
        refresh-enabled: true
        # 扩展配置
        extension-configs:
          - data-id: common.yaml
            group: COMMON_GROUP
            refresh: true
```

```yaml
# application.yml（业务配置，bootstap 之后加载）
spring:
  profiles:
    active: dev
# 业务配置都在 Nacos 上，本地只配 profile
```

### 核心区别

| 维度 | 新版（2023.x+ / Spring Boot 3.x） | 2021 版（Spring Boot 2.x） |
|------|-----------------------------------|---------------------------|
| **配置文件** | `application.yml` | `bootstrap.yml` + `application.yml` |
| **加载时机** | `spring.config.import` 阶段 | Bootstrap Context 初始化阶段 |
| **额外依赖** | 不需要 | `spring-cloud-starter-bootstrap` |
| **配置方式** | `nacos:dataId?group=xxx` URI 方式 | `spring.cloud.nacos.config.*` 命名空间方式 |
| **优先级** | import 顺序决定 | bootstrap 优先于 application |
| **兼容性** | Spring Boot 3.x / Spring Cloud 2023.x+ | Spring Boot 2.x / 2021.x |

### ⚠️ 常见错误：新版用 bootstrap.yml

```yaml
# ❌ 新版不需要 bootstrap.yml！
# spring.cloud.bootstrap.enabled=true 已废弃
# 即使强制开启也会 Warning

# ✅ 新版配置
spring:
  config:
    import: nacos:order-service.yaml
```

## 🔄 动态刷新

### @RefreshScope

```java
@RestController
@RefreshScope  // ⚠️ 配置变更时重新创建 Bean
public class DemoController {
    
    @Value("${myapp.timeout:10}")
    private int timeout;  // 改 Nacos 配置后，访问接口会得到新值
}
```

### 监听配置变更

```java
@Component
public class ConfigListener {
    
    @NacosConfigListener(dataId = "order-service.yaml")
    public void onConfigChange(String newContent) {
        log.info("配置变更: {}", newContent);
        // 执行业务逻辑（重新初始化连接池等）
    }
}
```

### 编程式获取配置

```java
@Service
public class DynamicConfigService {
    
    @Autowired
    private NacosConfigManager nacosConfigManager;
    
    public String getConfig(String dataId) {
        return nacosConfigManager.getConfigService()
            .getConfig(dataId, "DEFAULT_GROUP", 5000);
    }
}
```

## 🌐 Namespace 多环境隔离

```
命名空间设计：
- public：所有环境共享
- dev：开发环境
- test：测试环境
- prod：生产环境
```

### Nacos 控制台创建 Namespace

```
登录 Nacos 控制台 → 命名空间 → 新建命名空间

┌────────────────────────────────────────┐
│  命名空间列表                           │
├────────────────────────────────────────┤
│  名称      ID                          │
│  public    (空)     ← 默认，无需创建    │
│  dev       dev-xxxx                    │
│  test      test-yyyy                   │
│  prod      prod-zzzz                   │
└────────────────────────────────────────┘
```

创建后会分配一个 Namespace ID（UUID），配置时填入。

### 新版配置（Spring Boot 3.x / 2023.x+）

```yaml
# application-dev.yml
spring:
  config:
    import:
      - nacos:order-service-dev.yaml?group=DEFAULT_GROUP&refreshEnabled=true
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        namespace: dev      # ⚠️ 对应 Nacos 控制台的 Namespace ID
        # file-extension 不需要 — import 已指定完整 dataId
```

```yaml
# application-prod.yml
spring:
  config:
    import:
      - nacos:order-service-prod.yaml?group=DEFAULT_GROUP&refreshEnabled=true
  cloud:
    nacos:
      config:
        server-addr: 192.168.1.10:8848
        namespace: prod     # ⚠️ 生产 Namespace
```

```yaml
# Nacos 控制台 -> 配置列表（按 Namespace 切换）
#
# dev 命名空间下：
#   Data ID: order-service-dev.yaml
#   配置：
#     server:
#       port: 8082
#     myapp:
#       timeout: 30
#       db:
#         url: jdbc:mysql://dev-db:3306/order
#
# prod 命名空间下：
#   Data ID: order-service-prod.yaml
#   配置：
#     server:
#       port: 8082
#     myapp:
#       timeout: 60
#       db:
#         url: jdbc:mysql://prod-db:3306/order
```

### 2021 版配置（Spring Boot 2.x）

```yaml
# bootstrap-dev.yml（dev 环境）
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        namespace: dev        # ⚠️ Namespace ID
        group: DEFAULT_GROUP
        refresh-enabled: true
        extension-configs:
          - data-id: common.yaml
            group: COMMON_GROUP
            refresh: true
```

```yaml
# bootstrap-prod.yml（prod 环境）
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 192.168.1.10:8848
        file-extension: yaml
        namespace: prod       # ⚠️ 对应 Nacos 控制台的 prod Namespace ID
        group: DEFAULT_GROUP
        refresh-enabled: true
```

```yaml
# application.yml（公共配置，bootstrap 之后加载）
spring:
  profiles:
    active: ${PROFILE:dev}  # 环境变量控制

# 启动时选择环境：
# java -jar order-service.jar --spring.profiles.active=dev
```

### 环境隔离最佳实践

```
目录结构推荐：
src/main/resources/
├── application.yml                # 公共配置（日志级别等）
├── application-dev.yml            # 开发环境本地覆盖
├── application-prod.yml           # 生产环境本地覆盖
├── bootstrap.yml（2021 版）        # Nacos 连接配置
├── bootstrap-dev.yml（2021 版）    # 开发环境 bootstrap
└── bootstrap-prod.yml（2021 版）   # 生产环境 bootstrap
```

```yaml
# application.yml — 启动时自动加载对应 profile
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}

# 推荐用法：启动脚本指定环境
# 开发：java -jar app.jar --spring.profiles.active=dev
# 测试：java -jar app.jar --spring.profiles.active=test
# 生产：java -jar app.jar --spring.profiles.active=prod
```

### Namespace 与 Group 组合策略

```
方案一：Namespace 隔离环境，Group 隔离业务线
├── Namespace: dev
│   ├── Group: ORDER_GROUP
│   │   ├── order-service.yaml
│   │   └── order-service-dev.yaml
│   └── Group: USER_GROUP
│       ├── user-service.yaml
│       └── user-service-dev.yaml
├── Namespace: prod
│   ├── Group: ORDER_GROUP
│   │   └── order-service.yaml
│   └── Group: USER_GROUP
│       └── user-service.yaml

方案二：Namespace 隔离业务线，Group 隔离环境（不推荐）
⚠️ 会导致 Nacos 控制台反复切换 Namespace

推荐方案一：Namespace = 环境，Group = 业务线
```

## 📁 配置加载规则

```
${spring.application.name}-${profile}.${file-extension}

示例：order-service-dev.yaml
```

### 加载优先级

```
1. order-service.yaml        (公共)
2. order-service-dev.yaml    (环境)
3. application.yaml           (本地)
4. application-dev.yaml       (本地环境)

# 优先级：环境 > 公共 > 本地环境 > 本地公共
```

## 🔧 @ConfigurationProperties

```java
@Data
@Component
@ConfigurationProperties(prefix = "myapp")
@RefreshScope
public class MyAppProperties {
    private String apiKey;
    private int timeout = 30;
    private List<String> servers;
    private Map<String, String> headers;
}
```

```yaml
# Nacos 配置
myapp:
  api-key: my-secret
  timeout: 60
  servers:
    - server1
    - server2
  headers:
    Content-Type: application/json
```

## 📦 共享配置（Data Extension）

```yaml
spring:
  cloud:
    nacos:
      config:
        # 扩展配置（多个 dataId）
        extension-configs:
          - data-id: common.yaml
            group: COMMON_GROUP
            refresh: true
          - data-id: redis.yaml
            group: DEFAULT_GROUP
            refresh: true
```

## 🔒 敏感配置加密

```java
// 使用 Nacos 加密插件
spring:
  cloud:
    nacos:
      config:
        # 加密方式
        encryption:
          type: nacos-aes
          key: my-secret-key
```

```yaml
# Nacos 中的加密配置
# password: ENC(base64-encoded-encrypted-value)
```

## 🛠️ 实战：完整的配置中心方案

### 场景

```
Nacos 配置：
- common.yaml     # 公共配置（DB / Redis / MQ 地址）
- order-service.yaml   # 订单服务配置
- order-service-dev.yaml   # 开发环境
```

### common.yaml（Nacos 控制台）

```yaml
spring:
  datasource:
    url: jdbc:mysql://mysql-host:3306/order_db
    username: app
    password: ${MYSQL_PASSWORD}  # 引用环境变量
  
  redis:
    host: redis-host
    port: 6379
    password: ${REDIS_PASSWORD}
  
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
```

### order-service.yaml（Nacos 控制台）

```yaml
myapp:
  order:
    timeout: 30
    max-retry: 3
    kafka:
      topic: order-events
```

### application.yml（本地）

```yaml
spring:
  application:
    name: order-service
  profiles:
    active: dev
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        extension-configs:
          - data-id: common.yaml
            group: COMMON_GROUP
            refresh: true
```

## 🐛 常见问题

### 问题 1：配置不生效

```
1. 检查 Data ID 是否正确
   = ${spring.application.name}.${file-extension}
   = order-service.yaml

2. 检查 Group
   = DEFAULT_GROUP（默认）

3. 检查 Namespace
   = public（默认）

4. 检查配置格式
   = YAML 时 file-extension: yaml
   = Properties 时 file-extension: properties
```

### 问题 2：@Value 拿不到值

```java
// ⚠️ 类没有加 @RefreshScope
@RestController  // 缺 @RefreshScope
public class DemoController {
    @Value("${myapp.timeout}")
    private int timeout;  // 启动时拿一次，配置改了不更新
}

// ✅ 加上 @RefreshScope
@RestController
@RefreshScope
public class DemoController { ... }
```

### 问题 3：配置变更不生效

```java
// 检查 1：refresh-enabled
spring.cloud.nacos.config.refresh-enabled=true

// 检查 2：@RefreshScope
@RestController
@RefreshScope
public class DemoController { ... }

// 检查 3：Nacos 控制台配置格式正确
```

## 🎯 总结

**Nacos 配置中心核心：**
- ✅ 集中管理（Web 控制台）
- ✅ 实时推送（@RefreshScope）
- ✅ Namespace 多环境隔离
- ✅ 版本管理 + 灰度发布
- ✅ 配置加密

**加载规则：**
```
order-service.yaml（公共）
  + order-service-dev.yaml（dev 环境）
  + application.yaml（本地公共）
  + application-dev.yaml（本地环境）
```

**最佳实践：**
- ✅ 公共配置（DB / Redis）放 Nacos
- ✅ 环境配置（dev / test / prod）用 Namespace 隔离
- ✅ 敏感配置加密存储
- ✅ 用 `@ConfigurationProperties` 绑定
- ✅ 关键 Bean 加 `@RefreshScope`

**下一步：** [🚪 Gateway 网关](/03-gateway/basic) — 微服务统一入口

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
