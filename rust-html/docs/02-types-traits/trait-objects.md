---
title: Trait 对象与动态分发
date: 2026-08-15  # date-auto-injected
---

# Trait 对象与动态分发

dyn Trait 是运行时多态：通过虚函数表（vtable）在运行时决定调用的具体实现。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Rust Trait 分发机制</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">静态（泛型单态化）vs 动态（dyn Trait vtable）</text>

  <!-- 静态分发 -->
  <rect class="at-hover-card" x="30" y="90" width="265" height="180" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="162" y="115" text-anchor="middle" font-size="13" font-weight="700" fill="#1e40af">① 静态分发 Static Dispatch</text>
  <text x="50" y="140" font-size="10" font-family="monospace" fill="#1e293b">fn call&lt;T: Speak&gt;(t: T) {</text>
  <text x="60" y="158" font-size="10" font-family="monospace" fill="#1e293b">t.speak()</text>
  <text x="50" y="175" font-size="10" font-family="monospace" fill="#1e293b">}</text>

  <text x="50" y="200" font-size="10" font-weight="700" fill="#1e40af">单态化（Monomorphization）</text>
  <text x="50" y="220" font-size="9" fill="#334155">call(Dog) → call_dog()</text>
  <text x="50" y="235" font-size="9" fill="#334155">call(Cat) → call_cat()</text>
  <text x="50" y="252" font-size="9" fill="#475569" font-style="italic">编译器生成具体类型副本</text>

  <text x="50" y="268" font-size="10" font-weight="700" fill="#10b981">+ 零运行时开销 / 可内联</text>
  <text x="50" y="282" font-size="10" font-weight="600" fill="#dc2626">- 泛型膨胀（binary size↑）</text>

  <!-- 动态分发 -->
  <rect class="at-hover-card" x="305" y="90" width="265" height="180" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="437" y="115" text-anchor="middle" font-size="13" font-weight="700" fill="#991b1b">② 动态分发 Dynamic Dispatch</text>
  <text x="325" y="140" font-size="10" font-family="monospace" fill="#1e293b">fn call(t: &amp;dyn Speak) {</text>
  <text x="335" y="158" font-size="10" font-family="monospace" fill="#1e293b">t.speak()</text>
  <text x="325" y="175" font-size="10" font-family="monospace" fill="#1e293b">}</text>

  <text x="325" y="200" font-size="10" font-weight="700" fill="#991b1b">虚表（vtable）查找</text>
  <text x="325" y="220" font-size="9" fill="#334155">trait object = data + vtable ptr</text>
  <text x="325" y="235" font-size="9" fill="#334155">vtable: [speak, drop, ...]</text>
  <text x="325" y="252" font-size="9" fill="#475569" font-style="italic">运行时通过 vtable 间接调用</text>

  <text x="325" y="268" font-size="10" font-weight="700" fill="#10b981">+ 二进制小 / 异构集合</text>
  <text x="325" y="282" font-size="10" font-weight="600" fill="#dc2626">- 一次间接跳转 · 不可内联</text>

  <!-- 内存布局对比 -->
  <text x="300" y="295" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">内存布局对比</text>

  <rect x="50" y="305" width="220" height="70" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="160" y="325" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">泛型 T: Speak（具体类型）</text>
  <rect x="60" y="335" width="50" height="30" fill="#3b82f6" opacity="0.4" stroke="#3b82f6"/>
  <text x="85" y="355" text-anchor="middle" font-size="9" fill="white" font-weight="700">data</text>
  <rect x="120" y="335" width="140" height="30" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="190" y="355" text-anchor="middle" font-size="9" fill="#1e40af">（无 vtable）</text>

  <rect x="330" y="305" width="240" height="70" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="450" y="325" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">dyn Speak（trait object）</text>
  <rect x="340" y="335" width="50" height="30" fill="#dc2626" opacity="0.4" stroke="#dc2626"/>
  <text x="365" y="355" text-anchor="middle" font-size="9" fill="white" font-weight="700">data</text>
  <rect x="400" y="335" width="50" height="30" fill="#f59e0b" opacity="0.4" stroke="#f59e0b"/>
  <text x="425" y="355" text-anchor="middle" font-size="9" fill="white" font-weight="700">vptr</text>
  <rect x="460" y="335" width="100" height="30" fill="#fee2e2" stroke="#dc2626"/>
  <text x="510" y="355" text-anchor="middle" font-size="9" fill="#991b1b">→vtable</text>

  <!-- 选择策略 -->
  <rect x="30" y="395" width="540" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="418" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">选择策略</text>
  <text x="50" y="438" font-size="10" fill="#334155">· 默认静态（impl Trait / &lt;T: Trait&gt;）— 性能优先</text>
  <text x="50" y="456" font-size="10" fill="#334155">· 异构集合 Vec&lt;Box&lt;dyn Trait&gt;&gt; — 允许不同具体类型</text>
  <text x="320" y="438" font-size="10" fill="#334155">· 插件架构 / 减少二进制大小 → dyn</text>
  <text x="320" y="456" font-size="10" fill="#334155">· 注意：dyn Trait 不实现 Send/Sync 自动派生</text>
</svg>

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [go](https://java-px.bot.cd/go/):Go 对比
- [linux](https://java-px.bot.cd/linux/):Linux 系统编程
- [android](https://java-px.bot.cd/android/):NDK 集成
