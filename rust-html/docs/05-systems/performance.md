---
title: 性能优化
date: 2026-08-15  # date-auto-injected
---

# 性能优化

Rust 的"零成本抽象"已接近最优，但仍有优化空间：剖析 + SIMD + 内存布局 + 并行。

## 一句话总结

> **性能优化 = 剖析先行 + 针对性优化 + 测量验证**。**核心：cargo flamegraph / criterion / SIMD / rayon**。

---

## 性能优化 4 步法

```
1. Measure  -  测量
2. Profile  -  剖析
3. Optimize -  优化
4. Verify   -  验证
```

## 1. 测量 + 剖析

```bash
# 编译优化
cargo build --release

# 火焰图
cargo install flamegraph
cargo flamegraph

# 基准测试
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_bench"
harness = = "false"
```

```rust
// benches/my_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_process(c: &mut Criterion) {
    c.bench_function("process", |b| {
        b.iter(|| process(black_box(100)));
    });
}

criterion_group!(benches, bench_process);
criterion_main!(benches);
```

## 2. 内存布局优化

```rust
// 默认布局
struct Unoptimized {
    a: u8,
    b: u32,
    c: u8,
}

// 手动排序（按大小降序）
struct Optimized {
    b: u32,
    a: u8,
    c: u8,
}

#[repr(C)]
struct CStruct {
    a: u8,
    b: u32,
    c: u8,
}

// 避免 Box 包装小类型
let x = Box::new(42);  // 反模式
let x: i32 = 42;  // 推荐
```

## 3. SIMD

```rust
use std::arch::x86_64::*;

#[target_feature(enable = "avx2")]
unsafe fn simd_add(a: &[f32; 8], b: &[f32; 8]) -> [f32; 8] {
    let va = _mm256_loadu_ps(a.as_ptr());
    let vb = _mm256_loadu_ps(b.as_ptr());
    let result = _mm256_add_ps(va, vb);
    let mut out = [0.0f32; 8];
    _mm256_storeu_ps(out.as_mut_ptr(), result);
    out
}
```

## 4. 并行（rayon）

```rust
use rayon::prelude::*;

let sum: i64 = (1..=1_000_000).into_par_iter().sum();

let mut data = vec![3, 1, 4, 1, 5, 9, 2, 6];
data.par_sort();

let evens: Vec<i32> = data.par_iter().filter(|x| *x % 2 == 0).cloned().collect();
```

## 5. 零拷贝

```rust
use std::borrow::Cow;

fn process_good(input: &str) -> Cow<str> {
    if input.chars().all(|c| c.is_uppercase() || !c.is_alphabetic()) {
        Cow::Borrowed(input)
    } else {
        Cow::Owned(input.to_uppercase())
    }
}

fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}
```

## 6. 避免分配

```rust
const PREFIX: &str = "item-";

fn better(n: usize) -> Vec<String> {
    (0..n).map(|i| format!("{}{}", PREFIX, i)).collect()
}
```

## 7. 异步并行（tokio）

```rust
async fn fetch_all() {
    let (a, b, c) = tokio::join!(
        fetch_url("https://a.com"),
        fetch_url("https://b.com"),
        fetch_url("https://c.com"),
    );
}
```

## 8. 二进制优化

```toml
# Cargo.toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true
```

```bash
cargo install cargo-bloat
cargo bloat --release --crates

upx --best target/release/my_app
```

## 实战案例：JSON 解析性能对比

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
    email: String,
}

fn parse_users(json: &str) -> Vec<User> {
    serde_json::from_str(json).unwrap()
}

// 性能：
// - from_str: 1.0x baseline
// - borrowed: 1.5-2x 更快（用 &str 替代 String）
// - streaming: 适合 1GB+ 文件
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/unsafe**：unsafe 优化
- **05-systems/wasm**：WASM 性能

## 一句话总结

> **性能优化 = 剖析先行 + 针对性优化 + 测量验证**。**Rust 零成本抽象让大部分代码已经接近最优**。


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
