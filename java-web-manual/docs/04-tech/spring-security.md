---
title: Spring Security
---

# Spring Security

Spring Security 提供认证（你是谁）和授权（你能做什么）功能。

## 核心概念

| 概念 | 说明 |
|---|---|
| Authentication | 认证：验证用户身份 |
| Authorization | 授权：验证用户权限 |
| Principal | 当前登录用户 |
| GrantedAuthority | 权限/角色 |
| SecurityContext | 安全上下文（存 Authentication） |
| FilterChain | 过滤器链，Security 的核心 |

## JWT 认证流程

```
客户端                      服务端
  │                          │
  │──── POST /login ────────→│ 验证用户名密码
  │                          │ 生成 JWT Token
  │←──── 返回 Token ────────│
  │                          │
  │──── GET /api/users ─────→│
  │  Header: Bearer <token>  │ 解析 Token → 获取用户信息 → 鉴权
  │←──── 返回数据 ──────────│
```

## 配置示例

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests()
                .requestMatchers("/api/login", "/api/register").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

## 方法级权限

```java
@PreAuthorize("hasRole('ADMIN')")
@DeleteMapping("/users/{id}")
public Result delete(@PathVariable Long id) {}

@PreAuthorize("hasPermission(#orderId, 'ORDER', 'READ')")
@GetMapping("/orders/{orderId}")
public Result getOrder(@PathVariable Long orderId) {}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="spring-security" :height="400" />
