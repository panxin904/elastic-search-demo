---
title: 字节码与执行
date: 2026-08-15  # date-auto-injected
---

# 🧠 字节码与执行

> Python 字节码是 **CPython 解释器执行的中间表示**。理解字节码有助于**性能优化、问题排查、深入 Python**。

## 🎯 字节码是什么？

```
字节码（Bytecode）= Python 解释器执行的中间指令

类似 Java 字节码、.NET IL

特点：
  ✅ 平台无关（不同 CPU 都执行同一字节码）
  ✅ 比源代码快（已编译）
  ✅ 比机器码慢（解释执行）
  ✅ 保存在 .pyc 文件中（缓存）
```

## 📊 字节码示例

### 简单示例

```python
# demo.py
def add(a, b):
    return a + b

# 查看字节码
import dis
dis.dis(add)
```

输出：
```
  0 LOAD_FAST     0 (a)         # 加载 a
  2 LOAD_FAST     1 (b)         # 加载 b
  4 BINARY_ADD                  # 相加
  6 RETURN_VALUE                # 返回
```

### 复杂示例

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

import dis
dis.dis(factorial)
```

```
  0 LOAD_FAST     0 (n)
  2 LOAD_CONST    1 (1)
  4 COMPARE_OP    <= (4)
  6 POP_JUMP_IF_FALSE  12
  8 LOAD_CONST    1 (1)
 10 RETURN_VALUE
 12 LOAD_FAST     0 (n)
 14 LOAD_GLOBAL    0 (factorial)
 16 LOAD_FAST     0 (n)
 18 LOAD_CONST    1 (1)
 20 BINARY_SUBTRACT
 22 CALL_FUNCTION  1
 24 BINARY_MULTIPLY
 26 RETURN_VALUE
```

## 🔍 常见字节码指令

### 加载 / 存储

| 指令 | 含义 | 操作数 |
|------|------|--------|
| LOAD_FAST | 加载局部变量 | 变量索引 |
| STORE_FAST | 存储局部变量 | 变量索引 |
| LOAD_GLOBAL | 加载全局变量 | 名称索引 |
| LOAD_CONST | 加载常量 | 常量索引 |
| LOAD_ATTR | 加载属性 | 名称索引 |
| STORE_ATTR | 存储属性 | 名称索引 |

### 运算

| 指令 | 含义 |
|------|------|
| BINARY_ADD | 加法 |
| BINARY_SUBTRACT | 减法 |
| BINARY_MULTIPLY | 乘法 |
| BINARY_DIVIDE | 除法（浮点） |
| BINARY_MODULO | 取模 |
| BINARY_POWER | 幂 |
| BINARY_FLOOR_DIVIDE | 整除 |

### 比较

| 指令 | 含义 |
|------|------|
| COMPARE_OP | 比较运算（<, ==, > 等） |
| POP_JUMP_IF_FALSE | False 时跳转 |
| POP_JUMP_IF_TRUE | True 时跳转 |
| JUMP_FORWARD | 无条件前跳 |
| JUMP_ABSOLUTE | 无条件跳到指定位置 |

### 函数

| 指令 | 含义 |
|------|------|
| CALL_FUNCTION | 调用函数 |
| RETURN_VALUE | 返回值 |
| YIELD_VALUE | 生成器 yield |
| SETUP_ANNOTATIONS | 启用 annotations |

## 📚 code object

```python
def add(a, b):
    return a + b

# 查看 code object
print(add.__code__)
# <code object add at 0x..., file "demo.py", line 1>

print(add.__code__.co_argcount)     # 参数数量: 2
print(add.__code__.co_varnames)     # ('a', 'b')
print(add.__code__.co_consts)       # (None, 1)
print(add.__code__.co_names)        # ()
print(add.__code__.co_code)         # 字节码（bytes）
```

### 常用 co_* 属性

```
co_argcount        参数数量
co_cellvars        闭包变量
co_code            字节码
co_consts          常量
co_filename        文件名
co_firstlineno     起始行号
co_flags           标志
co_freevars        自由变量
co_kwonlyargcount  仅关键字参数数量
co_lnotab          行号表
co_name            函数名
co_names           使用的全局名
co_nlocals         局部变量数量
co_posonlyargcount 仅位置参数数量
co_stacksize       栈大小
co_varnames        局部变量名
```

## 🛠️ dis 模块实战

### 反汇编函数

```python
import dis

