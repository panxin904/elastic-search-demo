---
title: Kratos / go-zero / go-micro
---

# Go 微服务框架

**三个主流 Go 微服务框架对比**——Kratos、go-zero、go-micro。

## 一句话总结

> **Kratos（字节/B 站）= 完整套件；go-zero（好未来）= 工程化；go-micro = 早期标杆**。**国内推荐 Kratos 或 go-zero**。

---

## 一、为什么需要微服务框架

**Gin 写单体服务够用，但微服务需要**：
- 服务注册 / 发现
- 负载均衡
- 限流 / 熔断
- 链路追踪
- 配置中心
- 监控埋点
- 错误处理
- 重试 / 超时

**这些是 Go 微服务框架提供的**。

## 二、Kratos（推荐）

**Bilibili 开源**（2019，2020 字节收购后并入），定位"Go 微服务全栈框架"。

```bash
go install github.com/go-kratos/kratos/cmd/kratos/v2@latest
kratos new helloworld
cd helloworld
kratos run
```

**目录结构**：

```
helloworld/
├── api/                 # proto 定义
│   └── helloworld/v1/
├── cmd/                 # 入口
│   └── helloworld/
│       └── main.go
├── configs/             # 配置
├── internal/
│   ├── biz/             # 业务逻辑
│   ├── data/            # 数据访问
│   ├── service/         # service 层（proto 实现）
│   └── server/          # HTTP/gRPC server
└── third_party/         # proto 依赖
```

**核心组件**：

```go
// cmd/helloword/main.go
func main() {
    flag.Parse()
    logger := log.With(log.NewStdLogger(os.Stdout),
        "ts", log.DefaultTimestamp,
        "caller", log.DefaultCaller,
    )
    
    c := config.New(config.WithSource(file.NewSource(flagconf)))
    bc := newBootstrapConfig()
    if err := c.Load(); err != nil { panic(err) }
    
    app, cleanup, err := wireApp(bc.Server, bc.Data, logger)
    if err != nil { panic(err) }
    defer cleanup()
    
    if err := app.Run(); err != nil { panic(err) }
}
```

**Kratos 优点**：
- 完整套件：HTTP + gRPC + 服务发现 + 配置 + 限流
- Wire 依赖注入
- 中间件丰富（recovery / logging / tracing / ratelimit / circuit breaker）
- 与 K8s 集成好
- 字节 / B 站生产验证

**Kratos 缺点**：
- 学习曲线陡
- 文档偏少（相对 Java Spring Cloud）
- 较新，社区生态中等

## 三、go-zero

**好未来开源**（2020），定位"极简工程化"，中国 Go 微服务首选。

```bash
goctl api new greet
goctl rpc new greet
goctl docker -go greet.api
```

**API 定义（DSL）**：

```go
// greet.api
syntax = "v1"

type HelloReq {
    Name string `form:"name"`
}
type HelloResp {
    Msg  string `json:"msg"`
}

service greet-api {
    @handler GreetHandler
    get /greet/hello (HelloReq) returns (HelloResp)
}
```

**生成的代码**：

```go
// internal/handler/greethandler.go
func (h *GreetHandler) Greet(ctx *rest.Context) {
    var req types.HelloReq
    if err := ctx.Bind(&req); err != nil { /* ... */ }
    
    resp, err := h.svc.Greet(ctx, &req)
    if err != nil { /* ... */ }
    
    httpx.OkJson(ctx, resp)
}
```

**goctl 一键生成**：API + RPC + Model + DDL + K8s YAML + Dockerfile + Helm。

**go-zero 优点**：
- goctl 代码生成（DSL 驱动）
- 内置 ETCD / K8s 注册中心
- 内置 JWT 鉴权
- 内置限流熔断
- 中国社区最大
- 文档中文友好

**go-zero 缺点**：
- 高度依赖 goctl，黑盒生成
- 框架侵入性强
- 升级时偶有 breaking change

## 四、go-micro

**早期 Go 微服务标杆**（2015，社区驱动），但 2020 年后维护放缓。

```go
import "go-micro.dev/v4"

service := micro.NewService(
    micro.Name("greeter"),
    micro.Version("latest"),
)
service.Init()

proto.RegisterGreeterHandler(service.Server(), &Greeter{})

if err := service.Run(); err != nil { log.Fatal(err) }
```

**go-micro 优点**：
- 插件化设计（broker / registry / transport / selector）
- 多语言支持（Java / Python sidecar）

**go-micro 缺点**：
- v3/v4 转向商业化
- 社区分裂（microhq vs go-micro/v4）
- 中文文档少

## 五、对比表

