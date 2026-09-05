---
title: channel
date: 2026-08-15  # date-auto-injected
---

![Go 内存分配模型](/go-memory-model.svg)

# channel
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Go Channel 内部结构</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">环形缓冲 · sendq/recvq · 阻塞协程队列</text>

  <!-- Channel 结构 -->
  <rect x="30" y="85" width="540" height="290" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="300" y="105" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">hchan struct (runtime.chansend / chanrecv)</text>

  <!-- 环形缓冲 -->
  <rect x="50" y="125" width="180" height="180" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="140" y="148" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">环形缓冲区 buf</text>
  <text x="140" y="166" text-anchor="middle" font-size="10" fill="#475569">[]T  ·  cap = 8</text>

  <!-- 格子 -->
  <rect x="65" y="180" width="35" height="35" fill="#3b82f6" stroke="#1e40af"/>
  <text x="82" y="203" text-anchor="middle" font-size="10" fill="white">1</text>
  <rect x="100" y="180" width="35" height="35" fill="#3b82f6" stroke="#1e40af"/>
  <text x="117" y="203" text-anchor="middle" font-size="10" fill="white">2</text>
  <rect x="135" y="180" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="152" y="203" text-anchor="middle" font-size="10" fill="#94a3b8">3</text>
  <rect x="170" y="180" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>

  <rect x="65" y="215" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>
  <rect x="100" y="215" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>
  <rect x="135" y="215" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>
  <rect x="170" y="215" width="35" height="35" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="140" y="270" text-anchor="middle" font-size="9" fill="#475569">sendx=2  recvx=0  qcount=2</text>
  <text x="140" y="288" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">无缓冲 cap=0：直接传递</text>

  <!-- 等待队列 -->
  <rect x="260" y="125" width="140" height="80" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="330" y="148" text-anchor="middle" font-size="12" font-weight="700" fill="#991b1b">recvq</text>
  <text x="330" y="166" text-anchor="middle" font-size="10" fill="#475569">等待接收的 G 队列</text>
  <rect x="275" y="178" width="22" height="20" fill="#dc2626"/>
  <rect x="300" y="178" width="22" height="20" fill="#dc2626"/>
  <rect x="325" y="178" width="22" height="20" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="350" y="192" font-size="9" fill="#475569">sudog</text>

  <rect x="260" y="220" width="140" height="80" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="330" y="243" text-anchor="middle" font-size="12" font-weight="700" fill="#047857">sendq</text>
  <text x="330" y="261" text-anchor="middle" font-size="10" fill="#475569">等待发送的 G 队列</text>
  <rect x="275" y="273" width="22" height="20" fill="#10b981"/>
  <rect x="300" y="273" width="22" height="20" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="350" y="287" font-size="9" fill="#475569">sudog</text>

  <!-- 锁 -->
  <rect x="430" y="125" width="130" height="80" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="495" y="148" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">lock</text>
  <text x="495" y="166" text-anchor="middle" font-size="10" fill="#475569">mutex 串行化操作</text>
  <text x="495" y="185" text-anchor="middle" font-size="9" fill="#92400e" font-style="italic">争抢时短暂阻塞</text>
  <text x="495" y="198" text-anchor="middle" font-size="9" fill="#92400e" font-style="italic">非阻塞时自旋</text>

  <!-- closed 标志 -->
  <rect x="430" y="220" width="130" height="80" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="495" y="243" text-anchor="middle" font-size="12" font-weight="700" fill="#5b21b6">closed</text>
  <text x="495" y="261" text-anchor="middle" font-size="10" fill="#475569">atomic bool</text>
  <text x="495" y="280" text-anchor="middle" font-size="9" fill="#5b21b6" font-style="italic">close(ch) 后置 true</text>
  <text x="495" y="293" text-anchor="middle" font-size="9" fill="#5b21b6" font-style="italic">recvq 全部唤醒返零值</text>

  <!-- 操作流程 -->
  <rect x="30" y="385" width="540" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="408" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">send / recv 决策树</text>
  <text x="50" y="428" font-size="10" fill="#334155">1. recvq 非空 → 直接出队传递（绕过 buf）</text>
  <text x="50" y="446" font-size="10" fill="#334155">2. buf 未满 → 写入环形 buf</text>
  <text x="320" y="428" font-size="10" fill="#334155">3. sendq 非空 → 出队并填 buf</text>
  <text x="320" y="446" font-size="10" fill="#334155">4. 都失败 → G 自身入队（gopark 阻塞）</text>
