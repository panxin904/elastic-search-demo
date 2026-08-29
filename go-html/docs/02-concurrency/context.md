---
title: context 上下文
---

# context 上下文

context 是 Go 并发编程的"瑞士军刀"：取消传播、超时控制、request-scoped 数据传递。

## 一句话总结

> **context = 请求级别的全局状态 + 取消信号传播**。**核心：WithCancel / WithTimeout / WithValue / Done() channel**。

---

## 一、为什么需要 context

### 典型场景

```go
// HTTP 请求 → RPC → DB 查询 → 第三方 API
// 任何一层超时都应该取消后续所有调用
```

```go
// ❌ 没有 context：超时无法传播
func handleRequest(w http.ResponseWriter, r *http.Request) {
    data := rpcCall()                    // 1s
    dbCall(data)                          // 5s
    thirdPartyCall(data)                  // 10s
    // 总耗时 16s，无法中途取消
}

// ✅ 有 context：整链路可取消
func handleRequest(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    data := rpcCallContext(ctx)           // 接收 ctx.Done()
    dbCallContext(ctx, data)              // 接收 ctx.Done()
    thirdPartyCallContext(ctx, data)      // 接收 ctx.Done()
    // 总耗时 ≤ 5s
}
```

---

## 二、context 接口

### 4 个方法

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)  // 返回截止时间
    Done() <-chan struct{}                     // 返回取消信号 channel
    Err() error                                // 返回取消原因
    Value(key any) any                         // 获取 request-scoped 值
}
```

### 两个实现

```go
// 1. Background：根 context
ctx := context.Background()

// 2. TODO：占位 context（不确定用什么时）
ctx := context.TODO()
```

---

## 三、4 个派生函数

### 1. WithCancel：手动取消

```go
ctx, cancel := context.WithCancel(parent)

// 取消
cancel()

// 在 goroutine 中监听
go func() {
    select {
    case <-ctx.Done():
        fmt.Println("cancelled:", ctx.Err())
        // cleanup
    case <-time.After(5 * time.Second):
        fmt.Println("done")
    }
}()
```

### 2. WithTimeout：超时取消

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()  // 释放资源

// 等价于
deadline := time.Now().Add(5 * time.Second)
ctx, cancel := context.WithDeadline(parent, deadline)
```

### 3. WithDeadline：截止时间

```go
deadline := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
ctx, cancel := context.WithDeadline(parent, deadline)
defer cancel()
```

### 4. WithValue：传值

```go
type traceIDKey struct{}

ctx := context.WithValue(parent, traceIDKey{}, "abc-123")

// 取值
traceID := ctx.Value(traceIDKey{}).(string)
```

### 取消传播

```
Background (根)
   │
   ├── WithCancel  → cancel1
   │      │
   │      ├── WithTimeout → cancel2 (timeout 触发的 cancel)
   │      │
   │      └── WithValue
   │
   └── WithValue
```

**取消规则**：父 context 取消 → 所有子 context 都取消。

---

## 四、实战模式

### 1. HTTP Server

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // r.Context() 是 server 自动管理的
    ctx := r.Context()

    data, err := fetchDataContext(ctx)
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            http.Error(w, "timeout", http.StatusGatewayTimeout)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    fmt.Fprint(w, data)
}

func fetchDataContext(ctx context.Context) (string, error) {
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.example.com", nil)
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    // 读 body 也监听 ctx.Done()
    done := make(chan error, 1)
    var data string
    go func() {
        b, _ := io.ReadAll(resp.Body)
        data = string(b)
        done <- nil
    }()

    select {
    case err := <-done:
        return data, err
    case <-ctx.Done():
        return "", ctx.Err()
    }
}
```

### 2. gRPC

```go
// gRPC 自动支持 context
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

