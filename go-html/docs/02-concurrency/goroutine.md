---
title: goroutine
date: 2026-08-15  # date-auto-injected
---

![Go GMP 调度模型（work-stealing）](/go-gmp-scheduler.svg)

# goroutine

goroutine 是 Go 最核心的并发原语：轻量协程，由 Go runtime 调度，单个程序可同时运行数十万个 goroutine。

## 一句话总结

> **goroutine = Go runtime 调度的协程（M:N 模型）**。**核心：go 关键字启动 / 2KB 栈 / GMP 调度 / 协作式+抢占式调度**。

---

## 一、基本用法

```go
// 启动 goroutine
go func() {
    fmt.Println("hello from goroutine")
}()

// 启动带参数的 goroutine
go func(msg string) {
    fmt.Println(msg)
}("hello")

// 启动调用方法的 goroutine
go obj.Method()
```

### 与函数调用的对比

```go
// 同步调用（阻塞）
func() {
    fmt.Println("sync")
}()

// 异步调用（不阻塞）
go func() {
    fmt.Println("async")
}()
fmt.Println("main")
// 输出：main（顺序不固定，async 可能先输出）
```

---

## 二、goroutine 生命周期

### 状态机

```
        ┌──────────┐
        │  Created │ (go 关键字创建)
        └─────┬────┘
              ▼
        ┌──────────┐
        │ Runnable │ (加入队列，等待调度)
        └─────┬────┘
              ▼
        ┌──────────┐
        │ Running  │ (M 上执行)
        └─────┬────┘
              ▼
        ┌──────────┐
        │  Waiting │ (channel / IO / syscall 阻塞)
        └─────┬────┘
              ▼
        ┌──────────┐
        │   Dead   │ (函数返回 / panic)
        └──────────┘
```

### goroutine 退出

```go
// 1. 函数返回：goroutine 正常结束
go func() {
    fmt.Println("done")
}()  // 函数返回后 goroutine 死亡

// 2. 主 goroutine 退出：所有 goroutine 强制结束
func main() {
    go func() {
        time.Sleep(10 * time.Second)
    }()
    // main 直接返回，未等 goroutine 完成
}

// 3. panic 未捕获：goroutine 死亡
go func() {
    panic("oops")  // goroutine crash，不影响 main
}()

// 4. context 取消：goroutine 主动退出
ctx, cancel := context.WithCancel(context.Background())
go func() {
    <-ctx.Done()
    fmt.Println("cancelled")
}()
cancel()
```

---

## 三、GMP 调度模型

### 三个核心组件

```
G (Goroutine) — 用户态协程（初始栈 2KB）
M (Machine)   — OS 线程
P (Processor) — 逻辑处理器（默认 GOMAXPROCS = CPU 核数）
```

### 调度流程

```
1. go func() 创建 G
2. G 加入 P 的 local run queue
3. M（绑定了 P）从 local queue 取 G 执行
4. local queue 满（256）→ 移动到 global queue
5. local queue 空 → work stealing（从其他 P 偷 G）
6. global queue 空 → 从 net poller / syscall 返回的 G 取
```

### M:N 调度优势

| 模型 | 调度方 | 数量级 |
|---|---|---|
| **1:1** (Java Thread) | OS kernel | 千级别 |
| **N:1** (Python asyncio) | 用户态 | 单线程 |
| **M:N** (Go) | Go runtime | 数十万 |

- **轻量**：创建 / 切换成本低
- **透明**：开发者无感
- **可扩展**：单进程轻松支持百万 goroutine

---

## 四、GOMAXPROCS

### 设置并行度

```go
// 默认 = CPU 核数
runtime.GOMAXPROCS(8)

// 通过环境变量
// GOMAXPROCS=4 ./myapp

// 查看当前值
fmt.Println(runtime.GOMAXPROCS(0))
```

### 何时调整

