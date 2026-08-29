---
title: 自动配置原理
date: 2026-08-15  # date-auto-injected
---

# ⚙️ Spring Boot 自动配置原理

> 理解 `@SpringBootApplication` 背后的魔法，是掌握 Spring Boot 的关键。

## 🎯 自动配置是什么？

Spring Boot 根据**类路径上的 jar 包**自动配置 Spring 应用：

```
类路径有 spring-boot-starter-data-jpa
→ 自动配置 DataSource、EntityManagerFactory、TransactionManager

类路径有 spring-boot-starter-web
→ 自动配置 DispatcherServlet、Tomcat

类路径有 spring-boot-starter-data-redis
→ 自动配置 RedisConnectionFactory、RedisTemplate
```

**核心思想：约定优于配置**

## 🔍 源码剖析

### @SpringBootApplication 三件套

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration  // ⭐ 关键
@ComponentScan(...)
public @interface SpringBootApplication {
}
```

### @EnableAutoConfiguration

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage  // 自动配置包
@Import(AutoConfigurationImportSelector.class)  // ⭐ 关键
public @interface EnableAutoConfiguration {
    boolean exclude() default false;
    String[] excludeName() default {};
}
```

### AutoConfigurationImportSelector

```java
public class AutoConfigurationImportSelector 
    implements DeferredImportSelector, BeanClassLoaderAware, ResourceLoaderAware, BeanFactoryAware, EnvironmentAware, Ordered {
    
    @Override
    public String[] selectImports(AnnotationMetadata annotationMetadata) {
        // ⭐ 核心：加载所有自动配置类
        return getCandidateConfigurations();
    }
    
    private String[] getCandidateConfigurations() {
        // 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
        // 这个文件列出了所有自动配置类
        return getAutoConfigurationImportImports();
    }
}
```

## 📁 自动配置类清单

```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports

内容：
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration
... (100+ 个)
```

**Spring Boot 内置 100+ 自动配置类**

## 🔬 实战剖析：DataSourceAutoConfiguration

### 1. 源码

```java
// DataSourceAutoConfiguration.java
@AutoConfiguration
@ConditionalOnClass({DataSource.class, EmbeddedDatabaseType.class})
@EnableConfigurationProperties(DataSourceProperties.class)
@Import(DataSourcePoolMetadataProvidersConfiguration.class)
public class DataSourceAutoConfiguration {
    
    @Configuration
    @ConditionalOnMissingBean(DataSource.class)
    static class EmbeddedDatabaseConfiguration {
        // 内嵌数据库（H2 / Derby）
    }
    
    @Configuration(proxyBeanMethods = false)
    @ConditionalOnMissingBean(DataSource.class)
    static class PooledDataSourceConfiguration {
        
        @Bean
        @ConditionalOnMissingBean(DataSource.class)
        @ConditionalOnProperty(name = "spring.datasource.type")
        public DataSource dataSource(DataSourceProperties properties) {
            return properties.initializeDataSourceBuilder().build();
        }
    }
}
```

### 2. 关键注解

| 注解 | 作用 |
|---|---|
| `@AutoConfiguration` | 标记为自动配置类 |
| `@ConditionalOnClass` | 类路径存在某个类时生效 |
| `@ConditionalOnMissingBean` | 容器中没有指定 Bean 时生效 |
| `@ConditionalOnProperty` | 配置文件中存在指定属性时生效 |
| `@EnableConfigurationProperties` | 启用 @ConfigurationProperties |

## 🔄 自动配置流程

```
启动应用
  ↓
@SpringBootApplication
  ↓ @EnableAutoConfiguration
  ↓ @Import(AutoConfigurationImportSelector.class)
AutoConfigurationImportSelector.selectImports()
  ↓ 读取 META-INF/spring/.../AutoConfiguration.imports
  ↓ 加载所有自动配置类
  ↓
对每个自动配置类执行 @Conditional 注解
  ↓
只有满足条件的配置类才会生效
  ↓
创建对应的 Bean 加入 Spring 容器
```

## 🔍 @Conditional 注解家族

```java
// 类条件
@ConditionalOnClass(DataSource.class)        // 类路径存在
@ConditionalOnMissingClass("com.xxx.Xxx")   // 类路径不存在

// Bean 条件
@ConditionalOnBean(DataSource.class)         // 容器中存在
@ConditionalOnMissingBean(DataSource.class)    // 容器中不存在

// 属性条件
@ConditionalOnProperty(
    name = "spring.datasource.url",           // 属性名
    havingValue = "true",                      // 期望值
    matchIfMissing = false                     // 缺失时是否匹配
)

// 资源条件
@ConditionalOnResource(resources = "classpath:mybatis.xml")

// Web 条件
@ConditionalOnWebApplication
@ConditionalOnNotWebApplication

// SpEL 条件
@ConditionalOnExpression("'${myapp.enabled}' == 'true'")

// Java 版本
@ConditionalOnJava(JavaVersion.ELEVEN)
```

