---
title: pprof 与 trace
date: 2026-08-15  # date-auto-injected
---

# Go pprof 与 trace

**pprof = Go 内置性能分析**——CPU / heap / goroutine / block / mutex / trace 全覆盖。

## 一句话总结

> **pprof = 5 种 profile（CPU/heap/goroutine/block/mutex）+ trace 时序图**。**生产 10 行接入，定位慢在哪儿**。

---

## 一、五大 profile 类型

| Profile | 抓什么 | 何时用 |
|---|---|---|
| **CPU** | 函数执行时间 | CPU 100% |
| **Heap** | 内存分配 / 堆对象 | 内存泄漏 / OOM |
| **Goroutine** | goroutine 栈 | goroutine 泄漏 |
| **Block** | 阻塞（channel / IO / syscall） | 卡顿 |
| **Mutex** | 锁竞争 | 锁争抢 |

## 二、HTTP 端点（推荐生产方式）

```go
import (
    "net/http"
    "net/http/pprof"
    "runtime"
)

func main() {
    runtime.SetMutexProfileFraction(5)  // 开启 mutex profile
    runtime.SetBlockProfileRate(1)       // 开启 block profile
    
    mux := http.NewServeMux()
    mux.HandleFunc("/debug/pprof/", pprof.Index)
    mux.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
    mux.HandleFunc("/debug/pprof/profile", pprof.Profile)
    mux.HandleFunc("/debug/pprof/symbol", pprof.Symbol)
    mux.HandleFunc("/debug/pprof/trace", pprof.Trace)
    
    // 单独端点（auth）
    go func() {
        http.ListenAndServe("localhost:6060", mux)  // ⚠️ 加 auth
    }()
}
```

**访问**：
- `http://localhost:6060/debug/pprof/` — 索引
- `http://localhost:6060/debug/pprof/profile?seconds=30` — 30s CPU
- `http://localhost:6060/debug/pprof/heap` — heap
- `http://localhost:6060/debug/pprof/goroutine` — goroutine
- `http://localhost:6060/debug/pprof/trace?seconds=5` — trace

**生产**：
- 防火墙限制访问 IP
- 或加 basic auth
- 或走 sidecar

## 三、CPU profile

```bash
# 远程抓 30s CPU
curl http://localhost:6060/debug/pprof/profile?seconds=30 -o cpu.prof

# 交互分析
go tool pprof cpu.prof
(pprof) top 10
      flat  flat%   sum%        cum   cum%
         0     0%   50.0%     8.50s 50.0%  runtime.scanobject
     1.50s 8.33%  58.3%     3.00s 16.7%  compress/flate.(*compressor).deflate
# flat：函数本身耗时
# cum：函数 + 调用链总耗时

(pprof) list myFunction
# 看 myFunction 每行耗时

(pprof) web
# 生成 callgraph.svg，浏览器看调用图
```

**火焰图**：
```bash
# pprof 自带 -http
go tool pprof -http=:8080 cpu.prof
# 浏览器打开 http://localhost:8080 → View → Flame Graph
```

## 四、Heap profile

```bash
# 远程抓 heap
curl http://localhost:6060/debug/pprof/heap -o heap.prof

# 分析
go tool pprof heap.prof
(pprof) top 10 -cum
(pprof) list myAllocFunc
(pprof) alloc_space  # 按分配字节
(pprof) inuse_space  # 按当前使用字节
(pprof) alloc_objects
(pprof) inuse_objects
```

**关键指标**：
- **alloc_space**：从启动累计分配字节（含已 GC）
- **inuse_space**：当前使用字节
- **alloc_objects**：累计分配对象数
- **inuse_objects**：当前存活对象数

**代码中**：
```go
import "runtime/pprof"

pprof.Lookup("heap").WriteTo(f, 0)
```

## 五、Goroutine profile

```bash
# 抓当前所有 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2
# 详细文本输出

# profile 格式
curl http://localhost:6060/debug/pprof/goroutine -o goroutine.prof
go tool pprof goroutine.prof
(pprof) top
(pprof) trace  # 看调用链
```

**代码**：
```go
import "runtime/pprof"

pprof.Lookup("goroutine").WriteTo(f, 0)
```

**泄漏排查**：
```go
// 1. 启动时基线
buf1 := make([]byte, 1<<20)
runtime.Stack(buf1, true)
os.WriteFile("goroutines.before.txt", buf1, 0644)

// 2. 运行一段时间后再抓
buf2 := make([]byte, 1<<20)
runtime.Stack(buf2, true)
os.WriteFile("goroutines.after.txt", buf2, 0644)

// 3. diff 找新增的 goroutine
diff goroutines.before.txt goroutines.after.txt
```

