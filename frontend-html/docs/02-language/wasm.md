---
title: WebAssembly 入门
---

# WebAssembly 入门

## 🎯 什么是 WebAssembly

Wasm 是**可移植、体积小、加载快、接近原生性能**的二进制指令格式。可以理解为浏览器的"汇编"。

主要用途：
- 计算密集型任务（图像处理、视频编解码、CAD、加密、游戏）
- 把 C/C++/Rust 编译到 Wasm，拿到浏览器跑
- 替代部分 JS "慢点"

## 🧰 Wasm 的角色

```
┌────────────┐    编译     ┌────────┐     fetch     ┌──────────┐
│ C/C++/Rust │ ──────────► │ .wasm  │ ────────────► │ Browser  │
└────────────┘             └────────┘               └──────────┘
                              │                         │
                              │ + JS 胶水代码（实例化） ▼
                          WebAssembly.instantiateStreaming(...)
```

## 📦 一个最小例子

```js
// 假设我们有一个 add.wasm，提供 (module (export "add" (func $add ...)))
async function loadWasm() {
  const response = await fetch('/add.wasm')
  const { instance } = await WebAssembly.instantiateStreaming(response)
  const { add } = instance.exports
  return add
}

const add = await loadWasm()
add(1, 2)  // 3
```

## 🦀 Rust → Wasm（最常见）

```bash
# 安装 wasm-pack
cargo install wasm-pack

# 在 lib.rs 中标记函数
#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 { a + b }

# 编译
wasm-pack build --target web
```

```html
<script type="module">
  import init, { add } from './pkg/my_crate.js'
  await init()
  console.log(add(1, 2))  // 3
</script>
```

## 🛠️ 主流工具栈

| 工具 | 来源语言 | 输出 |
|------|---------|------|
| Emscripten | C/C++ | .wasm + .js glue |
| wasm-pack | Rust | npm 包 |
| AssemblyScript | TypeScript-like | .wasm（适合前端） |
| wazero / wasmtime | Go runtime | 浏览器外执行 |

## ⚖️ 与 JS 对比

| | JS | Wasm |
|--|----|------|
| 类型 | 动态 | 静态 |
| 性能 | JIT 优化良好 | 更接近原生 |
| 启动 | 几乎瞬时 | 需下载 + 实例化 |
| 体积 | 不适用 | 一般几百 KB~几 MB |
| 互操作 | 直接 | 需通过 JS 实例化 |

## 🚀 实际生产用例

- Figma / Photoshop Web：图像处理核心用 C++→Wasm
- Google Earth：3D 渲染用 Wasm 加速
- eBay：条码扫描用 Wasm
- Photoshop 滤镜：大量算法搬到 Wasm

## ⚠️ 限制

- 不能直接操作 DOM（要走 JS 胶水）
- 不会自动并行（除非 SharedArrayBuffer + Web Workers）
- 浏览器对 `SharedArrayBuffer` 需要 COOP/COEP 头部

## 🔗 下一步

- [Vite 原理](/05-build/vite)
- [运行时性能](/12-perf/runtime)