| 维度 | Kratos | go-zero | go-micro |
|---|---|---|---|
| 厂商 | 字节 / B 站 | 好未来 | 个人 |
| Stars | 22k+ | 28k+ | 12k+ |
| 上手难度 | 中 | 中（goctl 驱动） | 中 |
| 代码生成 | protoc + wire | goctl | protoc |
| 依赖注入 | Wire | 手写 | 手写 |
| 注册中心 | consul/etcd/k8s/nacos | etcd/k8s | consul/etcd/k8s/mdns |
| 限流 | 内置 | 内置 | 插件 |
| 熔断 | 内置 | 内置 | 插件 |
| 链路追踪 | OpenTelemetry | 内置 | OpenTracing |
| 文档 | 中文好 | 中文好 | 英文 |
| 社区 | 中（活跃） | 大（活跃） | 小（不活跃） |
| 生产验证 | 字节 / B 站 / 哔哩哔哩 | 好未来 / 腾讯 | 较老项目 |

## 六、如何选型

**选 Kratos 如果**：
- 项目需要完整套件
- 已经在 K8s 环境
- 需要灵活的依赖注入
- 团队愿意学习

**选 go-zero 如果**：
- 想用 goctl 提高效率
- 团队是 Java 转 Go（DSL 风格类似 Spring）
- 需要中文文档
- 业务规模中等（10-100 个服务）

**选 go-micro 如果**：
- 维护老项目
- 需要多语言 sidecar

**不用框架如果**：
- 5 个服务以下
- 业务简单（CRUD）
- 想用 K8s Service 替代服务发现

## 七、自建微服务栈

**用 K8s 替代服务发现**：

```go
// 直接调 K8s Service
conn, _ := grpc.Dial("myservice.default.svc.cluster.local:50051", ...)

// K8s Service 自带负载均衡 + 服务发现
// 用 Istio 加限流 / 熔断 / 链路追踪
```

**优势**：
- 简单：Gin + gRPC + K8s 足够
- K8s 资源管控一体化
- 减少框架绑定

**适合**：10-30 个服务，K8s 原生团队。

## 八、实战：Kratos 完整示例

**1. proto**：

```protobuf
syntax = "proto3";
package user.v1;
option go_package = "github.com/myorg/myapp/api/user/v1;userv1";

service User {
    rpc CreateUser(CreateUserRequest) returns (CreateUserReply);
}

message CreateUserRequest {
    string name = 1;
    string email = 2;
}

message CreateUserReply {
    int64 id = 1;
}
```

**2. biz**（业务逻辑）：

```go
// internal/biz/user.go
type User struct {
    ID    int64
    Name  string
    Email string
}

type UserRepo interface {
    Save(ctx context.Context, u *User) (*User, error)
}

type UserUsecase struct {
    repo UserRepo
    log  *log.Helper
}

func NewUserUsecase(repo UserRepo, logger log.Logger) *UserUsecase {
    return &UserUsecase{repo: repo, log: log.NewHelper(logger)}
}

func (uc *UserUsecase) Create(ctx context.Context, name, email string) (*User, error) {
    if name == "" {
        return nil, errors.BadRequest("INVALID_NAME", "name cannot be empty")
    }
    return uc.repo.Save(ctx, &User{Name: name, Email: email})
}
```

**3. data**（数据访问）：

```go
// internal/data/user.go
type userRepo struct {
    data *Data
    log  *log.Helper
}

func NewUserRepo(data *Data, logger log.Logger) biz.UserRepo {
    return &userRepo{data: data, log: log.NewHelper(logger)}
}

func (r *userRepo) Save(ctx context.Context, u *biz.User) (*biz.User, error) {
    res, err := r.data.db.ExecContext(ctx, "INSERT INTO users (name, email) VALUES (?, ?)", u.Name, u.Email)
    if err != nil { return nil, err }
    id, _ := res.LastInsertId()
    return &biz.User{ID: id, Name: u.Name, Email: u.Email}, nil
}
```

**4. service**（proto 实现）：

```go
// internal/service/user.go
type UserService struct {
    usecase *biz.UserUsecase
}

func NewUserService(usecase *biz.UserUsecase) *UserService {
    return &UserService{usecase: usecase}
}

func (s *UserService) CreateUser(ctx context.Context, req *userv1.CreateUserRequest) (*userv1.CreateUserReply, error) {
    u, err := s.usecase.Create(ctx, req.Name, req.Email)
    if err != nil { return nil, err }
    return &userv1.CreateUserReply{Id: u.ID}, nil
}
```

**5. main**（wire 注入）：

```go
// cmd/user/main.go
func main() {
    // wire 生成的 main
    app, cleanup, err := wireApp(bc.Server, bc.Data, logger)
    defer cleanup()
    app.Run()
}
```

## 关联章节

- **05-microservices/grpc**：底层 RPC
- **05-microservices/gin-framework**：单体框架
- **05-microservices/service-governance**：服务治理
- **05-microservices/case-study**：真实案例

## 一句话总结

> **Kratos = 字节系，go-zero = 工程化，go-micro = 老牌**。**国内首选 Kratos 或 go-zero**。
