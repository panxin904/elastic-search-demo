---
title: WebAssembly
date: 2026-08-15  # date-auto-injected
---

# WebAssembly

Rust 是 WebAssembly 编译目标的事实标准：单一语言，浏览器 / Node.js / 边缘计算 / Serverless 全覆盖。

## 一句话总结

> **WASM = 浏览器 + 边缘 + Serverless 的跨平台运行时**。**核心：wasm-bindgen / wasm-pack / wasmtime / WasmEdge**。

---

## 安装 WASM 工具链

```bash
rustup target add wasm32-unknown-unknown
rustup target add wasm32-wasi

cargo install wasm-pack
```

## 第一个 WASM 模块

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
```

```bash
wasm-pack build --target web

# 输出
pkg/
├── my_code.d.ts
├── my_code.js
├── my_code_bg.wasm
└── my_code_bg.wasm.d.ts
```

## 在 JavaScript 中调用

```javascript
import init, { add, fibonacci } from "./pkg/my_code.js";

await init();

console.log(add(2, 3));            // 5
console.log(fibonacci(10));         // 55
```

## JS 互操作

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    pub fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet(name: &str) {
    alert(&("Hello, ".to_string() + name));
}
```

## WASI：服务端 WASM

```rust
use std::io::{self, Read, Write};

fn main() -> io::Result<()> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let output = input.to_uppercase();
    io::stdout().write_all(output.as_bytes())?;
    Ok(())
}
```

```bash
cargo build --target wasm32-wasi --release
wasmtime target/wasm32-wasi/release/my_app.wasm < input.txt > output.txt
```

## 边缘计算（Cloudflare Workers）

```rust
use worker::*;

#[event(fetch)]
async fn main(req: Request, env: Env, ctx: Context) -> Result<Response> {
    let path = req.path();

    let response = match path.as_str() {
        "/api/hello" => {
            let name = req.query().get("name").unwrap_or("World");
            Response::ok(format!("Hello, {}!", name))?
        }
        "/" => Response::ok("Rust WASM Worker")?,
        _ => Response::error("Not Found", 404)?,
    };

    Ok(response)
}
```

## 4 大 WASM 优势

```
1. 跨平台：浏览器 / Node.js / Deno / Workers / Wasmtime
2. 性能：接近原生（V8 优化 + AOT 编译）
3. 内存安全：沙箱执行
4. 小体积：gzip 后几十 KB
```

## 实战案例：图像处理

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn grayscale(input: &[u8], width: u32, height: u32) -> Vec<u8> {
    let mut output = Vec::with_capacity(input.len());
    for chunk in input.chunks(4) {
        let r = chunk[0] as f32;
        let g = chunk[1] as f32;
        let b = chunk[2] as f32;
        let gray = (0.299 * r + 0.587 * g + 0.114 * b) as u8;
        output.extend_from_slice(&[gray, gray, gray, chunk[3]]);
    }
    output
}
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **05-systems/performance**：性能优化

## 一句话总结

> **WASM = Rust 的跨平台目标**：浏览器 / Node.js / 边缘 / Serverless / 桌面，唯一语言覆盖所有场景**。


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
