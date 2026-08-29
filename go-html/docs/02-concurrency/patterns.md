---
title: 并发模式实战
date: 2026-08-15  # date-auto-injected
---

# 并发模式实战

Go 并发的 7 大实战模式：Worker Pool、Pipeline、Fan-out/Fan-in、Pub-Sub、限流、熔断、分布式协调。

## 一句话总结

> **Go 并发模式 = Worker Pool + Pipeline + Fan-out/Fan-in + errgroup**。**核心：用 channel 通信、用 errgroup 错误传播、用 context 取消**。

---

## 一、Worker Pool（线程池）

### 基础版本

```go
func workerPool(jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- processJob(j)
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go workerPool(jobs, results)
    }

    // 发送 5 个任务
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    // 接收 5 个结果
    for a := 1; a <= 5; a++ {
        <-results
    }
}

func processJob(j int) int {
    time.Sleep(100 * time.Millisecond)
    return j * 2
}
```

### 增强版（errgroup + ctx）

```go
func workerPoolCtx(ctx context.Context, jobs <-chan int) error {
    for j := range jobs {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := processJobCtx(ctx, j); err != nil {
                return err
            }
        }
    }
    return nil
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    jobs := make(chan int, 100)
    var g errgroup.Group

    // 启动 5 个 worker
    for w := 1; w <= 5; w++ {
        g.Go(func() error {
            return workerPoolCtx(ctx, jobs)
        })
    }

    // 发送任务
    g.Go(func() error {
        defer close(jobs)
        for j := 1; j <= 100; j++ {
            select {
            case jobs <- j:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    if err := g.Wait(); err != nil {
        log.Fatal(err)
    }
}
```

---

## 二、Pipeline（管道）

### 三阶段管道

```go
// 阶段 1：生成数据
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// 阶段 2：平方
func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// 阶段 3：求和
func sum(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        total := 0
        for n := range in {
            total += n
        }
        out <- total
    }()
    return out
}

// 组合
func main() {
    // gen(2, 3) → sq → sq → sum
    result := <-sum(sq(sq(gen(2, 3))))
    fmt.Println(result)  // ((2^2)^2 + (3^2)^2) = 16 + 81 = 97
}
```

### 带 ctx 的管道

```go
func genCtx(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            select {
            case out <- n:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}
```

---

## 三、Fan-out / Fan-in

### Fan-out：分发任务到多个 worker

```go
func distribute(in <-chan Job, workers int) []<-chan Job {
    outs := make([]<-chan Job, workers)
    for i := 0; i < workers; i++ {
        outs[i] = worker(in)
    }
    return outs
}

func worker(in <-chan Job) <-chan Job {
    out := make(chan Job)
    go func() {
        defer close(out)
        for j := range in {
            out <- process(j)
        }
    }()
    return out
}
```

### Fan-in：合并多个 channel

```go
func merge(cs ...<-chan Job) <-chan Job {
    out := make(chan Job)
    var wg sync.WaitGroup

    for _, c := range cs {
        wg.Add(1)
        go func(c <-chan Job) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

### 完整 Fan-out + Fan-in

```go
func main() {
    in := genJobs(100)

    // Fan-out：3 个 worker
    workers := distribute(in, 3)

    // Fan-in：合并结果
    out := merge(workers...)

    for result := range out {
        fmt.Println(result)
    }
}
```

---

## 四、限流模式

### 信号量限流

```go
type Semaphore chan struct{}

func NewSemaphore(n int) Semaphore {
    return make(chan struct{}, n)
}

func (s Semaphore) Acquire() {
    s <- struct{}{}
}

func (s Semaphore) Release() {
    <-s
}

// 使用
sem := NewSemaphore(10)  // 最多 10 并发
for _, item := range items {
    sem.Acquire()
    go func(item Item) {
        defer sem.Release()
        process(item)
    }(item)
}
```

### 令牌桶限流（基于 time/rate）

```go
import "golang.org/x/time/rate"

limiter := rate.NewLimiter(100, 50)  // 100 QPS，桶容量 50

func handler(w http.ResponseWriter, r *http.Request) {
    if !limiter.Allow() {
        http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
        return
    }
    // 处理请求
}
```

### 漏桶限流

```go
import "github.com/uber-go/ratelimit"

rl := ratelimit.New(100)  // 100 QPS

func handler(w http.ResponseWriter, r *http.Request) {
    rl.Take()  // 阻塞直到令牌可用
    // 处理请求
}
```

---

## 五、熔断模式

### sony/gobreaker

```go
import "github.com/sony/gobreaker"

cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
    Name:        "downstream-service",
    MaxRequests: 3,                // 半开状态最大请求数
    Interval:    60 * time.Second, // 统计周期
    Timeout:     30 * time.Second, // 熔断后恢复时间
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        return counts.ConsecutiveFailures > 5
    },
})

result, err := cb.Execute(func() (interface{}, error) {
    return callDownstream()
})
```

### 手动熔断

```go
type CircuitBreaker struct {
    mu             sync.Mutex
    state          string  // closed / open / half-open
    failureCount   int
    successCount   int
    lastFailureTime time.Time
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    cb.mu.Lock()
    if cb.state == "open" {
        if time.Since(cb.lastFailureTime) > 30*time.Second {
            cb.state = "half-open"
        } else {
            cb.mu.Unlock()
            return errors.New("circuit open")
        }
    }
    cb.mu.Unlock()

    err := fn()
    cb.mu.Lock()
    defer cb.mu.Unlock()

    if err != nil {
        cb.failureCount++
        cb.lastFailureTime = time.Now()
        if cb.failureCount >= 5 {
            cb.state = "open"
        }
        return err
    }

    cb.successCount++
    if cb.state == "half-open" {
        cb.state = "closed"
        cb.failureCount = 0
    }
    return nil
}
```

---

## 六、Pub-Sub（发布订阅）

### 基础实现

```go
type PubSub struct {
    mu       sync.RWMutex
    subs     map[string][]chan Message
}

