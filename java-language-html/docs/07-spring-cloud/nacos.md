---
title: Nacos 注册/配置中心
date: 2026-08-15  # date-auto-injected
---
# Nacos
- Service discovery: CP (Raft) for registry, AP (Distro) for instances
- Config center: namespace/group/dataId, dynamic refresh (@RefreshScope)
```yaml
spring.cloud.nacos.discovery.server-addr: localhost:8848
spring.cloud.nacos.config.server-addr: localhost:8848
```
```java
@RefreshScope @RestController
class ConfigController {
  @Value("${app.version}") String version;
}
```