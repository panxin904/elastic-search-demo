---
title: Spring Boot
---

# Spring Boot

Spring Boot 是 Java Web 开发的事实标准框架，核心价值是**约定大于配置**。

## 核心特性

| 特性 | 说明 |
|---|---|
| 自动配置 | 根据依赖自动配置 Bean，减少 XML/注解配置 |
| 起步依赖 | starter 包一站式引入相关依赖 |
| 内嵌容器 | 内嵌 Tomcat/Jetty/Undertow，jar 包直接运行 |
| Actuator | 生产级监控端点：健康检查、指标、环境信息 |

## 项目结构

```
spring-boot-project/
├── pom.xml                      # Maven 配置
├── src/main/java/
│   └── com.example/
│       ├── Application.java     # 启动类
│       ├── controller/          # Controller 层
│       ├── service/             # Service 层
│       ├── mapper/              # Mapper 层
│       ├── entity/              # 实体
│       ├── config/              # 配置类
│       └── common/              # 公共类
├── src/main/resources/
│   ├── application.yml          # 主配置
│   ├── application-dev.yml      # 开发环境
│   └── application-prod.yml     # 生产环境
└── src/test/java/               # 测试代码
```

## 常用注解

| 注解 | 作用 |
|---|---|
| @SpringBootApplication | 启动类（= @Configuration + @EnableAutoConfiguration + @ComponentScan） |
| @RestController | REST 控制器 |
| @Service | 标记 Service 层 Bean |
| @Repository / @Mapper | 标记持久层 Bean |
| @Configuration | 配置类 |
| @Bean | 声明式创建 Bean |
| @Value | 注入配置值 |
| @ConfigurationProperties | 批量注入配置 |

## 多环境配置

```yaml
# application.yml
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # 环境变量切换

# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db

# application-prod.yml
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/prod_db
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="spring-boot" :height="400" />
