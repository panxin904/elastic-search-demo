---
title: async / await
---

# async / await

Rust async-await 是零成本抽象：编译为状态机，运行时由 tokio / async-std 调度。

## 一句话总结

> **async-await = 零成本协程**。**核心：Future trait / 状态机 / 运行时调度**。**与线程对比：内存更省、并发更高**。

---

## 基本语法

```rust
async fn fetch_url(url: &str) -> Result<String, reqwest::Error> {
    let body = reqwest::get(url).await?.text().await?;
    Ok(body)
}

// 调用：返回 Future（不执行）
let future = fetch_url("https://example.com");

// .await 触发 Future 执行
let body = fetch_url("https://example.com").await?;
```

## Future trait

```rust
trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context) -> Poll<Self::Output>;
}

enum Poll<T> {
    Ready(T),
    Pending,
}
```

## tokio runtime

```rust
// tokio 宏（推荐）
#[tokio::main]
async fn main() {
    let body = fetch_url("https://example.com").await.unwrap();
    println!("{}", body);
}
```

## 并发模式

```rust
// tokio::join! 并发执行
async fn parallel() {
    let (a, b, c) = tokio::join!(
        fetch_url("https://a.com"),
        fetch_url("https://b.com"),
        fetch_url("https://c.com"),
    );
}

// tokio::spawn 后台任务
async fn spawn_example() {
    let handle = tokio::spawn(async {
        tokio::time::sleep(Duration::from_secs(10)).await;
        "done"
    });
    do_other_work().await;
    let result = handle.await.unwrap();
}

// tokio::select! 等待多个 Future 任一完成
async fn select_example() {
    tokio::select! {
        result = task_a() => println!("a: {:?}", result),
        result = task_b() => println!("b: {:?}", result),
        _ = tokio::time::sleep(Duration::from_secs(5)) => println!("timeout"),
    }
}
```

## 4 个 async-await 反模式

```rust
// 反模式 1：在 async 中阻塞
async fn read_file_async() -> std::io::Result<String> {
    tokio::fs::read_to_string("file.txt").await  // 用 tokio 而非 std
}

// 反模式 2：持有锁跨 .await
async fn good(mutex: Arc<Mutex<i32>>) {
    {
        let mut guard = mutex.lock().unwrap();
        *guard += 1;
    }
    some_async_op().await;
}

// 反模式 3：spawn_blocking 滥用
async fn heavy_compute() {
    tokio::task::spawn_blocking(|| {
        expensive_calculation()
    }).await.unwrap();
}

// 反模式 4：async fn 递归死循环
async fn recursive() {
    recursive().await;
}
```

## 实战案例：HTTP 服务器

```rust
use axum::{routing::get, Router};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "Hello, world!" }))
        .route("/users/:id", get(get_user));

    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn get_user(Path(id): Path<u32>) -> String {
    format!("User: {}", id)
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/tokio**：Tokio 运行时
- **06-advanced/async-ecosystem**：异步生态对比

## 一句话总结

> **async-await = Rust 的零成本协程**。**编译为状态机，运行时调度，与线程互补**。
