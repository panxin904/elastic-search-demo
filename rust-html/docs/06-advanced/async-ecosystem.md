---
title: 异步生态对比
---

# 异步生态对比

Rust 异步生态有多个运行时选择：tokio / async-std / smol / embassy，各有侧重。

## 一句话总结

> **tokio = 事实标准 / async-std = 类 std 风格 / smol = 轻量 / embassy = 嵌入式**。**90% 项目选 tokio**。

---

## 4 大运行时横向对比

| 维度 | tokio | async-std | smol | embassy |
|------|-------|-----------|------|---------|
| **生态** | 最完整 | 中等 | 轻量 | 嵌入式 |
| **性能** | 最优 | 中等 | 中等 | 针对 MCU |
| **API 风格** | 自己的 | 类 std | 极简 | 嵌入式 |
| **学习曲线** | 中 | 低 | 低 | 中高 |
| **目标场景** | 服务端 | 服务端 | 工具 / 嵌入式 | 微控制器 |
| **维护状态** | 活跃 | 活跃 | 活跃 | 活跃 |
| **公司背景** | tokio-rs | async-rs | 个人 / tokio-rs | embassy-rs |

## tokio（推荐）

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    loop {
        let (mut socket, _) = listener.accept().await?;
        tokio::spawn(async move {
            let mut buf = [0; 1024];
            socket.read(&mut buf).await.unwrap();
            socket.write_all(b"HTTP/1.1 200 OK\r\n\r\nHello").await.unwrap();
        });
    }
}
```

## async-std

```rust
use async_std::net::TcpListener;
use async_std::io::{ReadExt, WriteExt};

#[async_std::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    let mut incoming = listener.incoming();
    while let Some(stream) = incoming.next().await {
        let mut stream = stream?;
        stream.write_all(b"Hello").await?;
    }
    Ok(())
}
```

## smol（轻量）

```rust
use smol::{net, Executor};

fn main() {
    smol::block_on(async {
        let listener = net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
        loop {
            let (mut stream, _) = listener.accept().await.unwrap();
            smol::spawn(async move {
                use smol::io::{AsyncReadExt, AsyncWriteExt};
                let mut buf = [0; 1024];
                stream.read(&mut buf).await.unwrap();
                stream.write_all(b"Hello").await.unwrap();
            }).detach();
        }
    });
}
```

## embassy（嵌入式）

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    loop {
        // 嵌入式主循环
        Timer::after(Duration::from_millis(1000)).await;
        // 闪烁 LED
    }
}
```

## 4 大决策维度

```
1. 生态
   tokio > async-std > smol
   （tokio 有 axum / tonic / sqlx 等完整生态）

2. 学习曲线
   async-std ≈ smol < tokio < embassy
   （async-std API 像 std，tokio 有自己的约定）

3. 性能
   tokio ≈ smol > async-std
   （tokio 多线程 + work-stealing 极致优化）

4. 部署目标
   服务端：tokio / async-std
   嵌入式：embassy
   WASM：smol / 直接用 tokio（在 WASM 中）
   库：抽象掉运行时（用 async-trait）
```

## async 库编写建议

```rust
// 1. 库不绑定特定运行时
use async_trait::async_trait;

#[async_trait]
trait Database {
    async fn get_user(&self, id: u32) -> Option<User>;
}

// 2. 让用户传入 runtime handle
struct MyService {
    runtime: tokio::runtime::Handle,
}

// 3. 用 Send + 'static 约束
async fn process(data: impl Send + 'static) -> Result<(), Error> {
    // ...
}

// 4. 提供 feature flags
[features]
default = ["tokio"]
async-std = ["async-std-runtime"]
smol = ["smol-runtime"]
```

## 4 大生态组件（基于 tokio）

```rust
// 1. Web 框架：axum / actix-web
use axum::{routing::get, Router};

// 2. gRPC：tonic
use tonic::{transport::Server, Request, Response};

// 3. 数据库：sqlx
use sqlx::postgres::PgPool;

// 4. 序列化：serde
use serde::{Serialize, Deserialize};

// 5. 日志：tracing
use tracing::{info, instrument};

// 6. 错误处理：anyhow / thiserror
use anyhow::Result;
```

## 实战案例：tokio 完整 HTTP 服务

```rust
use axum::{
    routing::{get, post},
    Router, Json,
};
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;

#[derive(Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "Hello, world!" }))
        .route("/users", get(list_users))
        .route("/users/:id", get(get_user));

    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn list_users() -> Json<Vec<User>> {
    Json(vec![User { id: 1, name: "Alice".to_string() }])
}

async fn get_user(Path(id): Path<u32>) -> Json<User> {
    Json(User { id, name: format!("User {}", id) })
}
```

## 关联章节

- **04-concurrency/async-await**：async-await 基础
- **04-concurrency/tokio**：Tokio 深度
- **05-systems/wasm**：WASM 运行时

## 一句话总结

> **异步生态 = tokio 主导，其他补充**。**90% 服务端项目选 tokio，嵌入式选 embassy，库用 async-trait 抽象**。
