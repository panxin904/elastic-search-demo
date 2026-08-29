---
title: 性能基准与 pprof
date: 2026-08-15  # date-auto-injected
---

# Go 性能基准与 pprof

**Go 的性能分析是其他语言望尘莫及的**——`pprof` + `trace` + `benchstat` 三大武器。

## 一句话总结

> **Go 性能 = benchmark + pprof CPU/Heap/Goroutine + trace 时序图 + benchstat 对比**。**10 行代码接入，定位慢在哪儿**。

---

## 一、Benchmark 基础

**测试函数命名**：`BenchmarkXxx(b *testing.B)`

```go
// 简单基准
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}

// table-driven
func BenchmarkAdd_TableDriven(b *testing.B) {
    cases := []struct{ name string; a, b int }{
        {"small", 1, 2},
        {"large", 1 << 30, 1 << 30},
    }
    for _, c := range cases {
        b.Run(c.name, func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                Add(c.a, c.b)
            }
        })
    }
}
```

**运行**：
```bash
go test -bench=.                              # 全部
go test -bench=BenchmarkAdd -benchmem         # 内存分配
go test -bench=. -benchtime=10s               # 跑 10 秒
go test -bench=. -count=5                     # 跑 5 次（统计）
go test -bench=. -cpu=1,2,4,8                 # 不同 GOMAXPROCS
```

**输出**：
```
BenchmarkAdd-8    1000000000    0.254 ns/op    0 B/op    0 allocs/op
```
- `-8`：8 核
- `1000000000`：b.N
- `0.254 ns/op`：每次耗时
- `0 B/op`：每次分配字节
- `0 allocs/op`：每次分配次数

## 二、benchstat — 对比基准

```bash
go install golang.org/x/perf/cmd/benchstat@latest

# 跑两次保存结果
go test -bench=. -count=10 > old.txt
# 改代码...
go test -bench=. -count=10 > new.txt

# 对比
benchstat old.txt new.txt
```

**输出**：
```
name      old time/op  new time/op  delta
Add-8     0.30ns ± 2%  0.25ns ± 1%  -16.67%  (p=0.000 n=10+10)
```

带置信区间，p-value，**科学对比**。

## 三、Reset / Stop / RunParallel

```go
func BenchmarkComplex(b *testing.B) {
    // 一次性 setup（不算入 b.N）
    expensiveSetup()
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        Complex()
    }
}

// 并行基准
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Complex()
        }
    })
}
```

## 四、pprof 五大类型

```go
import "runtime/pprof"

// 1. CPU profile
f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
// 跑被测代码

// 2. Heap profile（内存）
f, _ := os.Create("heap.prof")
pprof.WriteHeapProfile(f)

// 3. Goroutine profile
pprof.Lookup("goroutine").WriteTo(f, 0)

// 4. Block profile（阻塞）
runtime.SetBlockProfileRate(1)
pprof.Lookup("block").WriteTo(f, 0)

// 5. Mutex profile
runtime.SetMutexProfileFraction(1)
pprof.Lookup("mutex").WriteTo(f, 0)
```

**生产级 pprof — 暴露 HTTP 端点**：

```go
import "net/http/pprof"

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)  // pprof 端点
    }()
    // 业务代码...
}
```

**访问**：
- `http://localhost:6060/debug/pprof/` — 浏览器看索引
- `http://localhost:6060/debug/pprof/profile?seconds=30` — 30s CPU profile
- `http://localhost:6060/debug/pprof/heap` — 堆 profile
- `http://localhost:6060/debug/pprof/goroutine` — goroutine profile
- `http://localhost:6060/debug/pprof/trace?seconds=5` — execution trace

**生产环境**注意加鉴权！

## 五、go tool pprof 分析

```bash
# 交互式
go tool pprof cpu.prof
(pprof) top 10          # CPU 占用 top 10
(pprof) list Add        # 看 Add 函数源码级火焰
(pprof) web             # 生成 .svg 浏览器看
(pprof) peek Add        # 看调用链
(pprof) traces          # 看调用 trace

# 直接给 URL（实时采样）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

**火焰图**：
```bash
# 安装 FlameGraph
go install github.com/uber/go-torch@latest
go-torch -seconds 30 http://localhost:6060/debug/pprof/profile

# 或用 pprof 自带
go tool pprof -http=:8080 cpu.prof
# 浏览器打开 http://localhost:8080 看交互式火焰图
```

## 六、Execution Trace

**最强大工具**，看 goroutine 调度、GC、系统调用、阻塞：

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
# - View trace：时序图
# - Goroutine analysis
# - Network blocking profile
# - Synchronization blocking profile
# - Syscall blocking profile
```

**解决**：goroutine 阻塞、调度延迟、GC 停顿。

## 七、逃逸分析

**关键问题**：变量分配在栈还是堆？

```bash
go build -gcflags='-m' main.go
# 输出：moved to heap: x
```

**判定**：
- 返回局部变量指针 → 逃逸到堆
- 闭包引用 → 逃逸
- 切片/map 大小未知 → 逃逸
- interface{} 装箱 → 逃逸

**优化**：
- 避免大结构体传值（用指针）
- sync.Pool 重用对象
- 预分配 slice/map：`make([]T, 0, 100)`

## 八、内存优化技巧

```go
// ❌ 低效：每次 append 可能重新分配
var s []int
for i := 0; i < 1000; i++ {
    s = append(s, i)
}

// ✅ 高效：预分配
s := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    s = append(s, i)
}

// ❌ strings.Builder 低效
var s string
for _, v := range values {
    s += strconv.Itoa(v)  // 每次新建 string
}

// ✅ strings.Builder 高效
var b strings.Builder
b.Grow(1000)  // 预分配
for _, v := range values {
    b.WriteString(strconv.Itoa(v))
}
s := b.String()
```

## 九、常见性能陷阱

1. **defer 性能**：在热循环里 defer 有开销（虽然已经优化到 ~35ns）
2. **interface{} 装箱**：用泛型（Go 1.18+）替代
3. **map[string]X 取不到值**：两次 hash + 内存分配，用 sync.Map / map[uint64]X
4. **string/[]byte 转换**：用 unsafe 避免拷贝（`*(*string)(unsafe.Pointer(&b))`）
5. **GC 压力**：高频对象用 sync.Pool
6. **过多 goroutine**：worker pool 控制并发数
7. **同步锁竞争**：用 atomic 或 channel 替代

## 十、真实案例

**案例：JSON 序列化慢**：
```go
// 优化前：json.Marshal 5ms/op
// 优化方案：
// 1. jsoniter：2ms/op
// 2. easyjson：0.5ms/op（代码生成）
// 3. protobuf：0.1ms/op（跨服务推荐）
```

**案例：字符串拼接慢**：
```go
// 优化前：+= 50ms/op
// 优化后：strings.Builder 5ms/op（10x）
```

## 关联章节

- **03-ecosystem/testing**：单元测试
- **06-advanced/pprof**：runtime pprof 详解
- **06-advanced/runtime**：GMP 调度
- **06-advanced/gc**：GC 调优

## 一句话总结

> **Go 性能 = benchmark + pprof + trace + 逃逸分析**。**内置工具链够用，无需 async-profiler / YourKit**。


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
