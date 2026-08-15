---
title: Tokio 运行时
---

# Tokio 运行时

Tokio 是 Rust 生态最成熟的异步运行时：多线程调度 + IO reactor + 定时器 + 同步原语。

## 一句话总结

> **Tokio = Rust 异步事实标准**。**核心：reactor + 多线程调度 + timer + sync**。**生态完整（axum / hyper / tonic）**。

---

## 添加 Tokio

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

```bash
# 全功能
features = ["full"]

# 按需
features = ["rt-multi-thread", "macros", "net", "sync", "time"]
```

## 启动 Runtime

```rust
#[tokio::main]
async fn main() {
    // 主任务
}
```

## 5 大核心模块

```rust
// 1. tokio::spawn
let handle = tokio::spawn(async {
    do_work().await
});

// 2. tokio::time
use tokio::time::{sleep, timeout, Duration};
sleep(Duration::from_secs(1)).await;
timeout(Duration::from_secs(5), some_async_op()).await?;

// 3. tokio::net
use tokio::net::{TcpListener, TcpStream};
let listener = TcpListener::bind("127.0.0.1:8080").await?;
let (stream, addr) = listener.accept().await?;

// 4. tokio::sync
use tokio::sync::{mpsc, Mutex, RwLock, Semaphore};
let (tx, mut rx) = mpsc::channel(32);

// 5. tokio::fs
let content = tokio::fs::read_to_string("file.txt").await?;
```

## 同步原语

```rust
use tokio::sync::{mpsc, oneshot, broadcast, watch, Mutex, RwLock, Semaphore};

// mpsc：多生产者单消费者
let (tx, mut rx) = mpsc::channel::<String>(100);
tx.send("hello".to_string()).await?;
let msg = rx.recv().await;

// oneshot：单次发送
let (tx, rx) = oneshot::channel::<i32>();
tx.send(42).unwrap();
let value = rx.await.unwrap();

// broadcast：多对多
let (tx, _) = broadcast::channel::<String>(100);
let mut rx1 = tx.subscribe();
tx.send("hello".to_string()).unwrap();
```

## 性能调优

```rust
// 1. 控制并发
use tokio::sync::Semaphore;
let sem = Arc::new(Semaphore::new(100));
for req in reqs {
    let permit = sem.clone().acquire_owned().await.unwrap();
    tokio::spawn(async move {
        handle(req).await;
        drop(permit);
    });
}
```

## 实战案例：并发爬虫

```rust
use reqwest::Client;
use tokio::sync::Semaphore;
use std::sync::Arc;

#[tokio::main]
async fn main() {
    let urls = vec![
        "https://example.com",
        "https://example.org",
    ];

    let client = Client::new();
    let sem = Arc::new(Semaphore::new(10));  // 最多 10 并发

    let mut handles = vec![];
    for url in urls {
        let permit = sem.clone().acquire_owned().await.unwrap();
        let client = client.clone();
        let handle = tokio::spawn(async move {
            let body = client.get(url).send().await.unwrap().text().await.unwrap();
            println!("{}: {} bytes", url, body.len());
            drop(permit);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await.unwrap();
    }
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/async-await**：async-await
- **04-concurrency/channels**：Channel 与共享状态

## 一句话总结

> **Tokio = Rust 异步生态的事实标准**：完整 runtime + 同步原语 + 网络 / IO / 定时器**。
