---
title: 线程与 Thread
---

# 线程与 Thread

Rust 标准库的 std::thread 提供原生线程支持，类型系统保证线程安全。

## 一句话总结

> **std::thread = 原生 1:1 OS 线程**。**核心：spawn / join / Send + 'static 闭包**。

---

## 基本用法

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

    handle.join().unwrap();
}
```

## move 闭包

```rust
let v = vec![1, 2, 3];

let handle = thread::spawn(move || {
    println!("Vector: {:?}", v);
});

handle.join().unwrap();
```

## 线程返回 Result

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_file(path: String) -> io::Result<String> {
    let mut content = String::new();
    File::open(path)?.read_to_string(&mut content)?;
    Ok(content)
}

fn main() -> io::Result<()> {
    let handle = thread::spawn(|| {
        read_file("data.txt".to_string())
    });

    match handle.join() {
        Ok(Ok(content)) => println!("Read: {}", content),
        Ok(Err(e)) => eprintln!("Error: {}", e),
        Err(_) => eprintln!("Thread panicked"),
    }

    Ok(())
}
```

## 线程局部存储

```rust
use std::cell::RefCell;

thread_local! {
    static COUNTER: RefCell<u32> = RefCell::new(0);
}

fn main() {
    for _ in 0..10 {
        thread::spawn(|| {
            COUNTER.with(|c| {
                *c.borrow_mut() += 1;
                println!("Thread counter: {}", c.borrow());
            });
        });
    }
}
```

## 4 个线程反模式

```rust
// 反模式 1：未等待线程结束
thread::spawn(|| do_work());

// 反模式 2：数据竞争（编译错误）
let mut counter = 0;
thread::spawn(|| counter += 1);

// 反模式 3：线程数无限制
for _ in 0..1_000_000 {
    thread::spawn(|| do_work());
}

// 反模式 4：阻塞主线程
let handle = thread::spawn(|| do_work());
// 没有 handle.join()
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/channels**：Channel 与共享状态
- **04-concurrency/async-await**：async-await


## `Send` / `Sync` 标记 trait

```rust
// Send：可在线程间转移所有权
// Sync：可在线程间共享引用（&T 是 Send）

// 标准库自动实现
// - i32, String, Vec<T>: Send + Sync（如果 T: Send）
// - Rc<T>: !Send !Sync（引用计数非原子）
// - Mutex<T>: Send + Sync（如果 T: Send）
// - RefCell<T>: Send 但 !Sync（运行时借用检查）

// 自定义类型
struct MyType { /* ... */ }
// 编译器自动派生 Send/Sync（字段全 Send/Sync 时）

// 手动 opt-out
struct NotSend {
    _marker: PhantomData<*const ()>,  // raw pointer !Send !Sync
}
```

## 线程池（rayon）

```rust
use rayon::prelude::*;

// 数据并行（CPU-bound）
let sum: i64 = (0..1_000_000).into_par_iter().sum();

// 并行 map
let squares: Vec<i64> = vec![1, 2, 3, 4].into_par_iter().map(|x| x * x).collect();

// 并行排序
let mut data = vec![5, 3, 1, 4, 2];
data.par_sort();

// 线程池配置
rayon::ThreadPoolBuilder::new()
    .num_threads(8)
    .build_global()
    .unwrap();
```

## scoped threads（借用闭包）

```rust
use std::thread;

let mut data = vec![1, 2, 3, 4];

// 普通 spawn 必须 move（无法借用）
// thread::spawn(|| data.push(5));  // 错误

// scoped：线程保证在作用域内 join，可借用
thread::scope(|s| {
    s.spawn(|| {
        println!("len = {}", data.len());  // 借用合法
    });
    s.spawn(|| {
        data[0] += 1;  // 借用合法
    });
});  // 自动 join 所有线程
```

## 实战案例：并行下载

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let urls = vec![
    "https://example.com/a",
    "https://example.com/b",
    "https://example.com/c",
];
let results = Arc::new(Mutex::new(Vec::new()));

let handles: Vec<_> = urls.into_iter().enumerate().map(|(i, url)| {
    let results = Arc::clone(&results);
    thread::spawn(move || {
        // reqwest::blocking::get(url)...
        let content = format!("content of {}", url);
        results.lock().unwrap().push((i, content));
    })
}).collect();

for h in handles { h.join().unwrap(); }

println!("{:?}", results.lock().unwrap());
```

## 选型：原生 thread vs rayon vs tokio

| 场景 | 推荐 | 原因 |
|---|---|---|
| CPU-bound 数据并行 | **rayon** | 自动 work-stealing |
| 偶尔后台任务 | **std::thread** | 简单直接 |
| I/O-bound 高并发 | **tokio** | 异步 + 轻量 |
| 阻塞 syscall | **std::thread** + thread pool | 避免阻塞 runtime |
| 长期守护进程 | **tokio::task::spawn** | 优雅关闭 |


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
