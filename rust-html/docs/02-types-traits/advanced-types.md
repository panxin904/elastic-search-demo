---
title: 高级类型
date: 2026-08-15  # date-auto-injected
---

# 高级类型

Newtype / 类型别名 / 永不返回类型 / DST / PhantomData — Rust 类型系统的"瑞士军刀"。

## 一句话总结

> **高级类型 = 表达领域语义 + 类型安全 + 零成本抽象**。**核心：Newtype 模式 / PhantomData / never 类型**。

---

## Newtype 模式

```rust
// 用 tuple struct 包装已有类型，赋予新语义
struct UserId(u64);
struct ProductId(u64);

fn get_user(id: UserId) -> User { todo!() }
fn get_product(id: ProductId) -> Product { todo!() }

let uid = UserId(42);
let pid = ProductId(100);
// get_product(uid);  // 编译错误：类型不匹配
```

## 类型别名

```rust
type Kilometers = i32;
type Thunk = Box<dyn Fn() + Send + 'static>;

let x: Kilometers = 5;
println!("{}", x);  // 5（与 i32 完全等价）

// 类型别名 ≠ Newtype
// 类型别名与原类型完全相同
// Newtype 是新类型，类型检查更严格
```

## never 类型 !

```rust
fn diverging() -> ! {
    panic!("This function never returns!");
}

// never 类型可以强制转换为任何类型
let x: i32 = diverging();
```

## 动态大小类型（DST）

```rust
// str 是 DST：大小编译期未知
let s: str = "hello";  // 错误：DST 不能作为变量
let s: &str = "hello";  // 正确：&str 是胖指针（ptr + len）

// Sized trait：默认所有泛型参数都有 Sized 约束
fn generic<T>(t: T) {}  // 等价于 fn generic<T: Sized>(t: T)

// 放宽约束
fn generic<T: ?Sized>(t: &T) {}
```

## PhantomData

```rust
use std::marker::PhantomData;

struct Iter<'a, T: 'a> {
    ptr: *const T,
    _marker: PhantomData<&'a T>,
}

// 标识拥有所有权但不存储
struct Owned<T> {
    _marker: PhantomData<T>,
}
```

## 关联类型 vs 泛型

```rust
// 关联类型：每个类型只能实现一次
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}

// 泛型：可以多次实现
trait From<T> {
    fn from(value: T) -> Self;
}
```

## 实战案例：单位类型

```rust
use std::marker::PhantomData;
use std::ops::Add;

struct Meter;
struct Kilometer;

struct Distance<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

impl<Unit> Distance<Unit> {
    fn new(value: f64) -> Self {
        Self { value, _unit: PhantomData }
    }
}

impl Distance<Kilometer> {
    fn to_meters(self) -> Distance<Meter> {
        Distance::new(self.value * 1000.0)
    }
}

impl Add for Distance<Meter> {
    type Output = Distance<Meter>;
    fn add(self, other: Self) -> Self {
        Distance::new(self.value + other.value)
    }
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **02-types-traits/trait**：Trait
- **01-basics/lifetimes**：生命周期


## 类型转换：`From` / `Into` / `TryFrom` / `TryInto`

```rust
// From：标准转换（消费输入）
struct Meters(f64);
impl From<f64> for Meters {
    fn from(v: f64) -> Self { Meters(v) }
}

// Into：From 的反向（自动实现）
let m: Meters = 3.14.into();

// TryFrom：可能失败的转换
struct EvenNumber(i32);
impl TryFrom<i32> for EvenNumber {
    type Error = &'static str;
    fn try_from(v: i32) -> Result<Self, Self::Error> {
        if v % 2 == 0 { Ok(EvenNumber(v)) }
        else { Err("not even") }
    }
}
```

## `Sized` 与 `?Sized`

```rust
// T: Sized 默认所有泛型参数都有 Sized 约束
fn print<T: std::fmt::Debug>(t: T) { println!("{:?}", t); }

// ?Sized 放宽约束（接收 DST）
fn print_dyn<T: std::fmt::Debug + ?Sized>(t: &T) { println!("{:?}", t); }

print_dyn(&"hello");  // &str 是 DST
print_dyn(&[1, 2, 3]);  // &[T] 是 DST
```

## 内部可变性：`Cell` / `RefCell` / `Mutex`

```rust
use std::cell::Cell;

// Cell<T>：Copy 类型（无需 mut）
struct Counter { count: Cell<u32> }
impl Counter {
    fn increment(&self) { self.count.set(self.count.get() + 1); }
}

// RefCell<T>：运行时借用检查（用于单线程）
use std::cell::RefCell;
let data = RefCell::new(vec![1, 2, 3]);
data.borrow_mut().push(4);  // 运行时检查，可能 panic
```

## 实战案例：Builder 模式 + PhantomData

```rust
use std::marker::PhantomData;

// 类型状态（type state）模式
struct Uninitialized;
struct Initialized;

struct Connection<State> {
    handle: i32,
    _state: PhantomData<State>,
}

impl Connection<Uninitialized> {
    fn new() -> Self {
        Self { handle: 0, _state: PhantomData }
    }
    fn connect(self) -> Connection<Initialized> {
        Connection { handle: 1, _state: PhantomData }
    }
}

impl Connection<Initialized> {
    fn query(&self, sql: &str) -> String {
        format!("Result for {}", sql)
    }
}

let conn = Connection::new().connect();
conn.query("SELECT 1");  // 未初始化的连接无法 query
```

## 选型决策：何时用 Newtype vs 类型别名

| 场景 | 推荐 | 原因 |
|---|---|---|
| 防止单位混淆（米/千米） | **Newtype** | 编译期阻止错误 |
| 用户 ID vs 产品 ID | **Newtype** | 类型严格 |
| 简化复杂签名 `Box<dyn Fn() + Send + 'static>` | **类型别名** | 不增加类型严格度 |
| 字符串别名 | **类型别名** | String 还是 String |


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
