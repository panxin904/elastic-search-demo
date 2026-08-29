---
title: Spring Cloud Alibaba 总览
date: 2026-08-15  # date-auto-injected
---

# 📚 Spring Cloud Alibaba 总览

> Spring Cloud Alibaba 是阿里开源的**一站式微服务解决方案**，是对 Spring Cloud 标准实现的**国产化增强**。

## 🎯 核心组件

| 组件 | 功能 | 替代 |
|---|---|---|
| **Nacos** | 服务发现 + 配置中心 | Eureka + Config + Bus |
| **Sentinel** | 流量控制 + 熔断降级 | Hystrix + Turbine |
| **Seata** | 分布式事务 | - |
| **Gateway** | API 网关 | Zuul |
| **OpenFeign** | 声明式 HTTP 客户端 | Feign |
| **LoadBalancer** | 客户端负载均衡 | Ribbon |
| **RocketMQ** | 消息队列 | RabbitMQ |
| **OSS** | 对象存储 | - |

## 🔄 版本对应

| Spring Cloud Alibaba | Spring Cloud | Spring Boot | Nacos | Seata |
|---|---|---|---|---|
| 2023.0.1.x | 2023.0.1 | 3.2.x | 2.3.x | 1.7.x |
| 2022.0.0.x | 2022.0.0 | 3.0.x | 2.2.x | 1.6.x |
| 2021.0.5.x | 2021.0.5 | 2.7.x | 2.1.x | 1.5.x |

**查看版本：** https://github.com/alibaba/spring-cloud-alibaba/wiki/版本说明

## 🏗️ 微服务架构

```
┌──────────────────────────────────────────┐
│           Client (Web / Mobile)            │
└─────────────┬────────────────────────────┘
              │
       ┌──────▼──────┐
       │  Gateway    │ ← 路由 / 限流 / 鉴权
       └──────┬──────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌──────┐  ┌──────┐  ┌──────┐
│订单服务│ │库存服务│ │账户服务│  ← 业务微服务
│MySQL  │ │MySQL  │ │MySQL  │
└──────┘  └──────┘  └──────┘
    │         │         │
    └─────────┴─────────┘
              │
       ┌──────▼──────┐
       │   Nacos     │ ← 服务发现 + 配置中心
       └────────────┘
```

## 🚀 快速搭建

### 1. 父 POM

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<properties>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.1.0</spring-cloud-alibaba.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-alibaba-dependencies</artifactId>
            <version>${spring-cloud-alibaba.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 2. 启动 Nacos Server

```bash
# 下载 Nacos Server
wget https://github.com/alibaba/nacos/releases/download/2.3.2/nacos-server-2.3.2.tar.gz
tar -xzf nacos-server-2.3.2.tar.gz
cd nacos/bin

# 单机模式启动
./startup.sh -m standalone

# 集群模式（生产）
./startup.sh -m cluster

# 访问控制台
# http://localhost:8848/nacos
# 默认账号 nacos / nacos
```

### 3. 微服务接入

```xml
<dependencies>
    <!-- Nacos 服务发现 -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
    
    <!-- Nacos 配置中心 -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
    </dependency>
    
    <!-- OpenFeign -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>
</dependencies>
```

```yaml
# application.yml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: public
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        refresh-enabled: true
```

```java
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class OrderApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}
```

## 🎯 核心概念

### 服务发现

```
服务启动 → 自动注册到 Nacos
其他服务调用 → 从 Nacos 拉取实例列表
服务健康检查 → 定期心跳，异常自动剔除
```

### 配置中心

```
应用启动 → 从 Nacos 拉取配置
配置变更 → 通过 @RefreshScope 实时刷新
多环境隔离 → namespace + group
```

### 负载均衡

```
多个实例 → Ribbon / LoadBalancer 自动选择
策略：轮询 / 随机 / 一致性 Hash / 自定义
```

## 🔧 常用 starter

| Starter | 作用 |
|---|---|
| `spring-cloud-starter-alibaba-nacos-discovery` | 服务发现 |
| `spring-cloud-starter-alibaba-nacos-config` | 配置中心 |
| `spring-cloud-starter-alibaba-sentinel` | 流量控制 |
| `spring-cloud-starter-alibaba-seata` | 分布式事务 |
| `spring-cloud-starter-alibaba-oss` | 对象存储 |
| `spring-cloud-starter-openfeign` | RPC 调用 |
| `spring-cloud-starter-loadbalancer` | 负载均衡 |
| `spring-cloud-starter-gateway` | API 网关 |

## 🎯 总结

**Spring Cloud Alibaba 优势：**
- ✅ 国产开源，中文文档完善
- ✅ 与 Spring Cloud 完美兼容
- ✅ 组件丰富（Nacos/Sentinel/Seata 一站式）
- ✅ 阿里大规模生产验证

**核心组件：**
- ✅ **Nacos**：服务发现 + 配置（替代 Eureka + Config）
- ✅ **Sentinel**：流控 + 熔断（替代 Hystrix）
- ✅ **Seata**：分布式事务
- ✅ **Gateway**：统一网关

**下一步：** [🌐 Nacos 服务发现](/02-overview/nacos-discovery) — 替代 Eureka 的核心组件