type Message struct {
    Topic   string
    Payload interface{}
}

func NewPubSub() *PubSub {
    return &PubSub{subs: make(map[string][]chan Message)}
}

func (ps *PubSub) Subscribe(topic string) <-chan Message {
    ch := make(chan Message, 10)
    ps.mu.Lock()
    ps.subs[topic] = append(ps.subs[topic], ch)
    ps.mu.Unlock()
    return ch
}

func (ps *PubSub) Publish(topic string, payload interface{}) {
    ps.mu.RLock()
    defer ps.mu.RUnlock()
    for _, ch := range ps.subs[topic] {
        ch <- Message{Topic: topic, Payload: payload}
    }
}

func (ps *PubSub) Unsubscribe(topic string, ch <-chan Message) {
    ps.mu.Lock()
    defer ps.mu.Unlock()
    subs := ps.subs[topic]
    for i, c := range subs {
        if c == ch {
            ps.subs[topic] = append(subs[:i], subs[i+1:]...)
            close(c)
            return
        }
    }
}
```

### 使用

```go
ps := NewPubSub()

sub := ps.Subscribe("user.created")
go func() {
    for msg := range sub {
        fmt.Println("received:", msg.Payload)
    }
}()

ps.Publish("user.created", "alice")
```

---

## 七、errgroup 模式

### 并行 + 错误聚合

```go
import "golang.org/x/sync/errgroup"

func main() {
    var g errgroup.Group

    urls := []string{
        "https://api1.example.com",
        "https://api2.example.com",
        "https://api3.example.com",
    }

    for _, url := range urls {
        url := url
        g.Go(func() error {
            resp, err := http.Get(url)
            if err != nil {
                return fmt.Errorf("get %s: %w", url, err)
            }
            defer resp.Body.Close()
            // 处理响应
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        log.Fatal(err)  // 第一个错误
    }
}
```

### errgroup.WithContext：第一个错误取消其他

```go
g, ctx := errgroup.WithContext(context.Background())

for _, url := range urls {
    g.Go(func() error {
        req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
        resp, err := http.DefaultClient.Do(req)
        if err != nil {
            return err
        }
        defer resp.Body.Close()
        // 处理响应
        return nil
    })
}

if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

### errgroup.SetLimit：限制并发数

```go
g := errgroup.Group{}
g.SetLimit(10)  // 最多 10 个并发

for _, url := range urls {
    url := url
    g.Go(func() error {
        // 自动等待直到 < 10 并发
        resp, err := http.Get(url)
        // ...
        return nil
    })
}
```

---

## 八、Map-Reduce 模式

### 经典 MapReduce

```go
// Map：每个 goroutine 处理一个分片
func mapShards[T, U any](items []T, mapper func(T) U, workers int) []U {
    shardSize := (len(items) + workers - 1) / workers
    results := make([][]U, workers)
    var wg sync.WaitGroup

    for w := 0; w < workers; w++ {
        wg.Add(1)
        start, end := w*shardSize, (w+1)*shardSize
        if end > len(items) {
            end = len(items)
        }
        go func(shard []T, idx int) {
            defer wg.Done()
            for _, item := range shard {
                results[idx] = append(results[idx], mapper(item))
            }
        }(items[start:end], w)
    }

    wg.Wait()

    // Flatten
    var out []U
    for _, r := range results {
        out = append(out, r...)
    }
    return out
}

// Reduce
func reduce[T any](items []T, initial T, reducer func(T, T) T) T {
    result := initial
    for _, item := range items {
        result = reducer(result, item)
    }
    return result
}

// 使用
sum := reduce(mapShards(nums, func(n int) int { return n * n }, 4), 0, func(a, b int) int { return a + b })
```

---

## 九、超时模式

### 单层超时

```go
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

result, err := rpcCall(ctx)
if errors.Is(err, context.DeadlineExceeded) {
    // timeout
}
```

### 多层超时（递增）

```go
// 顶层 HTTP handler：30s
ctx1, cancel1 := context.WithTimeout(r.Context(), 30*time.Second)
defer cancel1()

// RPC 调用：10s
ctx2, cancel2 := context.WithTimeout(ctx1, 10*time.Second)
defer cancel2()

// DB 查询：3s
ctx3, cancel3 := context.WithTimeout(ctx2, 3*time.Second)
defer cancel3()

db.QueryContext(ctx3, ...)
```

### 整体超时 + 阶段超时

```go
ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
defer cancel()

// 阶段 1：5s
ctx1, cancel1 := context.WithTimeout(ctx, 5*time.Second)
defer cancel1()
stage1(ctx1)

// 阶段 2：剩余 25s
ctx2, cancel2 := context.WithTimeout(ctx, time.Until(deadline)-5*time.Second)
defer cancel2()
stage2(ctx2)
```

---

## 十、Graceful Shutdown 模式

```go
func main() {
    ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer cancel()

    srv := &http.Server{Addr: ":8080"}

    // 启动服务
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // 等待信号
    <-ctx.Done()
    log.Println("Shutting down...")

    // 30s 内优雅退出
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Printf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited")
}
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context

## 一句话总结

> **Go 并发模式 = Worker Pool + Pipeline + Fan-out + errgroup + 限流熔断**。**实战模板可直接复用**。


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

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
