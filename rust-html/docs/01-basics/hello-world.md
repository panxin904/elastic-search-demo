---
title: Hello World 实战
---

# Hello World 实战

第一个 Rust 程序：从安装到部署，完整实战。

## 一句话总结

> **Hello World = 安装 Rust → cargo new → cargo run**。**5 分钟跑通，30 分钟熟悉工具链**。

---

## 安装 Rust

```bash
# macOS / Linux：rustup（官方推荐）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 验证
rustc --version
cargo --version
```

## 创建项目

```bash
cargo new hello_rust
cd hello_rust

# 目录结构
hello_rust/
├── .gitignore
├── Cargo.toml        # 项目配置
└── src/
    └── main.rs       # 入口文件
```

```rust
// src/main.rs
fn main() {
    println!("Hello, world!");
}
```

## Cargo.toml

```toml
[package]
name = "hello_rust"
version = "0.1.0"
edition = "2021"     # Rust 版本（2015 / 2018 / 2021 / 2024）
```

## 构建运行

```bash
# 编译
cargo build

# 编译并运行
cargo run

# release 构建（优化，更慢但产物更快）
cargo build --release

# 检查（不生成可执行文件，快速验证代码）
cargo check
```

## 添加依赖

```toml
# Cargo.toml
[dependencies]
ferris-says = "2.2"
```

```rust
// src/main.rs
use ferris_says::say;
use std::io::{stdout, BufWriter};

fn main() {
    let stdout = stdout();
    let message = "Hello fellow Rustaceans!";
    let width = message.chars().count();

    let mut writer = BufWriter::new(stdout.lock());
    say(message, width, &mut writer).unwrap();
}
```

## 第一个测试

```rust
// src/lib.rs
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

```bash
cargo test
```

## 工具链

```bash
# 格式化
cargo fmt

# 代码检查
cargo clippy

# 文档生成
cargo doc --open
```

## IDE 配置

```bash
# VSCode：安装 rust-analyzer 扩展

# IntelliJ IDEA：安装 IntelliJ Rust 插件

# vim / neovim：配置 coc-rust-analyzer 或 LSP
```

## 调试技巧

```bash
# 1. dbg! 宏快速打印
fn main() {
    let x = 5;
    let y = dbg!(x * 2) + 3;
    println!("y = {}", y);
}

# 2. panic 时的 backtrace
RUST_BACKTRACE=1 cargo run
RUST_BACKTRACE=full cargo run
```

## 关联章节

- **01-basics/overview**：基础总览
- **03-ecosystem/cargo**：Cargo 深度
- **03-ecosystem/tooling**：工具链


## 完整工程结构（生产级 Hello World）

```bash
hello_rust/
├── .gitignore
├── Cargo.toml
├── Cargo.lock           # 锁定依赖版本（commit 到 git）
├── src/
│   ├── main.rs          # 二进制入口
│   ├── lib.rs           # 库入口（推荐拆分）
│   └── bin/
│       └── alt.rs       # 多个二进制
├── tests/               # 集成测试
│   └── integration.rs
├── examples/            # 可执行示例
│   └── basic.rs
├── benches/             # 基准测试（nightly）
│   └── bench.rs
└── target/              # 编译产物（git ignore）
```

## 实战案例：发布到 crates.io

```bash
# 1. 完善 Cargo.toml 元信息
# description / license / repository / keywords / categories

# 2. cargo login <api-token>

# 3. cargo publish --dry-run    # 预检
cargo publish                   # 真正发布

# 4. 撤回（24h 内只能一次）
cargo yank --vers 0.1.0

# 5. 文档自动部署到 docs.rs
#    cargo publish 后自动触发
#    访问 https://docs.rs/hello_rust
```

## 踩坑：rustup 版本管理

```bash
# 安装多个 toolchain
rustup toolchain install stable
rustup toolchain install nightly
rustup toolchain install 1.75.0      # 特定版本

# 项目级锁定
rustup override set nightly

# 全局默认
rustup default stable

# 跨平台编译
rustup target add aarch64-apple-darwin
rustup target add x86_64-unknown-linux-gnu

# 组件
rustup component add clippy rustfmt rust-src
```

## IDE 选择矩阵

| IDE / Editor | 插件 | 适合 |
|---|---|---|
| **VS Code** | rust-analyzer | 通用首选 |
| **IntelliJ IDEA** | IntelliJ Rust | 重度 Java 转 Rust |
| **Neovim** | nvim-lspconfig + rust-analyzer | vim 用户 |
| **Helix** | 内置 LSP | 现代编辑器 |
| **Zed** | 内置 | 极致性能 |
| **CLion** | IntelliJ Rust | C/C++ 转 Rust |


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
