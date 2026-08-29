---
title: Spring Boot 快速开始
---

# 🚀 Spring Boot 快速开始

> 5 分钟搭建第一个 Spring Boot 应用，理解约定优于配置的设计哲学。

## 🎯 Spring Boot 是什么？

Spring Boot 是 Pivotal 团队基于 Spring 框架开发的**快速脚手架**：

```
传统 Spring：
- 手动写大量 XML 配置
- 手动管理依赖版本
- 手动部署到 Tomcat
- 配置繁琐，启动慢

Spring Boot：
- ✅ 约定优于配置
- ✅ 启动器（Starter）自动管理依赖
- ✅ 内嵌 Tomcat，直接运行
- ✅ 自动配置（Auto-Configuration）
- ✅ 5 分钟第一个应用
```

## 🚀 第一个 Spring Boot 应用

### 方式 1：Spring Initializr（推荐）

```
访问 https://start.spring.io/
或使用 IDEA: File → New → Project → Spring Initializr

填写：
- Project: Maven Project
- Language: Java
- Spring Boot: 3.2.x
- Group: com.example
- Artifact: demo
- Dependencies: Spring Web, Lombok

点击 Generate，下载解压
```

### 方式 2：手动创建

```xml
<!-- pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    
    <!-- 继承 Spring Boot 父 POM -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <!-- Web 启动器：包含 Spring MVC + Tomcat -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <!-- Lombok：简化 Java 代码 -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        
        <!-- 测试 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### 启动类

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication  // 🎯 核心注解
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
        // 启动后访问 http://localhost:8080
    }
}
```

### 第一个 Controller

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController  // @Controller + @ResponseBody
public class HelloController {
    
    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
    
    @GetMapping("/hello/{name}")
    public String helloName(String name) {
        return "Hello, " + name + "!";
    }
}
```

### application.yml

```yaml
# resources/application.yml
server:
  port: 8080
  servlet:
    context-path: /api  # 所有接口前缀

spring:
  application:
    name: demo
```

### 运行

```bash
# IDE 中：右键 DemoApplication → Run

# 命令行：
mvn spring-boot:run

# 或打包后运行：
mvn clean package
java -jar target/demo-1.0.0.jar
```

## 🎯 核心注解

### @SpringBootApplication

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration  // 标识为 Spring Boot 配置
@EnableAutoConfiguration  // 🎯 启用自动配置
@ComponentScan(excludeFilters = { // 扫描包
    @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
    @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
    // ...
}
```

**三个核心注解的组合：**
- ✅ `@SpringBootConfiguration` — 标记为配置类
- ✅ `@EnableAutoConfiguration` — **开启自动配置**（核心）
- ✅ `@ComponentScan` — 扫描包内的组件

### 常用启动器（Starter）

| Starter | 用途 |
|---|---|
| `spring-boot-starter-web` | Spring MVC + Tomcat |
| `spring-boot-starter-data-jpa` | JPA + Hibernate |
| `spring-boot-starter-data-redis` | Redis 集成 |
| `spring-boot-starter-validation` | 参数校验（@Valid） |
| `spring-boot-starter-actuator` | 健康检查 + 监控 |
| `spring-boot-starter-test` | JUnit + Mockito |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-aop` | AOP 面向切面 |

## 🔧 配置文件详解

### application.yml / application.properties

```yaml
# 1. 服务配置
server:
  port: 8080
  servlet:
    context-path: /api
  compression:
    enabled: true
  tomcat:
    threads:
      max: 200

# 2. Spring 配置
spring:
  application:
    name: my-service        # 应用名
  profiles:
    active: dev             # 激活 dev 环境
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
    default-property-inclusion: non_null  # 序列化时忽略 null

# 3. 日志
logging:
  level:
    root: info
    com.example: debug
  pattern:
    console: '%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n'

# 4. 自定义配置
myapp:
  api-key: xxx
  timeout: 30
```

### 多环境配置

```
src/main/resources/
├── application.yml           # 公共配置
├── application-dev.yml       # 开发环境
├── application-test.yml      # 测试环境
└── application-prod.yml      # 生产环境
```

```yaml
# application-dev.yml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db
    username: dev

# application-prod.yml
server:
  port: 80
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/prod_db
    username: app_user
```

## 🎯 @Value 与 @ConfigurationProperties

### @Value（简单值）

```java
@Component
public class AppConfig {
    
    @Value("${myapp.api-key}")
    private String apiKey;
    
    @Value("${myapp.timeout:30}")  // 默认值 30
    private int timeout;
    
    @Value("#{T(java.lang.Math).random() * 100}")
    private double randomNum;
}
```

### @ConfigurationProperties（推荐）

```java
@Data
@Component
@ConfigurationProperties(prefix = "myapp")
public class AppProperties {
    private String apiKey;
    private int timeout = 30;
    private List<String> servers;
    private Map<String, String> headers;
}
```

```yaml
# application.yml
myapp:
  api-key: my-secret-key
  timeout: 60
  servers:
    - http://server1.com
    - http://server2.com
  headers:
    Content-Type: application/json
```

## 📦 打包与部署

### 打包成可执行 JAR

```bash
mvn clean package
# 生成 target/myapp-1.0.0.jar

# 运行
java -jar target/myapp-1.0.0.jar
# 访问 http://localhost:8080
```

### 部署到服务器

```bash
# 上传 JAR
scp target/myapp-1.0.0.jar user@server:/app/

# 服务器上运行
nohup java -jar /app/myapp-1.0.0.jar > /app/logs/app.log 2>&1 &

# 开机自启（systemd）
sudo vim /etc/systemd/system/myapp.service
```

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Spring Boot App
After=network.target

[Service]
Type=simple
User=app
ExecStart=/usr/bin/java -jar /app/myapp-1.0.0.jar
Restart=always
RestartSec=10
Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

## 🎯 总结

**Spring Boot 优势：**
- ✅ 5 分钟第一个应用
- ✅ 约定优于配置
- ✅ 内嵌 Tomcat，java -jar 直接跑
- ✅ 自动管理依赖版本
- ✅ 生产级特性（健康检查、监控）

**核心概念：**
- ✅ `@SpringBootApplication`：启动类注解
- ✅ Starter：依赖管理
- ✅ 自动配置：按需加载
- ✅ 外部化配置：application.yml

**下一步：** [⚙️ 自动配置原理](/01-springboot/auto-config) — 理解 @SpringBootApplication 背后的魔法

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
