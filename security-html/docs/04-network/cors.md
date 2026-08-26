---
title: CORS 跨域
---

# CORS（跨域资源共享）

## 一句话总结

> **CORS = 浏览器跨域访问控制**。**核心：浏览器 + 服务端 + 预检**。**常见错误：Access-Control-Allow-Origin: * + 凭证 = 灾难**。**实战：明确 origin 白名单 + 按需 allow credentials**。

---

## 什么是 CORS

```
┌────────────────────────────────────────┐
│  同源策略（Same-Origin Policy）         │
│  浏览器默认禁止跨域请求                  │
│  https://app.com 只能访问 https://app.com│
├────────────────────────────────────────┤
│  CORS 是 W3C 标准，跨域时增加头：       │
│  服务端说：我允许某 origin 访问         │
│  浏览器：OK，那我放行                   │
└────────────────────────────────────────┘
```

## 简单请求 vs 预检

| 类型 | 触发条件 |
|------|---------|
| **简单请求** | GET / HEAD / POST + 标准头 |
| **预检请求** | PUT / DELETE / 自定义头 / JSON |

### 简单请求

```http
GET /api/users HTTP/1.1
Origin: https://app.com
```

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.com
```

### 预检请求（OPTIONS）

```http
OPTIONS /api/users HTTP/1.1
Origin: https://app.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: X-Custom-Header
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: X-Custom-Header
Access-Control-Max-Age: 3600
```

## 实战：Spring Boot CORS

```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://app.com", "https://admin.example.com"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        config.setExposedHeaders(List.of("X-Total-Count"));
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
```

## 实战：Nginx CORS

```nginx
location /api/ {
    # 动态 origin（不建议）
    # add_header Access-Control-Allow-Origin "$http_origin" always;

    # 静态 origin（推荐）
    set $cors_origin "";
    if ($http_origin = "https://app.com") {
        set $cors_origin $http_origin;
    }
    if ($http_origin = "https://admin.example.com") {
        set $cors_origin $http_origin;
    }
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Access-Control-Max-Age 3600 always;

    # 预检请求直接返回 204
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    proxy_pass http://backend;
}
```

## 实战：Node.js cors 中间件

```javascript
const cors = require("cors");

app.use(cors({
    origin: ["https://app.com", "https://admin.example.com"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Authorization", "Content-Type"],
    credentials: true,
    maxAge: 3600,
}));
```

## 灾难示范

```python
# ❌ 灾难：allow * + credentials
response.headers["Access-Control-Allow-Origin"] = "*"
response.headers["Access-Control-Allow-Credentials"] = "true"
# 浏览器会拒绝（spec 禁止）
# 即使不禁止，任何网站都能带凭证调你的 API
```

```python
# ❌ 灾难：动态 origin 反射
origin = request.headers.get("Origin")
response.headers["Access-Control-Allow-Origin"] = origin
# 攻击者伪造 Origin 头绕过
```

## 实战：环境变量管理 origin

```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

@app.after_request
def cors(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
```

## CORS 攻击矩阵

| 攻击 | 危害 |
|------|------|
| CORS * + 凭证 | 任意网站读取 |
| Origin 反射 | 绕过白名单 |
| null origin | data: URL / iframe 绕过 |
| 缓存投毒 | 中间 CDN 缓存 |
| 预检缓存 | Max-Age 过长 |

## 实战：CSRF 配合 SameSite

```python
# 同源：Cookie SameSite=Strict
# → CORS 不发送 Cookie（除非 allow_credentials=true）

# 跨域：需要 allow_credentials=true + 显式 origin
response.headers["Access-Control-Allow-Credentials"] = "true"
response.headers["Access-Control-Allow-Origin"] = "https://app.com"  # 不能 *
```

## 实战：浏览器 DevTools 调试

```javascript
// 浏览器 console
fetch("https://api.example.com/users", {
    credentials: "include"
}).then(r => r.json());

// Failed to load: Response to preflight request doesn't pass
// → 说明预检失败
```

## 关联章节

- **02-auth/session-attack**：CSRF + SameSite
- **04-network/tls-pki**：HTTPS 跨域基础
- **01-web-top10/a05-misconfig**：A05 配置错误

## 一句话总结

> **CORS = 浏览器跨域规则**。**allow_credentials=true 时不能 allow-origin=***。**明确 origin 白名单 + 预检缓存**。**Nginx if + set 变量是经典配置**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
