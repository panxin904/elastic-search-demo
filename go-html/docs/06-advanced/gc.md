---
title: GC 三色标记
---

# Go GC 三色标记

**Go GC = 并发三色标记 + 写屏障**——STW < 1ms（Go 1.8+），vs Java G1 几 ms 到几十 ms。

## 一句话总结

> **Go GC = Concurrent Tri-color Mark + Write Barrier + Pacemaker**。**STW 阶段仅 ms 级，业务无感知**。

---

## 一、Go GC 演进

| 版本 | 算法 | STW |
|---|---|---|
| Go 1.0 | STW 全暂停 | 几秒 |
| Go 1.3 | mark-sweep | 几百 ms |
| Go 1.5 | 三色标记 + 写屏障 | < 100ms |
| Go 1.8 | hybrid write barrier | < 1ms |
| Go 1.19 | memory limit | < 1ms |

## 二、三色标记原理

**三种颜色**：
- **White**：未访问（待回收）
- **Grey**：已发现，子节点未扫描
- **Black**：已扫描，子节点已处理

**流程**：
```
初始：所有对象 White
GC 根（栈/全局变量）置 Grey
循环：
  1. 从 Grey 集合取对象
  2. 标 Black
  3. 它引用的子对象标 Grey
直到 Grey 集合空
剩余 White = 垃圾
```

**问题**：用户程序（mutator）并发修改对象，可能导致：
- **漏标**：本应存活的对象被回收 → **严重错误**
- **多标**：本应回收的对象没回收 → **下次回收**

## 三、写屏障（Write Barrier）

**Go 1.8+ hybrid write barrier**：

```go
// 写屏障伪代码
func writePointer(slot, ptr) {
    shade(ptr)  // 将 ptr 染 Grey
    *slot = ptr
}
```

**作用**：mutator 修改引用时，确保被引用对象不漏标。

**两种屏障**：
- **Dijkstra 插入屏障**：写时标灰新引用
- **Yuasa 删除屏障**：写时标灰旧引用

**Go 1.8+ 混合**：
- 启动时 STW 打开插入屏障
- 关闭插入屏障 → 打开删除屏障
- 用 stack rescan 弥补
- 关闭删除屏障

## 四、GC 阶段

```
GC 周期：
  1. STW: GC start (几十微秒)
     - 开 hybrid write barrier
     - 扫描栈 → Grey
  2. Concurrent Mark (并发标记)
     - GC 协程后台跑
     - mutator 继续运行
  3. STW: Mark termination (几十微秒)
     - 关 write barrier
     - 处理剩余工作
  4. Concurrent Sweep (并发清扫)
     - 释放 White 对象
     - mutator 同时分配
```

**Pacemaker**：GC 触发比例（`GOGC=100`）控制 GC 频率。

## 五、GC 调优

```go
import "runtime/debug"

// 1. 调整 GC 触发比例
debug.SetGCPercent(200)  // heap 翻倍才 GC（吞吐优先）
debug.SetGCPercent(50)   // heap 50% 增长就 GC（延迟优先）

// 2. 内存上限（Go 1.19+）
debug.SetMemoryLimit(8 << 30)  // 8GB 硬上限

// 3. 强制 GC
runtime.GC()           // 立刻 GC（生产慎用）
debug.FreeOSMemory()   // GC + 把内存还给 OS

// 4. 监控
import _ "net/http/pprof"
http.ListenAndServe(":6060", nil)
// 访问 http://localhost:6060/debug/pprof/heap
```

## 六、pacer 调优

**Pacer = GC 节奏控制**：

```go
// 目标：堆增长 1 倍时启动下一次 GC
// 计算：trigger = live + live * GOGC / 100
// live = 上次 GC 后存活堆
// GOGC=100 → trigger = 2 * live

// 调整策略
// - 延迟敏感（Web 服务）：GOGC=50，减少 GC 间隔
// - 吞吐敏感（批处理）：GOGC=200，减少 GC 次数
```

**Go 1.19 memory limit**：
- 超过 limit → 强制 GC
- limit 0 = 关闭

## 七、内存分配

```go
// 1. 栈分配
//   - 编译器逃逸分析决定
//   - 不需要 GC
//   - 函数返回自动释放

// 2. 堆分配
//   - runtime.newobject
//   - mcache（线程本地）→ mcentral（全局）→ mheap（OS）
//   - 多种 size class

// 3. 分配优化
//   - 预分配 make([]T, 0, n)
//   - sync.Pool 复用
//   - 避免大对象（>32KB）
//   - 减少指针（减少 GC 扫描）
```

**Go 内存布局**：
```
┌─────────────┐
│   mcache    │  // 线程本地，size class
└─────┬───────┘
      │ 不足
┌─────▼───────┐
│  mcentral   │  // 全局，按 size class 分组
└─────┬───────┘
      │ 不足
┌─────▼───────┐
│   mheap     │  // 调 OS 申请
└─────┬───────┘
      │ 不足
      OS mmap
```

## 八、GC 监控指标

```go
var stats runtime.MemStats
runtime.ReadMemStats(&stats)

stats.Alloc        // 当前使用
stats.HeapAlloc    // 堆使用
stats.HeapObjects  // 对象数
stats.NumGC        // GC 次数
stats.PauseNs      // 最近 GC 暂停时间
stats.PauseTotalNs // 总 GC 暂停
stats.NextGC       // 下次 GC 触发阈值
```

**Prometheus 指标**：
```go
import "github.com/prometheus/client_golang/prometheus"

var goGcDuration = prometheus.NewHistogram(prometheus.HistogramOpts{
    Name:    "go_gc_duration_seconds",
    Help:    "A summary of the GC invocation durations.",
})

// 或者直接用 promhttp.DefaultCollect
http.Handle("/metrics", promhttp.Handler())
```

## 九、GC 触发时机

```go
// 1. 堆增长到 trigger
// 2. 距离上次 GC 超过 forcegcperiod（2 分钟）
// 3. runtime.GC() 强制
// 4. SetMemoryLimit 超限
// 5. 分配大对象（>32KB）绕过 size class
```

## 十、逃逸分析

**决定变量分配在栈还是堆**：

```bash
go build -gcflags='-m' main.go
# 输出
# ./main.go:5:2: moved to heap: x
```

**逃逸场景**：
- 返回局部变量指针
- 闭包引用
- 切片/map 大小未知
- interface{} 装箱
- 大对象（>64KB）

**避免逃逸**：
- 局部变量不取地址
- 用值类型而非指针（结构体小）
- 预分配 slice/map 容量

## 十一、Go GC vs JVM GC

| 维度 | Go GC | Java G1/ZGC |
|---|---|---|
| 算法 | 三色标记 + 写屏障 | 分代 + 并发标记 |
| STW | < 1ms | G1: 几十 ms, ZGC: < 1ms |
| 分代 | 无 | 有（年轻代/老年代） |
| 调优 | 简单 | 复杂（10+ 参数） |
| 分配 | 栈优先 | 堆优先 |
| 适合 | I/O bound / 微服务 | 计算密集 / 大堆 |

**Go GC 优势**：
- 简单：少参数（GOGC / memory limit）
- 延迟：< 1ms STW
- 协作：mutator 友好

**Go GC 劣势**：
- 无分代：长生命周期对象反复扫描
- 大堆效率低（建议 4GB 以下）

## 关联章节

- **06-advanced/runtime**：GMP 调度
- **06-advanced/pprof**：性能分析
- **03-ecosystem/benchmark**：pprof 用法

## 一句话总结

> **Go GC = Concurrent Tri-color + Write Barrier**。**STW < 1ms，延迟友好**。
