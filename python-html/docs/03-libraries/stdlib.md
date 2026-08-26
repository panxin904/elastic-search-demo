---
title: 标准库概览
---

# 🎯 标准库概览

> Python **自带丰富标准库**，无需安装任何第三方包就能完成**日常大部分任务**。本章精选 10 个最常用模块。

## 🎯 10 个必学标准库

```
1. os           - 操作系统接口
2. sys          - Python 运行时环境
3. pathlib     - 路径操作（推荐）
4. json         - JSON 序列化
5. re           - 正则表达式
6. collections - 容器数据类型
7. itertools   - 迭代器工具
8. functools   - 函数工具
9. datetime    - 日期时间
10. logging     - 日志记录
```

## 📁 1. os - 操作系统接口

```python
import os

# 当前工作目录
print(os.getcwd())           # /home/user/project

# 路径拼接
path = os.path.join('/home', 'user', 'file.txt')
print(path)                  # /home/user/file.txt

# 判断路径
print(os.path.exists(path))  # True/False
print(os.path.isfile(path))
print(os.path.isdir(path))

# 路径分解
dirname, filename = os.path.split(path)
name, ext = os.path.splitext(filename)

# 列出目录
files = os.listdir('/home/user')
for f in files:
    print(f)

# 创建/删除目录
os.makedirs('/path/to/dir', exist_ok=True)
os.rmdir('/path/to/dir')

# 环境变量
print(os.environ['HOME'])
print(os.environ.get('PATH', '/default'))

# 执行命令
os.system('ls -la')
import subprocess
result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
print(result.stdout)
```

## ⚙️ 2. sys - 运行时环境

```python
import sys

# Python 版本
print(sys.version)        # 3.11.0 ...
print(sys.version_info)  # sys.version_info(major=3, minor=11, ...)

# 命令行参数
print(sys.argv)         # ['script.py', 'arg1', 'arg2']

# 平台信息
print(sys.platform)      # 'linux' / 'darwin' / 'win32'

# 退出
sys.exit(0)              # 正常退出
sys.exit(1)              # 异常退出

# 模块搜索路径
print(sys.path)

# 标准输入
name = input("Enter: ")  # 等同 sys.stdin.readline()

# 内存管理
print(sys.getrefcount(obj))
print(sys.getsizeof(obj))  # 对象大小（字节）
```

## 📂 3. pathlib - 路径操作（推荐）

```python
from pathlib import Path

# 创建路径对象
p = Path('/home/user/file.txt')
print(p.name)        # 'file.txt'
print(p.stem)        # 'file'
print(p.suffix)      # '.txt'
print(p.parent)     # PosixPath('/home/user')

# 路径拼接
new_p = p.parent / 'subdir' / 'new.txt'

# 检查路径
print(p.exists())
print(p.is_file())
print(p.is_dir())

# 路径操作
p.mkdir(parents=True, exist_ok=True)
p.unlink()  # 删除文件
p.rmdir()   # 删除空目录

# 读写文件
p.write_text("Hello")
content = p.read_text()

# 遍历目录
for f in Path('/home').iterdir():
    print(f)

for f in Path('/home').glob('*.py'):  # glob 模式
    print(f)

for f in Path('/home').rglob('*.py'):  # 递归
    print(f)
```

## 📋 4. json - JSON 序列化

```python
import json

# Python 对象 ↔ JSON
data = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "Go"]
}

# 序列化
s = json.dumps(data)
print(s)  # {"name": "Alice", "age": 30, "skills": ["Python", "Go"]}

# 美化输出
s = json.dumps(data, indent=2, ensure_ascii=False)

# 处理中文
s = json.dumps(data, ensure_ascii=False)

# 反序列化
obj = json.loads(s)
print(obj["name"])

# 文件操作
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 处理自定义对象
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# JSON 编码器
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.__dict__
        return super().default(obj)

print(json.dumps(User("Alice", 30), cls=MyEncoder))
```

## 🔍 5. re - 正则表达式

```python
import re

# 匹配
m = re.match(r'hello', 'hello world')
print(m.group())  # 'hello'

# 搜索
m = re.search(r'world', 'hello world')
print(m.group())  # 'world'

# 查找所有
matches = re.findall(r'\d+', 'a1b22c333')
print(matches)  # ['1', '22', '333']

# 替换
result = re.sub(r'\d+', '*', 'a1b22c333')
print(result)  # 'a*b*c*'

# 分割
parts = re.split(r'\s+', 'a  b   c')
print(parts)  # ['a', 'b', 'c']

# 编译（提高复用性能）
pattern = re.compile(r'\d+')
print(pattern.findall('a1b22'))  # ['1', '22']

# 命名分组
m = re.match(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-07')
print(m.group('year'))   # '2024'
print(m.group('month'))  # '07'
```