## 🎯 实战：自定义自动配置

### 场景：自动配置一个 HttpClient

```java
// 1. 业务代码
@Data
public class MyHttpClient {
    private String host;
    private int port;
    private int timeout;
    
    public String get(String path) {
        return "GET " + host + ":" + port + path;
    }
}

// 配置属性
@Data
@ConfigurationProperties(prefix = "myapp.http")
public class MyHttpClientProperties {
    private String host = "localhost";
    private int port = 8080;
    private int timeout = 5000;
}

// 2. 自动配置类
@AutoConfiguration
@ConditionalOnClass(MyHttpClient.class)
@EnableConfigurationProperties(MyHttpClientProperties.class)
public class MyHttpClientAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public MyHttpClient myHttpClient(MyHttpClientProperties properties) {
        MyHttpClient client = new MyHttpClient();
        client.setHost(properties.getHost());
        client.setPort(properties.getPort());
        client.setTimeout(properties.getTimeout());
        return client;
    }
}

// 3. 注册文件
// META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
// 添加：
com.example.MyHttpClientAutoConfiguration
```

```yaml
# 用户使用
myapp:
  http:
    host: api.example.com
    port: 443
    timeout: 3000
```

```java
// 业务代码直接注入
@Service
public class MyService {
    @Autowired
    private MyHttpClient httpClient;  // 自动配置注入
    
    public String fetchData() {
        return httpClient.get("/users");
    }
}
```

## 🔧 自定义 Starter

### 项目结构

```
myapp-spring-boot-starter/
├── src/main/java/com/example/autoconfigure/
│   ├── MyService.java                    # 业务类
│   ├── MyServiceProperties.java           # 配置类
│   └── MyServiceAutoConfiguration.java    # 自动配置类
├── src/main/resources/
│   └── META-INF/spring/
│       └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
└── pom.xml
```

### pom.xml

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>myapp-spring-boot-starter</artifactId>
    <version>1.0.0</version>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-autoconfigure</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>
</project>
```

### 自动配置文件

```java
// 1. 业务类
public class MyService {
    public String hello() {
        return "Hello from MyService!";
    }
}

// 2. 配置属性
@Data
@ConfigurationProperties(prefix = "myapp.service")
public class MyServiceProperties {
    private String name = "default";
    private int version = 1;
}

// 3. 自动配置类
@AutoConfiguration
@ConditionalOnClass(MyService.class)
@EnableConfigurationProperties(MyServiceProperties.class)
public class MyServiceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyServiceProperties properties) {
        return new MyService();
    }
}
```

### 注册文件

```
src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports

内容（一行一个）：
com.example.autoconfigure.MyServiceAutoConfiguration
```

## 🔍 查看生效的自动配置

```bash
# 启动时加 debug 参数
java -jar myapp.jar --debug

# 或 application.yml
debug: true
```

输出：

```
============================
CONDITIONS EVALUATION REPORT
============================

Positive matches:
-----------------
   DataSourceAutoConfiguration matched:
      - @ConditionalOnClass found required classes 'javax.sql.DataSource'

   WebMvcAutoConfiguration matched:
      - @ConditionalOnClass found required classes 'org.springframework.web.servlet.DispatcherServlet'

Negative matches:
-----------------
   ActiveMQAutoConfiguration:
      - @ConditionalOnClass did not find required class 'javax.jms.ConnectionFactory'

   ElasticsearchRestClientAutoConfiguration:
      - @ConditionalOnClass did not find required class 'org.elasticsearch.client.RestClient'
```

## 🎯 总结

**自动配置核心：**
- ✅ `@SpringBootApplication` = `@EnableAutoConfiguration` + `@ComponentScan`
- ✅ 自动配置类在 `META-INF/spring/.../AutoConfiguration.imports` 中
- ✅ `@Conditional` 注解决定是否生效
- ✅ 用户配置优先（application.yml）

**自定义 Starter 步骤：**
1. 创建业务类 + Properties
2. 创建 `XxxAutoConfiguration`（用 `@Conditional` 限定条件）
3. 在 `AutoConfiguration.imports` 中注册
4. 其他项目引入 starter 即可自动生效

**关键注解：**
- `@ConditionalOnClass`：类路径存在
- `@ConditionalOnMissingBean`：Bean 不存在
- `@ConditionalOnProperty`：配置存在
- `@EnableConfigurationProperties`：启用 @ConfigurationProperties

**下一步：** [🌐 Web 开发](/01-springboot/web) — REST API、参数校验、统一异常处理

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地

<!-- svg-injected:do-not-edit -->

## 图示：Spring Bean 生命周期

![Spring Bean 生命周期](/spring-ioc-lifecycle.svg)
