---
title: Spring Security 基础
---

# 🛡️ Spring Security 基础

> Spring Security 是 Spring 生态的**安全框架**，处理认证（Authentication）和授权（Authorization）。

## 🎯 核心概念

```
认证（Authentication）：
- 你是谁？验证身份
- 例：登录验证用户名密码

授权（Authorization）：
- 你能做什么？验证权限
- 例：管理员能删除，用户只能查看
```

## 🚀 快速开始

### 1. 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 2. 默认行为

```java
// 加上 starter-security 后，自动：
// 1. 所有接口需要登录
// 2. 启动生成随机密码（控制台输出）
// 3. 默认用户 user

// 使用：
@SpringBootApplication
public class Application { }
```

```bash
# 控制台输出
Using generated security password: a8c5f4d3-2b1e-4a9c-8d7f-6e5d4c3b2a1f
```

### 3. 自定义配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults())    // 启用表单登录
            .httpBasic(Customizer.withDefaults())     // 启用 HTTP Basic
            .build();
    }
    
    @Bean
    public UserDetailsService users() {
        UserDetails admin = User.builder()
            .username("admin")
            .password("{noop}admin123")
            .roles("ADMIN")
            .build();
        return new InMemoryUserDetailsManager(admin);
    }
}
```

## 🔐 表单登录

```java
@Configuration
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .formLogin(form -> form
                .loginPage("/login")                  // 自定义登录页
                .loginProcessingUrl("/api/auth/login") // 登录处理 URL
                .defaultSuccessUrl("/home", true)     // 成功跳转
                .failureUrl("/login?error=true")      // 失败跳转
                .usernameParameter("username")        // 用户名参数
                .passwordParameter("password")        // 密码参数
                .successHandler((req, res, auth) -> {  // 成功处理器
                    res.setStatus(200);
                    res.getWriter().write("{\"token\":\"xxx\"}");
                })
                .failureHandler((req, res, ex) -> {   // 失败处理器
                    res.setStatus(401);
                    res.getWriter().write("{\"error\":\"登录失败\"}");
                })
                .permitAll()
            )
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .csrf(csrf -> csrf.disable())  // ⚠️ API 项目要禁用
            .build();
    }
}
```

## 🔒 密码加密

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();  // ⚠️ 必须用 BCrypt
}
```

```java
// 加密
String hash = passwordEncoder.encode("123456");
// $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy

// 验证
boolean match = passwordEncoder.matches("123456", hash);
// true
```

## 🛡️ 方法级权限

```java
@Service
public class UserService {
    
    @PreAuthorize("hasRole('ADMIN')")           // 只有 ADMIN 角色
    public void deleteUser(Long id) {
        userMapper.deleteById(id);
    }
    
    @PreAuthorize("hasAuthority('user:write')")  // 需要特定权限
    public User updateUser(UserDTO dto) {
        return userMapper.update(dto);
    }
    
    @PreAuthorize("#userId == authentication.principal.id")  // 只能改自己
    public User getMyInfo(Long userId) {
        return userMapper.selectById(userId);
    }
}
```

需要启用：
```java
@EnableMethodSecurity  // 启用方法级权限
@Configuration
public class SecurityConfig { }
```

## 🔗 JWT 集成（无状态认证）

```java
public class JwtUtil {
    
    private static final String SECRET = "my-secret-key";
    private static final long EXPIRE = 30 * 60 * 1000;  // 30 分钟
    
    public static String generate(Long userId, String role) {
        return Jwts.builder()
            .setSubject(String.valueOf(userId))
            .claim("role", role)
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + EXPIRE))
            .signWith(SignatureAlgorithm.HS256, SECRET)
            .compact();
    }
    
    public static Claims parse(String token) {
        return Jwts.parser()
            .setSigningKey(SECRET)
            .parseClaimsJws(token)
            .getBody();
    }
}
```

```java
@RestController
public class AuthController {
    
    @PostMapping("/login")
    public Result<Map> login(@RequestBody LoginDTO dto) {
        // 1. 验证密码
        User user = userService.findByUsername(dto.getUsername());
        if (!passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            return Result.error(401, "密码错误");
        }
        
        // 2. 生成 JWT
        String token = JwtUtil.generate(user.getId(), user.getRole());
        
        return Result.success(Map.of("token", token));
    }
}
```

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest req, 
                                    HttpServletResponse res, 
                                    FilterChain chain) {
        // 1. 提取 Token
        String token = req.getHeader("Authorization");
        if (token != null && token.startsWith("Bearer ")) {
            token = token.substring(7);
            
            try {
                // 2. 验证
                Claims claims = JwtUtil.parse(token);
                Long userId = Long.parseLong(claims.getSubject());
                String role = (String) claims.get("role");
                
                // 3. 设置认证信息
                UsernamePasswordAuthenticationToken auth = 
                    new UsernamePasswordAuthenticationToken(
                        userId, null, 
                        List.of(new SimpleGrantedAuthority("ROLE_" + role))
                    );
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (Exception e) {
                // Token 无效
            }
        }
        
        chain.doFilter(req, res);
    }
}
```

```java
@Configuration
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .build();
    }
    
    @Autowired
    private JwtAuthFilter jwtAuthFilter;
}
```

## 🛡️ Spring Security 过滤器链

```
请求 → SecurityFilterChain:
  1. SecurityContextPersistenceFilter
  2. CsrfFilter（API 项目禁用）
  3. UsernamePasswordAuthenticationFilter
  4. JwtAuthFilter（自定义）
  5. AuthorizationFilter（权限检查）
  → 到达 Controller
```

## 🔒 CORS + CSRF 实战

```java
@Configuration
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            // CORS（必须）
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            
            // CSRF（API 项目禁用）
            .csrf(csrf -> csrf.disable())
            
            // Session 策略（无状态）
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            
            // 自定义 JWT 过滤器
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            
            // 授权
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/login").permitAll()
                .anyRequest().authenticated()
            )
            .build();
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration cfg = new CorsConfiguration();
        cfg.addAllowedOriginPattern("*");
        cfg.addAllowedMethod("*");
        cfg.addAllowedHeader("*");
        cfg.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", cfg);
        return source;
    }
}
```

## 🎯 总结

**Spring Security 核心：**
- ✅ 认证（Authentication）：你是谁
- ✅ 授权（Authorization）：你能做什么
- ✅ Filter Chain：请求拦截链
- ✅ SecurityContext：存储当前用户信息

**实战模式：**
- ✅ 前后端分离：JWT + 无状态 Session
- ✅ 传统 Web：Session + Cookie
- ✅ 微服务：API Gateway 统一鉴权

**关键配置：**
- ✅ `csrf().disable()`（API 项目）
- ✅ `sessionCreationPolicy(STATELESS)`（无状态）
- ✅ `BCryptPasswordEncoder`（密码加密）
- ✅ `@EnableMethodSecurity`（方法级权限）

**下一步：** [🔑 OAuth2 + JWT 实战](/05-security/oauth2) — 完整的认证授权方案