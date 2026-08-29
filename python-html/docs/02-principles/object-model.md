---
title: 对象模型
date: 2026-08-15  # date-auto-injected
---

# 📦 对象模型

> Python 中**一切皆对象**。理解 PyObject 底层结构是掌握 Python 内存管理和性能优化的基础。

## 🎯 Python 对象基础

```
Python 中一切都是对象（object）：
  - 整数、浮点、字符串
  - 列表、字典、集合
  - 函数、类、模块
  - 甚至类型本身（type）

所有对象都在堆上分配（引用类型）
```

## 🏗️ PyObject 结构

```c
// CPython 源码：Include/object.h

typedef struct _object {
    _PyObject_HEAD_EXTRA        // 调试相关（GC 链表）
    Py_ssize_t ob_refcnt;        // 引用计数
    PyTypeObject *ob_type;       // 指向类型对象
} PyObject;

// 实际定义
typedef struct {
    PyObject ob_base;            // ob_refcnt + ob_type
    Py_ssize_t ob_size;          // 变长对象的长度（如字符串、列表）
} PyVarObject;
```

### 关键字段

```
ob_refcnt：引用计数（垃圾回收核心）
ob_type：指向类型对象（决定对象行为）
ob_size：变长对象的大小（str/bytes/list/tuple）
```

## 📊 常见对象结构

### 整数（int）

```c
typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size;        // 数字位数
    digit ob_digit[1];          // 数字数组（任意精度）
} PyLongObject;
```

```python
import sys
x = 1000
print(sys.getsizeof(x))  # 28 字节（小整数）
print(sys.getsizeof(10**100))  # 数字越大，占用越大
```

### 字符串（str）

```c
typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size;
    Py_hash_t ob_shash;        // 缓存 hash
    int ob_sstate;              // 状态（interned？）
    char ob_sval[1];            // 字符数组
} PyUnicodeObject;
```

```python
import sys
print(sys.getsizeof("hello"))  # 54 字节
print(sys.getsizeof(""))  # 49 字节（空字符串）
```

### 列表（list）

```c
typedef struct {
    PyVarObject ob_base;
    PyObject **ob_item;          // 元素数组
    Py_ssize_t allocated;        // 分配的容量
} PyListObject;
```

```python
import sys
print(sys.getsizeof([]))        # 56 字节（空列表）
print(sys.getsizeof([1, 2]))   # 88 字节
# 注意：列表是动态数组，append 可能触发扩容
```

### 字典（dict）

```python
# Python 3.6+ 使用紧凑字典
# 内存效率提升 20-25%
# 迭代顺序 = 插入顺序
```

## 🔍 类型对象（PyTypeObject）

```c
typedef struct _typeobject {
    PyObject_VAR_HEAD              // ob_refcnt + ob_type + ob_size
    const char *tp_name;            // 类型名
    Py_ssize_t tp_basicsize;        // 对象大小
    Py_ssize_t tp_itemsize;         // 变长对象元素大小
    
    // 函数指针
    destructor tp_dealloc;          // 析构
    printfunc tp_print;             // print
    getattrfunc tp_getattr;         // getattr
    setattrfunc tp_setattr;         // setattr
    hashfunc tp_hash;               // hash
    
    // 数字方法
    binaryfunc tp_add;
    binaryfunc tp_subtract;
    // ...
    
    // 序列方法
    lenfunc tp_length;
    // ...
} PyTypeObject;
```

### 自定义类创建类型对象

```python
class Dog:
    species = "Canis familiaris"  # 类属性
    
    def __init__(self, name):
        self.name = name  # 实例属性
    
    def bark(self):
        return f"{self.name}: woof!"

# Dog 是 type 的实例
print(type(Dog))  # <class 'type'>

# 访问类型对象的属性
print(Dog.species)  # 'Canis familiaris'
print(Dog.bark)     # <function Dog.bark>
```

## 🧬 Python 之"一切皆对象"

