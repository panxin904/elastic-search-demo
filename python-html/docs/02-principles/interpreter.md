---
title: Python 解释器
---

# 🏗️ Python 解释器

> Python 解释器是**执行 Python 代码**的程序。理解解释器的工作原理对**性能调优、问题排查、深入 Python** 至关重要。

## 🎯 Python 解释器是什么？

```
Python 解释器 = 读取 Python 代码 + 编译成字节码 + 执行的程序

最常见：CPython（官方 C 实现）
其他实现：PyPy、Jython、IronPython、MicroPython
```

### CPython 工作流程

```
源代码（.py 文件）
   ↓ 词法分析（Tokenize）
Token 流
   ↓ 语法分析（Parse）
抽象语法树（AST）
   ↓ 编译（Compile）
字节码（.pyc 文件）
   ↓ 解释执行（Interpret）
机器指令
```

## 🏗️ CPython 架构

```
┌─────────────────────────────────────────────┐
│              CPython 解释器                    │
│                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ 词法分析 │ → │ 语法分析 │ → │ 编译器   │ │
│  │  (Tokenizer)  │  (Parser)  │  (Compiler) │ │
│  └──────────┘   └──────────┘   └──────────┘ │
│        ↓              ↓             ↓         │
│      Token         AST        Bytecode       │
│  ┌─────────────────────────────────────────┐ │
│  │         内存管理（Memory）                  │ │
│  │  - 引用计数                              │ │
│  │  - 垃圾回收（GC）                         │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │         运行时（Runtime）                  │ │
│  │  - 字节码解释器（CEval）                 │ │
│  │  - GIL 全局锁                           │ │
│  │  - 对象系统（PyObject）                 │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │         解释器循环                         │ │
│  │  - 读取字节码指令                         │ │
│  │  - 执行                                  │ │
│  │  - 维护执行状态                          │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## 📦 Python 实现对比

### CPython（默认）

```
✅ 优点：
  - 官方实现，最稳定
  - 第三方库最全（C 扩展最简单）
  - 工具链最完善

❌ 缺点：
  - GIL（多线程受限）
  - 速度慢（纯解释）

适用：
  - 大多数生产环境
  - 需要 C 扩展
  - 标准库和第三方库兼容
```

### PyPy

```
✅ 优点：
  - JIT 编译（热路径编译）
  - 长时间运行性能提升 5-20x
  - 内存占用少
  - 兼容 CPython API

❌ 缺点：
  - 启动慢（JIT 预热）
  - 某些 C 扩展不兼容
  - 实时性要求高的场景不适合

适用：
  - 长时间运行的 CPU 密集型任务
  - 数值计算、Web 后端
```

### 其他实现

```
- Jython：跑在 JVM 上（已不活跃）
- IronPython：跑在 .NET 上
- MicroPython：嵌入式设备
- Brython：浏览器（JavaScript）
- Cython：编译为 C（性能优化）
```

## 🔍 字节码

```python
# 编译成字节码
import dis

def add(a, b):
    return a + b

dis.dis(add)
# 输出字节码指令：
#   0 LOAD_FAST 0 (a)
#   2 LOAD_FAST 1 (b)
#   4 BINARY_ADD
#   6 RETURN_VALUE
```

### 常用字节码指令

| 指令 | 含义 |
|------|------|
| LOAD_FAST | 加载局部变量 |
| STORE_FAST | 存储局部变量 |
| LOAD_GLOBAL | 加载全局变量 |
| BINARY_ADD | 二元加法 |
| BINARY_SUBTRACT | 二元减法 |
| COMPARE_OP | 比较运算 |
| JUMP_IF_TRUE | 条件跳转 |
| CALL_FUNCTION | 调用函数 |
| RETURN_VALUE | 返回值 |

## 📁 .pyc 文件

```
Python 编译字节码后保存为 .pyc（缓存）

缓存位置：
  - Python 3.2+：__pycache__/<module>.cpython-311.pyc
  - 加快启动速度（无需重新编译）

删除 .pyc 不影响运行（会重新生成）
```

### 检查 .pyc

```bash
# 查看缓存目录
ls __pycache__/

# 强制重新生成
find . -name __pycache__ -exec rm -r {} +

# 禁用 .pyc 缓存
python -B script.py
```

## 🚀 启动流程

```
1. 启动 Python 解释器
   ↓
2. 加载 site.py（初始化标准库）
   ↓
3. 解析命令行参数
   ↓
4. 执行 -c 命令 或 运行 script.py
   ↓
5. 编译：源代码 → 字节码
   ↓
6. 创建模块对象（__main__）
   ↓
7. 执行字节码
   ↓
8. 触发 __main__ 模块的执行
   ↓
9. 运行结束（或保持 REPL 交互）
```

## 🛠️ 工具：dis 模块

```python
import dis

# 反汇编函数
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

dis.dis(factorial)

# 输出（部分）：
#   0 LOAD_FAST 0 (n)
#   2 LOAD_CONST 1 (1)
#   4 COMPARE_OP <= (4)
#   6 POP_JUMP_IF_FALSE 12
#   8 LOAD_CONST 1 (1)
#  10 RETURN_VALUE
# ...
```

```python
# 查看 code object
import dis
print(factorial.__code__.co_consts)  # 常量
print(factorial.__code__.co_varnames)  # 变量名
print(factorial.__code__.co_code)  # 字节码
```

## 📊 性能对比

```
测试：递归斐波那契 fib(30)

CPython 3.11：    ~0.5s
PyPy 7.3：         ~0.05s （快 10x）
Jython 2.7：      ~10s   （慢 20x）
```

## 🎯 总结

**Python 解释器核心要点**：
- ✅ CPython 是默认实现（官方 C 实现）
- ✅ 执行流程：源代码 → 字节码 → 解释执行
- ✅ 字节码缓存为 .pyc（__pycache__）
- ✅ PyPy 用 JIT 提升性能（5-20x）
- ✅ dis 模块可查看字节码
- ⚠️ GIL 是 CPython 多线程的限制
- ⚠️ 启动慢 / 长运行任务考虑 PyPy

**下一步：** [🧠 字节码与执行](/02-principles/bytecode) — 深入字节码
