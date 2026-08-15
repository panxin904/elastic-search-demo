---
title: OAuth2 + JWT 实战
---

# 🔑 OAuth2 + JWT 实战

> OAuth2 + JWT 是**前后端分离 + 微服务**最主流的认证授权方案。本章从协议到代码完整实现。

## 🎯 OAuth2 四种模式

| 模式 | 适用 | 流程 |
|---|---|---|
| **授权码模式** | **最常用**（第三方登录） | 用户 → 授权服务器 → 回调 code → 用 code 换 token |
| 密码模式 | **自有应用**（推荐内部用） | 用户名密码直接换 token |
| 简化模式 | 纯前端 SPA | 直接返回 token（不安全，不推荐） |
| 客户端模式 | 服务对服务 | 客户端 ID + Secret 换 token |

## 🚀 密码模式（最简单）

### 后端实现

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

```yaml
# 资源服务器配置（验证 Token）
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          # JWT 签名密钥（HMAC SHA-256）
          # 生产环境用 RSA 公钥（jwk-set-uri）
          # 临时用对称密钥
          # ⚠️ 密钥必须 ≥ 256 bit
```

```java
@Configuration
@EnableWebSecurity
public class ResourceServerConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .build();
    }
    
    // HMAC SHA-256 解码器
    @Bean
    public JwtDecoder jwtDecoder() {
        SecretKeySpec key = new SecretKeySpec(
            "my-secret-key-my-secret-key-my-secret-key".getBytes(),
            "HmacSHA256"
        );
        return NimbusJwtDecoder.withSecretKey(key).macAlgorithm(MacAlgorithm.HS256).build();
    }
}
```

### 颁发 Token（认证服务）

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @PostMapping("/login")
    public Result<Map> login(@RequestBody LoginDTO dto) {
        // 1. 验证用户
        User user = userService.findByUsername(dto.getUsername());
        if (user == null || !passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            return Result.error(401, "用户名或密码错误");
        }
        
        // 2. 生成 JWT
        String token = Jwts.builder()
            .setSubject(String.valueOf(user.getId()))
            .claim("username", user.getUsername())
            .claim("role", user.getRole())
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + 3600 * 1000))
            .signWith(SignatureAlgorithm.HS256, "my-secret-key-my-secret-key-my-secret-key")
            .compact();
        
        return Result.success(Map.of(
            "token", token,
            "expiresIn", 3600
        ));
    }
}
```

### 前端使用

```javascript
// 1. 登录获取 token
const res = await axios.post('/api/auth/login', {
    username: 'admin',
    password: 'admin123'
});
const token = res.data.data.token;

// 2. 存储 token
localStorage.setItem('token', token);

// 3. 每次请求带 token
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 4. 调用 API
const userInfo = await axios.get('/api/users/me');
```

## 🔄 Refresh Token 机制

Access Token 有效期短（如 30 分钟），过期后用 Refresh Token 换新 Access Token。

### 后端

```java
@Data
public class TokenInfo {
    private String accessToken;   // 30 分钟过期
    private String refreshToken;  // 7 天过期
    private long expiresIn;
    private String tokenType = "Bearer";
}
```

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @PostMapping("/login")
    public Result<TokenInfo> login(@RequestBody LoginDTO dto) {
        // ... 验证用户 ...
        
        return Result.success(new TokenInfo(
            generateAccessToken(user),
            generateRefreshToken(user),
            3600
        ));
    }
    
    @PostMapping("/refresh")
    public Result<TokenInfo> refresh(@RequestParam String refreshToken) {
        try {
            Claims claims = parseRefreshToken(refreshToken);
            Long userId = Long.parseLong(claims.getSubject());
            User user = userService.findById(userId);
            
            return Result.success(new TokenInfo(
                generateAccessToken(user),
                refreshToken,  // refresh token 可继续用
                3600
            ));
        } catch (Exception e) {
            return Result.error(401, "refresh token 无效");
        }
    }
}
```

### 前端

```javascript
// axios 拦截器：自动刷新 token
axios.interceptors.response.use(
    response => response,
    async error => {
        if (error.response?.status === 401 && 
            !error.config._retry &&
            localStorage.getItem('refreshToken')) {
            
            // 用 refresh token 换新 access token
            const res = await axios.post('/api/auth/refresh', null, {
                params: { refreshToken: localStorage.getItem('refreshToken') }
            });
            localStorage.setItem('token', res.data.data.accessToken);
            
            // 重试原请求
            error.config._retry = true;
            error.config.headers.Authorization = `Bearer ${res.data.data.accessToken}`;
            return axios.request(error.config);
        }
        return Promise.reject(error);
    }
);
```

## 🔐 Gateway 统一鉴权

