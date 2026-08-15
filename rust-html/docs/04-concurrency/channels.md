---
title: Channel 与共享状态
---

# Channel 与共享状态

并发原语两大阵营：消息传递（Channel）与共享状态（Arc + Mutex）。Rust 都提供类型安全版本。

## 一句话总结

> **Channel = 消息传递、Arc`<Mutex>` = 共享状态**。**Rust 哲学："恐惧共享，鼓励消息传递"**。

---

## std::sync::mpsc

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(42).unwrap();
});
let value = rx.recv().unwrap();

// 多生产者
let (tx, rx) = mpsc::channel();
for i in 0..3 {
    let tx_clone = tx.clone();
    thread::spawn(move || {
        tx_clone.send(i).unwrap();
    });
}
drop(tx);

for received in rx {
    println!("{}", received);
}
```

## crossbeam-channel

```rust
use crossbeam_channel::{unbounded, bounded, select};

let (tx, rx) = unbounded();
let (tx2, rx2) = unbounded();

tx.send(1).unwrap();

select! {
    recv(rx) -> msg => println!("rx: {:?}", msg),
    recv(rx2) -> msg => println!("rx2: {:?}", msg),
}

// bounded
let (tx, rx) = bounded(100);
```

## Arc + Mutex

```rust
use std::sync::{Arc, Mutex};
use std::thread;

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
```

## RwLock（读写锁）

```rust
use std::sync::{Arc, RwLock};

let data = Arc::new(RwLock::new(vec![1, 2, 3]));

{
    let r1 = data.read().unwrap();
    let r2 = data.read().unwrap();
    println!("{:?}", r1);
}

{
    let mut w = data.write().unwrap();
    w.push(4);
}
```

## 原子类型

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let counter = AtomicUsize::new(0);
counter.fetch_add(1, Ordering::SeqCst);
let value = counter.load(Ordering::SeqCst);
counter.store(42, Ordering::SeqCst);
```

## tokio 异步 Channel

```rust
use tokio::sync::{mpsc, oneshot, broadcast, watch};

let (tx, mut rx) = mpsc::channel::<String>(100);
tx.send("hello".to_string()).await.unwrap();
let msg = rx.recv().await;

let (tx, rx) = oneshot::channel::<i32>();
let value = rx.await.unwrap();

let (tx, _) = broadcast::channel::<String>(100);
let mut rx1 = tx.subscribe();

let (tx, rx) = watch::channel(0);
let value = rx.borrow().clone();
```

## 死锁 4 大场景

```
场景 1：循环等待
场景 2：持锁等待异步操作
场景 3：回调中重新获取锁
场景 4：信号量泄漏
```

## 实战案例：生产者-消费者

```rust
use crossbeam_channel::bounded;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = bounded(10);

    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            for j in 0..100 {
                tx.send(format!("P{}-{}", i, j)).unwrap();
                thread::sleep(Duration::from_millis(10));
            }
        });
    }
    drop(tx);

    let mut handles = vec![];
    for i in 0..2 {
        let rx = rx.clone();
        let handle = thread::spawn(move || {
            while let Ok(msg) = rx.recv() {
                println!("C{} received: {}", i, msg);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/threads**：线程
- **04-concurrency/tokio**：Tokio 运行时

## 一句话总结

> **Channel 与 Arc`<Mutex>` 各有适用场景**：Channel 用于消息流、Arc`<Mutex>` 用于共享可变状态。**Rust 类型系统保证两者都线程安全**。
