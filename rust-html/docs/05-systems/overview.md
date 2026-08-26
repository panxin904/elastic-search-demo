---
title: 系统编程总览
---

# 系统编程总览

Rust 是少数同时具备"系统级性能 + 内存安全"的语言。本章覆盖 unsafe / FFI / 嵌入式 / WASM / 性能优化 5 大方向。

## 一句话总结

> **Rust 系统编程 = unsafe 精确控制 + 安全抽象边界**。**核心：unsafe 块隔离危险、FFI 与 C 互操作、嵌入式裸机、WASM 跨平台、性能零开销**。

---

## 5 大方向

```
1. unsafe Rust       - 绕过安全检查，精确控制内存
2. FFI               - 与 C 库互操作（Python/C++/JS 桥接）
3. 嵌入式            - 微控制器裸机编程
4. WebAssembly       - 浏览器 / 边缘 / Serverless 部署
5. 性能优化          - 剖析 + SIMD + 并行
```

## unsafe Rust：4 种超能力

```rust
// unsafe 块内可以做 4 件事：
// 1. 解引用裸指针
// 2. 调用 unsafe 函数
// 3. 访问或修改可变静态变量
// 4. 实现 unsafe Trait

// 解引用裸指针
let mut num = 5;
let r1 = &num as *const i32;
let r2 = &mut num as *mut i32;

unsafe {
    println!("r1 is: {}", *r1);
    *r2 = 10;
}

// unsafe 块不关闭借用检查器
// 只关闭这 4 个检查，其他规则仍然生效
```

## unsafe 的使用原则

```rust
// ✅ 推荐模式：unsafe 封装在安全 API 内
pub struct SafeVec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

impl<T> SafeVec<T> {
    pub fn new() -> Self {
        Self { ptr: std::ptr::null_mut(), len: 0, cap: 0 }
    }

    pub fn push(&mut self, val: T) {
        // unsafe 块限制在最小范围
        unsafe {
            if self.len == self.cap {
                self.grow();
            }
            std::ptr::write(self.ptr.add(self.len), val);
            self.len += 1;
        }
    }
}

// ❌ 反模式：unsafe 散布全代码
// ❌ 反模式：用 unsafe 绕过借用检查
```

## FFI：调用 C 库

```rust
// 声明外部 C 函数
extern "C" {
    fn abs(input: i32) -> i32;
    fn strlen(s: *const c_char) -> usize;
}

use std::os::raw::c_char;

fn main() {
    unsafe {
        println!("abs(-5) = {}", abs(-5));
    }
}

// 调用 Rust 函数从 C
#[no_mangle]
pub extern "C" fn rust_function(x: i32) -> i32 {
    x * 2
}
```

## bindgen：从 C 头生成绑定

```rust
// build.rs
fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");
    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .unwrap();
}
```

## 嵌入式 Rust

```rust
#![no_std]      // 不使用 std
#![no_main]     // 不使用标准 main

use panic_halt as _;  // panic 时停止 CPU
use cortex_m_rt::entry;

#[entry]
fn main() -> ! {
    // 操作硬件寄存器
    let peripherals = cortex_m::Peripherals::take().unwrap();
    let gpioa = &peripherals.GPIOA;
    
    // 配置 GPIO（直接写寄存器）
    unsafe {
        gpioa.MODER.modify(|_, w| w.bits(0b01));  // 输出模式
    }
    
    loop {
        // 闪烁 LED
        unsafe {
            gpioa.BSRR.write(|w| w.bits(1 << 5));  // set
        }
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
        unsafe {
            gpioa.BSRR.write(|w| w.bits(1 << (5 + 16)));  // reset
        }
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
    }
}
```

## WebAssembly

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u64 {
    let mut a: u64 = 0;
    let mut b: u64 = 1;
    for _ in 0..n {
        let temp = a + b;
        a = b;
        b = temp;
    }
    a
}

#[wasm_bindgen(start)]
pub fn main() {
    console_log!("WASM module loaded!");
}
```

```bash
# 编译为 WASM
cargo build --target wasm32-unknown-unknown --release
wasm-pack build --target web

# 在 JS 中使用
import init, { add } from "./my_pkg/my_code.js";
await init();
console.log(add(2, 3));  // 5
```

## 性能优化

```rust
// 1. 剖析（用 cargo-flamegraph）
cargo install flamegraph
cargo flamegraph

// 2. SIMD（手写或用 std::simd nightly）
#[cfg(target_arch = "x86_64")]
unsafe {
    use std::arch::x86_64::*;
    let a = _mm256_set_ps(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0);
    let b = _mm256_set_ps(8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0);
    let sum = _mm256_add_ps(a, b);
}

// 3. 内存布局：避免 padding
#[repr(C)]
struct Compact {
    a: u8,
    b: u32,
    c: u8,
}

// 4. 零拷贝：用 &[u8] / Cow<str>
fn parse(s: &str) -> &str {
    s.trim()  // 切片，无分配
}
```

## 实战案例：JSON 解析器

```rust
// 用 serde_json 解析（高性能）
use serde::Deserialize;

#[derive(Deserialize)]
struct User {
    name: String,
    age: u8,
    email: String,
}

fn main() {
    let json = r#"{"name":"Alice","age":30,"email":"alice@example.com"}"#;
    let user: User = serde_json::from_str(json).unwrap();
    println!("{} ({})", user.name, user.age);
}

// 性能：serde_json 解析 100MB JSON 仅 1-2 秒
// 对比 Java Jackson：3-5 倍性能提升
```

## 关联章节

- **05-systems/unsafe**：unsafe Rust 深度
- **05-systems/ffi**：FFI 与 C 互操作
- **05-systems/wasm**：WebAssembly 实战
- **05-systems/performance**：性能优化技巧

## 一句话总结

> **Rust 系统编程 = 安全抽象 + unsafe 精确控制**。**适合：嵌入式 / 高性能服务 / WASM / CLI 工具 / 系统级库**。


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
