---
title: A03 注入攻击
---

# A03 · Injection（注入攻击）

## 一句话总结

> **注入 = 把代码当数据执行**。**SQL 注入 / NoSQL 注入 / 命令注入 / LDAP 注入 / XSS（HTML 注入）**。**核心防御：参数化查询 / ORMs / 输入校验 + 输出转义**。

---

## SQL 注入经典案例

```http
POST /api/v1/login
{
    "username": "admin' OR '1'='1",
    "password": "anything"
}
```

```sql
-- 查询被拼接 → 恒真
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
```

```python
# ❌ 字符串拼接
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")

# ✅ 参数化查询（Prepared Statement）
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

## 各类注入一览

| 类型 | 攻击向量 | 防御 |
|------|---------|------|
| **SQL 注入** | `' OR 1=1 --` | 参数化查询 |
| **NoSQL 注入** | `{"$gt": ""}` | MongoDB 类型校验 |
| **OS 命令注入** | `; rm -rf /` | 白名单命令 + 沙箱 |
| **LDAP 注入** | `*)(&` | 框架转义 |
| **XSS（HTML 注入）** | `<script>alert(1)</script>` | 输出转义 |
| **XPATH 注入** | `' or '1'='1` | XQuery 参数化 |
| **模板注入（SSTI）** | `{{7*7}}` | 不用字符串拼接 |

## 实战：SQL 注入读取整张表

```sql
-- 攻击 payload
' UNION SELECT username, password FROM users --
```

```sql
-- 防御 1：参数化
SELECT * FROM products WHERE id = ?

-- 防御 2：ORM（Hibernate / SQLAlchemy / MyBatis #{}）
Product.find_by(id=123)

-- 防御 3：最小权限（应用账号只读 + 限定表）
GRANT SELECT ON shop.products TO 'app'@'%';
```

## 实战：Command Injection（Python）

```python
import subprocess

# ❌ 字符串拼接（危险）
user_input = input("Domain: ")
result = subprocess.run(f"nslookup {user_input}", shell=True)

# 用户输入："; rm -rf /; echo " → 直接删库

# ✅ 用列表 + shell=False
result = subprocess.run(["nslookup", user_input], shell=False, capture_output=True)
```

## 实战：MongoDB NoSQL 注入

```python
# ❌ 接受 JSON 直接传 MongoDB
db.users.find({
    "username": request.json["username"],
    "password": request.json["password"]
})

# 攻击者 POST：
# {"username": "admin", "password": {"$gt": ""}}
# → password 永远为真

# ✅ 类型校验
from pydantic import BaseModel, constr
class LoginReq(BaseModel):
    username: constr(min_length=1, max_length=64)
    password: constr(min_length=1, max_length=128)
```

## 防御清单

| 措施 | 落地 |
|------|------|
| **参数化查询** | SQLAlchemy / MyBatis #{} / Hibernate |
| **ORM** | 95% 场景 ORM 够用 |
| **输入校验** | 白名单 + 长度限制 |
| **输出转义** | Thymeleaf / React 自动转义 |
| **最小权限** | DB 账号降权 |
| **WAF** | ModSecurity / Cloudflare |

## 关联章节

- **mysql** / **postgresql** → SQL 注入原理与防御
- **cloud-native** → 容器逃逸（含命令执行）
- **01-web-top10/a05-misconfig**：A05 配置错误含 SQL 调试模式

## 一句话总结

> **A03 注入 = 把代码当数据**。**核心防御：参数化查询 + ORM + 输入校验 + 输出转义**。**拼接字符串 = 危险**。
