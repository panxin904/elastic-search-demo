---
title: 安全最佳实践
---

# 🛡️ 安全最佳实践

> Web 应用安全至关重要。本章总结 Python Web 开发中**最常见的安全威胁**和防护措施。

## 🎯 OWASP Top 10

```
OWASP（Open Web Application Security Project）Top 10：
1. 注入（Injection）
2. 身份认证失效（Broken Authentication）
3. 敏感数据泄露（Sensitive Data Exposure）
4. XML 外部实体（XXE）
5. 访问控制失效（Broken Access Control）
6. 安全配置错误（Security Misconfiguration）
7. 跨站脚本（XSS）
8. 不安全的反序列化（Insecure Deserialization）
9. 使用含已知漏洞的组件
10. 日志和监控不足
```

## 🔒 1. 注入攻击

### SQL 注入

```python
# ❌ 危险：字符串拼接
def login_bad(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
# 攻击：username = "admin' OR '1'='1"

# ✅ 安全：参数化查询
def login_good(username, password):
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    return db.execute(query, (username, hash_password(password)))
```

### SQLAlchemy 安全写法

```python
# ✅ SQLAlchemy（自动参数化）
user = session.query(User).filter_by(username=username).first()

# ✅ SQLAlchemy Core
from sqlalchemy import text
stmt = text("SELECT * FROM users WHERE username = :u")
result = session.execute(stmt, {"u": username})
```

### ORM 注入（SQLAlchemy）

```python
# SQLAlchemy 1.4+ 默认安全
# order_by() 不允许列名参数化（防 SQL 注入）
# 但 filter() 中的字符串拼接仍危险

# ❌ 危险
query = session.query(User).filter(f"username = '{username}'")

# ✅ 安全
query = session.query(User).filter(User.username == username)
```

### NoSQL 注入（MongoDB）

```python
# ❌ 危险：直接传用户输入
def find_user_bad(username):
    return db.users.find_one({"username": username})
# 攻击：username = {"$gt": ""}

# ✅ 安全：使用类型校验
from pydantic import BaseModel, constr

class UsernameInput(BaseModel):
    username: constr(min_length=1, max_length=50, regex=r"^[a-zA-Z0-9_]+$")

def find_user_good(username: str):
    # 先验证输入
    validated = UsernameInput(username=username)
    return db.users.find_one({"username": validated.username})
```

### 命令注入

```python
import subprocess

# ❌ 危险：shell=True
def list_files_bad(directory):
    return subprocess.check_output(f"ls {directory}", shell=True)
# 攻击：directory = "; rm -rf /"

# ✅ 安全：列表参数
def list_files_good(directory):
    # 先验证
    if not directory.startswith("/allowed/"):
        raise ValueError("Invalid directory")
    return subprocess.check_output(["ls", directory])
```

## 🔒 2. 身份认证

### 密码安全

```python
from passlib.context import CryptContext

# ✅ 密码哈希（使用 bcrypt / argon2）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ✅ 验证
hashed = hash_password("my_secret")
print(verify_password("my_secret", hashed))  # True
print(verify_password("wrong", hashed))       # False

# ❌ 禁止明文存储密码
# ❌ 禁止使用 MD5 / SHA1（已不安全）
# ❌ 禁止自己实现加密算法
```

### JWT 最佳实践

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-very-long-random-secret-key"  # 至少 32 字节
ALGORITHM = "HS256"

def create_token(data: dict, expires_minutes: int = 15) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload["iat"] = datetime.utcnow()  # 签发时间
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token 已过期")
    except jwt.JWTError:
        raise ValueError("Token 无效")

# ❌ 错误：使用不安全的算法
# jwt.encode(payload, key, algorithm="none")  # 危险！
# ❌ 错误：硬编码密钥
# jwt.encode(payload, "secret", algorithm="HS256")
# ✅ 正确：使用环境变量
# import os
# SECRET_KEY = os.environ["JWT_SECRET"]
```

### 密码策略

```python
import re
from pydantic import BaseModel, validator

class PasswordSchema(BaseModel):
    password: str
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError("密码至少 12 位")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("密码必须包含特殊字符")
        return v

# ❌ 不要限制太严格（如必须包含特殊字符）
# ❌ 不要定期要求修改密码（NIST 不推荐）
# ✅ 推荐：密码 + 多因素认证
```

## 🔒 3. 访问控制

### 最小权限原则

```python
# ❌ 危险：所有用户都能访问
@app.get("/admin/users")
def list_all_users():
    return db.query("SELECT * FROM users")

# ✅ 安全：基于角色
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

def require_role(required_role: Role):
    def dependency(current_user = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(403, "权限不足")
        return current_user
    return dependency

@app.get("/admin/users")
def list_all_users(_ = Depends(require_role(Role.ADMIN))):
    return db.query("SELECT * FROM users")
```

### 资源所有权检查

```python
# ❌ 危险：任何人都能查看任何订单
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    return db.get_order(order_id)

# ✅ 安全：检查所有权
@app.get("/orders/{order_id}")
def get_order(order_id: int, user = Depends(get_current_user)):
    order = db.get_order(order_id)
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(403, "无权访问此订单")
    return order
```

## 🔒 4. XSS 防护

### 输出编码

```python
# ❌ 危险：直接返回用户输入
@app.get("/search")
def search(q: str):
    return f"<h1>搜索结果：{q}</h1>"

# ✅ 安全：使用模板引擎（自动转义）
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/search")
def search(request: Request, q: str):
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q  # Jinja2 自动 HTML 转义
    })
