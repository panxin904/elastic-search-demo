---
title: Gateway / Sentinel
date: 2026-08-15  # date-auto-injected
---
# Spring Cloud Gateway
- Route: id + uri + predicates + filters
- Predicates: Path, Host, Method, Header, Query, Weight
- Filters: AddRequestHeader, StripPrefix, RequestRateLimiter, CircuitBreaker
- Sentinel: flow control, circuit breaking, hotspot param, system adaptive
```yaml
spring.cloud.gateway.routes:
- id: user-service
  uri: lb://user-service
  predicates: [Path=/api/users/**]
  filters: [StripPrefix=1]
```