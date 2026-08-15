---
title: 分布式 Session
---

# 👤 分布式 Session

> 在**集群部署**的 Web 应用中，多台服务器需要**共享 Session**。Redis 是实现分布式 Session 的经典方案。

## 🎯 为什么需要分布式 Session？

```
单机应用：
  用户登录 → Session 存在 Tomcat 内存
  后续请求 → 同 Tomcat 处理 → Session 有效 ✅

集群应用（问题）：
  用户登录 → 请求到 Tomcat A → Session 存 Tomcat A
  后续请求 → 负载均衡到 Tomcat B → Session 不在 B → 重新登录 ❌
```

**解决方案**：把 Session 存到外部共享存储（Redis），所有 Tomcat 共享。

## 🔧 Spring Session + Redis

> Spring Session 是 Spring 提供的 Session 统一抽象层，自动把 Session 存到 Redis。

### 引入依赖

```xml
<dependency>
    <groupId>org.springframework.session</groupId>
    <artifactId>spring-session-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

### 启用 Session

```java
@SpringBootApplication
@EnableRedisHttpSession    // 启用 Redis Session
public class Application { }
```

### 配置

```yaml
# application.yml
spring:
  session:
    store-type: redis
    timeout: 30m             # Session 过期时间
    redis:
      namespace: myapp:session    # Redis key 前缀
  redis:
    host: localhost
    port: 6379
    password: password
```

### 使用 Session（与 Servlet API 一致）

```java
@RestController
public class UserController {
    
    // 1. 登录存 Session
    @PostMapping("/login")
    public String login(@RequestBody UserDTO dto, HttpSession session) {
        User user = userService.login(dto);
        
        // 存 Session
        session.setAttribute("user", user);
        session.setAttribute("loginTime", Instant.now());
        
        return "OK";
    }
    
    // 2. 读取 Session
    @GetMapping("/profile")
    public User profile(HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            throw new BusinessException("未登录");
        }
        return user;
    }
    
    // 3. 注销
    @PostMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();  // 销毁 Session
        return "OK";
    }
}
```

## 📂 Session 存储结构

```
Redis 中的 Session：
  Key:    spring:session:sessions:<session-id>
  Value:  Hash 结构
          {
            "user": "{...}",         // session attribute
            "loginTime": "..."
            ...
          }
  TTL:    30 分钟（自动过期）

辅助 Key：
  spring:session:sessions:expires:<session-id>
    用于 Redis 过期监听
  spring:session:index:org.springframework.session.FindByIndexNameSessionRepository.PRINCIPAL_NAME_INDEX_NAME:<username>
    用于按用户名查找 Session
```

## ⚙️ Session 序列化

> Spring Session 默认使用 **JDK 序列化**（有反序列化漏洞风险）。生产推荐改用 JSON。

```java
@Configuration
public class SessionConfig {
    
    @Bean
    public RedisSerializer<Object> springSessionDefaultRedisSerializer() {
        // 使用 JSON 序列化（推荐）
        return new GenericJackson2JsonRedisSerializer();
    }
}
```

## 🔄 Session 过期与续期

```yaml
# Session 过期时间
spring.session.timeout=30m          # 30 分钟

# Session 失效策略
spring.session.redis.flush-mode=on_save    # 保存时刷新（默认）
spring.session.redis.flush-mode=immediate # 立即刷新

# Cookie 配置
server.servlet.session.cookie.name=SESSION
server.servlet.session.cookie.http-only=true
server.servlet.session.cookie.secure=true
server.servlet.session.cookie.max-age=1800  # 30 分钟
```

```java
// 手动续期
session.setMaxInactiveInterval(1800);   // 30 分钟

// 监听 Session 销毁事件
@Component
public class SessionListener implements ApplicationListener<SessionDestroyedEvent> {
    
    @Override
    public void onApplicationEvent(SessionDestroyedEvent event) {
        String sessionId = event.getId();
        // 清理关联数据
        userService.logout(sessionId);
    }
}
```

## 🌐 多应用共享 Session（同域名）

```
场景：
  www.example.com 主应用
  api.example.com API 服务
  admin.example.com 管理后台

