---
title: 配置中心
date: 2026-08-15  # date-auto-injected
---
# 配置中心

## 1. 解决的问题

```
微服务配置：
  - 100 个服务 × 多环境（dev/test/staging/prod）= 1000+ 配置文件
  - 改一个配置 = 重启 100 个服务？
  - 配置散落：配置错误 = 全军覆没

配置中心 = 配置的单一事实源
  - 配置集中管理
  - 实时推送（无需重启）
  - 版本控制 + 灰度
  - 权限控制
```

## 2. 主流方案

| 系统 | 特点 |
|------|------|
| **Nacos** | 配置 + 注册中心，国内最常用 |
| **Apollo**（携程） | 配置中心，Java 生态，灰度完善 |
| **Spring Cloud Config** | Spring 生态，Git 后端 |
| **Consul KV** | 多数据中心，Service Mesh 配套 |
| **etcd** | K8s 内置，强一致，但功能简单 |

## 3. Apollo 架构

```
┌─ Portal (管理) ─┐
│  - 改配置       │
└────────┬────────┘
         │ 发布
┌────────▼────────┐
│  Config Service │  ← 推送
└────────┬────────┘
         │ 拉
┌────────▼────────┐
│  Client         │
│  - 长轮询       │
│  - 内存缓存     │
│  - 实时推送     │
└─────────────────┘
```

**特色**：发布审核 + 灰度（按集群 / IP）+ 版本回滚。

## 4. Nacos Config 实战

```yaml
# application.yml
spring:
  cloud:
    nacos:
      config:
        server-addr: 192.168.1.1:8848
        namespace: dev
        file-extension: yaml
        refresh-enabled: true
```

数据 ID 格式：`{spring.application.name}-{spring.profiles.active}.{file-extension}`

```
# user-service-dev.yaml
db:
  url: jdbc:mysql://dev-db:3306/user
  password: dev123

# user-service-prod.yaml
db:
  url: jdbc:mysql://prod-db.cluster:3306/user
  password: ${secret.db_password}
```

## 5. Spring Cloud Config 实战

```yaml
# config-server
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config
          default-label: main
          search-paths: '{application}'
```

```bash
# 仓库结构
config-repo/
  user-service.yml
  user-service-dev.yml
  user-service-prod.yml
```

客户端拉取：`{app}-{profile}.yml`

## 6. 实时推送

```java
@RefreshScope
@RestController
public class UserController {
  @Value("${app.feature.new-algorithm:false}")
  private boolean newAlgorithm;

  @GetMapping("/feature")
  public Map<String, Object> feature() {
    return Map.of("newAlgorithm", newAlgorithm);
  }
}
```

配置变更 → Config Server 通知 → 客户端 `/refresh` 端点 → 重新注入 Bean。

**生产推荐**：用消息队列（Kafka / RabbitMQ）做配置变更广播，避免每个客户端轮询。

## 7. 配置分类

| 类别 | 例子 | 管理方式 |
|------|------|---------|
| 启动配置 | 端口、日志级别 | 配置中心，启动时拉取 |
| 业务配置 | 特性开关 / 限流阈值 | 配置中心，**实时推送** |
| 敏感配置 | 数据库密码、API Key | **不存配置中心**，用 Vault / KMS |
| 环境配置 | host / port / region | K8s ConfigMap（静态） |

## 8. 敏感配置管理

```java
// Spring Cloud + Vault
@Value("${db.password}")  // 从 Vault 拉
private String dbPassword;

// HashiCorp Vault
vault kv put secret/myapp/db password=xxx
vault kv get -field=password secret/myapp/db

// 动态拉取 + 自动轮转
@Scheduled(fixedRate = 30000)
public void refreshSecrets() {
  // 重新拉 Vault
}
```

## 9. 配置中心 vs K8s ConfigMap

| | 配置中心 (Nacos/Apollo) | K8s ConfigMap |
|--|------------------------|----------------|
| 动态推送 | ✅ 实时 | ❌ 重启 Pod |
| 版本管理 | ✅ 完整 | ⚠ 需 Git 管理 |
| 灰度 | ✅ 完整 | ❌ |
| 适用 | 业务配置 | 环境配置 / 启动配置 |

**最佳实践**：
- 启动配置（端口、依赖地址）→ K8s ConfigMap
- 业务配置（feature flag、限流阈值）→ 配置中心
- 敏感配置 → Vault / KMS

## 10. 实战选型

```
Java + Spring 生态   →  Nacos / Apollo
多语言 / 微服务       →  Nacos / Consul
多数据中心          →  Consul KV（多 DC）
多 K8s 集群        →  Nacos Cluster / Consul Federation
简单场景            →  K8s ConfigMap + Reloader
敏感配置            →  Vault / KMS（独立）
```

## 🔗 下一步
- [服务发现](/06-microservice/discovery)
- [API 网关](/06-microservice/gateway)
