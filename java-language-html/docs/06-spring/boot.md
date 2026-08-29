---
title: Spring Boot 自动配置
date: 2026-08-15  # date-auto-injected
---
# Spring Boot
- @SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan
- Auto-configuration: spring.factories → @ConditionalOnClass/@ConditionalOnMissingBean
- application.yml > application.properties > command line args > env vars
- Starters: spring-boot-starter-web, spring-boot-starter-data-jpa, etc.
```java
@SpringBootApplication
public class App {
  public static void main(String[] args) { SpringApplication.run(App.class, args); }
}
```