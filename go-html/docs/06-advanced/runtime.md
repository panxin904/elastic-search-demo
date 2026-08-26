---
title: runtime 调度器 GMP
---

# Go runtime 与 GMP 调度

**Go runtime = GMP 调度器 + GC + goroutine + channel**——理解它 = 写出高性能 Go。

## 一句话总结

> **GMP = G (goroutine) + M (machine/OS thread) + P (processor/逻辑 CPU)**。**work-stealing + hand-off 调度算法**。

---

## 一、GMP 模型

```
┌─────┐         ┌─────┐
│  M1 │ ── P1 ──┤ LRQ │ Local Run Queue (256 slots)
└─────┘    │    └─────┘
           │
           │    ┌────────────┐
           │    │   GRQ      │ Global Run Queue
           │    │ (unlimited)│
           │    └────────────┘
┌─────┐    │    ┌─────┐
│  M2 │ ── P2 ──┤ LRQ │
└─────┘         └─────┘
   ▲                ▲
   │                │
   └──syscall───────┘
```

- **G（Goroutine）**：用户态协程，初始栈 2KB
- **M（Machine）**：OS 线程，由 runtime 管理
- **P（Processor）**：逻辑 CPU，持有 LRQ；M 必须绑定 P 才能执行 G
- **LRQ**：每个 P 的本地队列，256 槽位
- **GRQ**：全局队列，无 M 偷取时新 G 放这里

## 二、调度算法

```go
// runtime/proc.go
func schedule() *g {
    top:
        gp, inheritTime, _ := runqget(_p_)  // 1. 优先从 LRQ 取
        if gp == nil {
            gp, inheritTime = globrunqget(_, _p_)  // 2. LRQ 空，从 GRQ 取
        }
        if gp == nil {
            gp, inheritTime = runqsteal(_p_, sched)  // 3. 偷其他 P 的一半 LRQ
        }
        if gp == nil {
            gp, _ = findrunnable()  // 4. 偷 + GC + polling
        }
        return gp
}
```

**调度时机**：
1. goroutine 阻塞（syscall / channel / IO）
2. goroutine 主动让出（runtime.Gosched()）
3. goroutine 运行时间过长（10ms 强制调度）
4. 启动新 goroutine

## 三、goroutine 创建

```go
go func() {  // go func
    // 1. newproc → g
    // 2. 优先放当前 P 的 LRQ
    // 3. LRQ 满（256）放 GRQ
}()

// runtime 内部
func newproc(siz int32, fn *funcval) {
    _p_ := getg().m.p.ptr()
    newg := gfget(_p_)  // 优先复用空闲 g
    if newg == nil {
        newg = malg(_StackMin)  // 分配新的 g
    }
    runqput(_p_, newg, true)  // 放 LRQ
}
```

## 四、M 数量控制

```go
// GOMAXPROCS = P 数量 = 可同时执行的 M 数量
// 默认 = CPU 核数
runtime.GOMAXPROCS(8)

// M 数量无上限（最大 10000）
// 但实际 M >> P 会导致线程切换开销
// M 阻塞在 syscall 时，P 会解绑给其他 M
```

**Syscall 处理**：
```
G 调 syscall → M 阻塞 → P 解绑 → GRQ 或其他 M 接管 → syscall 返回后 P 再绑定
```

**netpoller（Go 核心黑科技）**：
- Linux epoll / macOS kqueue
- goroutine 网络 IO 不阻塞 M
- epoll_wait 后唤醒 G

## 五、栈管理

```go
// goroutine 栈：动态伸缩
// 初始 2KB，最大 1GB（默认）
// 每次函数调用检查栈是否够
// 不够就 grow

// runtime/stack.go
func newstack() {
    // 分配 2 倍新栈
    // 拷贝旧栈内容
    // 调整指针
    // 用 copystack
}
```

**栈拷贝**：
- 1.x 之前是 split stack（hot split 性能问题）
- 1.x 之后是 contiguous stack（一次 grow，2x）

## 六、抢占式调度（Go 1.14+）

**问题**：goroutine 里死循环，runtime 没法调度其他 G。

**Go 1.14 引入基于信号的抢占**：
- sysmon 线程发送 SIGURG
- 目标 G 的 signal handler 检查是否需要让出
- 强制调度点

```go
// runtime/proc.go
func retake(now int64) uint32 {
    // 1. M 在 syscall 超 10ms：解绑 P
    // 2. G 运行超过 10ms：发 SIGURG 抢占
}
```

**Go 1.14 之前**：只能依靠函数调用作为调度点，纯 for 循环无法抢占。

## 七、调度可视化

**GODEBUG**：

```bash
GODEBUG=schedtrace=1000 ./myapp
# 输出每秒调度器状态：
# SCHED 0ms: gomaxprocs=8 idleprocs=8 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0 0 0 0 0 0 0]

GODEBUG=scheddetail=1,schedtrace=1000 ./myapp
# 详细：每个 P 的状态
```

**trace**（更强大）：

```go
import "runtime/trace"
f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
```

```bash
go tool trace trace.out
# 浏览器看时序图
```

## 八、runtime 调优

```go
// 1. GOMAXPROCS
runtime.GOMAXPROCS(runtime.NumCPU())  // 容器环境按 CPU limit 设置

// 2. 调试
import _ "net/http/pprof"
go func() { http.ListenAndServe(":6060", nil) }()

// 3. 内存分配
debug.SetGCPercent(100)        // GC 触发比例
debug.SetMemoryLimit(8 << 30)  // 8GB 内存上限（Go 1.19+）
debug.SetMaxStack(1 << 20)     // 单 goroutine 栈最大

// 4. goroutine 数量
runtime.NumGoroutine()
```

## 九、runtime 关键函数

```go
// goroutine
runtime.Goexit()       // 退出当前 goroutine
runtime.Gosched()      // 让出 CPU
runtime.NumGoroutine() // goroutine 数量

// 内存
runtime.ReadMemStats(&m)
runtime.MemStats{Alloc, HeapAlloc, NumGC, PauseNs, ...}

// GC
runtime.GC()           // 强制 GC
debug.SetGCPercent(n)  // GC 触发比例
debug.FreeOSMemory()   // 强制返回 OS 内存

// 锁
runtime.LockOSThread() // 锁线程
runtime.UnlockOSThread()
```

## 十、真实问题排查

**问题 1：goroutine 泄漏**
```go
// ❌ 死循环
go func() {
    for {
        // 不退出
    }
}()

// ✅ context 退出
ctx, cancel := context.WithCancel(ctx)
go func() {
    for {
        select {
        case <-ctx.Done(): return
        default:
            // work
        }
    }
}()
```

**问题 2：调度延迟**
```bash
# 看 GODEBUG=schedtrace 中 stw（Stop The World）时间
SCHED 1000ms: ... stw=2.0ms
# stw > 10ms 需要调优
```

**问题 3：M 太多**
```go
// 看 runtime.Stack 是否有大量 M 在 syscall
buf := make([]byte, 1<<20)
runtime.Stack(buf, true)
fmt.Println(string(buf))
```

## 关联章节

- **02-concurrency/goroutine**：goroutine 基础
- **06-advanced/gc**：GC
- **06-advanced/pprof**：性能分析

## 一句话总结

> **GMP = G (goroutine) + M (machine) + P (processor) + work-stealing**。**Go 调度的灵魂**。


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