## 📦 6. collections - 容器数据类型

```python
from collections import (
    Counter, defaultdict, OrderedDict,
    deque, namedtuple, ChainMap
)

# Counter：计数器
c = Counter(['apple', 'banana', 'apple'])
print(c)                # Counter({'apple': 2, 'banana': 1})
print(c.most_common())  # [('apple', 2), ('banana', 1)]

# defaultdict：默认值字典
d = defaultdict(int)
d['x'] += 1
print(d['x'])  # 1（不存在时自动设为 0）

# deque：双端队列
dq = deque([1, 2, 3])
dq.append(4)        # 右侧添加
dq.appendleft(0)    # 左侧添加
dq.pop()            # 右侧弹出
dq.popleft()        # 左侧弹出
dq.rotate(1)        # 旋转

# namedtuple：命名元组
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
print(p.x, p.y)  # 1 2
print(p[0], p[1])  # 也支持索引
```

## 🔄 7. itertools - 迭代器工具

```python
import itertools

# count：无限计数
for i in itertools.count(start=10, step=2):
    if i > 20: break
    print(i)  # 10 12 14 16 18 20

# cycle：循环迭代
counter = itertools.cycle(['A', 'B', 'C'])
print([next(counter) for _ in range(7)])  # ['A', 'B', 'C', 'A', 'B', 'C', 'A']

# chain：连接多个迭代器
a = [1, 2, 3]
b = ['x', 'y']
print(list(itertools.chain(a, b)))  # [1, 2, 3, 'x', 'y']

# islice：切片迭代器
print(list(itertools.islice(range(100), 5)))  # [0, 1, 2, 3, 4]

# permutations：排列
print(list(itertools.permutations('AB', 2)))  # [('A', 'B'), ('B', 'A')]

# combinations：组合
print(list(itertools.combinations('ABC', 2)))  # [('A', 'B'), ('A', 'C'), ('B', 'C')]

# groupby：分组
data = [('A', 1), ('A', 2), ('B', 3), ('B', 4)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
```

## 🎁 8. functools - 函数工具

```python
from functools import (
    partial, reduce, lru_cache,
    wraps, total_ordering
)

# partial：偏函数
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)
print(square(5))  # 25
print(cube(5))    # 125

# reduce：归约
print(reduce(lambda a, b: a + b, [1, 2, 3, 4]))  # 10

# lru_cache：LRU 缓存
@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

print(fib(100))  # 极快（缓存）

# wraps：装饰器保留元信息
def my_decorator(func):
    @wraps(func)  # 保留原函数名、文档
    def wrapper(*args, **kwargs):
        """Wrapper docstring"""
        return func(*args, **kwargs)
    return wrapper
```

## 📅 9. datetime - 日期时间

```python
from datetime import datetime, date, time, timedelta

# 当前时间
now = datetime.now()
print(now)  # 2024-07-15 10:30:45.123456

today = date.today()
print(today)  # 2024-07-15

# 创建
dt = datetime(2024, 7, 15, 10, 30)
print(dt)

# 格式化
print(now.strftime("%Y-%m-%d %H:%M:%S"))  # 2024-07-15 10:30:45
print(now.isoformat())                     # ISO 8601 格式

# 解析
dt = datetime.strptime("2024-07-15", "%Y-%m-%d")

# 时间运算
tomorrow = today + timedelta(days=1)
next_week = now + timedelta(weeks=1)
diff = tomorrow - today

# 时间戳
timestamp = now.timestamp()  # Unix 时间戳
dt = datetime.fromtimestamp(timestamp)
```

## 📝 10. logging - 日志记录

```python
import logging

# 基本配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 记录日志
logging.debug("调试信息")
logging.info("普通信息")
logging.warning("警告")
logging.error("错误")
logging.critical("致命")

# 命名 logger
logger = logging.getLogger(__name__)
logger.info("模块日志")

# 配置到文件
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)
```

## 🎯 总结

**Python 标准库核心要点**：
- ✅ 10 个必学模块（os/sys/pathlib/json/re/collections/itertools/functools/datetime/logging）
- ✅ pathlib 替代 os.path（推荐）
- ✅ lru_cache 加速函数调用
- ✅ Counter、defaultdict、deque 实用
- ✅ itertools 迭代器工具
- ✅ logging 替代 print
- ⚠️ 不要重复造轮子
- ⚠️ 优先用标准库，无第三方依赖

**下一步：** [🌐 requests HTTP](/03-libraries/requests) — 最常用的 HTTP 库


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
