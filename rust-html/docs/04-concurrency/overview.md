---
title: 并发总览
---

# 并发总览

Rust 的并发模型建立在"类型系统保证线程安全"之上：用类型防止数据竞争，编译期消灭一类 bug。

## 一句话总结

> **Rust 并发 = 类型系统保证线程安全**。**核心原语：Thread / Channel / Arc+Mutex / async-await**。**目标：fearless concurrency**。

---

## 4 大并发模型

```
1. 线程 + 共享状态
   std::thread + Arc<Mutex<T>>
   适合：CPU 密集型、共享内存场景

2. 消息传递
   std::sync::mpsc + crossbeam
   适合：流水线、Actor 模式

3. async-await
   tokio / async-std
   适合：IO 密集型、高并发网络服务

4. 数据并行
   rayon
   适合：SIMD 数据并行（map/reduce）
```

## 编译期线程安全

```rust
// Send：可以在线程间转移所有权
// Sync：可以在线程间共享引用（&T）

// 编译器自动推导
// - i32, String, Vec<T>: Send + Sync
// - Rc<T>: !Send + !Sync（不能在多线程用）
// - Mutex<T>: Send + Sync（如果 T: Send）
// - RefCell<T>: !Sync（运行时借用检查）

use std::rc::Rc;       // !Send !Sync（单线程）
use std::sync::Arc;    // Send + Sync（多线程）

let rc = Rc::new(5);
// thread::spawn(move || println!("{}", rc));  // ❌ 编译错误：Rc 不是 Send

let arc = Arc::new(5);
thread::spawn(move || println!("{}", arc));  // ✅ OK
```

## 线程基础

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }

    handle.join().unwrap();  // 等待子线程结束
}
```

## 消息传递（Channel）

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hi");
        tx.send(val).unwrap();
        // println!("{}", val);  // ❌ val 已被 move
    });

    let received = rx.recv().unwrap();
    println!("Got: {}", received);
}

// 多生产者
let (tx, rx) = mpsc::channel();
for i in 0..3 {
    let tx_clone = tx.clone();
    thread::spawn(move || {
        tx_clone.send(i).unwrap();
    });
}
drop(tx);  // 关闭原始 sender
for received in rx {
    println!("{}", received);
}
```

## 共享状态（Arc + Mutex）

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```

## async-await 入门

```rust
// async 函数返回 Future
async fn fetch_url(url: &str) -> Result<String, reqwest::Error> {
    let body = reqwest::get(url).await?.text().await?;
    Ok(body)
}

// 调用（返回 Future）
let future = fetch_url("https://example.com");

// 需要 runtime 执行
fn main() {
    let runtime = tokio::runtime::Runtime::new().unwrap();
    let result = runtime.block_on(future);
    println!("{:?}", result);
}

// 或使用 #[tokio::main]
#[tokio::main]
async fn main() {
    let body = fetch_url("https://example.com").await.unwrap();
    println!("{}", body);
}
```

## async 并发模式

```rust
use tokio::time::{sleep, Duration};

// 1. 并发执行多个 Future
let (a, b, c) = tokio::join!(
    async_task_a(),
    async_task_b(),
    async_task_c(),
);

// 2. spawn 后台任务
let handle = tokio::spawn(async {
    // 后台运行
    sleep(Duration::from_secs(10)).await;
});

// 3. select 等待多个 Future 任一完成
tokio::select! {
    result = task_a() => println!("a: {:?}", result),
    result = task_b() => println!("b: {:?}", result),
    _ = sleep(Duration::from_secs(5)) => println!("timeout"),
}
```

## 数据并行（rayon）

```rust
use rayon::prelude::*;

let numbers: Vec<i32> = (1..=1_000_000).collect();

// 串行 sum
let sum: i32 = numbers.iter().sum();

// 并行 sum（自动切分到多线程）
let sum: i32 = numbers.par_iter().sum();

// 并行 map
let squares: Vec<i32> = numbers.par_iter().map(|x| x * x).collect();

// 并行 filter
let evens: Vec<i32> = numbers.par_iter().filter(|x| x % 2 == 0).collect();
```

## 4 个 Send/Sync 错误模式

```rust
// ❌ 反模式 1：Rc 在多线程
let rc = std::rc::Rc::new(5);
thread::spawn(move || println!("{}", rc));  // 编译错误

// ❌ 反模式 2：Mutex guard 跨 await
async fn bad() {
    let guard = mutex.lock().unwrap();
    some_async_op().await;  // ❌ 跨 await 持有锁
    drop(guard);
}

// ❌ 反模式 3：&mut 跨线程
let mut x = 5;
thread::spawn(move || x += 1);  // ❌ x 不是 Send

// ❌ 反模式 4：循环中 spawn
for i in 0..1_000_000 {
    tokio::spawn(async move { process(i).await });
    // ❌ 资源耗尽（每个 spawn 占内存）
}
```

## 关联章节

- **04-concurrency/threads**：线程深度
- **04-concurrency/async-await**：async-await 详解
- **04-concurrency/tokio**：Tokio 运行时
- **04-concurrency/channels**：Channel 与共享状态
- **06-advanced/async-ecosystem**：异步生态对比

## 一句话总结

> **Rust 并发 = 类型保证 + 4 大模型 + 0 运行时开销**。**fearless concurrency：编译器帮你消灭数据竞争**。


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