```python
# int 是对象
print(type(42))        # <class 'int'>

# int 类型本身也是对象（type 的实例）
print(type(int))        # <class 'type'>

# type 是自己的实例
print(type(type))       # <class 'type'>

# 函数是对象
def func():
    pass
print(type(func))       # <class 'function'>

# 模块是对象
import sys
print(type(sys))         # <class 'module'>

# None 是对象
print(type(None))       # <class 'NoneType'>
```

## 📦 对象的可变性

### 可变对象

```python
# list、dict、set 是可变的
lst = [1, 2, 3]
lst[0] = 99        # ✅ 允许
print(lst)          # [99, 2, 3]

d = {"a": 1}
d["a"] = 99         # ✅ 允许
print(d)             # {'a': 99}

s = {1, 2, 3}
s.add(99)           # ✅ 允许
print(s)             # {1, 2, 3, 99}
```

### 不可变对象

```python
# int、float、str、tuple、frozenset 是不可变的
x = 42
# x[0] = 99  # TypeError

s = "hello"
# s[0] = 'H'  # TypeError

t = (1, 2, 3)
# t[0] = 99  # TypeError
```

### 可变 vs 不可变的影响

```python
# 可变对象：引用传递（修改会影响原对象）
def modify(lst):
    lst.append(99)

a = [1, 2, 3]
modify(a)
print(a)  # [1, 2, 3, 99]（被修改了！）

# 不可变对象：值传递
def modify(x):
    x = 99  # 创建新对象

a = 42
modify(a)
print(a)  # 42（没变）
```

## 🆔 对象的身份与相等

```python
# is 比较身份（同一对象）
# == 比较值（相等）

a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True（值相等）
print(a is b)  # False（不同对象）

c = a
print(a is c)  # True（同一对象）

# 小整数池（小整数共享）
a = 100
b = 100
print(a is b)  # True（小整数缓存）

a = 1000
b = 1000
print(a is b)  # False（大整数不缓存）

# 字符串 intern
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True（字符串 intern）

s1 = "hello world" * 1000
s2 = "hello world" * 1000
print(s1 is s2)  # False（长字符串不 intern）
```

## 🔧 对象操作底层

```python
# 属性访问底层
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.x 实际是调用 __getattribute__('x')
# 流程：type(p).__dict__['x'] → descriptor
```

### 魔术方法（Magic Methods）

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)
    
    def __getitem__(self, key):
        if key == 0: return self.x
        if key == 1: return self.y
        raise IndexError

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2
print(v3)        # (4, 6)
print(repr(v3))  # Vector(4, 6)
print(len(v1))   # 2（约等于 √5）
print(v1[0])     # 1
```

## 📊 内存占用

```python
import sys

# 不同对象的大小
print(sys.getsizeof(0))           # 24 字节
print(sys.getsizeof(1))           # 28 字节
print(sys.getsizeof(2**30))       # 32 字节
print(sys.getsizeof(2**64))       # 40 字节
print(sys.getsizeof(""))          # 49 字节
print(sys.getsizeof([]))          # 56 字节
print(sys.getsizeof([1]))         # 88 字节
print(sys.getsizeof({}))          # 64 字节
print(sys.getsizeof(True))        # 28 字节
print(sys.getsizeof(None))        # 16 字节
print(sys.getsizeof(object()))    # 16 字节

# 自定义对象大小
class Empty:
    pass

e = Empty()
print(sys.getsizeof(e))  # 56 字节（基础对象大小）
```

## 🎯 总结

**Python 对象模型核心要点**：
- ✅ 一切皆对象（int、str、func、class 都是对象）
- ✅ PyObject 包含 ob_refcnt 和 ob_type
- ✅ 不可变对象：int、float、str、tuple
- ✅ 可变对象：list、dict、set
- ✅ `is` 比较身份，`==` 比较值
- ✅ 小整数池、字符串 intern
- ✅ 魔术方法定义对象行为
- ⚠️ 可变对象作为函数参数需小心
- ⚠️ 大量对象占用内存

**下一步：** [🗑️ 内存管理](/02-principles/memory) — 引用计数与垃圾回收


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
