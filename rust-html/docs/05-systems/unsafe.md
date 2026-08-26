---
title: unsafe Rust
---

# unsafe Rust

unsafe 块绕过 Rust 编译器的部分检查（4 种操作），允许直接操作内存和硬件。

## 一句话总结

> **unsafe = 关闭 4 种编译期检查**。**核心：解引用裸指针 / 调用 unsafe fn / 访问可变静态 / 实现 unsafe Trait**。**用途：性能优化 + 硬件抽象 + FFI**。

---

## 4 种 unsafe 超能力

```rust
unsafe fn dangerous() {}

// 1. 解引用裸指针
let mut num = 5;
let r1 = &num as *const i32;
let r2 = &mut num as *mut i32;

unsafe {
    println!("r1 is: {}", *r1);
    *r2 = 10;
}

// 2. 调用 unsafe 函数
unsafe {
    dangerous();
}

// 3. 访问或修改可变静态变量
static mut COUNTER: u32 = 0;
unsafe {
    COUNTER += 1;
}

// 4. 实现 unsafe Trait
unsafe trait Send {}
unsafe impl Send for MyType {}
```

## unsafe 块的范围

```rust
fn mixed() {
    let mut num = 5;
    let r = &mut num as *mut i32;

    // unsafe 块限制在最小范围
    unsafe {
        *r = 10;
    }

    println!("{}", num);
}
```

## 何时用 unsafe

```rust
// 1. 调用 C 库（FFI）
extern "C" {
    fn abs(input: i32) -> i32;
}

unsafe {
    println!("{}", abs(-5));
}

// 2. 性能关键路径（绕过边界检查）
let v = vec![1, 2, 3];
unsafe {
    let elem = v.get_unchecked(1);
    println!("{}", elem);
}

// 3. 嵌入式 / OS 开发
unsafe {
    let peripherals = cortex_m::Peripherals::take().unwrap();
    peripherals.GPIOA.bsrr.write(|w| w.bits(1));
}

// 4. 自定义数据结构
pub struct Vec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

impl<T> Vec<T> {
    pub fn push(&mut self, val: T) {
        unsafe {
            if self.len == self.cap {
                self.grow();
            }
            std::ptr::write(self.ptr.add(self.len), val);
            self.len += 1;
        }
    }
}

// 5. 内联汇编
use std::arch::asm;
unsafe {
    asm!("nop");
}
```

## 5 大安全抽象模式

```rust
// 模式 1：unsafe 封装在 safe API 内
pub struct SafeVec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

unsafe impl<T: Send> Send for SafeVec<T> {}
unsafe impl<T: Sync> Sync for SafeVec<T> {}

// 模式 2：模块化 unsafe
mod internal {
    pub unsafe fn unchecked_operation() { }
}

pub fn safe_wrapper() {
    unsafe {
        internal::unchecked_operation();
    }
}

// 模式 3：unsafe trait
pub unsafe trait Zeroable {}
unsafe impl Zeroable for i32 {}

// 模式 4：RAII 自动清理
pub struct Guard {
    ptr: *mut T,
}

impl Drop for Guard {
    fn drop(&mut self) {
        unsafe {
            std::ptr::drop_in_place(self.ptr);
        }
    }
}
```

## Miri：检测 unsafe UB

```bash
rustup +nightly component add miri
cargo +nightly miri test
```

## 5 大 unsafe 反模式

```
反模式 1：绕过借用检查 → 越界
反模式 2：双重释放
反模式 3：use-after-free
反模式 4：数据竞争
反模式 5：未初始化内存
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **02-types-traits/advanced-types**：PhantomData / MaybeUninit

## 一句话总结

> **unsafe = 性能 + 控制 + 互操作**。**用 unsafe 封装安全抽象，避免散布 unsafe 代码**。


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