```yaml
# Gateway 的 application.yml
spring:
  cloud:
    gateway:
      default-filters:
        - TokenRelay=   # 转发 Authorization 头
      routes:
        - id: api_route
          uri: lb://order-service
          predicates:
            - Path=/api/**
```

```java
// 自定义 JWT 验证 GlobalFilter
@Component
public class JwtGlobalFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();
        
        // 1. 公开路径（不需要 Token）
        if (path.startsWith("/api/auth/login") || path.startsWith("/api/public/")) {
            return chain.filter(exchange);
        }
        
        // 2. 检查 Token
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            return unauthorized(exchange, "缺少 Token");
        }
        
        // 3. 验证 Token
        try {
            Claims claims = Jwts.parser()
                .setSigningKey("my-secret-key-my-secret-key-my-secret-key")
                .parseClaimsJws(token.substring(7))
                .getBody();
            
            // 4. 传递用户信息到下游
            ServerHttpRequest newReq = exchange.getRequest().mutate()
                .header("X-User-Id", claims.getSubject())
                .header("X-User-Role", claims.get("role").toString())
                .build();
            return chain.filter(exchange.mutate().request(newReq).build());
        } catch (Exception e) {
            return unauthorized(exchange, "Token 无效");
        }
    }
    
    @Override
    public int getOrder() { return -100; }
}
```

## 🔑 JWT 安全最佳实践

### 1. 密钥管理

```yaml
# ❌ 不要硬编码
signWith(SignatureAlgorithm.HS256, "my-secret-key")

# ✅ 用配置
jwt:
  secret: ${JWT_SECRET:default-dev-secret-min-256-bits-long!!}
  expire: 3600
```

```java
@Value("${jwt.secret}")
private String secret;
```

### 2. HTTPS 传输

```yaml
# 生产环境必须 HTTPS
# Token 在 HTTP 明文传输 = 裸奔
server:
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: xxx
    key-store-type: PKCS12
    key-alias: myapp
```

### 3. Token 黑名单

```java
// 用户登出时，把 Token 加入黑名单（Redis）
@PostMapping("/logout")
public Result<Void> logout(@RequestHeader("Authorization") String token) {
    String jti = JwtUtil.parseJti(token);  // JWT ID
    long ttl = JwtUtil.getExpireTime(token) - System.currentTimeMillis();
    redisTemplate.opsForValue().set(
        "jwt:blacklist:" + jti, "1", Duration.ofMillis(ttl)
    );
    return Result.success();
}

// 验证时检查黑名单
public Claims parse(String token) {
    String jti = Jwts.parser().parseClaimsJws(token).getBody().getId();
    if (redisTemplate.hasKey("jwt:blacklist:" + jti)) {
        throw new RuntimeException("Token 已失效");
    }
    return Jwts.parser().parseClaimsJws(token).getBody();
}
```

### 4. 短有效期 + Refresh Token

```
Access Token: 30 分钟
Refresh Token: 7 天
```

即使 Access Token 泄露，30 分钟后失效。
Refresh Token 只在 Auth Center 使用，且可以撤销。

## 🎯 完整流程图

```
┌─────────┐  1.登录   ┌──────────┐
│  Client │ ────────→ │ Auth     │
│         │ ←──────── │ Center   │
│         │ 2.token  │ (签发JWT) │
└────┬────┘          └──────────┘
     │
     │ 3.带 token 访问 /api/users/me
     ↓
┌──────────┐         ┌──────────────┐
│ Gateway │ ──────→ │ User Service │
│ 验证JWT │         │ 业务处理     │
│ 转发用户 │         └──────────────┘
└──────────┘
     │
     │ 4.token 过期
     ↓
┌─────────┐  5.refresh  ┌──────────┐
│  Client │ ──────────→ │ Auth     │
│         │ ←─────────── │ Center   │
│         │ 6.新 token  │          │
└─────────┘              └──────────┘
```

## 🎯 总结

**OAuth2 选型：**
- ✅ 前后端分离：密码模式 + JWT
- ✅ 第三方登录：授权码模式
- ✅ 微服务：JWT + 资源服务器

**JWT 最佳实践：**
- ✅ 密钥 ≥ 256 bit，从配置读取
- ✅ 短 Access Token（30 分钟）
- ✅ Refresh Token 机制
- ✅ HTTPS 传输
- ✅ 黑名单机制（登出时失效）
- ✅ 不在 Token 存敏感信息

**微服务鉴权：**
- ✅ Gateway 统一验证
- ✅ 业务服务不重复验证（信任 Gateway）
- ✅ 用户信息用 Header 传递

**下一步：** [🏛️ 统一认证中心](/05-security/auth-center) — 完整的 Auth Center 实现