---
title: 闭包与迭代器
---

# 闭包与迭代器

闭包是匿名函数，迭代器是惰性序列。两者结合是 Rust 函数式编程的核心。

## 一句话总结

> **闭包 + 迭代器 = Rust 函数式编程**。**核心：Fn / FnMut / FnOnce / Iterator trait**。**性能：零成本抽象**。

---

## 闭包基础

```rust
let add = |a, b| a + b;

// 捕获环境
let x = 5;
let print_x = || println!("x = {}", x);

// 移动所有权
let s = String::from("hello");
let consume = move || println!("{}", s);
```

## 3 大闭包 Trait

```rust
fn call_fn<F: Fn()>(f: F) {
    f();
    f();
}

fn call_fn_mut<F: FnMut()>(mut f: F) {
    f();
    f();
}

fn call_fn_once<F: FnOnce()>(f: F) {
    f();
}
```

## 迭代器基础

```rust
let v = vec![1, 2, 3, 4, 5];

let sum: i32 = v.iter().sum();
let v2: Vec<i32> = v.into_iter().map(|x| x * 2).collect();

let mut v = vec![1, 2, 3];
for x in v.iter_mut() {
    *x *= 2;
}
```

## Iterator trait

```rust
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;

    fn map<B, F>(self, f: F) -> Map<Self, F>
    where F: FnMut(Self::Item) -> B;

    fn filter<P>(self, predicate: P) -> Filter<Self, P>
    where P: FnMut(&Self::Item) -> bool;

    fn collect<B>(self) -> B
    where B: FromIterator<Self::Item>;

    fn fold<B, F>(self, init: B, f: F) -> B
    where F: FnMut(B, Self::Item) -> B;
}
```

## 常用适配器

```rust
let v = vec![1, 2, 3, 4, 5];

let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
let evens: Vec<&i32> = v.iter().filter(|x| *x % 2 == 0).collect();
let first3: Vec<&i32> = v.iter().take(3).collect();

let a = vec![1, 2, 3];
let b = vec!["a", "b", "c"];
let pairs: Vec<(i32, &str)> = a.iter().zip(b.iter()).map(|(x, y)| (*x, *y)).collect();
```

## 消费器

```rust
let v = vec![1, 2, 3, 4, 5];

let total: i32 = v.iter().sum();
let sum = v.iter().fold(0, |acc, x| acc + x);

let has_negative = v.iter().any(|x| *x < 0);
let all_positive = v.iter().all(|x| *x > 0);

let first_even = v.iter().find(|x| *x % 2 == 0);

let count = v.iter().filter(|x| *x > 2).count();
```

## 自定义迭代器

```rust
struct Counter {
    count: u32,
}

impl Counter {
    fn new() -> Self { Self { count: 0 } }
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count < 6 {
            Some(self.count)
        } else {
            None
        }
    }
}

let counter = Counter::new();
let sum: u32 = counter.sum();
```

## 实战案例：惰性斐波那契

```rust
struct Fib {
    curr: u64,
    next: u64,
}

impl Fib {
    fn new() -> Self { Self { curr: 0, next: 1 } }
}

impl Iterator for Fib {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let curr = self.curr;
        self.curr = self.next;
        self.next = curr + self.next;
        Some(curr)
    }
}

let fib = Fib::new();
let first10: Vec<u64> = fib.take(10).collect();
```

## 关联章节

- **02-types-traits/trait**：Trait
- **06-advanced/macro**：宏
- **06-advanced/smart-pointer**：智能指针

## 一句话总结

> **闭包 + 迭代器 = Rust 函数式核心**。**零成本抽象，性能等同手写循环**。


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
