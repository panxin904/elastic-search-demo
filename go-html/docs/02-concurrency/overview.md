---
title: CSP 并发总览
---

# CSP 并发总览

Go 的并发模型基于 **CSP（Communicating Sequential Processes）** 理论，由 Tony Hoare 在 1978 年提出。Go 通过 **goroutine + channel** 让并发编程变得直观。

## 一句话总结

> **CSP = "通过通信共享内存，而不是通过共享内存通信"**。**核心：goroutine（M:N 协程）+ channel（消息传递）+ context（取消传播）**。

---

## 一、CSP vs 共享内存模型

### 传统共享内存模型（Java / C++）

```java
// Java：共享内存 + 锁
class Counter {
    private int count = 0;
    public synchronized void increment() {
        count++;
    }
}
```

- **痛点**：锁竞争、死锁、活锁
- **心智负担**：开发者必须考虑线程安全

### CSP 模型（Go）

```go
// Go：通过 channel 通信
func main() {
    ch := make(chan int)
    go func() {
        ch <- 42  // 发送
    }()
    v := <-ch  // 接收
    fmt.Println(v)
}
```

- **核心**：goroutine 之间不共享状态，通过 channel 传递数据
- **优势**：避免显式锁，代码更易推理

### Go 哲学（Rob Pike）

> "Don't communicate by sharing memory; share memory by communicating."

> "通过通信共享内存，而不是通过共享内存通信。"

---

## 二、goroutine：M:N 协程

### 什么是 goroutine

```go
go func() {
    // 在新的 goroutine 中执行
    fmt.Println("hello from goroutine")
}()
```

- **轻量**：初始栈 2KB（线程 1-8MB）
- **廉价**：可创建数十万 goroutine
- **协作式调度**：由 Go runtime 调度，而非 OS

### goroutine vs OS 线程 vs 协程

| 维度 | goroutine | OS 线程 | Python coroutine |
|---|---|---|---|
| 调度 | Go runtime (M:N) | OS kernel | 用户态事件循环 |
| 栈 | 2KB 动态增长 | 1-8MB 固定 | 几乎无栈 |
| 数量 | 数十万 | 数千 | 数万 |
| 切换成本 | ~100ns | ~1μs | ~50ns |
| 多核 | ✅ | ✅ | ❌ (GIL) |

### M:N 调度模型（GMP）

```
G (Goroutine) — 用户态协程
M (Machine)   — OS 线程
P (Processor) — 逻辑处理器（默认 GOMAXPROCS = CPU 核数）
```

- **GOMAXPROCS**：控制并行度（默认 = CPU 核数）
- **work stealing**：空闲 P 从其他 P 偷 G
- **抢占式调度**（≥Go 1.14）：基于信号抢占，避免某个 goroutine 独占

---

## 三、channel：goroutine 之间的通信

### 基本用法

```go
// 无缓冲 channel（同步）
ch := make(chan int)
go func() { ch <- 42 }()
v := <-ch

// 有缓冲 channel（异步）
ch := make(chan int, 10)
ch <- 1  // 不阻塞
ch <- 2

// 只发送 / 只接收 channel
func send(ch chan<- int) { ch <- 1 }
func recv(ch <-chan int) int { return <-ch }
```

### channel 状态

| 操作 | nil channel | 已关闭 channel | 正常 channel |
|---|---|---|---|
| 发送 | 永久阻塞 | panic | 阻塞 / 发送 |
| 接收 | 永久阻塞 | 返回零值 + false | 阻塞 / 接收 |
| 关闭 | panic | panic | 关闭成功 |

### select 多路复用

```go
select {
case msg := <-ch1:
    fmt.Println("ch1:", msg)
case msg := <-ch2:
    fmt.Println("ch2:", msg)
case ch3 <- 42:
    fmt.Println("sent to ch3")
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
}
```

---

## 四、sync 包：共享内存场景

### Mutex / RWMutex

```go
var mu sync.Mutex
var count int

func increment() {
    mu.Lock()
    count++
    mu.Unlock()
}

// 读写锁（读多写少场景）
var rwmu sync.RWMutex
func read() int {
    rwmu.RLock()
    defer rwmu.RUnlock()
    return count
}
func write(n int) {
    rwmu.Lock()
    defer rwmu.Unlock()
    count = n
}
```

### WaitGroup / Once / Pool

```go
// WaitGroup：等待一组 goroutine 完成
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        fmt.Println(i)
    }(i)
}
wg.Wait()

// Once：只执行一次
var once sync.Once
var instance *Singleton
once.Do(func() {
    instance = &Singleton{}
})

// Pool：对象池（减少 GC 压力）
var bufPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}
```

