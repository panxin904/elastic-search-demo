---
title: 标准库
---

# Go 标准库

**Go 标准库是 Go 最大的优势**——`net/http` `encoding/json` `sync` `context` `database/sql` 全部开箱即用，无需 Spring/Hibernate/Express 这样的重量级框架。

## 一句话总结

> **Go 标准库 ≈ Java 17 + Spring Boot 核心 + Jackson + Guava 一半**。**`net/http` 起步就能写生产级 Web 服务**。

---

## 一、必学标准包 TOP 20

| 包 | 作用 | 关键 API |
|---|---|---|
| `fmt` | 格式化 I/O | `Printf`, `Sprintf`, `Errorf` |
| `errors` | 错误处理 | `New`, `Is`, `As`, `Join` (Go 1.20+) |
| `context` | 上下文/超时/取消 | `Background`, `WithCancel`, `WithTimeout` |
| `sync` | 同步原语 | `Mutex`, `WaitGroup`, `Once`, `Pool` |
| `sync/atomic` | 原子操作 | `AddInt64`, `LoadPointer`, `CAS` |
| `time` | 时间/定时器 | `Now`, `After`, `Ticker`, `Tick` |
| `io` | I/O 抽象 | `Reader`, `Writer`, `Copy`, `MultiWriter` |
| `os` | 操作系统 | `Open`, `Create`, `Getenv`, `Args` |
| `path/filepath` | 路径 | `Join`, `Base`, `Dir`, `Walk` |
| `encoding/json` | JSON | `Marshal`, `Unmarshal`, `Decoder` |
| `net/http` | HTTP 客户端/服务端 | `Get`, `Post`, `ListenAndServe`, `Handler` |
| `net/url` | URL 解析 | `Parse`, `Values`, `QueryEscape` |
| `strings` | 字符串 | `Split`, `Join`, `Contains`, `Builder` |
| `strconv` | 类型转换 | `Itoa`, `Atoi`, `FormatFloat`, `ParseBool` |
| `sort` | 排序 | `Slice`, `SliceStable`, `Strings` |
| `container/list` | 双向链表 | `PushBack`, `Remove` |
| `container/heap` | 堆 | `Push`, `Pop`, `Init` |
| `bufio` | 缓冲 I/O | `NewReader`, `NewWriter`, `Scanner` |
| `log` / `log/slog` | 日志 | `Println`, `Default`, `slog.Info` (Go 1.21+) |
| `reflect` | 反射 | `TypeOf`, `ValueOf`, `DeepEqual` |
| `database/sql` | SQL 抽象 | `Open`, `Query`, `Exec`, `Scan` |
| `crypto/*` | 加密 | `sha256`, `hmac`, `rsa`, `tls` |
| `encoding/*` | 编码 | `gob`, `base64`, `hex`, `csv`, `xml` |
| `runtime` | runtime 控制 | `GOMAXPROCS`, `NumGoroutine`, `GC` |
| `testing` | 测试 | `T`, `B`, `M`, `Run` |

## 二、`net/http` — Web 服务核心

**Hello World Web 服务**：

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
    })
    http.ListenAndServe(":8080", nil)
}
```

**生产级 server**（自定义 mux + 中间件）：

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /users/{id}", getUser)
    mux.HandleFunc("POST /users", createUser)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      loggingMiddleware(mux),
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }
    log.Fatal(srv.ListenAndServe())
}
```

**Go 1.22+ 路由增强**：
- `GET /users/{id}`：方法+路径模式
- `{id}` 占位符
- `r.PathValue("id")` 拿值

**HTTP 客户端**：

```go
resp, err := http.Get("https://api.github.com/users/octocat")
if err != nil { return err }
defer resp.Body.Close()

body, _ := io.ReadAll(resp.Body)
fmt.Println(string(body))

// POST JSON
data, _ := json.Marshal(payload)
resp, err := http.Post(url, "application/json", bytes.NewReader(data))

// 自定义 Client（推荐）
client := &http.Client{Timeout: 10 * time.Second}
req, _ := http.NewRequest("GET", url, nil)
req.Header.Set("Authorization", "Bearer "+token)
resp, err := client.Do(req)
```

## 三、`encoding/json` — 序列化

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`  // 零值跳过
}

// 编码
u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
data, _ := json.Marshal(u)
// {"id":1,"name":"Alice","email":"alice@example.com"}

// 美化输出
data, _ := json.MarshalIndent(u, "", "  ")

// 解码
var u2 User
json.Unmarshal(data, &u2)

// 流式编码（适合大对象）
enc := json.NewEncoder(w)
enc.Encode(u)

// 流式解码（HTTP 处理器里常用）
dec := json.NewDecoder(r.Body)
var u User
dec.Decode(&u)
```