</svg>


channel 是 goroutine 之间的通信机制：类型安全的消息队列，遵循 CSP（Communicating Sequential Processes）模型。

## 一句话总结

> **channel = goroutine 间的消息队列**。**核心：make 创建 / ch <- 发送 / <-ch 接收 / close 关闭 / select 多路复用**。

---

## 一、基本用法

### 创建

```go
// 无缓冲 channel（同步）
ch := make(chan int)

// 有缓冲 channel（异步）
ch := make(chan int, 10)

// 只发送 / 只接收
sendCh := chan<- int   // 只发送
recvCh := <-chan int   // 只接收
```

### 发送与接收

```go
ch := make(chan int)

// 发送（阻塞直到有接收者）
go func() { ch <- 42 }()

// 接收（阻塞直到有数据）
v := <-ch

// 多返回值接收
v, ok := <-ch  // ok 表示 channel 是否关闭
```

### 关闭

```go
ch := make(chan int)
close(ch)

// 检查是否关闭
v, ok := <-ch
if !ok {
    // channel 已关闭
}

// 关闭后发送会 panic
// ch <- 1  // panic: send on closed channel

// 重复关闭会 panic
// close(ch) // panic: close of closed channel

// 关闭 nil channel 会 panic
var ch chan int
// close(ch) // panic: close of nil channel
```

---

## 二、channel 状态

| 操作 | nil channel | 已关闭 channel | 正常 channel |
|---|---|---|---|
| **发送** | 永久阻塞 | panic | 阻塞 / 发送 |
| **接收** | 永久阻塞 | 返回零值 + false | 阻塞 / 接收 |
| **关闭** | panic | panic | 关闭成功 |
| **len** | 0 | 0 | 缓冲中元素数 |
| **cap** | 0 | 0 | 缓冲容量 |

### 利用 nil channel

```go
// 用 nil channel 禁用某个分支（select 中常用）
func merge(ch1, ch2 <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for ch1 != nil || ch2 != nil {
            select {
            case v, ok := <-ch1:
                if !ok { ch1 = nil; continue }
                out <- v
            case v, ok := <-ch2:
                if !ok { ch2 = nil; continue }
                out <- v
            }
        }
    }()
    return out
}
```

---

## 三、缓冲 vs 无缓冲

### 无缓冲（同步）

```go
ch := make(chan int)  // 容量 0

// 发送阻塞直到有接收者
// 接收阻塞直到有发送者
// 用途：同步信号、握手
```

### 有缓冲（异步）

```go
ch := make(chan int, 10)  // 容量 10

// 发送：缓冲未满时不阻塞，缓冲满时阻塞
// 接收：缓冲非空时不阻塞，缓冲空时阻塞
// 用途：消息队列、限流
```

### 容量选择

```text
小容量（1-10）：同步信号、限流
中容量（100-1000）：任务队列
大容量（10000+）：批处理
无缓冲：必须同步
```

---

## 四、channel 方向

### 双向 vs 单向

```go
// 双向
ch := make(chan int)

// 单向（只发送）
var sendCh chan<- int = ch

// 单向（只接收）
var recvCh <-chan int = ch

// 转换：双向可以隐式转单向，单向不能转双向
```

### 函数签名推荐

