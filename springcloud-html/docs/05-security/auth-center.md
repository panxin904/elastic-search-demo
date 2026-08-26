---
title: 统一认证中心
---

# 🏛️ 统一认证中心

> 多个微服务下，**统一认证中心（Auth Center）** 是标准方案。SSO 单点登录，所有服务共用一个 Token 颁发方。

## 🎯 为什么需要认证中心？

```
无认证中心：
- 每个微服务都要做登录
- 用户信息分散在各处
- 改密码要改 10 个服务

有认证中心：
- 一次登录，全服务通行（SSO）
- 用户信息统一管理
- 改密码只改 1 处
```

## 🏗️ 整体架构

```
┌──────────────────────────────────────┐
│            Auth Center                 │
│  - 登录 / 登出 / 注册                  │
│  - JWT 颁发 / 验证 / 刷新              │
│  - 用户 / 角色 / 权限管理              │
│  - OAuth2 / OIDC 支持                 │
│  - 单点登录（SSO）                    │
└──────────────────────────────────────┘
              ↑
       颁发 Token / 验证 Token
              ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Gateway  │  │订单服务  │  │用户服务  │
│ 验 Token │  │ 信任      │  │ 信任     │
│          │  │ Auth     │  │ Auth     │
│          │  │ Center   │  │ Center   │
└──────────┘  └──────────┘  └──────────┘
```

## 🚀 Auth Center 实现

### 1. 项目结构

```
auth-center/
├── src/main/java/com/example/auth/
│   ├── AuthCenterApplication.java
│   ├── controller/
│   │   ├── AuthController.java      # 登录/登出/刷新
│   │   └── UserController.java       # 用户管理
│   ├── service/
│   │   ├── AuthService.java
│   │   ├── UserService.java
│   │   └── JwtService.java
│   ├── entity/
│   │   ├── User.java
│   │   └── Role.java
│   ├── repository/
│   │   └── UserRepository.java
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   └── JwtConfig.java
│   └── util/
│       └── JwtUtil.java
└── src/main/resources/
    └── application.yml
```

### 2. application.yml

```yaml
server:
  port: 9000

spring:
  application:
    name: auth-center
  datasource:
    url: jdbc:mysql://mysql:3306/auth_db
    username: root
    password: xxx
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
      config:
        server-addr: 127.0.0.1:8848

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
  global-config:
    db-config:
      id-type: assign_id

# JWT 配置
jwt:
  secret: ${JWT_SECRET:default-dev-secret-min-256-bits-long!!}
  access-token-expire: 1800      # 30 分钟
  refresh-token-expire: 604800   # 7 天
  issuer: auth-center
```

### 3. JwtUtil

```java
@Component
public class JwtUtil {
    
    @Value("${jwt.secret}")
    private String secret;
    
    @Value("${jwt.access-token-expire}")
    private long accessExpire;
    
    @Value("${jwt.refresh-token-expire}")
    private long refreshExpire;
    
    @Value("${jwt.issuer}")
    private String issuer;
    
    private SecretKey getKey() {
        return Keys.hmacShaKeyFor(secret.getBytes());
    }
    
    public String generateAccessToken(Long userId, String username, List<String> roles) {
        Date now = new Date();
        return Jwts.builder()
            .setId(UUID.randomUUID().toString())  // jti（用于黑名单）
            .setIssuer(issuer)
            .setSubject(String.valueOf(userId))
            .claim("username", username)
            .claim("roles", roles)
            .claim("type", "access")
            .setIssuedAt(now)
            .setExpiration(new Date(now.getTime() + accessExpire * 1000))
            .signWith(getKey(), SignatureAlgorithm.HS256)
            .compact();
    }
    
    public String generateRefreshToken(Long userId) {
        Date now = new Date();
        return Jwts.builder()
            .setId(UUID.randomUUID().toString())
            .setIssuer(issuer)
            .setSubject(String.valueOf(userId))
            .claim("type", "refresh")
            .setIssuedAt(now)
            .setExpiration(new Date(now.getTime() + refreshExpire * 1000))
            .signWith(getKey(), SignatureAlgorithm.HS256)
            .compact();
    }
    
    public Claims parse(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(getKey())
            .requireIssuer(issuer)
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
    
    public long getExpireTime(String token) {
        return parse(token).getExpiration().getTime();
    }
}
```

### 4. AuthService

