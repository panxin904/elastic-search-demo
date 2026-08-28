---
title: 控制流
---

# 🔁 控制流

> Python 控制流包括**条件分支（if/elif/else）、循环（for/while）、异常处理（try/except）**。Python 用**缩进**表示代码块，简洁优雅。

## 🔀 条件分支

### if / elif / else

```python
# 基本 if
age = 20
if age >= 18:
    print("成年人")

# if-else
if age >= 18:
    print("成年人")
else:
    print("未成年人")

# if-elif-else（多分支）
score = 85
if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# 多个条件
age = 25
has_license = True
if age >= 18 and has_license:
    print("可以开车")
```

### 真值判断

```python
# Python 中以下值为 False：
# False, None, 0, 0.0, "", [], (), {}, set()
# 其他都是 True

if []:       # False
    print("not empty")
else:
    print("empty")  # 输出

if "hello":  # True
    print("non-empty")  # 输出

# 简化写法
items = [1, 2, 3]
if items:
    print("有数据")
```

### 三元表达式

```python
# Python 风格：x if condition else y
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)

# 嵌套（不推荐，复杂）
score = 85
grade = "A" if score >= 90 else "B" if score >= 80 else "C"
```

### match-case（Python 3.10+）

```python
# 类似 switch-case
status_code = 200

match status_code:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case 500:
        print("Server Error")
    case _:  # 默认
        print("Unknown")

# 模式匹配
match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"X-axis: {x}")
    case (0, y):
        print(f"Y-axis: {y}")
    case (x, y):
        print(f"Point: ({x}, {y})")
```

## 🔁 循环

### for 循环

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 遍历字符串
for char in "Hello":
    print(char)

# range()
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 8):   # 2, 3, 4, 5, 6, 7
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)

# 遍历字典
user = {"name": "Alice", "age": 30}
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(f"{key}: {value}")

# enumerate（带索引）
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# zip（并行遍历）
names = ['Alice', 'Bob', 'Carol']
ages = [30, 25, 28]
for name, age in zip(names, ages):
    print(f"{name}: {age}")

# 列表推导式
squares = [x**2 for x in range(10)]
```

### while 循环

```python
# 基本
count = 0
while count < 5:
    print(count)
    count += 1

# 无限循环 + break
n = 0
while True:
    n += 1
    if n > 100:
        break

# while-else（条件不满足时执行 else）
n = 0
while n < 5:
    n += 1
else:
    print("循环正常结束")

# for-else
for i in range(5):
    pass
else:
    print("循环正常结束")
```

### 循环控制

```python
# break：跳出循环
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue：跳过本次
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4

# pass：占位符（语法需要）
for i in range(5):
    pass  # TODO

def func():
    pass  # 待实现
```

## 🚨 异常处理

### try-except

```python
# 基本
try:
    result = 10 / 0
except ZeroDivisionError:
    print("除数不能为 0")

# 多个异常
try:
    value = int(input("Enter a number: "))
    result = 10 / value
except ValueError:
    print("无效输入")
except ZeroDivisionError:
    print("除数不能为 0")

# 合并多个异常
try:
    value = int(input("Enter: "))
    result = 10 / value
except (ValueError, ZeroDivisionError) as e:
    print(f"错误: {e}")

# 捕获所有异常（不推荐）
try:
    risky_operation()
except Exception as e:
    print(f"出错了: {e}")

# else 和 finally
try:
    f = open("file.txt")
    data = f.read()
except FileNotFoundError:
    print("文件不存在")
else:
    print("读取成功")
    print(data)
finally:
    if 'f' in locals():
        f.close()
    print("执行完毕")

# 自定义异常
class MyError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

try:
    raise MyError("自定义错误")
except MyError as e:
    print(f"捕获到: {e.message}")
```

### 抛出异常

```python
# raise 抛出异常
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(e)

# 重新抛出
try:
    risky_op()
except Exception as e:
    log_error(e)
    raise  # 重新抛出原异常

# 抛出不同异常
try:
    result = "abc" + 123
except TypeError as e:
    raise ValueError("类型不匹配") from e
```

## 🛠️ 实战示例

### 示例 1：用户输入验证

```python
def get_age():
    while True:
        try:
            age = int(input("Enter your age: "))
            if age < 0 or age > 150:
                raise ValueError("年龄无效")
            return age
        except ValueError as e:
            print(f"错误: {e}，请重新输入")

age = get_age()
print(f"你的年龄是 {age}")
```

### 示例 2：FizzBuzz

```python
for i in range(1, 16):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

### 示例 3：购物车

```python
cart = []
while True:
    action = input("(a)dd (r)emove (q)uit: ").lower()
    
    if action == 'a':
        item = input("Item name: ")
        cart.append(item)
        print(f"Added: {item}")
    elif action == 'r':
        if cart:
            item = cart.pop()
            print(f"Removed: {item}")
        else:
            print("Cart is empty")
    elif action == 'q':
        break
    else:
        print("Invalid action")
    
    print(f"Cart ({len(cart)}): {cart}")
```

### 示例 4：用户登录重试

```python
MAX_ATTEMPTS = 3
CORRECT_PASSWORD = "secret"

for attempt in range(1, MAX_ATTEMPTS + 1):
    password = input(f"Attempt {attempt}/{MAX_ATTEMPTS} - Password: ")
    if password == CORRECT_PASSWORD:
        print("✓ 登录成功")
        break
    print(f"✗ 密码错误（剩 {MAX_ATTEMPTS - attempt} 次机会）")
else:
    print("🚫 账户已锁定")
```

## 🎯 实战

<ClientOnly>
  <PythonPlayground />
</ClientOnly>

试试在 Playground 里运行控制流代码：

```python
# FizzBuzz
for i in range(1, 16):
    if i % 15 == 0:
        print("FizzBuzz", end=" ")
    elif i % 3 == 0:
        print("Fizz", end=" ")
    elif i % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(i, end=" ")
print()

# 异常处理
try:
    n = int("abc")
except ValueError as e:
    print(f"转换失败: {e}")
```

## 🎯 总结

**Python 控制流核心要点**：
- ✅ 缩进表示代码块（4 空格）
- ✅ if / elif / else 条件分支
- ✅ for 遍历、while 循环
- ✅ break / continue / pass
- ✅ try / except / finally 异常处理
- ✅ match-case 模式匹配（3.10+）
- ⚠️ 不要混用 tab 和空格
- ⚠️ 不要捕获所有异常（用具体异常类型）

**下一步：** [🔬 底层原理 - 解释器](/02-principles/interpreter) — 深入理解 Python

<!-- svg-injected:do-not-edit -->

## 图示：Python asyncio 事件循环与协程状态

![Python asyncio 事件循环与协程状态](/python-asyncio-loop.svg)