def complex_func(x, y):
    total = 0
    for i in range(10):
        if i % 2 == 0:
            total += i
    return total

dis.dis(complex_func)
```

### 反汇编类

```python
class MyClass:
    def method(self):
        return "hello"

import dis
dis.dis(MyClass)
```

### 反汇编模块

```python
import dis
import math

# 反汇编整个模块
dis.dis(math)
```

### 自定义字节码

```python
# 用 types.CodeType 构造字节码
import types

code = types.CodeType(
    0,           # argcount
    0,           # posonlyargcount
    0,           # kwonlyargcount
    0,           # nlocals
    1,           # stacksize
    67,          # flags
    b'd\x00S',   # bytecode (LOAD_CONST 0, RETURN_VALUE)
    (None,),     # constants
    (),          # names
    (),          # varnames
    'demo.py',   # filename
    'hello',     # name
    1,           # firstlineno
    b'',         # lnotab
    (),          # freevars
    ()           # cellvars
)

func = types.FunctionType(code, {})
print(func())  # None
```

## 🔧 字节码优化技巧

### 1. 局部变量访问更快

```python
import dis

# 全局变量慢
import math
def use_global():
    return math.sin(1) + math.cos(1)

# 局部变量快（赋值给本地）
def use_local():
    sin = math.sin
    cos = math.cos
    return sin(1) + cos(1)

# 字节码对比
print("=== Global ===")
dis.dis(use_global)
print("=== Local ===")
dis.dis(use_local)
```

### 2. 字符串拼接用 join

```python
# 慢
result = ""
for s in strings:
    result += s

# 快
result = "".join(strings)
```

### 3. 避免属性访问

```python
# 慢（每次循环都查 .append）
result = []
for x in data:
    result.append(x)

# 快（局部变量）
append = result.append
for x in data:
    append(x)
```

## 📦 __pycache__ 缓存

```
当 Python 编译模块时，字节码会缓存到 __pycache__/<module>.cpython-311.pyc

缓存目的：
  ✅ 避免重复编译（加快启动）
  ✅ 字节码跨 Python 版本不兼容

禁用 .pyc 缓存：
  python -B script.py
  或设置环境变量：PYTHONDONTWRITEBYTECODE=1
```

## 📊 字节码缓存文件结构

```
myproject/
├── main.py
├── module.py
└── __pycache__/
    ├── main.cpython-311.pyc
    └── module.cpython-311.pyc
```

`.pyc` 文件内容：
- magic number（验证 Python 版本）
- 时间戳
- 源文件大小
- 编译后的字节码

## 🛠️ 性能分析

```python
import dis
import timeit

# 对比两个函数
def for_loop():
    result = []
    for i in range(1000):
        result.append(i)
    return result

def list_comp():
    return [i for i in range(1000)]

# 查看字节码差异
dis.dis(for_loop)
dis.dis(list_comp)

# 性能测试
print(timeit.timeit(for_loop, number=1000))
print(timeit.timeit(list_comp, number=1000))
# 列表推导式通常快 30-50%
```

## 🎯 总结

**字节码与执行核心要点**：
- ✅ 字节码是 Python 解释执行的中间表示
- ✅ dis 模块可查看字节码
- ✅ code object 包含函数的所有元信息
- ✅ 局部变量访问比全局快
- ✅ 列表推导式比循环快
- ✅ .pyc 缓存加速启动
- ⚠️ GIL 是单线程执行
- ⚠️ 字节码版本不兼容（Python 3.10 vs 3.11）

**下一步：** [📦 对象模型](/02-principles/object-model) — PyObject 底层结构
