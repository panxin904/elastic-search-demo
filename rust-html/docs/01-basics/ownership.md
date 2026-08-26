---
title: 所有权 Ownership
---

# 所有权 Ownership

所有权是 Rust 最核心的概念：每个值有且仅有一个所有者，所有者离开作用域时值被自动 drop。

## 一句话总结

> **所有权 = Rust 的"内存安全无 GC"密码**。**三大规则：唯一所有者 / move 转移 / drop 自动释放**。**目标：编译期消灭 use-after-free / double-free**。

---

## 三大规则

```rust
// 规则 1：每个值有且仅有一个所有者
let s = String::from("hello");  // s 是所有者
// take_ownership(s);           // s 已经无效
// println!("{}", s);           // 编译错误

// 规则 2：赋值或传参时所有权转移（move）
let s1 = String::from("hello");
let s2 = s1;  // s1 无效，所有权转移给 s2
// println!("{}", s1);  // 编译错误

// 规则 3：所有者离开作用域，值自动 drop
{
    let s = String::from("hello");
    // 使用 s
}  // s 离开作用域，自动 drop，内存释放
```

## Copy vs Move

```rust
// Copy trait：按位复制（如 i32, bool, f64）
let x = 5;
let y = x;       // 复制（Copy）
println!("{} {}", x, y);  // x 仍然有效

// Move：堆上的值默认 Move
let s1 = String::from("hello");
let s2 = s1;     // Move（堆上的 String）
// println!("{}", s1);  // s1 无效

// 显式 Clone（深拷贝）
let s1 = String::from("hello");
let s2 = s1.clone();  // 深拷贝
println!("{} {}", s1, s2);  // 都有效
```

## 所有权转移实战

```rust
// 函数参数：所有权进入函数
fn take_ownership(s: String) {
    println!("{}", s);
}  // s 在这里 drop

fn main() {
    let s = String::from("hello");
    take_ownership(s);  // s 所有权转移给函数
    // println!("{}", s);  // s 无效
}

// 返回值：所有权返回调用者
fn give_ownership() -> String {
    String::from("hello")
}

fn take_and_give_back(s: String) -> String {
    s
}
```

## Copy 类型清单

```
按位复制（Copy）：
  - 所有整数类型：i8 i16 i32 i64 i128 isize
                    u8 u16 u32 u64 u128 usize
  - 浮点数：f32 f64
  - bool, char
  - 元组（如果所有元素都是 Copy）：(i32, i32)
  - 数组（如果元素是 Copy）：[i32; 3]

堆分配（Move）：
  - String
  - Vec<T>
  - Box<T>
  - 所有自定义 struct / enum（默认）
```

## 实战案例：字符串所有权

```rust
// 反模式：clone 过度
fn process_bad(s: String) -> String {
    let _ = s.trim();
    s.clone()  // 不必要的 clone
}

// 推荐：返回新的 String
fn process_good(s: String) -> String {
    s.trim().to_string()  // 返回新的 owned String
}

// 推荐：借用不修改
fn print_good(s: &String) {
    println!("{}", s);
}
```

## 关联章节

- **01-basics/borrowing**：借用规则
- **01-basics/lifetimes**：生命周期
- **02-types-traits/advanced-types**：Copy/Clone trait

## 一句话总结

> **所有权是 Rust 的"心智负担"，但换来的是"内存安全 + 零运行时开销"**。**过了这一关，Rust 变得自然**。


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