配置：Cookie 路径设置为根域名
server.servlet.session.cookie.domain=.example.com
```

## 🛠️ 实战：分布式 Session + Redis Cluster

```yaml
spring:
  session:
    store-type: redis
    timeout: 30m
    redis:
      namespace: myapp:session
      # Cluster 配置（与 Spring Data Redis 共享）
  redis:
    cluster:
      nodes:
        - 192.168.1.10:7001
        - 192.168.1.10:7002
        - 192.168.1.10:7003
    lettuce:
      pool:
        max-active: 50
```

## 🔐 安全最佳实践

```yaml
# 1. Cookie 安全
server.servlet.session.cookie.http-only=true    # 防 XSS
server.servlet.session.cookie.secure=true       # HTTPS only
server.servlet.session.cookie.same-site=lax     # 防 CSRF

# 2. Session ID 定期更新（防固定会话攻击）
http.session.change-session-id-on-login=true

# 3. Session 过期时间不能过长
spring.session.timeout=30m    # 业务可根据需要调整

# 4. 多设备登录限制
http.session.maximum-sessions=1
http.session.maximum-sessions=1;USER
```

## 🛠️ 实战：单点登录（SSO）

> **多个子系统共享同一个登录态**，用户登录一次即可访问所有子系统。

```java
// 1. SSO 认证中心
@RestController
public class SsoController {
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    // 生成全局 Token
    @PostMapping("/sso/login")
    public Result login(@RequestBody LoginDTO dto) {
        User user = userService.login(dto);
        
        // 生成全局 Token（UUID）
        String token = UUID.randomUUID().toString();
        
        // Token 存 Redis（30 分钟过期）
        redisTemplate.opsForValue().set("sso:token:" + token, user.getId(), 30, TimeUnit.MINUTES);
        
        // 同时为每个子系统生成 Session
        // 或者通过 Cookie + 共享 Token 实现
        
        return Result.ok(token);
    }
    
    // 验证 Token
    @GetMapping("/sso/verify")
    public Result verify(@RequestParam String token) {
        String userId = redisTemplate.opsForValue().get("sso:token:" + token);
        if (userId == null) {
            return Result.fail("Token invalid");
        }
        // 续期
        redisTemplate.expire("sso:token:" + token, 30, TimeUnit.MINUTES);
        return Result.ok(userId);
    }
}
```

## 📊 传统方案 vs Spring Session

| 维度 | 传统 Session 复制 | Tomcat + Redis 共享 | Spring Session |
|------|-------------------|---------------------|----------------|
| 实现复杂度 | 中 | 中 | 低 |
| 网络开销 | 高（全量复制） | 低（仅 Redis） | 低 |
| 存储 | 各 Tomcat 内存 | Redis | Redis |
| 性能 | 差 | 好 | 好 |
| 跨容器 | ❌ | ✅ | ✅ |
| 多语言支持 | ⚠️ | ⚠️ | ⚠️ |
| 推荐 | ❌ | ✅ | ✅（推荐） |

## ⚠️ 常见问题

### 问题 1：Session 丢失

```
现象：登录后刷新页面要求重新登录
原因：
  1. Redis 连接中断
  2. Session 过期时间过短
  3. Cookie 路径不匹配
解决：
  1. 监控 Redis 健康
  2. 调大过期时间
  3. 统一 Cookie 配置
```

### 问题 2：Session 不能序列化

```
现象：存对象到 Session 报错
原因：JDK 序列化要求对象实现 Serializable
解决：
  1. 实现 Serializable 接口
  2. 改用 JSON 序列化
```

### 问题 3：跨域 Session 失效

```
现象：跨子域名 session 失效
原因：Cookie 作用域限制
解决：设置 Cookie domain=.example.com
```

## 🎯 总结

**分布式 Session 核心要点**：
- ✅ Spring Session + Redis 集群
- ✅ JSON 序列化（避免 JDK 反序列化漏洞）
- ✅ Cookie 配置：HttpOnly + Secure + SameSite
- ✅ Session 续期 + 监听销毁事件
- ⚠️ 跨域需配置 Cookie domain

**下一步：** [🆔 全局唯一 ID](/06-practice/global-id) — 分布式 ID 生成方案
