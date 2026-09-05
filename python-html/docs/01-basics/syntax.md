---
title: 基础语法
date: 2026-08-15  # date-auto-injected
---

# 🔤 基础语法
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Python 装饰器栈调用</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">闭包 + 包装 · 顺序自下而上、调用自上而下</text>

  <!-- 调用栈（左） -->
  <text x="120" y="100" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">调用栈（运行时）</text>
  <rect class="at-hover-card" x="50" y="115" width="140" height="50" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="120" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">@retry(max=3)</text>
  <text x="120" y="155" text-anchor="middle" font-size="9" fill="#475569">最先包裹，最外层</text>

  <rect class="at-hover-card" x="50" y="180" width="140" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="120" y="203" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">@timing</text>
  <text x="120" y="220" text-anchor="middle" font-size="9" fill="#475569">测耗时</text>

  <rect class="at-hover-card" x="50" y="245" width="140" height="50" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="120" y="268" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">@cache</text>
  <text x="120" y="285" text-anchor="middle" font-size="9" fill="#475569">命中走缓存</text>

  <rect class="at-hover-card" x="50" y="310" width="140" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="120" y="333" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">def foo():</text>
  <text x="120" y="350" text-anchor="middle" font-size="9" fill="#475569">原始函数</text>

  <!-- 箭头 -->
  <line x1="120" y1="165" x2="120" y2="178" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="120" y1="230" x2="120" y2="243" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="120" y1="295" x2="120" y2="308" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 等价展开 -->
  <text x="430" y="100" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">等价于</text>

  <rect x="280" y="115" width="320" height="245" rx="6" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="295" y="140" font-size="11" font-family="monospace" fill="#1e293b">foo = retry(max=3)(</text>
  <text x="315" y="160" font-size="11" font-family="monospace" fill="#1e293b">timing(</text>
  <text x="335" y="180" font-size="11" font-family="monospace" fill="#1e293b">cache(foo)</text>
  <text x="315" y="200" font-size="11" font-family="monospace" fill="#1e293b">)</text>
  <text x="295" y="220" font-size="11" font-family="monospace" fill="#1e293b">)</text>
  <text x="295" y="248" font-size="10" fill="#475569" font-style="italic">↓</text>
  <text x="295" y="270" font-size="10" fill="#475569" font-style="italic">装饰顺序 = 自下而上：</text>
  <text x="295" y="288" font-size="10" fill="#475569" font-style="italic">cache 最先包 foo，</text>
  <text x="295" y="306" font-size="10" fill="#475569" font-style="italic">retry 最后包整个栈</text>
  <text x="295" y="332" font-size="10" fill="#475569" font-style="italic">调用顺序 = 自上而下：</text>
  <text x="295" y="350" font-size="10" fill="#475569" font-style="italic">retry → timing → cache → foo</text>

  <!-- 关键点 -->
  <rect x="30" y="385" width="540" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="408" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">关键点</text>
  <text x="50" y="428" font-size="10" fill="#334155">· functools.wraps(func) 保留原函数 __name__/__doc__</text>
  <text x="50" y="446" font-size="10" fill="#334155">· 带参装饰器 = 装饰器工厂：外层接受参数返回装饰器</text>
  <text x="320" y="428" font-size="10" fill="#334155">· 类装饰器：__call__ 实现可调用；或继承实现</text>
  <text x="320" y="446" font-size="10" fill="#334155">· stack 顺序决定执行顺序，retry 包最外层才有 retry 缓存</text>
</svg>


> Python 的语法以**简洁优雅**著称。本章覆盖**变量、运算符、字符串、输入输出**等基础语法。

## 🎯 变量

### 变量赋值

```python
# 基本赋值
name = "Python"
age = 30
pi = 3.14159
is_active = True

# 多变量赋值
a, b, c = 1, 2, 3
x, y = y, x  # 交换

# 链式赋值
a = b = c = 0

# 增量赋值
count = 0
count += 1   # 等同于 count = count + 1
count -= 1
count *= 2
count /= 4
count **= 2  # count = count ** 2
```

### 变量命名

```python
# 命名规则：
# 1. 字母、数字、下划线
# 2. 数字不能开头
# 3. 区分大小写
# 4. 不能使用关键字

# 命名风格（PEP 8）：
my_var = 1         # 蛇形命名（推荐）
myVar = 1          # 驼峰命名（不推荐）
MY_CONST = 100     # 常量
_private = "私有"   # 私有（约定）

# 关键字
import keyword
print(keyword.kwlist)
# ['False', 'None', 'True', 'and', 'as', ...]
```

## 📊 数据类型

### 基本类型

```python
# 整数 int
age = 30
big_num = 10**100  # 大整数（无溢出）

# 浮点数 float
price = 19.99
pi = 3.14159

# 复数
c = 1 + 2j

# 字符串 str
name = "Python"
multiline = """多行
字符串"""

# 布尔 bool
is_ok = True
is_failed = False

# 空值 None
result = None

# 类型检查
type(42)         # <class 'int'>
isinstance(42, int)  # True
```

### 类型转换

```python
# 字符串 ↔ 数字
int("42")       # 42
float("3.14")    # 3.14
str(42)         # "42"

# 进制转换
int("ff", 16)   # 255
bin(255)        # '0b11111111'
hex(255)        # '0xff'
oct(8)          # '0o10'

# 布尔
bool(0)         # False
bool(1)         # True
bool("")        # False
bool("a")       # True
```

## 🔢 运算符

### 算术运算符

```python
print(10 + 3)   # 13 加
print(10 - 3)   # 7  减
print(10 * 3)   # 30 乘
print(10 / 3)   # 3.333... 除（浮点）
print(10 // 3)  # 3 整除
print(10 % 3)   # 1  取模
print(10 ** 3)  # 1000 幂
print(-5)       # -5 负
print(+5)       # 5  正
```

