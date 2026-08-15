---
title: Trait 对象与动态分发
---

# Trait 对象与动态分发

dyn Trait 是运行时多态：通过虚函数表（vtable）在运行时决定调用的具体实现。

## 一句话总结

> **dyn Trait = 运行时多态**。**核心：堆分配的 Box\<dyn Trait\> / 引用形式 &dyn Trait**。**对比泛型：性能略低、灵活性高**。

---

## 静态分发 vs 动态分发

```rust
// 静态分发（泛型）
fn print_summary<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}
// 优点：内联优化、性能最优
// 缺点：二进制膨胀

// 动态分发（Trait Object）
fn print_summary(item: &dyn Summary) {
    println!("{}", item.summarize());
}
// 优点：灵活、支持异构集合
// 缺点：间接调用、不能内联
```

## Trait Object 用法

```rust
trait Draw {
    fn draw(&self);
}

struct Circle { radius: f64 }
struct Square { side: f64 }

impl Draw for Circle {
    fn draw(&self) { println!("Circle r={}", self.radius); }
}

impl Draw for Square {
    fn draw(&self) { println!("Square s={}", self.side); }
}

// 异构集合
let shapes: Vec<Box<dyn Draw>> = vec![
    Box::new(Circle { radius: 1.0 }),
    Box::new(Square { side: 2.0 }),
];

for shape in shapes.iter() {
    shape.draw();  // 动态分发
}
```

## Box\<dyn Trait\>

```rust
let circle: Box<dyn Draw> = Box::new(Circle { radius: 1.0 });

// 用途：
// 1. 异构集合
// 2. 返回实现 Trait 的类型（不知道具体类型）
// 3. 减小栈占用
```

## Object Safety（对象安全）

```rust
// 不是所有 Trait 都能作为 Trait Object
// 要求：
// 1. 方法签名不返回 Self
// 2. 方法没有泛型参数
// 3. 父 Trait 也必须是对象安全的

trait Clone {
    fn clone(&self) -> Self;  // 返回 Self，不是对象安全的
}
```

## dyn Trait Send / Sync

```rust
// 默认 dyn Trait 不是 Send
fn spawn_draw(shape: Box<dyn Draw>) {
    thread::spawn(move || shape.draw());  // 编译错误
}

// 加约束
fn spawn_draw(shape: Box<dyn Draw + Send>) {
    thread::spawn(move || shape.draw());  // OK
}
```

## 实战案例：插件系统

```rust
trait Plugin: Send + Sync {
    fn name(&self) -> &str;
    fn execute(&self, input: &str) -> Result<String, String>;
}

struct UppercasePlugin;
impl Plugin for UppercasePlugin {
    fn name(&self) -> &str { "uppercase" }
    fn execute(&self, input: &str) -> Result<String, String> {
        Ok(input.to_uppercase())
    }
}

struct PluginRegistry {
    plugins: Vec<Box<dyn Plugin>>,
}

impl PluginRegistry {
    fn register<P: Plugin + 'static>(&mut self, plugin: P) {
        self.plugins.push(Box::new(plugin));
    }

    fn run(&self, name: &str, input: &str) -> Result<String, String> {
        for plugin in &self.plugins {
            if plugin.name() == name {
                return plugin.execute(input);
            }
        }
        Err(format!("Plugin not found: {}", name))
    }
}
```

## 关联章节

- **02-types-traits/trait**：Trait 基础
- **02-types-traits/generics**：泛型（静态分发）
- **04-concurrency/channels**：消息传递

## 一句话总结

> **dyn Trait = 运行时多态**。**用于异构集合与插件系统，但有性能开销**。