```java
@Service
public class AuthService {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Autowired
    private StringRedisTemplate redis;
    
    public TokenInfo login(LoginDTO dto) {
        // 1. 验证用户
        User user = userService.findByUsername(dto.getUsername());
        if (user == null) {
            throw new BusinessException(401, "用户不存在");
        }
        if (!passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            throw new BusinessException(401, "密码错误");
        }
        if (user.getStatus() == 0) {
            throw new BusinessException(403, "账号已禁用");
        }
        
        // 2. 查询角色
        List<String> roles = userService.getRoles(user.getId());
        
        // 3. 生成 Token
        String accessToken = jwtUtil.generateAccessToken(user.getId(), user.getUsername(), roles);
        String refreshToken = jwtUtil.generateRefreshToken(user.getId());
        
        return new TokenInfo(accessToken, refreshToken, 1800, "Bearer");
    }
    
    public TokenInfo refresh(String refreshToken) {
        try {
            Claims claims = jwtUtil.parse(refreshToken);
            
            // 验证是 refresh token
            if (!"refresh".equals(claims.get("type"))) {
                throw new BusinessException(401, "不是 refresh token");
            }
            
            // 检查黑名单
            String jti = claims.getId();
            if (Boolean.TRUE.equals(redis.hasKey("jwt:blacklist:" + jti))) {
                throw new BusinessException(401, "refresh token 已失效");
            }
            
            // 重新生成 access token
            Long userId = Long.parseLong(claims.getSubject());
            User user = userService.findById(userId);
            List<String> roles = userService.getRoles(userId);
            String newAccessToken = jwtUtil.generateAccessToken(userId, user.getUsername(), roles);
            
            return new TokenInfo(newAccessToken, refreshToken, 1800, "Bearer");
        } catch (ExpiredJwtException e) {
            throw new BusinessException(401, "refresh token 已过期，请重新登录");
        } catch (JwtException e) {
            throw new BusinessException(401, "refresh token 无效");
        }
    }
    
    public void logout(String accessToken, String refreshToken) {
        // 把 token 加入黑名单
        if (accessToken != null) {
            addToBlacklist(accessToken);
        }
        if (refreshToken != null) {
            addToBlacklist(refreshToken);
        }
    }
    
    private void addToBlacklist(String token) {
        Claims claims = jwtUtil.parse(token);
        String jti = claims.getId();
        long ttl = claims.getExpiration().getTime() - System.currentTimeMillis();
        if (ttl > 0) {
            redis.opsForValue().set(
                "jwt:blacklist:" + jti, "1",
                Duration.ofMillis(ttl)
            );
        }
    }
}
```

### 5. AuthController

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @PostMapping("/login")
    public Result<TokenInfo> login(@RequestBody @Valid LoginDTO dto) {
        return Result.success(authService.login(dto));
    }
    
    @PostMapping("/refresh")
    public Result<TokenInfo> refresh(@RequestParam String refreshToken) {
        return Result.success(authService.refresh(refreshToken));
    }
    
    @PostMapping("/logout")
    public Result<Void> logout(
        @RequestHeader(value = "Authorization", required = false) String authHeader,
        @RequestParam(value = "refreshToken", required = false) String refreshToken
    ) {
        String accessToken = authHeader != null && authHeader.startsWith("Bearer ")
            ? authHeader.substring(7)
            : null;
        authService.logout(accessToken, refreshToken);
        return Result.success();
    }
    
    @GetMapping("/verify")
    public Result<Map> verify(@RequestParam String token) {
        try {
            // 检查黑名单
            Claims claims = jwtUtil.parse(token);
            String jti = claims.getId();
            if (Boolean.TRUE.equals(redis.hasKey("jwt:blacklist:" + jti))) {
                return Result.error(401, "Token 已失效");
            }
            
            Map<String, Object> data = new HashMap<>();
            data.put("userId", claims.getSubject());
            data.put("username", claims.get("username"));
            data.put("roles", claims.get("roles"));
            return Result.success(data);
        } catch (Exception e) {
            return Result.error(401, "Token 无效");
        }
    }
}
```

## 🔧 Gateway 集成

```java
@Component
public class AuthCenterFilter implements GlobalFilter, Ordered {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();
        
        // 1. 公开路径
        if (isPublicPath(path)) {
            return chain.filter(exchange);
        }
        
        // 2. 检查 Token
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            return unauthorized(exchange, "缺少 Token");
        }
        token = token.substring(7);
        
        // 3. 调用 Auth Center 验证（推荐用本地 JWT 验证减少 RPC）
        try {
            ResponseEntity<Result> resp = restTemplate.exchange(
                "http://auth-center/api/auth/verify?token=" + token,
                HttpMethod.GET, null, Result.class
            );
            if (resp.getBody() == null || resp.getBody().getCode() != 200) {
                return unauthorized(exchange, "Token 无效");
            }
            
            // 4. 提取用户信息，传递到下游
            Map<String, Object> userInfo = (Map<String, Object>) resp.getBody().getData();
            ServerHttpRequest newReq = exchange.getRequest().mutate()
                .header("X-User-Id", userInfo.get("userId").toString())
                .header("X-Username", userInfo.get("username").toString())
                .header("X-User-Roles", String.join(",", 
                    (List<String>) userInfo.get("roles")))
                .build();
            return chain.filter(exchange.mutate().request(newReq).build());
        } catch (Exception e) {
            return unauthorized(exchange, "Token 验证失败");
        }
    }
    
    private boolean isPublicPath(String path) {
        return path.startsWith("/api/auth/login")
            || path.startsWith("/api/auth/refresh")
            || path.startsWith("/api/public/");
    }
    
    @Override
    public int getOrder() { return -100; }
}
```

## 🔑 多端登录（Web / App / 小程序）

```
Web 端：账号密码登录
App 端：手机号 + 验证码登录
小程序：微信授权登录
↓
Auth Center 统一处理
↓
颁发 JWT
↓
不同端共用一套 Token 体系
```

```java
@RestController
@RequestMapping("/api/auth")
public class MultiLoginController {
    
