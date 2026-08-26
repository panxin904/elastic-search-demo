---
title: sync 包
---

# sync 包

Go 标准库 sync 包提供传统并发原语：Mutex、WaitGroup、Once、Pool 等。channel 是 Go 的"高级抽象"，sync 包则是"底层原语"。

## 一句话总结

> **sync 包 = Mutex + WaitGroup + Once + Pool + atomic**。**核心：锁保护共享内存 + 信号量同步 + 对象池复用**。

---

## 一、Mutex（互斥锁）

### 基本用法

```go
var (
    mu sync.Mutex
    counter int
)

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}
```

### RWMutex（读写锁）

```go
var (
    rwmu sync.RWMutex
    config map[string]string
)

// 读（多个 goroutine 可同时读）
func get(key string) string {
    rwmu.RLock()
    defer rwmu.RUnlock()
    return config[key]
}

// 写（独占）
func set(key, value string) {
    rwmu.Lock()
    defer rwmu.Unlock()
    config[key] = value
}
```

### Mutex vs RWMutex 选择

| 场景 | 推荐 |
|---|---|
| 读多写少（>10:1） | RWMutex |
| 写多读少 | Mutex |
| 简单计数 / 状态 | Mutex 或 atomic |

---

## 二、WaitGroup（等待组）

### 基本用法

```go
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)  // 计数器 +1
    go func(i int) {
        defer wg.Done()  // 计数器 -1
        fmt.Println(i)
    }(i)
}

wg.Wait()  // 阻塞直到计数器 = 0
```

### 注意事项

```go
// ❌ 错：Add 在 goroutine 内（可能 Wait 已经返回）
for i := 0; i < 10; i++ {
    go func() {
        wg.Add(1)  // 危险！
        defer wg.Done()
    }()
}
wg.Wait()

// ✅ 对：Add 在 goroutine 外
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
    }()
}
wg.Wait()
```

### WaitGroup vs errgroup

```go
// WaitGroup：等待完成，不收集错误
var wg sync.WaitGroup
wg.Add(2)
go func() { defer wg.Done() }()
go func() { defer wg.Done() }()
wg.Wait()

// errgroup：等待完成 + 收集错误
import "golang.org/x/sync/errgroup"

var g errgroup.Group
g.Go(func() error { return nil })
g.Go(func() error { return errors.New("failed") })
if err := g.Wait(); err != nil {
    log.Fatal(err)  // 第一个错误
}
```

---

## 三、Once（只执行一次）

### 基本用法

```go
var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{
            conn: openDB(),
        }
    })
    return instance
}
```

### 内部实现

```go
// 标准库实现
func (o *Once) Do(f func()) {
    if o.done.Load() == 0 {  // fast path
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done.Load() == 0 {
        defer o.done.Store(1)
        f()
    }
}
```

### OnceValue / OnceFunc（Go 1.21+）

```go
// 返回值的 Once
config := sync.OnceValue(func() *Config {
    return loadConfig("config.yaml")
})
cfg := config()  // 首次调用加载，后续直接返回

// 函数形式的 Once
init := sync.OnceFunc(func() {
    fmt.Println("initialized")
})
init()  // 第一次执行
init()  // 不执行
```

---

## 四、Pool（对象池）

### 基本用法

```go
var bufPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process(data []byte) string {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()  // 重要：清空
        bufPool.Put(buf)
    }()

    buf.Write(data)
    return buf.String()
}
```

### 适用场景

1. **频繁分配/释放的对象**：bytes.Buffer / 连接 / 大对象
2. **GC 压力优化**：减少堆分配
3. **临时对象复用**：避免重复初始化

### 注意事项

```go
// ❌ 错：不清空
defer bufPool.Put(buf)

// ✅ 对：先 Reset 再 Put
defer func() {
    buf.Reset()
    bufPool.Put(buf)
}()
```

### Pool vs sync.Pool vs typed pool

```go
// 标准 sync.Pool（interface{}）
var pool = sync.Pool{New: func() interface{} { return new(Buffer) }}
buf := pool.Get().(*Buffer)  // 需要类型断言

// 泛型版本（社区库）
import "github.com/samber/go-sync"
pool := go_sync.NewPool(func() *Buffer { return new(Buffer) })
buf := pool.Get()  // 无需类型断言
```

---

## 五、Cond（条件变量）

### 基本用法

```go
var (
    mu    sync.Mutex
    cond  = sync.NewCond(&mu)
    ready bool
)

// 等待方
cond.L.Lock()
for !ready {
    cond.Wait()  // 释放锁并等待，唤醒后重新获取锁
}
cond.L.Unlock()

// 通知方
cond.L.Lock()
ready = true
cond.Broadcast()  // 唤醒所有等待者
// cond.Signal()  // 唤醒一个等待者
cond.L.Unlock()
```

### 适用场景

- **生产者-消费者**：buffer 满/空时等待
- **资源就绪**：等待初始化完成

### 实战：限制并发数

```go
type Semaphore struct {
    mu    sync.Mutex
    cond  *sync.Cond
    n     int
    limit int
}

func NewSemaphore(limit int) *Semaphore {
    s := &Semaphore{limit: limit}
    s.cond = sync.NewCond(&s.mu)
    return s
}

func (s *Semaphore) Acquire() {
    s.mu.Lock()
    for s.n >= s.limit {
        s.cond.Wait()
    }
    s.n++
    s.mu.Unlock()
}

func (s *Semaphore) Release() {
    s.mu.Lock()
    s.n--
    s.cond.Broadcast()
    s.mu.Unlock()
}
```