- **CPU 密集任务**：GOMAXPROCS = CPU 核数
- **I/O 密集任务**：可适当调大（让 M 多等待 syscall）
- **容器环境**：GOMAXPROCS 应该 = 容器 CPU limit（可用 `automaxprocs` 自动检测）

### uber-go/automaxprocs

```go
import _ "go.uber.org/automaxprocs"

// 启动时自动检测容器 CPU limit 并设置 GOMAXPROCS
```

---

## 五、goroutine 实战

### 1. 并行计算

```go
func parallelSum(nums []int) int {
    n := len(nums)
    if n == 0 { return 0 }

    mid := n / 2
    sumCh := make(chan int, 2)

    go func() {
        s := 0
        for _, v := range nums[:mid] {
            s += v
        }
        sumCh <- s
    }()

    go func() {
        s := 0
        for _, v := range nums[mid:] {
            s += v
        }
        sumCh <- s
    }()

    return <-sumCh + <-sumCh
}
```

### 2. goroutine 池

```go
type WorkerPool struct {
    jobs    chan Job
    results chan Result
    workers int
}

func NewWorkerPool(workers int) *WorkerPool {
    return &WorkerPool{
        jobs:    make(chan Job, 100),
        results: make(chan Result, 100),
        workers: workers,
    }
}

func (p *WorkerPool) Start() {
    for i := 0; i < p.workers; i++ {
        go func(workerID int) {
            for job := range p.jobs {
                p.results <- processJob(job)
            }
        }(i)
    }
}
```

### 3. goroutine 监控

```go
import "runtime"

// 当前 goroutine 数量
fmt.Println("goroutines:", runtime.NumGoroutine())

// 设置最多 goroutine（软限制）
runtime.GOMAXPROCS(8)

// 强制 GC（一般不需要）
runtime.GC()
```

---

## 六、goroutine 泄漏

### 什么是泄漏

goroutine 启动后**永远无法结束**，占用内存不释放。

### 常见原因

```go
// 1. channel 永远没人接收
func leak1() {
    ch := make(chan int)
    go func() { ch <- 1 }()  // 永久阻塞
}

// 2. 死锁
func leak2() {
    var mu sync.Mutex
    mu.Lock()
    go func() { mu.Lock() }()  // 永久阻塞
}

// 3. 死循环
func leak3() {
    go func() {
        for {
            // 没有退出条件
        }
    }()
}

// 4. select 缺少退出分支
func leak4() {
    ch := make(chan int)
    go func() {
        select {
        case <-ch:
            // 永远不会执行
        }
    }()
}
```

### 检测泄漏

```go
// pprof 检测
import _ "net/http/pprof"

// goroutine profile
curl http://localhost:6060/debug/pprof/goroutine?debug=2

// 输出：所有 goroutine 的堆栈
// 如果某个 goroutine 数量持续增长 → 泄漏
```

### 修复模式

```go
// 用 context 退出
func noLeak(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case <-ch:
            // work
        case <-ctx.Done():
            return
        }
    }()
}
```

---

## 七、goroutine 调试

### 1. runtime.Stack

```go
buf := make([]byte, 1<<16)
n := runtime.Stack(buf, true)  // true = 所有 goroutine
fmt.Println(string(buf[:n]))
```

### 2. pprof goroutine profile

```go
import _ "net/http/pprof"

go http.ListenAndServe("localhost:6060", nil)
```

```bash
# 浏览器查看
http://localhost:6060/debug/pprof/goroutine?debug=1

# 命令行
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

### 3. goleak 工具

```go
import "go.uber.org/goleak"

func TestNoLeak(t *testing.T) {
    defer goleak.VerifyNone(t)
    // ...
}
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/channel**：channel
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context
- **02-concurrency/patterns**：并发模式
- **06-advanced/runtime**：GMP 调度器

## 一句话总结

> **goroutine = 轻量协程 + M:N 调度 + GMP 模型**。**几十行代码启动数万个并发任务**。


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

<!-- svg-injected:do-not-edit -->

## 图示：Go GMP 调度模型

![Go GMP 调度模型](/go-goroutine.svg)
