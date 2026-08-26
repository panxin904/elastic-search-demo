---
title: Go pprof 剖析
description: Go 内置的性能剖析工具
---

# Go pprof 剖析

> **TL;DR**：**Go pprof = Go 内置的 profiler**（runtime/pprof 包 + net/http/pprof）。**支持 5 类 profile：CPU / Heap / Goroutine / Block / Mutex**。**可视化：go tool pprof + 火焰图（brendangregg/FlameGraph）**。**生产标配：开启 pprof HTTP 端口 + 持续收集 + 自动化分析**。

## 一句话定义

```
Go pprof = Go runtime 内置的性能剖析工具
         = 5 类 profile：
           - CPU（CPU 时间）
           - Heap（堆内存分配）
           - Goroutine（协程栈）
           - Block（阻塞事件）
           - Mutex（锁竞争）
         = 可视化：火焰图 / 树状图 / 调用图
```

## 启用 pprof

```go
// 1. 在 main 函数中开启（生产环境）
import (
    "net/http"
    _ "net/http/pprof"   // 自动注册 /debug/pprof 路由
)

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
    // 业务代码
}
```

```bash
# 2. 抓取 profile
# CPU profile（30 秒）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap profile（堆内存）
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine（当前所有 goroutine 栈）
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Block（阻塞事件）
go tool pprof http://localhost:6060/debug/pprof/block

# Mutex（锁竞争）
go tool pprof http://localhost:6060/debug/pprof/mutex
```

## 火焰图生成

```bash
# 1. 安装 FlameGraph 脚本
git clone https://github.com/brendangregg/FlameGraph.git
export PATH=$PATH:./FlameGraph

# 2. CPU profile → 火焰图
go tool pprof -raw -output=cpu.raw http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof -top cpu.raw

# 或生成火焰图 SVG
go tool pprof -svg cpu.raw > cpu.svg

# 3. 直接可视化
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile?seconds=30
# 浏览器打开 http://localhost:8080
```

## Heap 分析

```bash
# 1. 当前内存使用
go tool pprof -inuse_space http://localhost:6060/debug/pprof/heap

# 2. 累计分配字节（找内存泄漏点）
go tool pprof -alloc_space http://localhost:6060/debug/pprof/heap

# 3. 累计分配对象数
go tool pprof -alloc_objects http://localhost:6060/debug/pprof/heap

# 4. 找泄漏 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutine.txt
# 看 goroutine 数量 + 阻塞在哪个 channel/lock
```

## 持续剖析（Pyroscope 集成）

```go
// 用 Pyroscope + pprof 自动采集
import "github.com/grafana/pyroscope-go"

func main() {
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "my-service",
        ServerAddress:   "http://pyroscope:4040",
        Tags: map[string]string{
            "env":     "prod",
            "version": "1.0.0",
        },
        ProfileTypes: []pyroscope.ProfileType{
            pyroscope.ProfileCPU,
            pyroscope.ProfileAllocObjects,
            pyroscope.ProfileAllocSpace,
            pyroscope.ProfileInuseObjects,
            pyroscope.ProfileInuseSpace,
            pyroscope.ProfileGoroutines,
        },
    })
    // 业务代码
}
```

## 实战案例：定位内存泄漏

```bash
# 1. 抓两次 heap（间隔 5 分钟）
curl -o heap1.pb.gz http://localhost:6060/debug/pprof/heap
sleep 300
curl -o heap2.pb.gz http://localhost:6060/debug/pprof/heap

# 2. 对比两次内存增长
go tool pprof -base heap1.pb.gz heap2.pb.gz
# (pprof) top
# Showing nodes accounting for 1500MB, 95% of 1580MB total
#       flat  flat%   sum%        cum   cum%
#    1200MB 75.9% 75.9%   1200MB 75.9%  bytes.makeSlice
#     200MB 12.7% 88.6%    300MB 19.0%  cache.(*LRU).Add

# 3. 火焰图看调用链
go tool pprof -http=:8080 -base heap1.pb.gz heap2.pb.gz
```

## 实战案例：定位 goroutine 泄漏

```bash
# 1. 看 goroutine 数量
curl http://localhost:6060/debug/pprof/goroutine?debug=1 | head -20

# 2. dump 所有 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutines.txt
grep -A 20 "goroutine profile:" goroutines.txt | head -30
# 看哪些 goroutine 数量异常（应该 ≤ CPU 数 * 2）
```

## 实战案例：定位锁竞争

```go
// 1. 在 main 中启用 mutex profile
runtime.SetMutexProfileFraction(5)   // 5% 采样
```

```bash
# 2. 抓 mutex profile
go tool pprof http://localhost:6060/debug/pprof/mutex

# (pprof) top
# Showing nodes accounting for 800ms, 90% of 888ms total
#       flat  flat%   sum%        cum   cum%
#      500ms 56.3% 56.3%    500ms 56.3%  sync.(*Mutex).Lock
#      300ms 33.8% 89.9%    800ms 90.1%  mypkg.(*Cache).Get
```

## 一句话总结

> **Go pprof = Go 内置 profiler**。**5 类 profile：CPU / Heap / Goroutine / Block / Mutex**。**生产标配：pprof HTTP 端口 + Pyroscope 持续剖析**。

---

## 关联章节

- [持续剖析](./continuous-profiling.md) — Continuous Profiling
- [Pyroscope](./pyroscope.md) — 多语言持续剖析
- [Java async-profiler](./async-profiler.md) — Java 等价工具

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