## 六、Block profile（阻塞）

```go
// 必须先开
runtime.SetBlockProfileRate(1)  // 1ns 以上的阻塞都记录
```

```bash
curl http://localhost:6060/debug/pprof/block -o block.prof
go tool pprof block.prof
(pprof) top
# 看哪些函数阻塞最久（channel / mutex / select / IO）
```

## 七、Mutex profile（锁竞争）

```go
runtime.SetMutexProfileFraction(5)  // 5 次竞争采样 1 次
```

```bash
curl http://localhost:6060/debug/pprof/mutex -o mutex.prof
go tool pprof mutex.prof
```

**降低锁竞争**：
- 减小临界区
- sync.RWMutex 替代 Mutex
- 用 atomic 操作
- sharded map

## 八、Execution Trace

**最强大工具**，看 goroutine 调度、GC、syscall、阻塞全时序。

```go
import "runtime/trace"

f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// 跑被测代码
```

```bash
go tool trace trace.out
# 浏览器打开，5 个 tab：
# 1. View trace：时序图（goroutine 状态、GC、syscall、运行、阻塞）
# 2. Goroutine analysis：按 goroutine 状态统计
# 3. Network blocking profile
# 4. Synchronization blocking profile
# 5. Syscall blocking profile
```

**生产**：远程抓
```bash
curl http://localhost:6060/debug/pprof/trace?seconds=5 -o trace.out
go tool trace trace.out
```

## 九、火焰图

**Uber go-torch**（已弃用，推荐 pprof 自带）：

```bash
go install github.com/uber/go-torch@latest
go-torch -seconds 30 http://localhost:6060/debug/pprof/profile
# 生成 flamegraph.svg
```

**pprof 自带**：
```bash
go tool pprof -http=:8080 cpu.prof
# 浏览器 http://localhost:8080
# 菜单 View → Flame Graph
```

## 十、连续 profile（持续监控）

**pyroscope**（推荐开源）：

```go
import "github.com/pyroscope-io/client/pyroscope"

pyroscope.Start(pyroscope.Config{
    ApplicationName: "myapp",
    ServerAddress:   "http://pyroscope:4040",
    Tags:            map[string]string{"env": "prod"},
})
```

**parca**（CNCF）：eBPF 抓取，无需代码侵入。

## 十一、Profile-guided Optimization (PGO)

**Go 1.20+ PGO**：

```bash
# 1. 抓 default profile
go test -bench=. -cpuprofile=default.pgo

# 2. 用 PGO 编译（自动检测 default.pgo）
go build -pgo=default.pgo -o myapp .

# 3. 性能提升 2-7%（来自标准库）
```

**生产建议**：
- 关键服务持续抓取 CPU profile
- 定期重新编译启用 PGO

## 十二、真实排查案例

**案例 1：CPU 100%**

```bash
# 1. 抓 CPU profile
curl http://localhost:6060/debug/pprof/profile?seconds=30 -o cpu.prof
# 2. 看 top
go tool pprof -top -cum cpu.prof
# 3. 找到热点函数，list 看具体行
go tool pprof -list hotFunc cpu.prof
```

**案例 2：内存增长**

```bash
# 1. 抓 heap
curl http://localhost:6060/debug/pprof/heap -o heap.prof
# 2. 看 alloc_space（累计分配）
go tool pprof -top -cum -sample_index=alloc_space heap.prof
# 3. 找到分配最多的函数
```

**案例 3：goroutine 泄漏**

```bash
# 1. 抓 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 | head -100
# 2. 看哪些 goroutine 数量异常
curl http://localhost:6060/debug/pprof/goroutine?debug=2 | grep "^goroutine" | awk '{print $2}' | sort | uniq -c | sort -rn | head
```

**案例 4：调度延迟**

```bash
# 1. 抓 trace
curl http://localhost:6060/debug/pprof/trace?seconds=10 -o trace.out
# 2. 看 trace 里 GC、syscall、阻塞占比
go tool trace trace.out
```

## 关联章节

- **06-advanced/runtime**：GMP 调度
- **06-advanced/gc**：GC
- **03-ecosystem/benchmark**：benchmark

## 一句话总结

> **pprof + trace = Go 性能调优的瑞士军刀**。**10 行代码接入，无三方依赖**。


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