```go
// 生产者：参数 chan<- T（只发送）
func produce(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)
}

// 消费者：参数 <-chan T（只接收）
func consume(ch <-chan int) {
    for v := range ch {
        fmt.Println(v)
    }
}

// 用户：双向 channel
func main() {
    ch := make(chan int)
    go produce(ch)
    consume(ch)
}
```

**好处**：编译期保证职责单一。

---

## 五、select 多路复用

### 基本 select

```go
select {
case msg := <-ch1:
    fmt.Println("ch1:", msg)
case msg := <-ch2:
    fmt.Println("ch2:", msg)
case ch3 <- 42:
    fmt.Println("sent to ch3")
default:
    fmt.Println("no channel ready")
}
```

### 超时模式

```go
select {
case res := <-ch:
    return res
case <-time.After(1 * time.Second):
    return errors.New("timeout")
}
```

### context 取消

```go
select {
case res := <-ch:
    return res
case <-ctx.Done():
    return ctx.Err()
}
```

### 心跳检测

```go
heartbeat := time.NewTicker(1 * time.Second)
defer heartbeat.Stop()

for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-heartbeat.C:
        // 健康检查 / 续约
    case msg := <-ch:
        // 处理消息
    }
}
```

### 非阻塞接收

```go
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    fmt.Println("no message")
}
```

---

## 六、关闭 channel 的规则

### 谁创建谁关闭

```go
// ✅ 推荐：发送方关闭
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)  // 发送方关闭
}

func consumer(ch <-chan int) {
    for v := range ch {  // 自动检测关闭
        fmt.Println(v)
    }
}
```

### 多个发送方

```go
// 用 sync.Once 确保只关闭一次
var once sync.Once
func closeCh(ch chan int) {
    once.Do(func() {
        close(ch)
    })
}
```

### 通知式 channel

```go
// 不发送数据，只用作通知（关闭即可）
done := make(chan struct{})
go func() {
    // do work
    close(done)  // 通知完成
}()
<-done  // 等待完成
```

---

## 七、channel 实战模式

### 1. 信号量（限流）

```go
sem := make(chan struct{}, 10)  // 最多 10 个并发
for _, item := range items {
    sem <- struct{}{}  // 获取信号量
    go func(item Item) {
        defer func() { <-sem }()  // 释放信号量
        process(item)
    }(item)
}
```

### 2. Pipeline

```go
// 阶段 1
gen := func(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

// 阶段 2
sq := func(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用
for v := range sq(gen(1, 2, 3)) {
    fmt.Println(v)  // 1, 4, 9
}
```

### 3. Fan-out / Fan-in

```go
// Fan-out：多个 goroutine 读同一个 channel
// Fan-in：多个 channel 合并到一个

func fanIn(cs ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    for _, c := range cs {
        wg.Add(1)
        go func(c <-chan int) {
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

### 4. Context 取消传播

```go
func worker(ctx context.Context, ch <-chan int) {
    for {
        select {
        case <-ctx.Done():
            return
        case v, ok := <-ch:
            if !ok {
                return
            }
            // 处理 v
        }
    }
}
```

---

## 八、channel 性能

### 性能开销

- **无缓冲**：~100ns（每次 send/receive）
- **有缓冲**：~50ns（非阻塞时）
- **比 Mutex**：快 2-10x

### 性能陷阱

```go
// 1. 频繁的发送/接收（高频场景考虑 sync.Pool）
// 2. 大 channel 缓冲（占用内存）
// 3. 阻塞 channel 导致 goroutine 堆积
```

### channel vs Mutex 选择

| 场景 | 推荐 |
|---|---|
| **数据流 / 消息队列** | channel |
| **共享状态 / 计数器** | Mutex / atomic |
| **复杂状态同步** | Mutex + channel |
| **通知信号** | channel（close 即通知） |

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context
- **02-concurrency/patterns**：并发模式

## 一句话总结

> **channel = goroutine 间的消息队列**。**CSP 模型：通信代替共享内存**。


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