    // 账号密码
    @PostMapping("/login/password")
    public Result<TokenInfo> loginByPassword(@RequestBody LoginDTO dto) {
        return Result.success(authService.login(dto));
    }
    
    // 手机号 + 验证码
    @PostMapping("/login/sms")
    public Result<TokenInfo> loginBySms(@RequestBody SmsLoginDTO dto) {
        // 1. 验证验证码
        if (!smsService.verify(dto.getPhone(), dto.getCode())) {
            throw new BusinessException(401, "验证码错误");
        }
        // 2. 查找/创建用户
        User user = userService.findOrCreateByPhone(dto.getPhone());
        // 3. 颁发 Token
        return Result.success(authService.generateToken(user));
    }
    
    // 微信授权
    @PostMapping("/login/wechat")
    public Result<TokenInfo> loginByWechat(@RequestBody WechatLoginDTO dto) {
        // 1. 调微信接口获取 openid
        String openid = wechatService.getOpenid(dto.getCode());
        // 2. 查找/创建用户
        User user = userService.findOrCreateByWechat(openid);
        // 3. 颁发 Token
        return Result.success(authService.generateToken(user));
    }
}
```

## 🎯 SSO 单点登录

```
场景：用户登录 baidu.com 后访问 tieba.baidu.com 自动登录

1. 用户访问 tieba.baidu.com
2. tieba 检测到没有 session
3. 跳转到 sso.baidu.com 登录
4. 登录成功后回调带 ticket
5. tieba 用 ticket 换 session
6. 用户访问成功
```

```java
// 简化版 SSO（用 JWT）
// 1. 用户访问 tieba.baidu.com
// 2. 没有 token → 跳转到 sso.baidu.com/login?redirect=tieba
// 3. sso 登录后生成 JWT，重定向到 tieba.baidu.com?jwt=xxx
// 4. tieba 验证 JWT，颁发自己的 session
```

## 🛡️ 安全防护

### 1. 暴力破解防护

```java
@PostMapping("/login")
public Result<TokenInfo> login(@RequestBody LoginDTO dto, HttpServletRequest req) {
    String ip = getClientIp(req);
    String key = "login:fail:" + dto.getUsername() + ":" + ip;
    
    // 检查失败次数
    Integer fails = redis.opsForValue().get(key);
    if (fails != null && fails >= 5) {
        long ttl = redis.getExpire(key, TimeUnit.SECONDS);
        throw new BusinessException(429, "登录失败次数过多，请 " + (ttl/60) + " 分钟后重试");
    }
    
    try {
        TokenInfo token = authService.login(dto);
        redis.delete(key);  // 成功删除
        return Result.success(token);
    } catch (Exception e) {
        redis.opsForValue().increment(key);
        redis.expire(key, 15, TimeUnit.MINUTES);
        throw e;
    }
}
```

### 2. 异地登录提醒

```java
@PostMapping("/login")
public Result<TokenInfo> login(@RequestBody LoginDTO dto, HttpServletRequest req) {
    User user = userService.findByUsername(dto.getUsername());
    
    // 检测异地登录
    String currentIp = getClientIp(req);
    String usualIp = user.getLastLoginIp();
    if (usualIp != null && !usualIp.equals(currentIp)) {
        // 发送异地登录提醒邮件
        emailService.sendLoginAlert(user.getEmail(), currentIp, usualIp);
    }
    user.setLastLoginIp(currentIp);
    userService.updateById(user);
    
    return Result.success(authService.generateToken(user));
}
```

## 🎯 总结

**Auth Center 核心：**
- ✅ 独立部署的认证服务
- ✅ 颁发 / 验证 / 刷新 JWT
- ✅ Token 黑名单（登出失效）
- ✅ 多端登录（Web / App / 小程序）
- ✅ SSO 单点登录
- ✅ 暴力破解防护

**微服务集成：**
- ✅ Gateway 统一验证
- ✅ 业务服务信任 Gateway
- ✅ 用户信息 Header 传递

**下一步：** [💼 综合实战项目](/06-practice/comprehensive) — 完整电商微服务项目


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