resp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: "123"})
if err != nil {
    if status.Code(err) == codes.DeadlineExceeded {
        // timeout
    }
    return err
}
```

### 3. Database

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

var users []User
err := db.QueryContext(ctx, "SELECT * FROM users WHERE active = true", &users)
```

### 4. 跨服务链路追踪

```go
// 传递 trace ID
ctx := context.WithValue(parent, traceIDKey{}, "trace-abc-123")

// 在日志中打印
log.Printf("[trace=%s] processing request", ctx.Value(traceIDKey{}))
```

---

## 五、context 规则

### 1. 作为函数第一个参数

```go
// ✅ 标准
func DoSomething(ctx context.Context, arg1 string) error

// ❌ 不标准
func DoSomething(arg1 string, ctx context.Context) error
```

### 2. 不要把 context 放在 struct 字段

```go
// ❌ 错
type Service struct {
    ctx context.Context  // 不要
}

func (s *Service) Do() {}

// ✅ 对：context 作为参数
type Service struct{}

func (s *Service) Do(ctx context.Context) {}
```

**理由**：context 是 request-scoped，不是 service-scoped。

### 3. 不要传 nil context

```go
// ❌ 错：传 nil
DoSomething(nil, "arg")

// ✅ 对：用 Background 或 TODO
DoSomething(context.Background(), "arg")
```

### 4. WithValue 只能传递 request-scoped 数据

```go
// ✅ 对：trace ID / auth token / request ID
ctx := context.WithValue(parent, "traceID", "abc-123")

// ❌ 错：业务参数
ctx := context.WithValue(parent, "userID", "u-123")  // 不应该
```

**应该用参数传递**：
```go
func DoSomething(ctx context.Context, userID string) {}  // 对
```

### 5. defer cancel()

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()  // 必须！避免 context 泄漏
```

---

## 六、context.Value 的最佳实践

### 自定义 key 类型

```go
// 用 struct 类型作为 key（避免冲突）
type traceIDKey struct{}
type userIDKey struct{}

ctx := context.WithValue(parent, traceIDKey{}, "abc-123")
ctx = context.WithValue(ctx, userIDKey{}, "user-456")

// 取值
traceID := ctx.Value(traceIDKey{}).(string)
```

### 不要用 string 类型

```go
// ❌ 错：string key 容易冲突
ctx := context.WithValue(parent, "traceID", "abc")

// ✅ 对：自定义类型
type traceIDKey struct{}
ctx := context.WithValue(parent, traceIDKey{}, "abc")
```

### 封装访问方法

```go
type traceIDKey struct{}

func WithTraceID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, traceIDKey{}, id)
}

func TraceID(ctx context.Context) string {
    if id, ok := ctx.Value(traceIDKey{}).(string); ok {
        return id
    }
    return ""
}
```

---

## 七、常见陷阱

### 陷阱 1：忘记 cancel

```go
func leak() {
    ctx, cancel := context.WithCancel(context.Background())
    // 忘记 cancel()，ctx 不会被 GC
}

// 修复
func noLeak() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()  // 必须 defer
}
```

### 陷阱 2：覆盖 ctx 参数

```go
// ❌ 错：覆盖入参
func DoSomething(ctx context.Context) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    // ...
}

// ✅ 对：命名区分
func DoSomething(ctx context.Context) error {
    c, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    // 使用 c
}
```

### 陷阱 3：context.Value 类型断言失败

```go
// 不存在
v := ctx.Value("missing").(string)  // panic: interface conversion

// ✅ 修复：用 comma ok
v, ok := ctx.Value("missing").(string)
if !ok {
    return ""
}
```

---

## 八、性能开销

- **传递**：几乎无开销（interface 引用）
- **Done() channel**：每个 ctx 一个 channel（用完后要 cancel 释放）
- **WithValue**：每次都创建新 ctx（链式）

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/patterns**：并发模式

## 一句话总结

> **context = 取消传播 + 超时控制 + request-scoped 值**。**Go 并发的标配**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