### 比较运算符

```python
print(5 == 5)   # True
print(5 != 3)   # True
print(5 > 3)    # True
print(5 < 3)    # False
print(5 >= 5)   # True
print(5 <= 4)   # False

# 链式比较
print(1 < 2 < 3)    # True
print(1 < 2 > 0)    # True
```

### 逻辑运算符

```python
print(True and True)    # True
print(True and False)   # False
print(True or False)    # True
print(False or False)   # False
print(not True)         # False
```

### 位运算符

```python
print(0b1010 & 0b1100)   # 8   按位与
print(0b1010 | 0b1100)   # 14  按位或
print(0b1010 ^ 0b1100)   # 6   按位异或
print(~0b1010)           # -11 按位取反
print(0b1010 << 2)       # 40  左移
print(0b1010 >> 2)       # 2   右移
```

### 成员运算符

```python
fruits = ["apple", "banana", "cherry"]
print("apple" in fruits)        # True
print("grape" not in fruits)    # True

text = "Hello, World!"
print("World" in text)         # True
```

### 身份运算符

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]
print(a is b)      # True（同一对象）
print(a is c)      # False（不同对象）
print(a is not c)  # True
```

## 📝 字符串

### 字符串创建

```python
s1 = '单引号'
s2 = "双引号"
s3 = """三引号
多行
字符串"""
s4 = r"原始字符串\n不转义"
s5 = b"字节字符串"
```

### 字符串操作

```python
s = "Hello, World!"

# 索引和切片
print(s[0])         # 'H'
print(s[-1])        # '!' （最后一个）
print(s[0:5])       # 'Hello'
print(s[7:])        # 'World!'
print(s[::-1])      # '!dlroW ,olleH'（反转）

# 长度
print(len(s))       # 13

# 拼接
s1 = "Hello"
s2 = "World"
print(s1 + " " + s2)        # 'Hello World'
print(" ".join([s1, s2]))    # 'Hello World'

# 重复
print("ab" * 3)    # 'ababab'

# 查找
print(s.find("World"))     # 7
print(s.index("World"))    # 7
print(s.count("o"))        # 2

# 替换
print(s.replace("World", "Python"))  # 'Hello, Python!'

# 分割
print("a,b,c".split(","))   # ['a', 'b', 'c']

# 大小写
print("hello".upper())     # 'HELLO'
print("HELLO".lower())     # 'hello'
print("hello".title())     # 'Hello'
print("hello".capitalize()) # 'Hello'

# 去空白
print("  hello  ".strip())  # 'hello'
print("  hello  ".lstrip()) # 'hello  '
print("  hello  ".rstrip()) # '  hello'

# 格式化
name = "Alice"
age = 30
print(f"Name: {name}, Age: {age}")  # f-string（推荐）
print("Name: {}, Age: {}".format(name, age))
print("Name: %s, Age: %d" % (name, age))
```

### f-string 高级用法

```python
name = "Alice"
age = 30
pi = 3.14159

# 基本
print(f"Name: {name}, Age: {age}")

# 表达式
print(f"2 + 2 = {2 + 2}")

# 格式说明符
print(f"Pi: {pi:.2f}")        # Pi: 3.14
print(f"Age: {age:03d}")      # Age: 030
print(f"Name: {name:>10}")    # 右对齐，宽度 10

# 调试
print(f"{name=}, {age=}")     # name='Alice', age=30
```

## 🖨️ 输入输出

### print 输出

```python
# 基本输出
print("Hello, World!")

# 多个值
print("Name:", "Alice", "Age:", 30)  # Name: Alice Age: 30

# 自定义分隔符和结束符
print("a", "b", "c", sep="-")  # a-b-c
print("Hello", end="!")
print("World")  # 输出: Hello!World
```

### input 输入

```python
# 基本输入
name = input("Enter your name: ")
print(f"Hello, {name}")

# 输入数字（需要转换）
age = int(input("Enter your age: "))
print(f"You are {age} years old")

# 多值输入
a, b = input("Enter two numbers: ").split()
print(f"You entered: {a}, {b}")
```

## 🐍 Python 风格

```python
# 推荐：使用 is / is not 比较 None、True、False
if x is None:
    print("x is None")

if items is not None:
    print(items)

# 推荐：使用 enumerate 遍历索引
for i, item in enumerate(['a', 'b', 'c']):
    print(i, item)

# 推荐：使用 zip 并行遍历
names = ['Alice', 'Bob']
ages = [30, 25]
for name, age in zip(names, ages):
    print(f"{name} is {age}")

# 推荐：列表推导式
squares = [x**2 for x in range(10)]

# 推荐：使用 with 管理资源
with open('file.txt') as f:
    content = f.read()
```

## 🛠️ 实战

<ClientOnly>
  <PythonPlayground />
</ClientOnly>

试试在 Playground 里运行 Python 代码：

```python
name = "World"
print(f"Hello, {name}!")

for i in range(3):
    print(f"Count: {i}")

fruits = ["apple", "banana", "cherry"]
print(fruits[1])        # banana
print(len(fruits))      # 3
print(fruits[::-1])     # 反转
```

## 🎯 总结

**Python 基础语法核心要点**：
- ✅ 动态类型，无需声明
- ✅ 简洁优雅（接近自然语言）
- ✅ 字符串切片 `s[start:stop:step]`
- ✅ f-string 格式化（推荐）
- ✅ `in` / `not in` 检查成员
- ✅ `is` / `is not` 比较身份
- ⚠️ 不要用 `==` 比较 None
- ⚠️ 缩进敏感（4 空格）

**下一步：** [📦 数据结构](/01-basics/data-structures) — list/dict/set/tuple
