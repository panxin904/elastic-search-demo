---
title: 生态总览
---

# 生态总览

Rust 生态以 Cargo 为核心，crates.io 为包仓库，标准库 + 第三方库覆盖了现代软件工程的全部需求。

## 一句话总结

> **Rust 生态 = Cargo + crates.io + 标准库**。**核心：Cargo 一站式（build/test/format/lint/doc）、crates.io 是最大包仓库（130k+ crates）、标准库覆盖广**。

---

## 4 大基础设施

```
1. Cargo       包管理与构建工具（rustc 包装）
2. crates.io   包仓库（与 npm / pip 同级）
3. rustc       编译器（支持 x86_64 / aarch64 / wasm / riscv）
4. 标准库 std  核心（Vec / HashMap / String / Thread / File）
```

## Cargo：项目工作流

```toml
# Cargo.toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"        # Rust 版本（2015 / 2018 / 2021）

[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
mockall = "0.11"

[profile.release]
opt-level = 3           # 最大优化
lto = true              # 链接时优化
codegen-units = 1       # 单 codegen unit（更好的优化）
```

```bash
# 常用命令
cargo new my-app           # 新建二进制项目
cargo new --lib my-lib     # 新建库项目
cargo build                # 编译 debug
cargo build --release      # 编译 release
cargo run               # 编译并运行
cargo test               # 跑测试
cargo bench              # 跑基准（nightly）
cargo doc --open         # 生成并打开文档
cargo update             # 更新依赖
cargo check              # 快速类型检查（不生成代码）
cargo clippy             # 代码 lint
cargo fmt                # 格式化
```

## crates.io 生态版图

| 领域 | 主流 crate | 用途 |
|------|------------|------|
| **Web 框架** | axum / actix-web / warp | HTTP 服务 |
| **异步运行时** | tokio / async-std | async 运行时 |
| **序列化** | serde | JSON/YAML/TOML/Bincode |
| **数据库** | sqlx / diesel / sea-orm | ORM 与查询 |
| **HTTP Client** | reqwest | HTTP 客户端 |
| **CLI** | clap / structopt | 命令行参数解析 |
| **日志** | tracing / log / env_logger | 结构化日志 |
| **错误处理** | anyhow / thiserror | 错误包装 |
| **正则** | regex | 正则表达式 |
| **加密** | rustls / ring / aes-gcm | TLS / 加密 |
| **嵌入式** | embedded-hal / cortex-m | 嵌入式开发 |
| **WASM** | wasm-bindgen / wasmtime | WebAssembly |
| **FFI** | libc / bindgen / cbindgen | C 互操作 |
| **性能** | rayon / crossbeam | 并行计算 |
| **测试** | mockall / proptest / criterion | 单元测试 + 属性测试 + 基准 |

## 标准库：核心 API

```rust
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::sync::{Arc, Mutex};
use std::thread;

// 集合
let mut map = HashMap::new();
map.insert("alice", 30);
map.insert("bob", 25);

// 文件 IO
let file = File::open("data.txt")?;
let reader = BufReader::new(file);
for line in reader.lines() {
    println!("{}", line?);
}

// 线程
let handle = thread::spawn(|| {
    println!("Hello from thread");
});
handle.join().unwrap();

// 共享状态
let counter = Arc::new(Mutex::new(0));
let counter_clone = counter.clone();
thread::spawn(move || {
    let mut num = counter_clone.lock().unwrap();
    *num += 1;
});
```

## 4 大工具链

```bash
# rustfmt：格式化（团队代码风格统一）
cargo fmt

# clippy：lint（200+ 检查规则）
cargo clippy
cargo clippy -- -W clippy::pedantic

# rust-analyzer：LSP（IDE 智能提示）
# 自动安装到 VSCode / IntelliJ / vim

# cargo-outdated：依赖版本检查
cargo install cargo-outdated
cargo outdated
```

## 模块系统

```rust
// src/lib.rs
pub mod user;        // 公开 user 模块
mod internal;        // 私有 internal 模块

// src/user.rs
pub struct User { ... }
pub fn create_user() -> User { ... }

// src/user/order.rs  (子模块)
pub fn place_order() { ... }

// 使用
use my_crate::user::{User, create_user};
use my_crate::user::order::place_order;
```

```toml
# 引用本地路径
[dependencies]
my_lib = { path = "../my_lib" }

# 引用 git 仓库
my_lib = { git = "https://github.com/me/my_lib", branch = "main" }

# 引用 crates.io
tokio = "1.0"
```

## Feature Flags：条件编译

```toml
# Cargo.toml
[features]
default = ["json"]
json = ["serde_json"]
yaml = ["serde_yaml"]
full = ["json", "yaml"]
```

```rust
// src/lib.rs
#[cfg(feature = "json")]
pub fn parse_json(s: &str) -> Result<Value, Error> {
    serde_json::from_str(s)
}

#[cfg(feature = "yaml")]
pub fn parse_yaml(s: &str) -> Result<Value, Error> {
    serde_yaml::from_str(s)
}
```

## 实战案例：CLI 应用

```bash
# 创建 CLI 项目
cargo new my-cli --bin
cd my-cli
cargo add clap --features derive
cargo add anyhow
```

```rust
// src/main.rs
use clap::Parser;
use anyhow::Result;

#[derive(Parser)]
#[command(name = "my-cli", version, about)]
struct Args {
    /// 输入文件路径
    #[arg(short, long)]
    input: String,

    /// 详细模式
    #[arg(short, long)]
    verbose: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    if args.verbose {
        println!("Reading file: {}", args.input);
    }

    let content = std::fs::read_to_string(&args.input)?;
    println!("File size: {} bytes", content.len());

    Ok(())
}
```

## 关联章节

- **03-ecosystem/cargo**：Cargo 深度
- **03-ecosystem/crates-io**：crates.io 生态
- **03-ecosystem/std-lib**：标准库
- **03-ecosystem/tooling**：工具链

## 一句话总结

> **Rust 生态成熟度：基础设施完整 + 第三方库覆盖 95% 场景 + 工具链一流**。**比 Go 生态稍年轻，但工程质量显著更高**。


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