---

## 六、Map（并发安全 Map）

### 基本用法

```go
var m sync.Map

// 写
m.Store("key", "value")

// 读
v, ok := m.Load("key")

// 遍历
m.Range(func(k, v interface{}) bool {
    fmt.Println(k, v)
    return true  // 继续
})
```

### 适用场景

```go
// ✅ 适合：key 集合稳定、读多写少
// ❌ 不适合：高频写入（用 RWMutex + map 性能更好）
```

### sync.Map vs map + Mutex

| 维度 | sync.Map | map + RWMutex |
|---|---|---|
| 读性能 | ⭐⭐⭐⭐⭐（无锁） | ⭐⭐⭐⭐（RLock） |
| 写性能 | ⭐⭐（全局锁） | ⭐⭐⭐⭐（Lock） |
| 类型 | interface{} | 任意 |
| 适用 | 只读多、写少 | 读写均衡 |

### 实战：缓存

```go
type Cache struct {
    m sync.Map
}

func (c *Cache) Get(key string) (interface{}, bool) {
    return c.m.Load(key)
}

func (c *Cache) Set(key string, value interface{}) {
    c.m.Store(key, value)
}

func (c *Cache) GetOrCompute(key string, compute func() interface{}) interface{} {
    if v, ok := c.m.Load(key); ok {
        return v
    }
    v := compute()
    c.m.Store(key, v)
    return v
}
```

---

## 七、atomic（原子操作）

### 基本用法

```go
import "sync/atomic"

var counter int64

// 原子加
atomic.AddInt64(&counter, 1)

// 原子读
v := atomic.LoadInt64(&counter)

// 原子存
atomic.StoreInt64(&counter, 100)

// CAS
old := atomic.LoadInt64(&counter)
new := old + 1
swapped := atomic.CompareAndSwapInt64(&counter, old, new)
```

### atomic.Int64（Go 1.19+）

```go
var counter atomic.Int64

counter.Add(1)
v := counter.Load()
counter.Store(100)

// CAS
old := counter.Load()
new := old + 1
swapped := counter.CompareAndSwap(old, new)
```

### atomic.Value（任意类型）

```go
var config atomic.Value

config.Store(&Config{...})
cfg := config.Load().(*Config)

// 热更新配置
go func() {
    for {
        time.Sleep(1 * time.Minute)
        newCfg := loadConfig()
        config.Store(newCfg)
    }
}()
```

---

## 八、sync vs channel 选择

### 通用原则

| 场景 | 推荐 | 理由 |
|---|---|---|
| 通信 / 数据流 | channel | CSP 哲学 |
| 共享状态 | sync.Mutex | 简单直接 |
| 计数器 | atomic | 性能最佳 |
| 等待一组任务 | sync.WaitGroup | 简洁 |
| 单次初始化 | sync.Once | 线程安全 |
| 对象池 | sync.Pool | 减少 GC |
| 并发安全 map | sync.Map | 避免锁 |
| 复杂状态同步 | Mutex + channel | 组合 |

### 实战对比

```go
// channel 版：worker pool
jobs := make(chan Job, 100)
for w := 0; w < 10; w++ {
    go func() {
        for job := range jobs {
            process(job)
        }
    }()
}

// sync 版：worker pool（用 semaphore）
var wg sync.WaitGroup
sem := make(chan struct{}, 10)
for _, job := range jobs {
    wg.Add(1)
    sem <- struct{}{}
    go func(j Job) {
        defer wg.Done()
        defer func() { <-sem }()
        process(j)
    }(job)
}
wg.Wait()
```

---

## 九、最佳实践

### 1. 减少锁粒度

```go
// ❌ 一个全局锁
var mu sync.Mutex
var data map[string]int

// ✅ 分片锁
type ShardedMap struct {
    shards [16]struct {
        mu sync.RWMutex
        m  map[string]int
    }
}
```

### 2. 用 defer Unlock

```go
// ❌ 容易忘记 Unlock
mu.Lock()
if err := doSomething(); err != nil {
    mu.Unlock()  // 重复代码
    return err
}
mu.Unlock()

// ✅ defer 兜底
mu.Lock()
defer mu.Unlock()
if err := doSomething(); err != nil {
    return err  // defer 会执行
}
```

### 3. 用 atomic 代替 Mutex（简单计数）

```go
// ❌ Mutex 开销大
var (
    mu sync.Mutex
    counter int
)
mu.Lock()
counter++
mu.Unlock()

// ✅ atomic 快 5-10x
var counter atomic.Int64
counter.Add(1)
```

### 4. 避免锁嵌套

```go
// ❌ 死锁风险
func A() {
    mu1.Lock()
    defer mu1.Unlock()
    B()  // B 也加锁 mu2，可能死锁
}

func B() {
    mu2.Lock()
    defer mu2.Unlock()
}

// ✅ 用 channel 或避免嵌套
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/context**：context
- **06-advanced/runtime**：GMP 调度器

## 一句话总结

> **sync 包 = 锁 + 信号量 + 池 + 原子**。**channel 处理通信，sync 处理状态**。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
