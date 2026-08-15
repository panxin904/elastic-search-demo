---
title: Rust 基础总览
---

# Rust 基础总览

Rust 入门阶段的核心：所有权 / 借用 / 生命周期三大概念 + Rust 思维模型建立。

## 一句话总结

> **Rust 基础 = 所有权 + 借用 + 生命周期**。**核心理念：内存安全 + 零成本抽象 + 无 GC**。**学习曲线陡峭但回报丰厚**。

---

## 为什么 Rust 独特

| 维度 | C/C++ | Java/Go | Rust |
|------|-------|---------|------|
| **内存管理** | 手动 | GC | 编译期所有权 |
| **类型系统** | 弱 | 中等 | 极强 |
| **运行时** | 无 | GC | 无 |
| **学习曲线** | 平缓 | 平缓 | 陡峭 |
| **性能** | 最优 | 中等 | 最优 |
| **内存安全** | ❌ 容易出错 | ✅ GC 保证 | ✅ 编译期保证 |

## 三大核心概念

```
所有权 (Ownership)
  - 每个值有且仅有一个所有者
  - 所有者离开作用域，值被自动 drop
  - 没有 GC、没有手动 free

借用 (Borrowing)
  - & 不可变引用（多个）
  - &mut 可变引用（独占）
  - 编译期防止数据竞争

生命周期 (Lifetimes)
  - 引用必须有生命周期
  - 防止悬垂引用（dangling reference）
  - 多数情况自动推断
```

## Hello World

```rust
fn main() {
    println!("Hello, world!");
}
```

```bash
# 编译并运行
rustc main.rs
./main

# 或用 Cargo（推荐）
cargo new hello_rust
cd hello_rust
cargo run
```

## Cargo：Rust 的标准工具

```toml
# Cargo.toml
[package]
name = "hello_rust"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }
```

```bash
# 常用命令
cargo new my_project    # 新建项目
cargo build             # 编译
cargo run               # 编译并运行
cargo test              # 运行测试
cargo clippy            # 代码检查
cargo fmt               # 格式化
cargo doc --open        # 生成文档
```

## 内存模型：栈 vs 堆

```
栈（Stack）
  - 后进先出（LIFO）
  - 大小固定、编译期已知
  - 分配极快（移动栈指针）
  - 局部变量 / 函数参数

堆（Heap）
  - 运行时分配
  - 大小可变
  - 分配较慢（需要找连续空间）
  - String / Vec / Box<T>
```

```rust
// 栈分配（快）
let x = 42;             // i32，栈上
let y = [1, 2, 3];      // [i32; 3]，栈上

// 堆分配（需要所有权转移）
let s = String::from("hello");  // 堆上分配
let v = vec![1, 2, 3];         // 堆上分配
```

## 变量与可变性

```rust
// 不可变（默认）
let x = 5;       // x: i32，不可变

// 可变（显式 mut）
let mut y = 5;   // y: i32，可变
y = 10;

// shadowing（遮蔽）
let z = 5;
let z = z + 1;       // 新变量覆盖旧变量
let z = "hello";     // 类型都可以改变
```

## 实战路径

```
Stage 1：所有权（1-2 天）
  → 理解 move / copy / clone
  → 理解 String vs &str
  → 实战：写一个简单的字符串处理函数

Stage 2：借用（2-3 天）
  → 理解 & vs &mut
  → 实战：写一个迭代器（Iterator）

Stage 3：生命周期（2-3 天）
  → 理解 'a 标注
  → 实战：写一个返回引用的函数

Stage 4：组合（1 周）
  → 所有权 + 借用 + 生命周期
  → 实战：写一个链表 / 二叉树
```

## 关联章节

- **01-basics/ownership**：所有权机制深度
- **01-basics/borrowing**：借用规则详解
- **01-basics/lifetimes**：生命周期标注
- **02-types-traits/overview**：类型系统

## 一句话总结

> **Rust 基础 = 三大概念建立心智模型**。**坚持 1-2 周，过了"所有权之墙"后 Rust 会变得自然**。