**性能技巧**：
- `jsoniter` / `easyjson` 比标准库快 2-5 倍
- `[]byte` 而非 `string` 减少拷贝
- `json.Decoder` 流式避免整段加载

## 四、`context` — 上下文/取消

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 传给下游
result, err := db.QueryContext(ctx, "SELECT ...")

// goroutine 监听
go func() {
    select {
    case <-ctx.Done():
        return  // 取消
    case <-time.After(3 * time.Second):
        fmt.Println("done")
    }
}()

// 传值
ctx = context.WithValue(ctx, userIDKey, 42)
uid := ctx.Value(userIDKey).(int)
```

**规则**：ctx 是请求作用域的第一个参数，跨 API 边界传递。

## 五、`sync` — 并发原语

```go
// Mutex
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()

// RWMutex（读多写少）
var rwmu sync.RWMutex
rwmu.RLock()  // 多个读
rwmu.Lock()   // 排他写

// WaitGroup
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        // work
    }(i)
}
wg.Wait()

// Once（单例）
var once sync.Once
var instance *Singleton
once.Do(func() { instance = &Singleton{} })

// Pool（对象池）
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}
buf := bufPool.Get().(*bytes.Buffer)
defer bufPool.Put(buf)
```

## 六、`log/slog` — 结构化日志（Go 1.21+）

```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
slog.SetDefault(logger)

slog.Info("user login", "user_id", 42, "ip", r.RemoteAddr)
slog.Error("db error", "err", err, "query", query)
slog.Warn("rate limit", "limit", 100, "user", uid)

// 输出
// {"time":"2026-08-09T22:00:00Z","level":"INFO","msg":"user login","user_id":42}
```

**vs logrus/zap**：slog 是官方标准，无第三方依赖。

## 七、database/sql — 数据库抽象

```go
import "database/sql"
import _ "github.com/go-sql-driver/mysql"  // 注册驱动

db, err := sql.Open("mysql", "user:pass@tcp(localhost:3306)/dbname")
defer db.Close()

// 连接池配置
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)

// 查询
rows, err := db.Query("SELECT id, name FROM users WHERE age > ?", 18)
defer rows.Close()
for rows.Next() {
    var id int
    var name string
    rows.Scan(&id, &name)
}

// 单行
var name string
db.QueryRow("SELECT name FROM users WHERE id = ?", 1).Scan(&name)

// 事务
tx, _ := db.Begin()
tx.Exec("UPDATE ...")
tx.Commit()  // 或 tx.Rollback()
```

**注意**：`database/sql` 偏底层，常用 `sqlx` / `gorm` 增强。

## 八、crypto — 加密

```go
import (
    "crypto/sha256"
    "crypto/hmac"
    "crypto/rand"
    "crypto/rsa"
    "crypto/tls"
)

h := sha256.Sum256([]byte("hello"))
fmt.Printf("%x", h)

// HMAC
mac := hmac.New(sha256.New, []byte("secret"))
mac.Write([]byte("message"))
expectedMAC := mac.Sum(nil)

// RSA
priv, _ := rsa.GenerateKey(rand.Reader, 2048)
ciphertext, _ := rsa.EncryptOAEP(sha256.New(), rand.Reader, &priv.PublicKey, []byte("secret"), nil)
```

## 九、`testing` — 测试

见 03-ecosystem/testing 章节。

## 十、`runtime` — runtime 控制

```go
import "runtime"

runtime.GOMAXPROCS(8)  // P 数量（默认 = CPU 核数）
runtime.GC()            // 强制 GC
runtime.Gosched()       // 让出 CPU

var m runtime.MemStats
runtime.ReadMemStats(&m)
fmt.Printf("Alloc=%d MB\n", m.Alloc/1024/1024)
fmt.Printf("NumGoroutine=%d\n", runtime.NumGoroutine())
```

## 关联章节

- **03-ecosystem/go-toolchain**：工具链
- **03-ecosystem/testing**：测试
- **06-advanced/runtime**：GMP 调度
- **06-advanced/reflection**：反射

## 一句话总结

> **Go 标准库 = Production-Ready 工具集**。**`net/http` + `database/sql` + `encoding/json` 三件套能写出 90% 的服务**。
