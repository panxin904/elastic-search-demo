---
title: Cargo
---

# Cargo

Cargo 是 Rust 的官方构建系统与包管理器：一个工具搞定 build / test / bench / doc / publish。

## 一句话总结

> **Cargo = Rust 的 npm + maven + make + 文档生成器**。**核心：项目工作流 + 依赖管理 + 测试 + 发布**。

---

## 项目初始化

```bash
# 新建二进制项目
cargo new my_project
cd my_project

# 目录结构
my_project/
├── .git/
├── .gitignore
├── Cargo.toml
└── src/
    └── main.rs

# 新建库项目
cargo new --lib my_library
```

## Cargo.toml

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"
authors = ["Alice <alice@example.com>"]
license = "MIT OR Apache-2.0"
description = "A short description"

[dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
mockall = "0.11"

[build-dependencies]
cc = "1.0"

[[bin]]
name = "my_project"
path = "src/main.rs"

[lib]
name = "my_library"
path = "src/lib.rs"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

[features]
default = ["json"]
json = ["serde_json"]
yaml = ["serde_yaml"]
full = ["json", "yaml"]
```

## 常用命令

```bash
cargo build              # debug 构建
cargo build --release     # release 构建
cargo check              # 快速类型检查

cargo run                # 编译并运行
cargo run --release
cargo run -- arg1 arg2

cargo test               # 运行所有测试
cargo test --release
cargo test test_name
cargo test -- --nocapture

cargo doc                # 生成文档
cargo doc --open

cargo fmt                # 格式化
cargo clippy             # lint
cargo outdated
cargo tree
cargo bench              # nightly

cargo clean              # 删除 target/

cargo add serde
cargo add serde --dev
cargo update
cargo update -p serde
cargo remove serde

cargo publish
cargo login
cargo package
```

## Workspace

```toml
# Cargo.toml（workspace root）
[workspace]
members = [
    "crates/foo",
    "crates/bar",
]

[workspace.dependencies]
serde = "1.0"

[workspace.package]
version = "0.1.0"
edition = "2021"
```

```bash
cargo build --workspace
cargo test --workspace
cargo build -p foo
```

## Feature Flags

```toml
# Cargo.toml
[features]
default = ["json"]
json = ["dep:serde_json"]
yaml = ["dep:serde_yaml"]

[dependencies]
serde_json = { version = "1", optional = true }
```

```rust
#[cfg(feature = "json")]
pub fn parse_json(s: &str) -> Result<Value, serde_json::Error> {
    serde_json::from_str(s)
}
```

```bash
cargo build --features "yaml"
cargo build --features "full"
cargo build --no-default-features
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/crates-io**：crates.io
- **03-ecosystem/tooling**：工具链


## Cargo.lock 策略

```bash
# 二进制项目（应用）：commit lock
git add Cargo.lock
# 保证所有开发者 + CI 用同一版本

# 库项目（crate）：不 commit lock
# cargo publish 时强制 .gitignore

# 强制重新解析
rm Cargo.lock
cargo update
```

## 私有 crate 源（私有 registry）

```toml
# ~/.cargo/config.toml
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index"

# 或企业私有源
[source.my-company]
registry = "https://cargo.mycompany.com/git/index"
```

## 离线构建

```bash
# 预下载所有依赖到 vendor/
cargo vendor

# 项目内 vendor 目录
mkdir .cargo
cat > .cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# 离线构建
cargo build --offline
```

## 条件编译（target / feature）

```rust
// src/lib.rs
#[cfg(target_os = "linux")]
pub fn linux_only() { /* ... */ }

#[cfg(target_os = "windows")]
pub fn windows_only() { /* ... */ }

#[cfg(feature = "serde")]
pub use serde::{Serialize, Deserialize};
```

## Cargo 常用环境变量

```bash
CARGO_TARGET_DIR=/tmp/target cargo build     # 自定义产物目录
CARGO_BUILD_JOBS=4 cargo build               # 并行度
RUSTC_WRAPPER=sccache cargo build            # 编译缓存
RUSTFLAGS="-C target-cpu=native" cargo build # CPU 优化
RUST_BACKTRACE=full cargo run                # panic backtrace
```

## 实战案例：跨平台编译

```bash
# 安装目标
rustup target add aarch64-apple-darwin
rustup target add x86_64-unknown-linux-gnu
rustup target add wasm32-unknown-unknown

# 静态二进制（Linux）
RUSTFLAGS="-C target-feature=+crt-static"   cargo build --release --target x86_64-unknown-linux-gnu

# 最小镜像（约 5MB）
docker run --rm -v $(pwd):/app -w /app rust:slim   cargo build --release
```


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