```

```html
<!-- templates/search.html -->
<h1>搜索结果：{{ query }}</h1>
<!-- Jinja2 会自动转义 HTML 特殊字符 -->
```

### Content Security Policy

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## 🔒 5. CSRF 防护

### CSRF Token

```python
import secrets
from fastapi import FastAPI, Form, Depends, HTTPException

app = FastAPI()

# 生成 CSRF Token
@app.get("/csrf-token")
def get_csrf_token():
    token = secrets.token_urlsafe(32)
    response.set_cookie("csrf_token", token, httponly=True, secure=True)
    return {"csrf_token": token}

# 验证 CSRF Token
def verify_csrf(token: str, cookie_token: str):
    if not token or token != cookie_token:
        raise HTTPException(403, "CSRF 验证失败")
```

### SameSite Cookie

```python
response.set_cookie(
    "session_id",
    value,
    httponly=True,      # 防 JS 访问
    secure=True,        # 仅 HTTPS
    samesite="Strict",   # 防 CSRF
    max_age=3600
)
```

## 🔒 6. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "请求过于频繁，请稍后再试"}
    )

@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data(request: Request):
    return {"data": "..."}
```

## 🔒 7. 敏感数据保护

### 加密存储

```python
from cryptography.fernet import Fernet

# 生成密钥（保存到环境变量）
# key = Fernet.generate_key()

# 加密
def encrypt_data(plaintext: str) -> bytes:
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(plaintext.encode())

# 解密
def decrypt_data(ciphertext: bytes) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(ciphertext).decode()

# ✅ 存储敏感数据（身份证、银行卡等）
encrypted_id = encrypt_data(user.id_card)
db.save(id_card=encrypted_id)

# ✅ 解密显示
display_id = decrypt_data(user.id_card)
```

### 日志脱敏

```python
import re

def mask_sensitive_data(text: str) -> str:
    """日志脱敏"""
    # 身份证
    text = re.sub(r'\d{17}[\dXx]', '***ID***', text)
    # 手机号
    text = re.sub(r'1[3-9]\d{9}', '***PHONE***', text)
    # 邮箱
    text = re.sub(r'[\w.]+@[\w.]+', '***EMAIL***', text)
    # 银行卡
    text = re.sub(r'\d{16,19}', '***CARD***', text)
    return text

# 日志过滤器
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        record.msg = mask_sensitive_data(str(record.msg))
        return True

logger = logging.getLogger()
logger.addFilter(SensitiveDataFilter())
```

## 🔒 8. HTTPS 配置

```python
# Nginx 反向代理
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 安全 Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

## 🔒 9. 输入验证（Pydantic）

```python
from pydantic import BaseModel, Field, validator
import re

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, regex=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., regex=r"^[\w.-]+@[\w.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)
    website: str = Field(None, regex=r"^https?://")
    
    @validator("username")
    def username_not_reserved(cls, v):
        if v.lower() in ["admin", "root", "system"]:
            raise ValueError("保留用户名")
        return v
```

## 🔒 10. 安全清单

```markdown
✅ 注入防护
  - 参数化查询
  - ORM 使用
  - 输入验证

✅ 认证
  - bcrypt / argon2 哈希密码
  - JWT / Session
  - 多因素认证

✅ 授权
  - 基于角色的访问控制（RBAC）
  - 资源所有权检查
  - 最小权限原则

✅ 敏感数据
  - 加密存储
  - 日志脱敏
  - 传输加密（HTTPS）

✅ 配置
  - 关闭调试模式
  - 隐藏错误详情
  - 定期更新依赖

✅ 通信
  - HTTPS / TLS
  - HSTS
  - 安全 Headers

✅ 输入
  - 服务端验证
  - 白名单校验
  - 长度限制

✅ 会话
  - HttpOnly Cookie
  - Secure Cookie
  - SameSite

✅ 监控
  - 日志记录
  - 异常告警
  - 异常行为检测
```

## 🛠️ 实战：安全 FastAPI 应用

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

app = FastAPI()

# 1. 限制可信主机
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# 2. CORS（谨慎配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # 不要用 *
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 3. 速率限制
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# 4. 安全 Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# 5. 输入验证
class LoginInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=12)

# 6. 认证 + 授权
async def get_current_user(token: str = Depends(oauth2_scheme), 
                          db: Session = Depends(get_db)):
    user = verify_token(token, db)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user

def require_admin(user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin required")
    return user

# 7. 速率限制应用
@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginInput, db: Session = Depends(get_db)):
    user = authenticate(data.username, data.password, db)
    if not user:
        # 不要泄露是用户名错了还是密码错了
        raise HTTPException(401, "用户名或密码错误")
    token = create_token(user)
    return {"token": token}
```

## 🎯 总结

**安全最佳实践核心要点**：
- ✅ SQL 注入：使用参数化查询
- ✅ XSS：输出编码 + CSP
- ✅ CSRF：Token + SameSite Cookie
- ✅ 密码：bcrypt / argon2 哈希
- ✅ 认证：JWT + 多因素
- ✅ 授权：RBAC + 资源所有权
- ✅ HTTPS：TLS 1.2+
- ✅ 输入验证：白名单 + 长度限制
- ✅ 速率限制
- ✅ 监控 + 告警
- ⚠️ 安全是持续过程（不是一次性）
- ⚠️ 依赖定期更新（修补漏洞）

**下一步：** [🎯 爬虫基础](/05-scraping/basics) — Python 爬虫入门


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

## 🔗 相关阅读 · 09 工程化

<!-- xlink-subpage-injected:do-not-edit -->

本页（09 工程化）相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
