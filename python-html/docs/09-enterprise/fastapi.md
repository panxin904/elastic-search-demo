---
title: FastAPI Web 实战
---

# 🌐 FastAPI Web 实战

> **FastAPI** 是 Python **现代、高性能**的 Web 框架。基于 **Starlette**（ASGI）+ **Pydantic**（数据验证）+ **类型提示**，是构建 REST API 的**首选**。

## 🎯 FastAPI 优势

```
✅ 高性能（接近 Node.js / Go）
✅ 自动生成 OpenAPI 文档
✅ 类型提示 + 自动验证
✅ 异步支持（async/await）
✅ 依赖注入
✅ 现代化（基于 OpenAPI / JSON Schema）
✅ 测试友好
```

## 🚀 快速开始

### 安装

```bash
pip install fastapi uvicorn[standard]
```

### Hello World

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

```bash
# 运行
uvicorn main:app --reload

# 访问
# http://localhost:8000
# API 文档： http://localhost:8000/docs
```

## 📝 路径参数

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    """item_id 自动转为 int"""
    return {"item_id": item_id}

@app.get("/items/{item_id:path}")
def read_item_path(item_id: str):
    """item_id 包含 /（:path）"""
    return {"item_id": item_id}

# 枚举
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    """model_name 必须是枚举值"""
    return {"model_name": model_name}
```

## 🔍 查询参数

```python
from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/items/")
def read_items(
    skip: int = 0,             # 必填（无默认值）
    limit: int = 10,           # 可选（有默认值）
    q: Optional[str] = None    # 可选 + Optional
):
    return {"skip": skip, "limit": limit, "q": q}

# 必填参数
@app.get("/items/required")
def required(q: str):  # 无默认值 = 必填
    return {"q": q}

# 多类型
@app.get("/types")
def types(
    name: str,
    age: int,
    score: float,
    active: bool = True,
    tags: list = [],
):
    return locals()
```

## 📦 请求体（Pydantic）

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

app = FastAPI()

# 1. 基础模型
class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True

@app.post("/users/")
def create_user(user: User):
    return user

# 2. 字段验证
class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="价格必须大于 0")
    quantity: int = Field(default=0, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Apple",
                "price": 5.0,
                "quantity": 100
            }
        }

@app.post("/products/")
def create_product(product: Product):
    return product

# 3. 嵌套模型
class Address(BaseModel):
    street: str
    city: str
    zipcode: str

class UserWithAddress(BaseModel):
    name: str
    age: int
    address: Address

# 4. 列表
class Order(BaseModel):
    items: List[str]
    total: float

# 5. Optional 字段
class Profile(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# 6. Email 验证
class UserEmail(BaseModel):
    email: EmailStr  # 自动验证邮箱格式

# 7. 自定义验证器
class UserAge(BaseModel):
    name: str
    age: int
    
    @validator("age")
    def age_must_be_positive(cls, v):
        if v < 0 or v > 150:
            raise ValueError("年龄必须在 0-150 之间")
        return v
```

## 📤 响应模型

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class UserIn(BaseModel):
    name: str
    password: str

class UserOut(BaseModel):
    name: str
    created_at: str

# 输入 UserIn，输出 UserOut（不返回密码）
@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    return {
        "name": user.name,
        "created_at": "2024-07-15"
    }

# 响应模型列表
@app.get("/users", response_model=list[UserOut])
def list_users():
    return [...]

# 排除字段
class UserDetail(BaseModel):
    name: str
    email: str
    password: str
    
    class Config:
        fields = {"password": {"exclude": True}}

@app.get("/user", response_model=UserDetail)
def get_user():
    return {"name": "Alice", "email": "alice@example.com", "password": "xxx"}
# password 不会出现在响应中
```

## 🔌 依赖注入

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Optional

app = FastAPI()

# 1. 函数依赖
def get_db():
    """模拟数据库连接"""
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

# 2. 类依赖
class Database:
    def __init__(self):
        self.connection = "fake_connection"
    
    def close(self):
        pass

def get_database():
    db = Database()
    try:
        yield db
    finally:
        db.close()

# 3. 嵌套依赖
def get_token(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return verify_token(token)

def get_current_user(token: str = Depends(get_token)):
    user = lookup_user_by_token(token)
    return user

@app.get("/me")
def read_me(user = Depends(get_current_user)):
    return user

# 4. 全局依赖
app = FastAPI(dependencies=[Depends(get_token)])
```

## 🚨 异常处理

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# 1. HTTPException
@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "true"}
        )
    return {"item_id": item_id}

# 2. 自定义异常
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} not found"}
    )

@app.get("/items2/{item_id}")
def read_item2(item_id: int):
    if item_id != 1:
        raise ItemNotFoundError(item_id)
    return {"item_id": item_id}

# 3. 验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors()
        }
    )
```

## 🔐 认证与授权

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

# 1. Bearer Token 认证
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user = verify_token(token)  # 你的 token 验证逻辑
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/users/me")
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

# 2. OAuth2 + JWT
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user
```

## 🛠️ 实战：完整用户系统

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import models
import schemas

# 1. 创建应用
app = FastAPI(title="User API")

# 2. 数据库
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 4. 依赖：当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), 
                          db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 5. 路由
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, 
                          hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), 
          db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user
```

## 🛠️ 异步与数据库

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db"
)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

## 🛠️ 中间件

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义中间件
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

## 🛠️ 测试

```python
from fastapi.testclient import TestClient

def test_create_user():
    client = TestClient(app)
    response = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

## 🎯 总结

**FastAPI 核心要点**：
- ✅ 路径参数 + 查询参数 + 请求体
- ✅ Pydantic 自动数据验证
- ✅ 依赖注入（嵌套）
- ✅ 自动 OpenAPI 文档
- ✅ 异步支持（async/await）
- ✅ JWT / OAuth2 认证
- ✅ 异常处理（统一）
- ✅ 中间件（CORS、监控）
- ⚠️ 异步 vs 同步（不要混用）
- ⚠️ 数据库连接池

**下一步：** [🐳 Docker 部署](/09-enterprise/docker) — 容器化 Python 应用


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
