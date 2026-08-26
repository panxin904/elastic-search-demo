---
title: 借用 Borrowing
---

# 借用 Borrowing

借用允许"使用值而不获取所有权"。通过 `&` 和 `&mut` 两种引用实现，编译期防止数据竞争。

## 一句话总结

> **借用 = 不获取所有权的引用**。**两大规则：不可变借用可多个、可变借用独占、不可变与可变不可共存**。**编译期消灭数据竞争**。

---

## 两大借用规则

```rust
// 规则 1：在同一作用域内：
//   - 不可变借用（&T）可以有任意多个
//   - 可变借用（&mut T）只能有一个

// 规则 2：不可变借用与可变借用不可共存
let mut s = String::from("hello");

let r1 = &s;       // 不可变借用 #1
let r2 = &s;       // 不可变借用 #2（OK）
// let r3 = &mut s;  // 编译错误（不可变 + 可变）
println!("{} {}", r1, r2);

// 不可变借用用完后再可变借用
let r1 = &s;
let r2 = &s;
println!("{} {}", r1, r2);
// r1, r2 不再使用
let r3 = &mut s;  // OK
r3.push_str(" world");
```

## 不可变借用

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}  // s 离开作用域，但因为是借用，不会 drop

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s);  // 借用 s
    println!("'{}' length: {}", s, len);  // s 仍然有效
}
```

## 可变借用

```rust
fn append_world(s: &mut String) {
    s.push_str(" world");
}

fn main() {
    let mut s = String::from("hello");
    append_world(&mut s);
    println!("{}", s);  // "hello world"
}
```

## 借用检查器（NLL）

```rust
// Non-Lexical Lifetimes（NLL）：借用生命周期基于"使用"而非"作用域"
fn main() {
    let mut s = String::from("hello");

    let r1 = &s;
    let r2 = &s;
    println!("{} {}", r1, r2);  // r1, r2 最后一次使用

    let r3 = &mut s;
    r3.push_str(" world");
    println!("{}", r3);
}
```

## 实战案例：迭代器借用

```rust
// 经典反模式：可变借用 + 不可变借用
let mut v = vec![1, 2, 3];
let first = &v[0];          // 不可变借用
v.push(4);                  // 编译错误（同时存在）
println!("{}", first);

// 正确：错开生命周期
let mut v = vec![1, 2, 3];
let first = &v[0];          // 不可变借用
println!("{}", first);       // 使用完 first
v.push(4);                  // 此后可以可变借用

// 正确：用 index 而非引用
let first = v[0];           // Copy，自动复制
v.push(4);                  // 不冲突
println!("{}", first);
```

## 4 个借用反模式

```
❌ 反模式 1：可变借用 + 不可变借用
let mut v = vec![1, 2];
let r = &v[0];
v.push(3);  // 借用冲突

❌ 反模式 2：借用跨 await（async 中）
async fn bad() {
    let guard = mutex.lock().unwrap();
    some_async().await;  // 跨 await 持有锁 → 死锁

❌ 反模式 3：返回局部变量的引用
fn bad() -> &String {
    let s = String::from("hi");
    &s  // 悬垂引用 → 编译错误

❌ 反模式 4：借用超过变量生命周期
let r;
{
    let s = String::from("hi");
    r = &s;  // 借用内部变量
}
println!("{}", r);  // s 已 drop → 编译错误
```

## 关联章节

- **01-basics/ownership**：所有权基础
- **01-basics/lifetimes**：生命周期标注
- **04-concurrency/channels**：多线程借用

## 一句话总结

> **借用 = Rust 的"编译期线程安全"基础**。**记住两大规则，编译错误会逼你写出安全的代码**。


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