### atomic 包

```go
var counter int64
atomic.AddInt64(&counter, 1)
v := atomic.LoadInt64(&counter)
```

---

## 五、context：取消传播与超时

### 为什么需要 context

```go
// 场景：HTTP 请求 → DB 查询 → 第三方 API
// 任何一层超时都应该取消后续所有调用
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()

result, err := db.QueryContext(ctx, sql)
if err != nil {
    return err
}
```

### context 4 个用法

```go
// 1. WithCancel：手动取消
ctx, cancel := context.WithCancel(parent)
go func() { time.Sleep(1*time.Second); cancel() }()

// 2. WithTimeout：超时取消
ctx, cancel := context.WithTimeout(parent, 5*time.Second)

// 3. WithDeadline：截止时间
ctx, cancel := context.WithDeadline(parent, time.Now().Add(5*time.Second))

// 4. WithValue：传值（仅限 request-scoped 数据，如 trace ID）
ctx := context.WithValue(parent, "traceID", "abc123")
```

### context 传递规则

- **作为函数第一个参数**（惯例：`func Foo(ctx context.Context, ...)`）
- **不要把 context 放在 struct 字段里**
- **不要传 nil context**（用 `context.Background()`）
- **WithValue 只能传递 request-scoped 数据**，不能用于传业务参数

---

## 六、并发模式实战

### 模式 1：Worker Pool

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)
    for a := 1; a <= 9; a++ {
        <-results
    }
}
```

### 模式 2：Pipeline

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用：gen(2, 3) → sq → sq
```

### 模式 3：Fan-out / Fan-in

```go
// Fan-out：多个 goroutine 读同一个 channel
// Fan-in：多个 channel 合并到一个 channel
```

### 模式 4：ErrGroup

```go
import "golang.org/x/sync/errgroup"

func main() {
    var g errgroup.Group
    for i := 0; i < 5; i++ {
        g.Go(func() error {
            // do work
            return nil
        })
    }
    if err := g.Wait(); err != nil {
        log.Fatal(err)
    }
}
```

---

## 七、并发陷阱

### 陷阱 1：goroutine 泄漏

```go
// 错误：channel 永远没人接收
func leak() {
    ch := make(chan int)
    go func() {
        val := <-ch  // 永久阻塞
        fmt.Println(val)
    }()
    // 函数返回，goroutine 仍在等 channel
}

// 修复：用 select + ctx
func noLeak(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            return
        }
    }()
}
```

### 陷阱 2：race condition

```go
// 错误：并发写 map
var m = make(map[int]int)
go func() { m[1] = 1 }()
go func() { m[1] = 2 }()  // data race

// 修复 1：sync.Map
// 修复 2：Mutex 保护
```

### 陷阱 3：channel 死锁

```go
// 错误：无缓冲 channel + 单 goroutine
ch := make(chan int)
ch <- 42  // 永久阻塞（没人接收）
```

### 陷阱 4：循环变量捕获

```go
// Go ≤1.21：循环变量共享
for _, v := range items {
    go func() {
        fmt.Println(v)  // 所有 goroutine 看到相同的 v（最后那个）
    }()
}

// 修复（Go ≤1.21）：传参
for _, v := range items {
    go func(v int) {
        fmt.Println(v)
    }(v)
}

// Go ≥1.22：自动修复，循环变量每次迭代独立
```

---

## 八、性能调优

### GOMAXPROCS

```bash
# 设置并行度（默认 = CPU 核数）
GOMAXPROCS=8 ./myapp

# 或运行时
runtime.GOMAXPROCS(8)
```

### goroutine 数量

```go
// 经验公式：worker 数量 = CPU 核数 × 2~4（CPU 密集）
// worker 数量 = 任务并发数（I/O 密集）
// 避免创建百万 goroutine（OOM）
```

### channel 缓冲

```go
// 小缓冲（1-10）：同步信号
// 大缓冲（100-1000）：异步队列
// 无缓冲：同步握手
```

---

## 关联章节

- **02-concurrency/goroutine**：goroutine 详解
- **02-concurrency/channel**：channel 详解
- **02-concurrency/context**：context 详解
- **02-concurrency/patterns**：实战模式
- **06-advanced/runtime**：GMP 调度器原理

## 一句话总结

> **CSP = goroutine + channel + context**。**Go 让并发从"难题"变成"日常"**。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
