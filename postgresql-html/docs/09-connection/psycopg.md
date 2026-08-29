---
title: Psycopg Python 驱动
date: 2026-08-15  # date-auto-injected
description: Python 连接 PostgreSQL
---

# Psycopg Python 驱动

> **TL;DR**：Psycopg = PG 最流行的 **Python 驱动**。**Psycopg 3 是新一代**（异步 + 类型注解）。**Django / SQLAlchemy / pandas** 都用它。

## 一句话定义

```
Psycopg = Python 连接 PG 的标准库
        = 同步（psycopg2 / psycopg 3 sync）
        = 异步（psycopg 3 async）
```

## 安装

```bash
# Psycopg 3（推荐）
pip install psycopg[binary,pool]

# Psycopg 2（旧版兼容）
pip install psycopg2-binary
```

## 基本使用

### Psycopg 3（推荐）

```python
import psycopg

# 1. 连接
conn = psycopg.connect(
    "host=localhost dbname=mydb user=postgres password=xxx"
)

# 2. 自动提交模式
conn = psycopg.connect("...", autocommit=True)

# 3. 简单查询
with conn.cursor() as cur:
    cur.execute("SELECT version()")
    row = cur.fetchone()
    print(row[0])

# 4. 参数化查询（防 SQL 注入）
with conn.cursor() as cur:
    cur.execute(
        "SELECT * FROM users WHERE id = %s",
        (123,)
    )
    rows = cur.fetchall()

# 5. 上下文管理（自动关闭）
with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print(cur.fetchone())

# 6. 事务
with psycopg.connect("...") as conn:
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("INSERT INTO users ...")
        cur.execute("UPDATE ...")
```

### DictCursor

```python
import psycopg
from psycopg.rows import dict_row

with psycopg.connect("...") as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, name FROM users")
        for row in cur:
            print(row['name'])  # 直接按字段名访问
```

## 连接池

```python
from psycopg_pool import ConnectionPool

# 1. 创建连接池
pool = ConnectionPool(
    "host=localhost dbname=mydb user=postgres password=xxx",
    min_size=2,
    max_size=20,
    timeout=30
)

# 2. 使用
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (123,))
        row = cur.fetchone()

# 3. 关闭池
pool.close()
```

## 异步

```python
import psycopg
import asyncio

async def main():
    # 异步连接
    conn = await psycopg.AsyncConnection.connect(
        "host=localhost dbname=mydb user=postgres password=xxx"
    )
    
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM users WHERE id = %s", (123,))
        row = await cur.fetchone()
        print(row)
    
    await conn.close()

asyncio.run(main())
```

## COPY 协议（最快）

```python
import psycopg

with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        # 1. 准备 COPY
        with cur.copy("COPY users (name, email) FROM STDIN") as copy:
            # 2. 写入数据
            for user in users:
                copy.write_row((user.name, user.email))
        
        # 100 万行约 5 秒
```

## 类型适配

```python
from psycopg.types.json import Jsonb
from datetime import datetime

with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        # JSONB
        cur.execute(
            "INSERT INTO events (data) VALUES (%s)",
            (Jsonb({"key": "value"}),)
        )
        
        # datetime
        cur.execute(
            "INSERT INTO events (ts) VALUES (%s)",
            (datetime.now(),)
        )
        
        # UUID
        import uuid
        cur.execute(
            "INSERT INTO users (id) VALUES (%s)",
            (uuid.uuid4(),)
        )
```

## SQLAlchemy 集成

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://user:pass@host/dbname")

with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")
    for row in result:
        print(row)
```

## Django 集成

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'postgres',
        'PASSWORD': 'xxx',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

## 常见错误

### 1. 连接超时

```python
# 增加 timeout
conn = psycopg.connect("... connect_timeout=10 ...")
```

### 2. SSL 配置

```python
# 强制 SSL
conn = psycopg.connect("... sslmode=require ...")

# 自签证书
conn = psycopg.connect("... sslmode=verify-full sslrootcert=/path/to/ca.crt ...")
```

### 3. 编码问题

```python
# 强制 UTF-8
conn = psycopg.connect("...", client_encoding="UTF8")
```

## 实战案例

### 案例 1：批量导入 100 万行

```python
import psycopg
from psycopg_pool import ConnectionPool

pool = ConnectionPool("...", max_size=5)

users = [(f"user{i}", f"user{i}@example.com") for i in range(1000000)]

with pool.connection() as conn:
    with conn.cursor() as cur:
        with cur.copy("COPY users (name, email) FROM STDIN") as copy:
            for user in users:
                copy.write_row(user)
# 100 万行约 10 秒
```

### 案例 2：流式查询大表

```python
with psycopg.connect("...") as conn:
    with conn.cursor(name="streaming_cursor") as cur:  # 服务端游标
        cur.execute("SELECT * FROM huge_table")
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                process(row)
```

## 一句话总结

> **Psycopg 3 = Python 连接 PG 的现代标准**：**同步 + 异步 + 类型注解 + 连接池**。**COPY 协议批量导入 100 万行 10 秒**。**Django / SQLAlchemy / pandas** 都基于它。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
