---
title: Gin 框架
date: 2026-08-15  # date-auto-injected
---

# Gin Web 框架

**Gin = Go 生态最流行的 Web 框架**——80k+ stars，性能接近 net/http + httprouter。

## 一句话总结

> **Gin = httprouter 路由 + 中间件链 + JSON 绑定 + 错误处理**。**替代品：Echo / Fiber / Chi**。

---

## 一、为什么选 Gin

- 性能：50k+ QPS
- API 友好：JSON / XML / YAML
- 中间件：日志 / 认证 / 限流 / 跨域
- 错误恢复：`recover()` 防 panic 进程挂
- 生态：JWT / CORS / GORM / Redis / K8s client

## 二、Hello World

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()  // 包含 Logger + Recovery 中间件
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    r.Run()  // 监听 0.0.0.0:8080
}
```

## 三、路由

```go
// 静态
r.GET("/users", listUsers)
r.POST("/users", createUser)
r.PUT("/users/:id", updateUser)
r.DELETE("/users/:id", deleteUser)
r.PATCH("/users/:id", patchUser)

// 参数
c.Param("id")  // /users/123 → "123"

// 查询参数
c.Query("page")   // /users?page=2
c.DefaultQuery("page", "1")

// 通配
r.GET("/static/*filepath", serveStatic)

// 路由组（中间件 + 公共前缀）
v1 := r.Group("/v1")
{
    auth := v1.Group("/", authMiddleware())
    {
        auth.GET("/users", listUsers)
        auth.POST("/users", createUser)
    }
}
```

## 四、Handler

```go
func listUsers(c *gin.Context) {
    // 1. 拿参数
    page := c.DefaultQuery("page", "1")
    
    // 2. 调 service
    users, err := userService.List(page)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    
    // 3. 返回
    c.JSON(200, users)
    // 或：c.JSON(200, gin.H{"data": users, "code": 0})
}
```

## 五、绑定

```go
type CreateUserReq struct {
    Name  string `json:"name" binding:"required,min=2,max=20"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age" binding:"gte=0,lte=150"`
}

func createUser(c *gin.Context) {
    var req CreateUserReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // req 已验证通过
}

// 四种绑定
c.ShouldBindJSON(&req)      // JSON body
c.ShouldBind(&req)          // 自动识别（JSON / form / query）
c.ShouldBindUri(&req)       // URI 参数
c.ShouldBindQuery(&req)     // Query 字符串
```

**Validation**：Gin 用 go-playground/validator，支持 required / email / min / max / gte / lte / oneof / uuid / alphanum 等。

## 六、中间件

```go
// 自定义中间件
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Next()  // 执行 handler
        log.Printf("%s %s %v", c.Request.Method, c.Request.URL.Path, time.Since(start))
    }
}

// 全局中间件
r.Use(LoggerMiddleware(), gin.Recovery())

// 路由组中间件
authGroup := r.Group("/admin", authMiddleware())

// 单路由中间件
r.GET("/users", authMiddleware(), listUsers)
```

**常用中间件**：
- `gin.Recovery()`：panic 恢复
- `gin.Logger()`：访问日志
- `cors.New(...)`：CORS
- `jwt.New(...)`：JWT 验证
- `ratelimit.New(...)`：限流

## 七、完整 CRUD 例子

```go
package main

import (
    "net/http"
    "strconv"
    "github.com/gin-gonic/gin"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users = make(map[int]*User)
var nextID = 1

func main() {
    r := gin.Default()
    
    r.GET("/users", func(c *gin.Context) {
        list := make([]*User, 0, len(users))
        for _, u := range users { list = append(list, u) }
        c.JSON(200, list)
    })
    
    r.GET("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        u, ok := users[id]
        if !ok {
            c.JSON(404, gin.H{"error": "not found"})
            return
        }
        c.JSON(200, u)
    })
    
    r.POST("/users", func(c *gin.Context) {
        var u User
        if err := c.ShouldBindJSON(&u); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        u.ID = nextID
        nextID++
        users[u.ID] = &u
        c.JSON(201, u)
    })
    
    r.PUT("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        var u User
        c.ShouldBindJSON(&u)
        u.ID = id
        users[id] = &u
        c.JSON(200, u)
    })
    
    r.DELETE("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        delete(users, id)
        c.Status(204)
    })
    
    r.Run(":8080")
}
```

## 八、与其他框架对比

| 框架 | 路由算法 | 性能 | 特色 |
|---|---|---|---|
| **Gin** | httprouter（基数树） | 50k QPS | 生态最丰富 |
| **Echo** | 基数树 | 60k QPS | API 略胜 Gin |
| **Fiber** | fasthttp | 100k+ QPS | Express-like |
| **Chi** | 基数树 | 50k QPS | 标准库风格 |
| **net/http** | 无 | 30k QPS | 标准库 |
| **Iris** | 基数树 | 50k QPS | 较老，功能多 |

**建议**：Gin 适合 90% 场景；极致性能选 Fiber（但 fasthttp 不兼容 net/http）。

## 九、生产实践

**项目结构**：

```
myapp/
├── cmd/
│   └── server/main.go
├── internal/
│   ├── handler/    # HTTP handler
│   ├── service/    # 业务逻辑
│   ├── repo/       # 数据访问
│   └── model/      # 数据模型
├── pkg/
│   ├── middleware/
│   └── util/
├── configs/
│   └── config.yaml
├── go.mod
└── go.sum
```

**优雅关闭**：

```go
srv := &http.Server{Addr: ":8080", Handler: r}
go srv.ListenAndServe()

quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := srv.Shutdown(ctx); err != nil {
    log.Fatal("Server forced to shutdown:", err)
}
```

## 关联章节

- **05-microservices/grpc**：gRPC
- **05-microservices/kratos**：微服务框架
- **03-ecosystem/standard-library**：net/http

## 一句话总结

> **Gin = httprouter + 中间件 + 验证**。**90% Go Web 项目首选**。


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
