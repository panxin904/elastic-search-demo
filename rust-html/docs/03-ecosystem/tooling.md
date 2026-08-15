---
title: 测试与工具链
---

# 测试与工具链

Rust 工具链一流：rustfmt / clippy / rust-analyzer / cargo test / cargo bench 全内置。

## 一句话总结

> **Rust 工具链 = 格式化 + lint + IDE + 测试 + 基准**。**核心：cargo test / clippy / rust-analyzer**。

---

## cargo test

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(1, 2), 3);
    }

    #[test]
    #[should_panic]
    fn test_panic() {
        panic!("test panic");
    }

    #[test]
    #[ignore = "expensive test"]
    fn test_expensive() {
        // 长时间运行的测试
    }
}
```

```bash
# 运行所有测试
cargo test

# 详细输出
cargo test -- --nocapture

# 运行特定测试
cargo test test_add

# 运行被 ignore 的测试
cargo test -- --ignored
```

## 集成测试

```bash
# tests/integration_test.rs
use my_library;

#[test]
fn test_integration() {
    assert_eq!(my_library::add(1, 2), 3);
}
```

```bash
cargo test --test integration_test
```

## 文档测试

```rust
/// 加法函数
///
/// # Examples
///
/// ```
/// let result = my_library::add(1, 2);
/// assert_eq!(result, 3);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

```bash
cargo test --doc
```

## 属性测试（proptest）

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_add_commutative(a in 0..1000i32, b in 0..1000i32) {
        assert_eq!(add(a, b), add(b, a));
    }
}
```

## Mock 测试

```rust
use mockall::mock;

#[automock]
trait Database {
    fn get_user(&self, id: u32) -> Option<User>;
}
```

## 基准测试（criterion）

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_add(c: &mut Criterion) {
    c.bench_function("add", |b| {
        b.iter(|| add(black_box(1), black_box(2)));
    });
}

criterion_group!(benches, bench_add);
criterion_main!(benches);
```

```bash
cargo +nightly bench
```

## rustfmt

```bash
cargo fmt
cargo fmt --check  # CI 用
```

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
tab_spaces = 4
```

## clippy

```bash
cargo clippy
cargo clippy -- -W clippy::pedantic
cargo clippy --fix
```

```rust
// clippy 常见提示
let v: Vec<i32> = Vec::new();  // 反模式
v.push(1);
v.push(2);

let mut v = vec![1, 2];  // 推荐
```

## rust-analyzer

```bash
# VSCode：安装 rust-analyzer 扩展
# IntelliJ IDEA：安装 IntelliJ Rust 插件
# vim / neovim：配置 coc-rust-analyzer 或 LSP
```

## cargo 辅助命令

```bash
cargo install cargo-outdated      # 检查过期依赖
cargo install cargo-tree          # 依赖树
cargo install cargo-bloat         # 二进制大小分析
cargo install cargo-audit         # 安全审计
cargo install cargo-watch         # 文件变化自动重新构建
cargo install cargo-edit          # 命令行编辑 Cargo.toml
cargo install cargo-flamegraph    # 火焰图
```

## 实战案例：完整测试栈

```rust
// src/lib.rs
pub fn parse_positive(s: &str) -> Result<u32, String> {
    let n: u32 = s.parse().map_err(|e: std::num::ParseIntError| e.to_string())?;
    if n == 0 {
        return Err("must be positive".to_string());
    }
    Ok(n)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse() {
        assert_eq!(parse_positive("42").unwrap(), 42);
    }

    #[test]
    fn test_zero() {
        assert!(parse_positive("0").is_err());
    }

    #[test]
    fn test_negative() {
        assert!(parse_positive("-1").is_err());
    }
}
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/cargo**：Cargo
- **03-ecosystem/std-lib**：标准库

## 一句话总结

> **Rust 工具链 = 格式化 + lint + IDE + 测试 + 基准**。**核心：cargo test / clippy / rust-analyzer**。
